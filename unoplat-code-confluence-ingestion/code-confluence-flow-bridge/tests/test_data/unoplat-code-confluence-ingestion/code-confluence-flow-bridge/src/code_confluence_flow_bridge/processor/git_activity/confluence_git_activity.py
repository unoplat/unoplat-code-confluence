from src.code_confluence_flow_bridge.confluence_git.github_helper import GithubHelper
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_git_repository import (
    UnoplatGitRepository,
)
from src.code_confluence_flow_bridge.models.configuration.settings import (
    RepositorySettings,
)

from temporalio import activity
from temporalio.exceptions import ApplicationError


class GitActivity:
    """
    Temporal activity class for GitHub operations using GithubHelper
    """

    def __init__(self):
        self.github_helper = GithubHelper()
        activity.logger.info("Initialized GitActivity with GithubHelper")

    @activity.defn
    def process_git_activity(self, repository_settings: RepositorySettings, github_token: str) -> UnoplatGitRepository:
        """
        Process Git activity using GithubHelper

        Returns:
            UnoplatGitRepository containing processed git activity data
        """
        try:
            # Get activity info for context
            info = activity.info()
            activity.logger.info("Starting git activity processing", extra={"temporal_workflow_id": info.workflow_id, "temporal_activity_id": info.activity_id, "temporal_attempt": info.attempt, "git_url": repository_settings.git_url})

            activity_data = self.github_helper.clone_repository(repository_settings, github_token)

            activity.logger.info("Successfully processed git activity", extra={"temporal_workflow_id": info.workflow_id, "temporal_activity_id": info.activity_id, "git_url": repository_settings.git_url, "status": "success"})
            return activity_data

        except Exception as e:
            activity.logger.error("Failed to process git activity", extra={"temporal_workflow_id": activity.info().workflow_id, "temporal_activity_id": activity.info().activity_id, "error_type": type(e).__name__, "error_details": str(e), "git_url": repository_settings.git_url, "status": "error"})
            raise ApplicationError(message="Failed to process git activity", type="GIT_ACTIVITY_ERROR", details=[{"repository": repository_settings.git_url, "error": str(e)}])
