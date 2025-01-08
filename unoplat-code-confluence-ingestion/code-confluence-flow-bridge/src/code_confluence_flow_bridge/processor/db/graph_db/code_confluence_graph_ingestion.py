# Standard Library

# Third Party
from loguru import logger
from unoplat_code_confluence_commons.graph_models.code_confluence_codebase import CodeConfluenceCodebase
from unoplat_code_confluence_commons.graph_models.code_confluence_git_repository import CodeConfluenceGitRepository

from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_git_repository import UnoplatGitRepository
from src.code_confluence_flow_bridge.models.configuration.settings import EnvironmentSettings
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
        
    async def insert_code_confluence_git_repo(self,git_repo: UnoplatGitRepository) -> str:
        """
        Insert a git repository into the graph database
        
        Args:
            git_repo: UnoplatGitRepository containing git repository data
            
        Returns:
            Qualified name of the git repository
        """
        qualified_name = f"{git_repo.github_organization}_{git_repo.repository_name}"
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
                
                repo_results, _ = await CodeConfluenceGitRepository.create_or_update(repo_dict)
                if not repo_results:
                    raise Exception("Failed to create repository node")
                
                repo_node = repo_results[0]
                logger.success(f"Created repository node: {qualified_name}")
                
                # Create codebase nodes and establish relationships
                for codebase in git_repo.codebases:
                    codebase_dict = {
                        "qualified_name": f"{qualified_name}_{codebase.name}",
                        "name": codebase.name,
                        "readme": codebase.readme
                    }
                    
                    codebase_results, _ = await CodeConfluenceCodebase.create_or_update(codebase_dict)
                    if not codebase_results:
                        raise Exception(f"Failed to create codebase node for {codebase.name}")
                    
                    codebase_node = codebase_results[0]
                    logger.debug(f"Created codebase node: {codebase.name}")
                    
                    # Establish bidirectional relationships
                    await repo_node.codebases.connect(codebase_node)
                    await codebase_node.git_repository.connect(repo_node)
                    logger.debug(f"Established relationships for codebase: {codebase.name}")
                
                logger.success(f"Successfully ingested repository {qualified_name} with {len(git_repo.codebases)} codebases")
                return qualified_name
                
        except Exception as e:
            logger.error(f"Failed to insert repository {qualified_name}: {str(e)}")
            raise
        
                
      