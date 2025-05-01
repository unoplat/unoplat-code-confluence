from src.code_confluence_flow_bridge.confluence_git.github_helper import GithubHelper
from src.code_confluence_flow_bridge.logging.trace_utils import seed_and_bind_logger_from_trace_id
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_git_repository import UnoplatGitRepository
from src.code_confluence_flow_bridge.models.github.github_repo import GitHubRepoRequestConfiguration

from temporalio import activity
from temporalio.exceptions import ApplicationError


class GitActivity:
    """
    Temporal activity class for GitHub operations using GithubHelper
    """

    def __init__(self):
        self.github_helper = GithubHelper()

    @activity.defn
    async def process_git_activity(
        self,
        repo_request: GitHubRepoRequestConfiguration,
        github_token: str,
        trace_id: str,
    ) -> UnoplatGitRepository:
        """
        Process Git activity using GithubHelper

        Returns:
            UnoplatGitRepository containing processed git activity data
        """
        # Bind Loguru logger with the passed trace_id
        info: activity.Info = activity.info()
        workflow_id = info.workflow_id
        workflow_run_id = info.workflow_run_id
        log = seed_and_bind_logger_from_trace_id(trace_id, workflow_id, workflow_run_id, activity_id="process_git_activity")

        try:
            # Get activity info for context
            log.debug(
                "Starting git activity processing | attempt={} | git_url={} ",
                info.attempt, repo_request.repository_git_url
            )

            activity_data = await self.github_helper.clone_repository(repo_request, github_token)

            log.debug(
                "Successfully processed git activity | git_url={} | status=success",
                repo_request.repository_git_url
            )
            return activity_data

        except Exception as e:
            log.error(
                "Failed to process git activity | git_url={} | error_type={} | error_details={} | status=error",
                repo_request.repository_git_url, type(e).__name__, str(e)
            )
            raise ApplicationError(message="Failed to process git activity", type="GIT_ACTIVITY_ERROR", details=[{"repository": repo_request.repository_git_url, "error": str(e)}])
