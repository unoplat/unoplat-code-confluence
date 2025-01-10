# Standard Library
from typing import Optional

# Third Party
from loguru import logger
from temporalio.exceptions import ApplicationError
from unoplat_code_confluence_commons.graph_models.code_confluence_codebase import CodeConfluenceCodebase
from unoplat_code_confluence_commons.graph_models.code_confluence_git_repository import CodeConfluenceGitRepository

from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_git_repository import UnoplatGitRepository
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
            codebase_qualified_name=[]
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
                        "readme": codebase.readme
                    }
                    parent_child_clone_metadata.codebase_qualified_name.append(codebase_qualified_name)
                    
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
        
                
      