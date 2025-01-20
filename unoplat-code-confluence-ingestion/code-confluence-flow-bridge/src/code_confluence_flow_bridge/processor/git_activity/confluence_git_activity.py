from loguru import logger
from temporalio import activity
from temporalio.exceptions import ApplicationError

from src.code_confluence_flow_bridge.confluence_git.github_helper import GithubHelper
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_git_repository import UnoplatGitRepository
from src.code_confluence_flow_bridge.models.configuration.settings import RepositorySettings


class GitActivity:
    """
    Temporal activity class for GitHub operations using GithubHelper
    """
    def __init__(self):
        self.github_helper = GithubHelper()
        logger.info("Initialized GitActivity with GithubHelper")

    @activity.defn
    def process_git_activity(self,repository_settings: RepositorySettings, github_token: str) -> UnoplatGitRepository:
        """
        Process Git activity using GithubHelper
        
        Returns:
            UnoplatGitRepository containing processed git activity data
        """
        try:
            # Get activity info for context
            info = activity.info()
            logger.info(
                "Starting git activity processing",
                workflow_id=info.workflow_id,
                activity_id=info.activity_id,
                attempt=info.attempt
            )
            
            activity_data = self.github_helper.clone_repository(repository_settings, github_token)
            
            logger.success(
                "Successfully processed git activity",
                workflow_id=info.workflow_id,
                activity_id=info.activity_id,
                repository=repository_settings.git_url
            )
            return activity_data

        except Exception as e:
            logger.error(
                "Failed to process git activity",
                workflow_id=activity.info().workflow_id,
                activity_id=activity.info().activity_id,
                error=str(e),
                repository=repository_settings.git_url
            )
            raise ApplicationError(
                message="Failed to process git activity",
                type="GIT_ACTIVITY_ERROR",
                details=[{
                    "repository": repository_settings.git_url,
                    "error": str(e)
                }]
            )
            