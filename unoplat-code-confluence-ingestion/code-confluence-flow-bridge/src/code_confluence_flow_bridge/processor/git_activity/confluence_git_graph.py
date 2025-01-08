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
    def __init__(self,code_confluence_graph_ingestion: CodeConfluenceGraphIngestion):
        self.code_confluence_graph_ingestion = code_confluence_graph_ingestion
        logger.info("Initialized ConfluenceGitGraph with CodeConfluenceGraphIngestion")

    @activity.defn
    async def insert_git_repo_into_graph_db(self,git_repo: UnoplatGitRepository) -> str:
        """
        Insert a git repository into the graph database
        
        Args:
            git_repo: UnoplatGitRepository containing git repository data
            
        Returns:
            Qualified name of the git repository
        """
        try:
            git_repo_qualified_name: str = await self.code_confluence_graph_ingestion.insert_code_confluence_git_repo(git_repo)
            logger.success("Successfully inserted git repo into graph db")
        except Exception as e:
            logger.error("Failed to insert git repo into graph db: {}", str(e))
            raise ApplicationError(
                "Failed to insert git repo into graph db",
                details=tuple({"error": str(e)})
            )
        return git_repo_qualified_name