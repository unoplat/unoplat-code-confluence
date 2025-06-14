from src.code_confluence_flow_bridge.logging.trace_utils import activity_id_var, activity_name_var, workflow_id_var, workflow_run_id_var
from src.code_confluence_flow_bridge.models.code_confluence_parsing_models.unoplat_file import UnoplatFile
from src.code_confluence_flow_bridge.models.code_confluence_parsing_models.unoplat_git_repository import UnoplatGitRepository
from src.code_confluence_flow_bridge.models.code_confluence_parsing_models.unoplat_package import UnoplatPackage
from src.code_confluence_flow_bridge.models.code_confluence_parsing_models.unoplat_package_manager_metadata import UnoplatPackageManagerMetadata
from src.code_confluence_flow_bridge.models.configuration.settings import EnvironmentSettings
from src.code_confluence_flow_bridge.models.workflow.parent_child_clone_metadata import ParentChildCloneMetadata
from src.code_confluence_flow_bridge.processor.db.graph_db.code_confluence_graph import CodeConfluenceGraph

import hashlib
import traceback
from typing import Any, Dict, List, Tuple, Union

from loguru import logger
from neomodel.exceptions import RequiredProperty, UniqueProperty
from temporalio.exceptions import ApplicationError
from unoplat_code_confluence_commons import (
    CodeConfluenceFile,
    CodeConfluencePackage,
    CodeConfluencePackageManagerMetadata,
)
from unoplat_code_confluence_commons.graph_models.code_confluence_codebase import CodeConfluenceCodebase
from unoplat_code_confluence_commons.graph_models.code_confluence_git_repository import CodeConfluenceGitRepository


class CodeConfluenceGraphIngestion:
    def __init__(self, code_confluence_env: EnvironmentSettings):
        self.code_confluence_graph = CodeConfluenceGraph(code_confluence_env=code_confluence_env)

    async def initialize(self) -> None:
        """Initialize graph connection and schema"""
        try:
            await self.code_confluence_graph.connect()
            await self.code_confluence_graph.create_schema()
            logger.info("Graph initialization complete")
        except Exception as e:
            logger.error(f"Failed to initialize graph: {str(e)}")
            raise

    async def close(self) -> None:
        """Close graph connection"""
        await self.code_confluence_graph.close()

    def _get_node_identifier(self, node) -> str:
        """
        Get the appropriate identifier for a node for logging purposes.
        
        Args:
            node: The node to get identifier for
            
        Returns:
            str: The identifier value
        """
        # CodeConfluenceFile inherits from AsyncStructuredNode and uses file_path as unique identifier
        if hasattr(node, 'file_path') and node.file_path:
            return node.file_path
        # CodeConfluenceAnnotation inherits from AsyncStructuredNode and uses name as unique identifier
        elif hasattr(node, 'name') and node.name and not hasattr(node, 'qualified_name'):
            return node.name
        # All BaseNode-derived classes use qualified_name
        elif hasattr(node, 'qualified_name') and node.qualified_name:
            return node.qualified_name
        # Fallback to string representation
        else:
            return str(node)

    async def _safe_connect(self, source_node, relationship_attr: str, target_node) -> bool:
        """
        Safely connect two nodes, checking if relationship already exists.
        Logs at INFO level if relationship already exists and proceeds gracefully.
        
        Args:
            source_node: The source node
            relationship_attr: The name of the relationship attribute
            target_node: The target node
            
        Returns:
            bool: True if new connection made, False if already existed
        """
        try:
            relationship = getattr(source_node, relationship_attr)
            if await relationship.is_connected(target_node):
                # Use appropriate identifier for each node type based on inheritance
                source_id = self._get_node_identifier(source_node)
                target_id = self._get_node_identifier(target_node)
                logger.info(
                    "Relationship already exists: {}.{} -> {} (source: {}, target: {})",
                    source_node.__class__.__name__,
                    relationship_attr,
                    target_node.__class__.__name__,
                    source_id,
                    target_id
                )
                return False
            else:
                await relationship.connect(target_node)
                source_id = self._get_node_identifier(source_node)
                target_id = self._get_node_identifier(target_node)
                logger.debug(
                    "Created new relationship: {}.{} -> {} (source: {}, target: {})",
                    source_node.__class__.__name__,
                    relationship_attr,
                    target_node.__class__.__name__,
                    source_id,
                    target_id
                )
                return True
        except Exception as e:
            # Log the error but don't fail the application
            logger.warning(
                "Failed to create relationship {}.{} -> {}: {}. Proceeding gracefully.",
                source_node.__class__.__name__,
                relationship_attr,
                target_node.__class__.__name__,
                str(e)
            )
            return False

    async def _handle_node_creation(self, node_class, node_dict: dict):
        """
        Safely create or update a node with graceful error handling for constraint violations.
        Logs constraint violations and proceeds gracefully instead of failing.
        
        Args:
            node_class: The neomodel node class
            node_dict: Dictionary of node properties
            
        Returns:
            List of created/updated nodes, or empty list if failed
        """
        try:
            results = await node_class.create_or_update(node_dict)
            return results if results else []
        except UniqueProperty as e:
            logger.info(
                "Node already exists with unique property: {} for {}. Proceeding gracefully.",
                str(e),
                node_class.__name__
            )
            # Try to retrieve the existing node by unique properties
            try:
                # Find unique index properties in the node dict
                for prop_name, value in node_dict.items():
                    if hasattr(node_class, prop_name):
                        prop = getattr(node_class, prop_name)
                        if hasattr(prop, 'unique_index') and prop.unique_index:
                            existing_nodes = await node_class.nodes.filter(**{prop_name: value}).all()
                            if existing_nodes:
                                return existing_nodes[:1]  # Return as list for consistency
                # If no unique property found, try qualified_name (all nodes have this from BaseNode)
                if 'qualified_name' in node_dict:
                    existing_nodes = await node_class.nodes.filter(qualified_name=node_dict['qualified_name']).all()
                    if existing_nodes:
                        return existing_nodes[:1]
            except Exception as retrieval_error:
                logger.warning(
                    "Failed to retrieve existing {} node after UniqueProperty error: {}. Proceeding gracefully.",
                    node_class.__name__,
                    str(retrieval_error)
                )
            return []
        except RequiredProperty as e:
            logger.error(
                "Missing required property for {}: {}. Cannot proceed with node creation.",
                node_class.__name__,
                str(e)
            )
            return []
        except Exception as e:
            logger.warning(
                "Unexpected error creating {} node: {}. Proceeding gracefully.",
                node_class.__name__,
                str(e)
            )
            return []

    async def insert_code_confluence_git_repo(self, git_repo: UnoplatGitRepository) -> ParentChildCloneMetadata:
        """
        Insert a git repository into the graph database

        Args:
            git_repo: UnoplatGitRepository containing git repository data

        Returns:
            ParentChildCloneMetadata: Metadata about created nodes

        Raises:
            ApplicationError: If repository insertion fails
        """
        qualified_name = f"{git_repo.github_organization}_{git_repo.repository_name}"
        parent_child_clone_metadata = ParentChildCloneMetadata(repository_qualified_name=qualified_name, codebase_qualified_names=[])

        try:
            async with self.code_confluence_graph.transaction:
                # Create repository node
                repo_dict = {"qualified_name": qualified_name, "repository_url": git_repo.repository_url, "repository_name": git_repo.repository_name, "repository_metadata": git_repo.repository_metadata, "readme": git_repo.readme, "github_organization": git_repo.github_organization}

                repo_results = await self._handle_node_creation(CodeConfluenceGitRepository, repo_dict)
                if not repo_results:
                    raise ApplicationError(
                        f"Failed to create repository node: {qualified_name}", 
                        {"repository": qualified_name}, 
                        {"workflow_id": workflow_id_var.get("")},
                        {"workflow_run_id": workflow_run_id_var.get("")},
                        {"activity_name": activity_name_var.get("")},
                        {"activity_id": activity_id_var.get("")},
                        type="REPOSITORY_CREATION_ERROR"
                    )

                repo_node = repo_results[0]
                logger.debug(f"Created repository node: {qualified_name}")

                # Create codebase nodes and establish relationships
                for codebase in git_repo.codebases:
                    codebase_qualified_name = f"{qualified_name}_{codebase.name}"

                    codebase_dict = {"qualified_name": codebase_qualified_name, "name": codebase.name, "readme": codebase.readme, "root_packages": codebase.root_packages, "codebase_path": codebase.codebase_path}
                    parent_child_clone_metadata.codebase_qualified_names.append(codebase_qualified_name)

                    codebase_results = await self._handle_node_creation(CodeConfluenceCodebase, codebase_dict)
                    if not codebase_results:
                        raise ApplicationError(
                            f"Failed to create codebase node: {codebase.name}",
                            {"repository": qualified_name},
                            {"codebase": codebase.name},
                            {"workflow_id": workflow_id_var.get("")},
                            {"workflow_run_id": workflow_run_id_var.get("")},
                            {"activity_name": activity_name_var.get("")},
                            {"activity_id": activity_id_var.get("")},
                            type="CODEBASE_CREATION_ERROR"
                        )

                    codebase_node = codebase_results[0]

                    # Establish relationships using safe connect
                    await self._safe_connect(repo_node, 'codebases', codebase_node)
                    await self._safe_connect(codebase_node, 'git_repository', repo_node)

                logger.debug(f"Successfully ingested repository {qualified_name}")
                return parent_child_clone_metadata

        except Exception as e:
            # Capture detailed error information
            error_msg = f"Failed to insert repository {qualified_name}"
            logger.error(f"{error_msg} | error_type={type(e).__name__} | error={str(e)} | status=failed")
            
            # Capture the traceback string
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
                type="GRAPH_INGESTION_ERROR"
            ) from e

    async def insert_code_confluence_codebase_package_manager_metadata(self, codebase_qualified_name: str, package_manager_metadata: UnoplatPackageManagerMetadata) -> None:
        """
        Insert codebase package manager metadata into the graph database

        Args:
            codebase_qualified_name: Qualified name of the codebase
            package_manager_metadata: UnoplatPackageManagerMetadata containing package manager metadata
        """
        try:
            async with self.code_confluence_graph.transaction:
                # Use get() instead of filter() for unique index
                try:
                    codebase_node = await CodeConfluenceCodebase.nodes.get(qualified_name=codebase_qualified_name)
                except CodeConfluenceCodebase.DoesNotExist:
                    raise ApplicationError(
                        f"Codebase not found: {codebase_qualified_name}", 
                        {"codebase": codebase_qualified_name},
                        {"workflow_id": workflow_id_var.get("")},
                        {"workflow_run_id": workflow_run_id_var.get("")},
                        {"activity_name": activity_name_var.get("")},
                        {"activity_id": activity_id_var.get("")},
                        type="CODEBASE_NOT_FOUND"
                    )

                # Create package manager metadata node
                metadata_dict = {
                    "qualified_name": f"{codebase_qualified_name}_package_manager_metadata",
                    "dependencies": {k: v.model_dump() for k, v in package_manager_metadata.dependencies.items()},
                    "package_manager": package_manager_metadata.package_manager,
                    "programming_language": package_manager_metadata.programming_language,
                    "programming_language_version": package_manager_metadata.programming_language_version,
                    "project_version": package_manager_metadata.project_version,
                    "description": package_manager_metadata.description,
                    "license": package_manager_metadata.license,
                    "package_name": package_manager_metadata.package_name,
                    "entry_points": package_manager_metadata.entry_points,
                    "authors": package_manager_metadata.authors or [],
                }

                metadata_results = await self._handle_node_creation(CodeConfluencePackageManagerMetadata, metadata_dict)
                if not metadata_results:
                    raise ApplicationError(
                        f"Failed to create package manager metadata for {codebase_qualified_name}", 
                        {"codebase": codebase_qualified_name},
                        {"workflow_id": workflow_id_var.get("")},
                        {"workflow_run_id": workflow_run_id_var.get("")},
                        {"activity_name": activity_name_var.get("")},
                        {"activity_id": activity_id_var.get("")},
                        type="METADATA_CREATION_ERROR"
                    )

                metadata_node: CodeConfluencePackageManagerMetadata = metadata_results[0]

                # Connect metadata to codebase using safe connect
                await self._safe_connect(codebase_node, 'package_manager_metadata', metadata_node)

                logger.debug(f"Successfully inserted package manager metadata for {codebase_qualified_name}")

        except Exception as e:
            # Capture detailed error information
            error_msg = f"Failed to insert package manager metadata for {codebase_qualified_name}"
            logger.error(f"{error_msg} | error_type={type(e).__name__} | error={str(e)} | status=failed")
            
            # Capture the traceback string
            tb_str = traceback.format_exc()
            
            raise ApplicationError(
                error_msg,
                {"codebase": codebase_qualified_name},
                {"error": str(e)},
                {"error_type": type(e).__name__},
                {"traceback": tb_str},
                {"workflow_id": workflow_id_var.get("")},
                {"workflow_run_id": workflow_run_id_var.get("")},
                {"activity_name": activity_name_var.get("")},
                {"activity_id": activity_id_var.get("")},
                type="PACKAGE_METADATA_ERROR"
            )

    async def _create_file_node(
        self, file_path: str, file_obj: UnoplatFile, package_node: CodeConfluencePackage
    ) -> CodeConfluenceFile:
        """
        Create a file node and establish relationships with the package.
        
        Args:
            file_path: Path of the file
            file_obj: UnoplatFile object containing file data
            package_node: The parent package node
            
        Returns:
            Created CodeConfluenceFile node
        """
        # Generate checksum for the file content if not already present
        checksum = file_obj.checksum
        if not checksum and file_obj.content:
            checksum = hashlib.md5(file_obj.content.encode()).hexdigest()
            
        # Create file node
        file_dict = {
            "file_path": file_path,
            "content": file_obj.content,
            "checksum": checksum
        }
        
        file_results = await self._handle_node_creation(CodeConfluenceFile, file_dict)
        if not file_results:
            raise ApplicationError(
                f"Failed to create file node: {file_path}",
                {"file_path": file_path},
                {"package": package_node.name},
                {"workflow_id": workflow_id_var.get("")},
                {"workflow_run_id": workflow_run_id_var.get("")},
                {"activity_name": activity_name_var.get("")},
                {"activity_id": activity_id_var.get("")},
                type="FILE_CREATION_ERROR"
            )
        
        file_node: CodeConfluenceFile = file_results[0]
        
        # Connect package to file using safe connect
        await self._safe_connect(package_node, 'files', file_node)
        await self._safe_connect(file_node, 'package', package_node)
        
        logger.debug(f"Created file node: {file_path}")
        
        # # ============== BEGIN DEBUG CODE (REMOVE AFTER TESTING) ==============
        # # Add debug logging for file node creation with checksum
        # logger.debug(f"File node details - path: {file_path}, checksum: {checksum}")
        # # ============== END DEBUG CODE (REMOVE AFTER TESTING) ==============
        
        return file_node
        

    


    # #todo: we need to ingest packages into the graph database
    # async def insert_code_confluence_package(
    #     self, codebase_qualified_name: str, packages: List[UnoplatPackage]
    # ) -> None:
    #     # # ============== BEGIN DEBUG CODE (REMOVE AFTER TESTING) ==============
    #     # # Count total files in packages before ingestion
    #     # total_files = 0
    #     # file_paths = set()
        
    #     # def count_files_recursive(pkg_list):
    #     #     nonlocal total_files, file_paths
    #     #     for pkg in pkg_list:
    #     #         if pkg.files:
    #     #             for file_path in pkg.files.keys():
    #     #                 if file_path not in file_paths:
    #     #                     file_paths.add(file_path)
    #     #                     total_files += 1
    #     #         if pkg.sub_packages:
    #     #             count_files_recursive(pkg.sub_packages.values())
        
    #     # count_files_recursive(packages)
    #     # logger.info(f"Starting ingestion with {total_files} unique files across all packages")
    #     # logger.debug(f"Files to be ingested: {list(file_paths)}")
    #     # # ============== END DEBUG CODE (REMOVE AFTER TESTING) ==============
        
    #     """
    #     Insert packages (with classes and functions) into the graph database.
    #     Expects a list of root packages, where each package may contain nested sub-packages.

    #     Args:
    #         codebase_qualified_name (str): The qualified name of the codebase
    #         packages (List[UnoplatPackage]): List of root packages from the parser
    #     """
    #     try:
    #         codebase_node: CodeConfluenceCodebase = await CodeConfluenceCodebase.nodes.get(
    #             qualified_name=codebase_qualified_name
    #         )
    #     except CodeConfluenceCodebase.DoesNotExist as e:
    #         raise ApplicationError(
    #             f"Codebase not found: {codebase_qualified_name}",
    #             type="CODEBASE_NOT_FOUND"
    #         ) from e

    #     async with self.code_confluence_graph.transaction:
    #         # Initialize stack with root packages
    #         # Each stack item is (package, parent_node)
    #         stack: List[Tuple[UnoplatPackage, Union[CodeConfluenceCodebase, CodeConfluencePackage]]] = [
    #             (pkg, codebase_node) for pkg in packages
    #         ]
            
    #         while stack:
    #             current_pkg, parent_node = stack.pop()
                
    #             # Skip packages without names
    #             if not current_pkg.name:
    #                 logger.warning("Skipping package with no name")
    #                 continue

    #             # Create package node
    #             pkg_name = current_pkg.name
    #             package_dict = {
    #                 "name": pkg_name,
    #                 "qualified_name": (
    #                     f"{parent_node.qualified_name}.{pkg_name}"
    #                     if hasattr(parent_node, "qualified_name")
    #                     else pkg_name
    #                 ),
    #             }

    #             package_results = await self._handle_node_creation(CodeConfluencePackage, package_dict)
    #             if not package_results:
    #                 raise ApplicationError(
    #                     f"Failed to create package node: {pkg_name}",
    #                     {"package": pkg_name},
    #                     {"codebase": codebase_qualified_name},
    #                     {"workflow_id": workflow_id_var.get("")},
    #                     {"workflow_run_id": workflow_run_id_var.get("")},
    #                     {"activity_name": activity_name_var.get("")},
    #                     {"activity_id": activity_id_var.get("")},
    #                     type="PACKAGE_CREATION_ERROR"
    #                 )
    #             package_node: CodeConfluencePackage = package_results[0]

    #             # Connect to parent and codebase using safe connect
    #             if isinstance(parent_node, CodeConfluenceCodebase):
    #                 await self._safe_connect(parent_node, 'packages', package_node)
    #                 await self._safe_connect(package_node, 'codebase', parent_node)
    #             else:
    #                 await self._safe_connect(parent_node, 'sub_packages', package_node)
    #                 await self._safe_connect(package_node, 'sub_packages', parent_node)

    #             logger.debug(f"Created package node: {pkg_name}")

    #             # Process all files in this package
    #             file_nodes: Dict[str, CodeConfluenceFile] = {}
                
    #             # # ============== BEGIN DEBUG CODE (REMOVE AFTER TESTING) ==============
    #             # # Add debug logging for file count in current package
    #             # file_count = len(current_pkg.files) if current_pkg.files else 0
    #             # logger.info(f"Package '{pkg_name}' contains {file_count} files")
    #             # # ============== END DEBUG CODE (REMOVE AFTER TESTING) ==============
                
    #             # Create all file nodes for this package
    #             if current_pkg.files:
    #                 for file_path, file_obj in current_pkg.files.items():
    #                     file_node = await self._create_file_node(
    #                         file_path=file_path,
    #                         file_obj=file_obj,
    #                         package_node=package_node
    #                     )
    #                     file_nodes[file_path] = file_node
                        
    #                     # Process all nodes in each file
    #                     for node in file_obj.nodes:
    #                         await self._process_class(
    #                             node=node, 
    #                             package_node=package_node,
    #                             file_node=file_node
    #                         )

    #             # Add sub-packages to stack (in reverse order to maintain original order when popping)
    #             if current_pkg.sub_packages:
    #                 # Convert items to list and reverse it
    #                 sub_packages = list(current_pkg.sub_packages.items())
    #                 for sub_pkg_name, sub_pkg in reversed(sub_packages):
    #                     if sub_pkg.name is None:
    #                         sub_pkg.name = sub_pkg_name
    #                     # Add to stack with current package as parent
    #                     stack.append((sub_pkg, package_node))
            
    #         # ============== BEGIN DEBUG CODE (REMOVE AFTER TESTING) ==============
    #         # # After processing all packages, count total file nodes created
    #         # try:
    #         #     file_nodes_count = await CodeConfluenceFile.nodes.count()
    #         #     logger.info(f"Total number of file nodes in database: {file_nodes_count}")    
    #         # except Exception as e:
    #         #     logger.error(f"Error counting file nodes: {e}")
    #         # # ============== END DEBUG CODE (REMOVE AFTER TESTING) ==============


    # --------------------------------------------------------------------------
    # End of added methods for package ingestion
    # --------------------------------------------------------------------------
        