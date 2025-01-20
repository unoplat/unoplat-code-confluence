from temporalio import activity
from temporalio.exceptions import ApplicationError

from src.code_confluence_flow_bridge.confluence_git.github_helper import GithubHelper
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_git_repository import UnoplatGitRepository
from src.code_confluence_flow_bridge.models.workflow.parent_child_clone_metadata import ParentChildCloneMetadata
from src.code_confluence_flow_bridge.processor.db.graph_db.code_confluence_graph_ingestion import CodeConfluenceGraphIngestion


class ConfluenceGitGraph:
    """
    Temporal activity class for GitHub operations using GithubHelper
    """
    def __init__(self,code_confluence_graph_ingestion: CodeConfluenceGraphIngestion):
        self.code_confluence_graph_ingestion = code_confluence_graph_ingestion
        activity.logger.info("Initialized ConfluenceGitGraph with CodeConfluenceGraphIngestion")

    @activity.defn
    async def insert_git_repo_into_graph_db(self,git_repo: UnoplatGitRepository) -> ParentChildCloneMetadata:
        """
        Insert a git repository into the graph database
        
        Args:
            git_repo: UnoplatGitRepository containing git repository data
            
        Returns:
            ParentChildCloneMetadata containing the qualified name of the git repository and the codebase qualified names
        """
        try:
            info = activity.info()
            activity.logger.info(
                "Starting graph db insertion",
                extra={
                    "workflow_id": info.workflow_id,
                    "activity_id": info.activity_id,
                    "repository": git_repo.repository_url
                }
            )
            
            parent_child_clone_metadata = await self.code_confluence_graph_ingestion.insert_code_confluence_git_repo(git_repo=git_repo)
            
            activity.logger.info(
                "Successfully inserted git repo into graph db",
                extra={
                    "workflow_id": info.workflow_id,
                    "activity_id": info.activity_id,
                    "repository": git_repo.repository_url
                }
            )
            return parent_child_clone_metadata
            
        except Exception as e:
            error_msg = f"Failed to insert git repo into graph db: {git_repo.repository_url}"
            activity.logger.error(
                error_msg,
                extra={
                    "workflow_id": activity.info().workflow_id,
                    "activity_id": activity.info().activity_id,
                    "error": str(e),
                    "repository": git_repo.repository_url
                }
            )
            raise ApplicationError(
                message=error_msg,
                type="GRAPH_INGESTION_ERROR"
            )