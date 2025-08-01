from src.code_confluence_flow_bridge.logging.trace_utils import (
    activity_id_var,
    activity_name_var,
    workflow_id_var,
    workflow_run_id_var,
)
from src.code_confluence_flow_bridge.processor.db.graph_db.code_confluence_graph import (
    CodeConfluenceGraph,
)

import traceback
from typing import Dict, List, Optional, Set, Union

from loguru import logger
from neo4j import AsyncManagedTransaction, AsyncSession, Record
from neomodel import adb
from temporalio.exceptions import ApplicationError
from unoplat_code_confluence_commons.graph_models.code_confluence_file import (
    CodeConfluenceFile,
)
from unoplat_code_confluence_commons.graph_models.code_confluence_git_repository import (
    CodeConfluenceGitRepository,
)
from unoplat_code_confluence_commons.graph_models.code_confluence_package import (
    CodeConfluencePackage,
)


class CodeConfluenceGraphDeletion:
    """
    Class for handling deletion operations in the Code Confluence graph database.
    Uses shared Neo4j connection pool via CodeConfluenceGraph instance.
    """
    
    def __init__(self, code_confluence_graph: CodeConfluenceGraph) -> None:
        self.code_confluence_graph = code_confluence_graph
    
    async def _get_repository_by_qualified_name_txn(self, tx: AsyncManagedTransaction, qualified_name: str) -> Optional[Record]:
        """
        Transaction function to get repository by qualified name
        """
        query = """
        MATCH (r:CodeConfluenceGitRepository {qualified_name: $qualified_name})
        RETURN r
        """
        result = await tx.run(query, {"qualified_name": qualified_name})
        return await result.single()
    
    async def _get_repository_codebases_txn(self, tx: AsyncManagedTransaction, repository_qualified_name: str) -> List[Record]:
        """
        Transaction function to get all codebases for a repository
        """
        query = """
        MATCH (r:CodeConfluenceGitRepository {qualified_name: $repository_qualified_name})
        MATCH (r)-[:CONTAINS_CODEBASE]->(c:CodeConfluenceCodebase)
        RETURN c
        """
        result = await tx.run(query, {"repository_qualified_name": repository_qualified_name})
        return [record async for record in result]
    
    async def _get_codebase_packages_txn(self, tx: AsyncManagedTransaction, codebase_qualified_name: str) -> List[Record]:
        """
        Transaction function to get all packages for a codebase
        """
        query = """
        MATCH (c:CodeConfluenceCodebase {qualified_name: $codebase_qualified_name})
        MATCH (c)-[:CONTAINS_PACKAGE]->(p:CodeConfluencePackage)
        RETURN p
        """
        result = await tx.run(query, {"codebase_qualified_name": codebase_qualified_name})
        return [record async for record in result]
    
    async def _get_package_files_txn(self, tx: AsyncManagedTransaction, package_qualified_name: str) -> List[Record]:
        """
        Transaction function to get all files for a package
        """
        query = """
        MATCH (p:CodeConfluencePackage {qualified_name: $package_qualified_name})
        MATCH (p)-[:CONTAINS_FILE]->(f:CodeConfluenceFile)
        RETURN f
        """
        result = await tx.run(query, {"package_qualified_name": package_qualified_name})
        return [record async for record in result]
    
    async def _get_package_subpackages_txn(self, tx: AsyncManagedTransaction, package_qualified_name: str) -> List[Record]:
        """
        Transaction function to get all subpackages for a package
        """
        query = """
        MATCH (p:CodeConfluencePackage {qualified_name: $package_qualified_name})
        MATCH (p)-[:CONTAINS_PACKAGE]->(sp:CodeConfluencePackage)
        RETURN sp
        """
        result = await tx.run(query, {"package_qualified_name": package_qualified_name})
        return [record async for record in result]
    
    async def _get_codebase_metadata_txn(self, tx: AsyncManagedTransaction, codebase_qualified_name: str) -> List[Record]:
        """
        Transaction function to get all package manager metadata for a codebase
        """
        query = """
        MATCH (c:CodeConfluenceCodebase {qualified_name: $codebase_qualified_name})
        MATCH (c)-[:HAS_PACKAGE_MANAGER_METADATA]->(m:CodeConfluencePackageManagerMetadata)
        RETURN m
        """
        result = await tx.run(query, {"codebase_qualified_name": codebase_qualified_name})
        return [record async for record in result]
    
    async def _get_file_relationships_txn(self, tx: AsyncManagedTransaction, file_paths: List[str]) -> Dict[str, List[Record]]:
        """
        Transaction function to get all relationships for files that need to be deleted
        """
        if not file_paths:
            return {"uses_feature": [], "part_of_package": []}
        
        # Get USES_FEATURE relationships
        uses_feature_query = """
        MATCH (f:CodeConfluenceFile)-[r:USES_FEATURE]->(feat:CodeConfluenceFrameworkFeature)
        WHERE f.file_path IN $file_paths
        RETURN f.file_path as file_path, feat.qualified_name as feature_qualified_name, r
        """
        
        # Get PART_OF_PACKAGE relationships  
        part_of_package_query = """
        MATCH (f:CodeConfluenceFile)-[r:PART_OF_PACKAGE]->(p:CodeConfluencePackage)
        WHERE f.file_path IN $file_paths
        RETURN f.file_path as file_path, p.qualified_name as package_qualified_name, r
        """
        
        uses_feature_result = await tx.run(uses_feature_query, {"file_paths": file_paths})
        part_of_package_result = await tx.run(part_of_package_query, {"file_paths": file_paths})
        
        return {
            "uses_feature": [record async for record in uses_feature_result],
            "part_of_package": [record async for record in part_of_package_result]
        }
    
    async def _get_package_relationships_txn(self, tx: AsyncManagedTransaction, package_qualified_names: List[str]) -> Dict[str, List[Record]]:
        """
        Transaction function to get all relationships for packages that need to be deleted
        """
        if not package_qualified_names:
            return {"contains_package": [], "part_of_package": [], "part_of_codebase": [], "contains_file": []}
        
        # Get CONTAINS_PACKAGE relationships (parent -> child)
        contains_package_query = """
        MATCH (parent:CodeConfluencePackage)-[r:CONTAINS_PACKAGE]->(child:CodeConfluencePackage)
        WHERE parent.qualified_name IN $package_qualified_names
        RETURN parent.qualified_name as parent_package, child.qualified_name as child_package, r
        """
        
        # Get PART_OF_PACKAGE relationships (child -> parent)
        part_of_package_query = """
        MATCH (child:CodeConfluencePackage)-[r:PART_OF_PACKAGE]->(parent:CodeConfluencePackage)
        WHERE child.qualified_name IN $package_qualified_names
        RETURN child.qualified_name as child_package, parent.qualified_name as parent_package, r
        """
        
        # Get PART_OF_CODEBASE relationships
        part_of_codebase_query = """
        MATCH (p:CodeConfluencePackage)-[r:PART_OF_CODEBASE]->(c:CodeConfluenceCodebase)
        WHERE p.qualified_name IN $package_qualified_names
        RETURN p.qualified_name as package_qualified_name, c.qualified_name as codebase_qualified_name, r
        """
        
        # Get CONTAINS_FILE relationships
        contains_file_query = """
        MATCH (p:CodeConfluencePackage)-[r:CONTAINS_FILE]->(f:CodeConfluenceFile)
        WHERE p.qualified_name IN $package_qualified_names
        RETURN p.qualified_name as package_qualified_name, f.file_path as file_path, r
        """
        
        contains_package_result = await tx.run(contains_package_query, {"package_qualified_names": package_qualified_names})
        part_of_package_result = await tx.run(part_of_package_query, {"package_qualified_names": package_qualified_names})
        part_of_codebase_result = await tx.run(part_of_codebase_query, {"package_qualified_names": package_qualified_names})
        contains_file_result = await tx.run(contains_file_query, {"package_qualified_names": package_qualified_names})
        
        return {
            "contains_package": [record async for record in contains_package_result],
            "part_of_package": [record async for record in part_of_package_result],
            "part_of_codebase": [record async for record in part_of_codebase_result],
            "contains_file": [record async for record in contains_file_result]
        }
    
    async def _get_codebase_relationships_txn(self, tx: AsyncManagedTransaction, codebase_qualified_names: List[str]) -> Dict[str, List[Record]]:
        """
        Transaction function to get all relationships for codebases that need to be deleted
        """
        if not codebase_qualified_names:
            return {"uses_framework": []}
        
        # Get USES_FRAMEWORK relationships
        uses_framework_query = """
        MATCH (c:CodeConfluenceCodebase)-[r:USES_FRAMEWORK]->(f:CodeConfluenceFramework)
        WHERE c.qualified_name IN $codebase_qualified_names
        RETURN c.qualified_name as codebase_qualified_name, f.qualified_name as framework_qualified_name, r
        """
        
        uses_framework_result = await tx.run(uses_framework_query, {"codebase_qualified_names": codebase_qualified_names})
        
        return {
            "uses_framework": [record async for record in uses_framework_result]
        }
    
    async def _delete_files_batch_txn(self, tx: AsyncManagedTransaction, file_paths: List[str]) -> Optional[Record]:
        """
        Transaction function to delete multiple files in batch
        Note: CodeConfluenceFile uses file_path as unique identifier, not qualified_name
        """
        if not file_paths:
            # Return empty result
            query = "RETURN 0 as count"
            result = await tx.run(query)
            return await result.single()
        
        query = """
        MATCH (f:CodeConfluenceFile)
        WHERE f.file_path IN $file_paths
        WITH f, f.file_path as path
        DETACH DELETE f
        RETURN count(path) as count
        """
        result = await tx.run(query, {"file_paths": file_paths})
        return await result.single()
    
    async def _delete_package_manager_metadata_batch_txn(self, tx: AsyncManagedTransaction, metadata_qualified_names: List[str]) -> Optional[Record]:
        """
        Transaction function to delete multiple package manager metadata nodes in batch
        """
        if not metadata_qualified_names:
            query = "RETURN 0 as count"
            result = await tx.run(query)
            return await result.single()
        
        query = """
        MATCH (m:CodeConfluencePackageManagerMetadata)
        WHERE m.qualified_name IN $qualified_names
        WITH m, m.qualified_name as name
        DETACH DELETE m
        RETURN count(name) as count
        """
        result = await tx.run(query, {"qualified_names": metadata_qualified_names})
        return await result.single()
    
    async def _delete_packages_batch_txn(self, tx: AsyncManagedTransaction, package_qualified_names: List[str]) -> Optional[Record]:
        """
        Transaction function to delete multiple packages in batch
        """
        if not package_qualified_names:
            query = "RETURN 0 as count"
            result = await tx.run(query)
            return await result.single()
        
        query = """
        MATCH (p:CodeConfluencePackage)
        WHERE p.qualified_name IN $qualified_names
        WITH p, p.qualified_name as name
        DETACH DELETE p
        RETURN count(name) as count
        """
        result = await tx.run(query, {"qualified_names": package_qualified_names})
        return await result.single()
    
    async def _delete_codebases_batch_txn(self, tx: AsyncManagedTransaction, codebase_qualified_names: List[str]) -> Optional[Record]:
        """
        Transaction function to delete multiple codebases in batch
        """
        if not codebase_qualified_names:
            query = "RETURN 0 as count"
            result = await tx.run(query)
            return await result.single()
        
        query = """
        MATCH (c:CodeConfluenceCodebase)
        WHERE c.qualified_name IN $qualified_names
        WITH c, c.qualified_name as name
        DETACH DELETE c
        RETURN count(name) as count
        """
        result = await tx.run(query, {"qualified_names": codebase_qualified_names})
        return await result.single()
    
    async def _delete_repository_txn(self, tx: AsyncManagedTransaction, repository_qualified_name: str) -> Optional[Record]:
        """
        Transaction function to delete a repository
        """
        query = """
        MATCH (r:CodeConfluenceGitRepository {qualified_name: $qualified_name})
        DETACH DELETE r
        RETURN 1 as count
        """
        result = await tx.run(query, {"qualified_name": repository_qualified_name})
        return await result.single()
    
    async def _delete_file_relationships_batch_txn(self, tx: AsyncManagedTransaction, file_paths: List[str]) -> Dict[str, int]:
        """
        Transaction function to delete all relationships for files in batch
        """
        if not file_paths:
            return {"uses_feature_deleted": 0, "part_of_package_deleted": 0}
        
        stats = {}
        
        # Delete USES_FEATURE relationships
        uses_feature_query = """
        MATCH (f:CodeConfluenceFile)-[r:USES_FEATURE]->(feat:CodeConfluenceFrameworkFeature)
        WHERE f.file_path IN $file_paths
        DELETE r
        RETURN count(r) as count
        """
        uses_feature_result = await tx.run(uses_feature_query, {"file_paths": file_paths})
        uses_feature_record = await uses_feature_result.single()
        stats["uses_feature_deleted"] = uses_feature_record["count"] if uses_feature_record else 0
        
        # Delete PART_OF_PACKAGE relationships
        part_of_package_query = """
        MATCH (f:CodeConfluenceFile)-[r:PART_OF_PACKAGE]->(p:CodeConfluencePackage)
        WHERE f.file_path IN $file_paths
        DELETE r
        RETURN count(r) as count
        """
        part_of_package_result = await tx.run(part_of_package_query, {"file_paths": file_paths})
        part_of_package_record = await part_of_package_result.single()
        stats["part_of_package_deleted"] = part_of_package_record["count"] if part_of_package_record else 0
        
        return stats
    
    async def _delete_package_relationships_batch_txn(self, tx: AsyncManagedTransaction, package_qualified_names: List[str]) -> Dict[str, int]:
        """
        Transaction function to delete all relationships for packages in batch
        """
        if not package_qualified_names:
            return {"contains_package_deleted": 0, "part_of_package_deleted": 0, "part_of_codebase_deleted": 0, "contains_file_deleted": 0}
        
        stats = {}
        
        # Delete CONTAINS_PACKAGE relationships (parent -> child)
        contains_package_query = """
        MATCH (parent:CodeConfluencePackage)-[r:CONTAINS_PACKAGE]->(child:CodeConfluencePackage)
        WHERE parent.qualified_name IN $package_qualified_names
        DELETE r
        RETURN count(r) as count
        """
        contains_package_result = await tx.run(contains_package_query, {"package_qualified_names": package_qualified_names})
        contains_package_record = await contains_package_result.single()
        stats["contains_package_deleted"] = contains_package_record["count"] if contains_package_record else 0
        
        # Delete PART_OF_PACKAGE relationships (child -> parent) 
        part_of_package_query = """
        MATCH (child:CodeConfluencePackage)-[r:PART_OF_PACKAGE]->(parent:CodeConfluencePackage)
        WHERE child.qualified_name IN $package_qualified_names
        DELETE r
        RETURN count(r) as count
        """
        part_of_package_result = await tx.run(part_of_package_query, {"package_qualified_names": package_qualified_names})
        part_of_package_record = await part_of_package_result.single()
        stats["part_of_package_deleted"] = part_of_package_record["count"] if part_of_package_record else 0
        
        # Delete PART_OF_CODEBASE relationships
        part_of_codebase_query = """
        MATCH (p:CodeConfluencePackage)-[r:PART_OF_CODEBASE]->(c:CodeConfluenceCodebase)
        WHERE p.qualified_name IN $package_qualified_names
        DELETE r
        RETURN count(r) as count
        """
        part_of_codebase_result = await tx.run(part_of_codebase_query, {"package_qualified_names": package_qualified_names})
        part_of_codebase_record = await part_of_codebase_result.single()
        stats["part_of_codebase_deleted"] = part_of_codebase_record["count"] if part_of_codebase_record else 0
        
        # Delete CONTAINS_FILE relationships
        contains_file_query = """
        MATCH (p:CodeConfluencePackage)-[r:CONTAINS_FILE]->(f:CodeConfluenceFile)
        WHERE p.qualified_name IN $package_qualified_names
        DELETE r
        RETURN count(r) as count
        """
        contains_file_result = await tx.run(contains_file_query, {"package_qualified_names": package_qualified_names})
        contains_file_record = await contains_file_result.single()
        stats["contains_file_deleted"] = contains_file_record["count"] if contains_file_record else 0
        
        return stats
    
    async def _delete_codebase_relationships_batch_txn(self, tx: AsyncManagedTransaction, codebase_qualified_names: List[str]) -> Dict[str, int]:
        """
        Transaction function to delete all relationships for codebases in batch
        """
        if not codebase_qualified_names:
            return {
                "uses_framework_deleted": 0,
                "used_by_deleted": 0,
                "part_of_git_repository_deleted": 0,
                "contains_codebase_deleted": 0,
                "has_package_manager_metadata_deleted": 0
            }
        
        stats = {}
        
        # Delete USES_FRAMEWORK relationships (Codebase → Framework)
        uses_framework_query = """
        MATCH (c:CodeConfluenceCodebase)-[r:USES_FRAMEWORK]->(f:CodeConfluenceFramework)
        WHERE c.qualified_name IN $codebase_qualified_names
        DELETE r
        RETURN count(r) as count
        """
        uses_framework_result = await tx.run(uses_framework_query, {"codebase_qualified_names": codebase_qualified_names})
        uses_framework_record = await uses_framework_result.single()
        stats["uses_framework_deleted"] = uses_framework_record["count"] if uses_framework_record else 0
        
        # Delete USED_BY relationships (Framework → Codebase)
        used_by_query = """
        MATCH (f:CodeConfluenceFramework)-[r:USED_BY]->(c:CodeConfluenceCodebase)
        WHERE c.qualified_name IN $codebase_qualified_names
        DELETE r
        RETURN count(r) as count
        """
        used_by_result = await tx.run(used_by_query, {"codebase_qualified_names": codebase_qualified_names})
        used_by_record = await used_by_result.single()
        stats["used_by_deleted"] = used_by_record["count"] if used_by_record else 0
        
        # Delete PART_OF_GIT_REPOSITORY relationships (Codebase → Repository)
        part_of_git_repository_query = """
        MATCH (c:CodeConfluenceCodebase)-[r:PART_OF_GIT_REPOSITORY]->(repo:CodeConfluenceGitRepository)
        WHERE c.qualified_name IN $codebase_qualified_names
        DELETE r
        RETURN count(r) as count
        """
        part_of_git_repository_result = await tx.run(part_of_git_repository_query, {"codebase_qualified_names": codebase_qualified_names})
        part_of_git_repository_record = await part_of_git_repository_result.single()
        stats["part_of_git_repository_deleted"] = part_of_git_repository_record["count"] if part_of_git_repository_record else 0
        
        # Delete CONTAINS_CODEBASE relationships (Repository → Codebase)
        contains_codebase_query = """
        MATCH (repo:CodeConfluenceGitRepository)-[r:CONTAINS_CODEBASE]->(c:CodeConfluenceCodebase)
        WHERE c.qualified_name IN $codebase_qualified_names
        DELETE r
        RETURN count(r) as count
        """
        contains_codebase_result = await tx.run(contains_codebase_query, {"codebase_qualified_names": codebase_qualified_names})
        contains_codebase_record = await contains_codebase_result.single()
        stats["contains_codebase_deleted"] = contains_codebase_record["count"] if contains_codebase_record else 0
        
        # Delete HAS_PACKAGE_MANAGER_METADATA relationships (Codebase → Metadata)
        has_package_manager_metadata_query = """
        MATCH (c:CodeConfluenceCodebase)-[r:HAS_PACKAGE_MANAGER_METADATA]->(m:CodeConfluencePackageManagerMetadata)
        WHERE c.qualified_name IN $codebase_qualified_names
        DELETE r
        RETURN count(r) as count
        """
        has_package_manager_metadata_result = await tx.run(has_package_manager_metadata_query, {"codebase_qualified_names": codebase_qualified_names})
        has_package_manager_metadata_record = await has_package_manager_metadata_result.single()
        stats["has_package_manager_metadata_deleted"] = has_package_manager_metadata_record["count"] if has_package_manager_metadata_record else 0
        
        return stats
    
    async def delete_repository_by_qualified_name_managed(self, session: AsyncSession, qualified_name: str) -> Dict[str, Union[int, str]]:
        """
        NEW METHOD: Delete a repository and all its related nodes by qualified name using managed transactions.
        
        This method now properly handles all relationships before deleting nodes to avoid Neo4j constraint violations.
        
        Args:
            session: Neo4j async session for managed transactions
            qualified_name: The qualified name of the repository (format: {owner}_{repo_name})
            
        Returns:
            Dict containing deletion statistics including relationship cleanup
            
        Raises:
            ApplicationError: If repository not found or deletion fails
        """
        try:
            # First, check if the repository exists
            repo_record = await session.execute_read(self._get_repository_by_qualified_name_txn, qualified_name)
            if not repo_record:
                raise ApplicationError(
                    f"Repository not found: {qualified_name}",
                    {"repository": qualified_name},
                    {"workflow_id": workflow_id_var.get("")},
                    {"workflow_run_id": workflow_run_id_var.get("")},
                    {"activity_name": activity_name_var.get("")},
                    {"activity_id": activity_id_var.get("")},
                    type="REPOSITORY_NOT_FOUND"
                )
            
            # Initialize statistics (keeping original structure)
            stats: Dict[str, Union[int, str]] = {
                "repository_qualified_name": qualified_name,
                "repositories_deleted": 0,
                "codebases_deleted": 0,
                "packages_deleted": 0,
                "files_deleted": 0,
                "metadata_deleted": 0,
            }
            
            # Get all codebases for the repository
            codebase_records = await session.execute_read(self._get_repository_codebases_txn, qualified_name)
            codebase_qualified_names = [record["c"]["qualified_name"] for record in codebase_records]
            
            # For each codebase, collect all entities to delete
            all_file_paths: List[str] = []
            all_package_qualified_names: List[str] = []
            all_metadata_qualified_names: List[str] = []
            
            for codebase_qn in codebase_qualified_names:
                # Get metadata nodes
                metadata_records = await session.execute_read(self._get_codebase_metadata_txn, codebase_qn)
                metadata_qns = [record["m"]["qualified_name"] for record in metadata_records]
                all_metadata_qualified_names.extend(metadata_qns)
                
                # Get all packages (flat collection, not recursive)
                package_records = await session.execute_read(self._get_codebase_packages_txn, codebase_qn)
                package_qns = [record["p"]["qualified_name"] for record in package_records]
                
                # For each package, get files and subpackages
                packages_to_process = package_qns.copy()
                processed_packages: Set[str] = set()
                
                while packages_to_process:
                    current_pkg_qn = packages_to_process.pop(0)
                    if current_pkg_qn in processed_packages:
                        continue
                    processed_packages.add(current_pkg_qn)
                    all_package_qualified_names.append(current_pkg_qn)
                    
                    # Get files for this package
                    file_records = await session.execute_read(self._get_package_files_txn, current_pkg_qn)
                    file_paths = [record["f"]["file_path"] for record in file_records]
                    all_file_paths.extend(file_paths)
                    
                    # Get subpackages
                    subpackage_records = await session.execute_read(self._get_package_subpackages_txn, current_pkg_qn)
                    subpackage_qns = [record["sp"]["qualified_name"] for record in subpackage_records]
                    packages_to_process.extend(subpackage_qns)
            
            # PHASE 1: Delete all relationships BEFORE deleting nodes (Critical for Neo4j constraints)
            
            # 1. Delete codebase relationships first (highest level)
            total_codebase_relationships = 0
            if codebase_qualified_names:
                codebase_rel_stats = await session.execute_write(self._delete_codebase_relationships_batch_txn, codebase_qualified_names)
                total_codebase_relationships = sum(codebase_rel_stats.values())
                logger.info(f"Deleted codebase relationships: {codebase_rel_stats}")
            
            # 2. Delete package relationships
            total_package_relationships = 0
            if all_package_qualified_names:
                package_rel_stats = await session.execute_write(self._delete_package_relationships_batch_txn, all_package_qualified_names)
                total_package_relationships = sum(package_rel_stats.values())
                logger.info(f"Deleted package relationships: {package_rel_stats}")
            
            # 3. Delete file relationships
            total_file_relationships = 0
            if all_file_paths:
                file_rel_stats = await session.execute_write(self._delete_file_relationships_batch_txn, all_file_paths)
                total_file_relationships = sum(file_rel_stats.values())
                logger.info(f"Deleted file relationships: {file_rel_stats}")
            
            # PHASE 2: Now safely delete nodes in dependency order
            
            # 4. Delete files (now relationship-free)
            if all_file_paths:
                file_delete_record = await session.execute_write(self._delete_files_batch_txn, all_file_paths)
                stats["files_deleted"] = file_delete_record["count"] if file_delete_record else 0
            
            # 5. Delete package manager metadata
            if all_metadata_qualified_names:
                metadata_delete_record = await session.execute_write(self._delete_package_manager_metadata_batch_txn, all_metadata_qualified_names)
                stats["metadata_deleted"] = metadata_delete_record["count"] if metadata_delete_record else 0
            
            # 6. Delete packages (now relationship-free)
            if all_package_qualified_names:
                package_delete_record = await session.execute_write(self._delete_packages_batch_txn, all_package_qualified_names)
                stats["packages_deleted"] = package_delete_record["count"] if package_delete_record else 0
            
            # 7. Delete codebases (now relationship-free)
            if codebase_qualified_names:
                codebase_delete_record = await session.execute_write(self._delete_codebases_batch_txn, codebase_qualified_names)
                stats["codebases_deleted"] = codebase_delete_record["count"] if codebase_delete_record else 0
            
            # 8. Finally delete the repository
            repository_delete_record = await session.execute_write(self._delete_repository_txn, qualified_name)
            stats["repositories_deleted"] = repository_delete_record["count"] if repository_delete_record else 0
            
            # Calculate total relationships deleted for logging
            total_relationships = total_file_relationships + total_package_relationships + total_codebase_relationships
            
            logger.info(
                "Successfully deleted repository: {} | repositories: {} | codebases: {} | packages: {} | files: {} | metadata: {} | relationships: {} total",
                qualified_name,
                stats["repositories_deleted"],
                stats["codebases_deleted"],
                stats["packages_deleted"],
                stats["files_deleted"],
                stats["metadata_deleted"],
                total_relationships
            )
            
            return stats
                
        except ApplicationError:
            # Re-raise ApplicationError as is
            raise
        except Exception as e:
            error_msg = f"Failed to delete repository {qualified_name}"
            logger.error(f"{error_msg} | error_type={type(e).__name__} | error={str(e)}")
            
            tb_str = traceback.format_exc()
            
            raise ApplicationError(
                error_msg,
                {"repository": qualified_name},
                {"error": str(e)},
                {"error_type": type(e).__name__},
                {"traceback": tb_str},
                {"workflow_id": workflow_id_var.get("")},
                {"workflow_run_id": workflow_run_id_var.get("")},
                {"activity_name": activity_name_var.get("")},
                {"activity_id": activity_id_var.get("")},
                type="GRAPH_DELETION_ERROR"
            )
    
    
    async def _delete_package_recursive_old(
        self,
        package: CodeConfluencePackage,
        stats: Dict[str, Union[int, str]],
        visited: Set[str],
    ) -> None:
        """[DEPRECATED - Use managed transactions] Recursively delete a package, all its nested sub-packages and files.

        Args:
            package: Package node to delete.
            stats: Shared statistics collector.
            visited: Set to track visited packages to avoid infinite recursion
        """
        # Prevent cycles / revisiting the same package
        if package.qualified_name in visited:
            return
        visited.add(package.qualified_name)

        # Delete files contained directly in this package via CONTAINS_FILE edge
        files = await package.files.all()
        for file in files:
            await file.delete()
            stats["files_deleted"] = int(stats.get("files_deleted", 0)) + 1

        # Fallback: There might be legacy graphs where only the reverse relationship exists
        if not files:
            

            alt_files = await CodeConfluenceFile.nodes.filter(
                package__qualified_name=package.qualified_name
            ).all()
            for file in alt_files:
                await file.delete()
                stats["files_deleted"] = int(stats.get("files_deleted", 0)) + 1

        # Recursively delete all nested sub-packages
        sub_packages = await package.sub_packages.all()
        for sub_pkg in sub_packages:
            await self._delete_package_recursive_old(sub_pkg, stats, visited)

        # Finally delete this package node itself
        await package.delete()
        stats["packages_deleted"] = int(stats.get("packages_deleted", 0)) + 1

    async def delete_repository_by_qualified_name_old(self, qualified_name: str) -> Dict[str, Union[int, str]]:
        """
        [DEPRECATED - Use delete_repository_by_qualified_name_managed] Delete a repository and all its related nodes by qualified name.
        
        Args:
            qualified_name: The qualified name of the repository (format: {owner}_{repo_name})
            
        Returns:
            Dict containing deletion statistics
            
        Raises:
            ApplicationError: If repository not found or deletion fails
        """
        try:
            async with adb.transaction:
                # First, check if the repository exists
                try:
                    repo_node = await CodeConfluenceGitRepository.nodes.get(qualified_name=qualified_name)
                except CodeConfluenceGitRepository.DoesNotExist:
                    raise ApplicationError(
                        f"Repository not found: {qualified_name}",
                        {"repository": qualified_name},
                        {"workflow_id": workflow_id_var.get("")},
                        {"workflow_run_id": workflow_run_id_var.get("")},
                        {"activity_name": activity_name_var.get("")},
                        {"activity_id": activity_id_var.get("")},
                        type="REPOSITORY_NOT_FOUND"
                    )
                
                # Collect statistics
                stats: Dict[str, Union[int, str]] = {
                    "repository_qualified_name": "",  # Placeholder – will be removed before return
                    "codebases_deleted": 0,
                    "packages_deleted": 0,
                    "files_deleted": 0,
                    "metadata_deleted": 0,
                }
                
                # Get all connected codebases
                codebases = await repo_node.codebases.all()
                
                # Delete each codebase and its children
                for codebase in codebases:
                    # Delete package manager metadata
                    metadata_nodes = await codebase.package_manager_metadata.all()
                    for metadata in metadata_nodes:
                        await metadata.delete()
                        stats["metadata_deleted"] = int(stats.get("metadata_deleted", 0)) + 1
                    
                    # Delete packages and their files
                    packages = await codebase.packages.all()
                    visited_pkgs: Set[str] = set()
                    for package in packages:
                        # Recursively delete package, its sub-packages and files
                        await self._delete_package_recursive_old(package, stats, visited_pkgs)
                    
                    # Delete the codebase
                    await codebase.delete()
                    stats["codebases_deleted"] = int(stats.get("codebases_deleted", 0)) + 1
                
                # Finally delete the repository
                await repo_node.delete()
                
                # Attach repository qualified name now that deletion succeeded
                stats["repository_qualified_name"] = qualified_name
                return stats
                
        except ApplicationError:
            # Re-raise ApplicationError as is
            raise
        except Exception as e:
            error_msg = f"Failed to delete repository {qualified_name}"
            logger.error(f"{error_msg} | error_type={type(e).__name__} | error={str(e)}")
            
            tb_str = traceback.format_exc()
            
            raise ApplicationError(
                error_msg,
                {"repository": qualified_name},
                {"error": str(e)},
                {"error_type": type(e).__name__},
                {"traceback": tb_str},
                {"workflow_id": workflow_id_var.get("")},
                {"workflow_run_id": workflow_run_id_var.get("")},
                {"activity_name": activity_name_var.get("")},
                {"activity_id": activity_id_var.get("")},
                type="GRAPH_DELETION_ERROR"
            )