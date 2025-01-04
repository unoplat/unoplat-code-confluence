from loguru import logger
from temporalio import activity
from temporalio.exceptions import ApplicationError

from src.code_confluence_flow_bridge.confluence_git.github_helper import GithubHelper
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_git_repository import UnoplatGitRepository
from src.code_confluence_flow_bridge.models.configuration.settings import EnvironmentSettings, RepositorySettings
from src.code_confluence_flow_bridge.processor.db.graph_db.code_confluence_graph_ingestion import CodeConfluenceGraphIngestion


class ConfluenceGitGraph:
    """
    Temporal activity class for GitHub operations using GithubHelper
    """
    def __init__(self,code_confluence_env: EnvironmentSettings):
        self.code_confluence_graph_ingestion = CodeConfluenceGraphIngestion(code_confluence_env=code_confluence_env)
        logger.info("Initialized ConfluenceGitGraph with CodeConfluenceGraphIngestion")

    @activity.defn
    async def insert_git_repo_into_graph_db(self,git_repo: UnoplatGitRepository) -> str:
        """
        Process Git activity using GithubHelper
        
        Returns:
            UnoplatGitRepository containing processed git activity data
        """
        try:
            logger.info("inserting git repo into graph db")
            
            # Process git activity using github helper
            git_repo_qualified_name: str = self.code_confluence_graph_ingestion.insert_code_confluence_git_repo(git_repo)
            
            logger.success("Successfully inserted git repo into graph db")
            

        except Exception as e:
            logger.error("Failed to insert git repo into graph db: {}", str(e))
            raise ApplicationError(
                "Failed to insert git repo into graph db",
                details={"error": str(e)}
            )
            
        return git_repo_qualified_name