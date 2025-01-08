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
            logger.info("Starting git activity processing")
            
            # Process git activity using github helper
            activity_data: UnoplatGitRepository = self.github_helper.clone_repository(repository_settings, github_token)
            
            logger.success("Successfully processed git activity")
            return activity_data

        except Exception as e:
            logger.error("Failed to process git activity: {}", str(e))
            raise ApplicationError(
                "Failed to process git activity",
                details={"error": str(e)}
            )
            