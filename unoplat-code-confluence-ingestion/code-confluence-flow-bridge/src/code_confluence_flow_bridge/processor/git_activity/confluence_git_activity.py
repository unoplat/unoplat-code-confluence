from src.code_confluence_flow_bridge.confluence_git.github_helper import GithubHelper
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_git_repository import UnoplatGitRepository
from src.code_confluence_flow_bridge.models.github.github_repo import GitHubRepoRequestConfiguration

from temporalio import activity
from temporalio.exceptions import ApplicationError
from loguru import logger


class GitActivity:
    """
    Temporal activity class for GitHub operations using GithubHelper
    """

    def __init__(self):
        self.github_helper = GithubHelper()
        logger.debug("Initialized GitActivity with GithubHelper")

    @activity.defn
    async def process_git_activity(self, repo_request: GitHubRepoRequestConfiguration, github_token: str) -> UnoplatGitRepository:
        """
        Process Git activity using GithubHelper

        Returns:
            UnoplatGitRepository containing processed git activity data
        """
        try:
            # Get activity info for context
            info = activity.info()
            logger.debug(
                "Starting git activity processing | workflow_id={} | activity_id={} | attempt={} | git_url={}",
                info.workflow_id, info.activity_id, info.attempt, repo_request.repository_git_url
            )

            activity_data = await self.github_helper.clone_repository(repo_request, github_token)

            logger.debug(
                "Successfully processed git activity | workflow_id={} | activity_id={} | git_url={} | status=success",
                info.workflow_id, info.activity_id, repo_request.repository_git_url
            )
            return activity_data

        except Exception as e:
            info = activity.info()
            logger.debug(
                "Failed to process git activity | workflow_id={} | activity_id={} | git_url={} | error_type={} | error_details={} | status=error",
                info.workflow_id, info.activity_id, repo_request.repository_git_url, type(e).__name__, str(e)
            )
            raise ApplicationError(message="Failed to process git activity", type="GIT_ACTIVITY_ERROR", details=[{"repository": repo_request.repository_git_url, "error": str(e)}])
