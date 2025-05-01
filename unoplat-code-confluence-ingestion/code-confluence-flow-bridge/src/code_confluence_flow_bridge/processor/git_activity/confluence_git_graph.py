from src.code_confluence_flow_bridge.logging.trace_utils import seed_and_bind_logger_from_trace_id
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_git_repository import UnoplatGitRepository
from src.code_confluence_flow_bridge.models.workflow.parent_child_clone_metadata import ParentChildCloneMetadata
from src.code_confluence_flow_bridge.processor.db.graph_db.code_confluence_graph_ingestion import CodeConfluenceGraphIngestion

from loguru import logger
from temporalio import activity
from temporalio.exceptions import ApplicationError


class ConfluenceGitGraph:
    """
    Temporal activity class for GitHub operations using GithubHelper
    """

    def __init__(self, code_confluence_graph_ingestion: CodeConfluenceGraphIngestion):
        self.code_confluence_graph_ingestion = code_confluence_graph_ingestion
        logger.debug(
            "Initialized ConfluenceGitGraph with CodeConfluenceGraphIngestion"
        )

    @activity.defn
    async def insert_git_repo_into_graph_db(self, git_repo: UnoplatGitRepository, trace_id: str) -> ParentChildCloneMetadata:
        """
        Insert a git repository into the graph database

        Args:
            git_repo: UnoplatGitRepository containing git repository data

        Returns:
            ParentChildCloneMetadata containing the qualified name of the git repository and the codebase qualified names
        """
        # Bind a Loguru logger with the provided trace_id
        info: activity.Info = activity.info()
        workflow_id = info.workflow_id
        workflow_run_id = info.workflow_run_id
        log = seed_and_bind_logger_from_trace_id(trace_id, workflow_id, workflow_run_id, activity_id="insert_git_repo_into_graph_db")
        try:
            log.debug(
                "Starting graph db insertion for repo: {} ",
                git_repo.repository_url
            )
            
            parent_child_clone_metadata = await self.code_confluence_graph_ingestion.insert_code_confluence_git_repo(git_repo=git_repo)
            
            log.debug(
                "Successfully inserted git repo into graph db: {} ",
                git_repo.repository_url
            )
            return parent_child_clone_metadata

        except Exception as e:
            error_msg = f"Failed to insert git repo into graph db: {git_repo.repository_url}"
            log.debug(
                "{} | error={}",
                error_msg, str(e)
            )
            raise ApplicationError(message=error_msg, type="GRAPH_INGESTION_ERROR")
