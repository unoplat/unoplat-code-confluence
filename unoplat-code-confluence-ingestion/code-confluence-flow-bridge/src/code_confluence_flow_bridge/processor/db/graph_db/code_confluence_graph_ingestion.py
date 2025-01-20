# Standard Library
from typing import Optional

# Third Party
from loguru import logger
from temporalio.exceptions import ApplicationError
from unoplat_code_confluence_commons import CodeConfluencePackageManagerMetadata
from unoplat_code_confluence_commons.graph_models.code_confluence_codebase import CodeConfluenceCodebase
from unoplat_code_confluence_commons.graph_models.code_confluence_git_repository import CodeConfluenceGitRepository

from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_git_repository import UnoplatGitRepository
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_package_manager_metadata import UnoplatPackageManagerMetadata
from src.code_confluence_flow_bridge.models.configuration.settings import EnvironmentSettings
from src.code_confluence_flow_bridge.models.workflow.parent_child_clone_metadata import ParentChildCloneMetadata
from src.code_confluence_flow_bridge.processor.db.graph_db.code_confluence_graph import CodeConfluenceGraph


class CodeConfluenceGraphIngestion:
    def __init__(self,code_confluence_env: EnvironmentSettings):
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
        parent_child_clone_metadata = ParentChildCloneMetadata(
            repository_qualified_name=qualified_name,
            codebase_qualified_names=[]
        )
        
        try:
            async with self.code_confluence_graph.transaction:
                # Create repository node
                repo_dict = {
                    "qualified_name": qualified_name,
                    "repository_url": git_repo.repository_url,
                    "repository_name": git_repo.repository_name,
                    "repository_metadata": git_repo.repository_metadata,
                    "readme": git_repo.readme,
                    "github_organization": git_repo.github_organization
                }
                
                repo_results = await CodeConfluenceGitRepository.create_or_update(repo_dict)
                if not repo_results:
                    raise ApplicationError(
                        message=f"Failed to create repository node: {qualified_name}",
                        type="REPOSITORY_CREATION_ERROR",
                        details=[{"repository": qualified_name}]
                    )
                
                repo_node = repo_results[0]
                logger.success(f"Created repository node: {qualified_name}")
                
                # Create codebase nodes and establish relationships
                for codebase in git_repo.codebases:
                    codebase_qualified_name = f"{qualified_name}_{codebase.name}"
                    
                    codebase_dict = {
                        "qualified_name": codebase_qualified_name,
                        "name": codebase.name,
                        "readme": codebase.readme,
                        "local_path": codebase.local_path
                    }
                    parent_child_clone_metadata.codebase_qualified_names.append(codebase_qualified_name)
                    
                    codebase_results = await CodeConfluenceCodebase.create_or_update(codebase_dict)
                    if not codebase_results:
                        raise ApplicationError(
                            message=f"Failed to create codebase node: {codebase.name}",
                            type="CODEBASE_CREATION_ERROR",
                            details=[{
                                "repository": qualified_name,
                                "codebase": codebase.name
                            }]
                        )
                    
                    codebase_node = codebase_results[0]
                    
                    # Establish relationships
                    await repo_node.codebases.connect(codebase_node)
                    await codebase_node.git_repository.connect(repo_node)
                
                logger.success(f"Successfully ingested repository {qualified_name}")
                return parent_child_clone_metadata
                
        except Exception as e:
            error_msg = f"Failed to insert repository {qualified_name}"
            logger.error(f"{error_msg}: {str(e)}")
            raise ApplicationError(
                message=error_msg,
                type="GRAPH_INGESTION_ERROR"
            ) from e
        
                
    async def insert_code_confluence_codebase_package_manager_metadata(
        self,
        codebase_qualified_name: str,
        package_manager_metadata: UnoplatPackageManagerMetadata
    ) -> None:
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
                    codebase_node = await CodeConfluenceCodebase.nodes.get(
                        qualified_name=codebase_qualified_name
                    )
                except CodeConfluenceCodebase.DoesNotExist:
                    raise ApplicationError(
                        message=f"Codebase not found: {codebase_qualified_name}",
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
                    "authors": package_manager_metadata.authors or []
                }
                
                metadata_results = await CodeConfluencePackageManagerMetadata.create_or_update(metadata_dict)
                if not metadata_results:
                    raise ApplicationError(
                        message=f"Failed to create package manager metadata for {codebase_qualified_name}",
                        type="METADATA_CREATION_ERROR"
                    )
                
                metadata_node: CodeConfluencePackageManagerMetadata = metadata_results[0]
                
                # Connect metadata to codebase
                await codebase_node.package_manager_metadata.connect(metadata_node)
                
                logger.success(f"Successfully inserted package manager metadata for {codebase_qualified_name}")
                
        except Exception as e:
            error_msg = f"Failed to insert package manager metadata for {codebase_qualified_name}"
            logger.error(f"{error_msg}: {str(e)}")
            raise ApplicationError(
                message=error_msg,
                type="PACKAGE_METADATA_ERROR"
            )
        
 