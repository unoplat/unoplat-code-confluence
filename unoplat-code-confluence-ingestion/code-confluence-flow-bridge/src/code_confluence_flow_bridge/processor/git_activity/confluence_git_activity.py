import traceback

from temporalio import activity
from temporalio.exceptions import ApplicationError

from src.code_confluence_flow_bridge.confluence_git.github_helper import GithubHelper
from src.code_confluence_flow_bridge.logging.trace_utils import (
    seed_and_bind_logger_from_trace_id,
)
from src.code_confluence_flow_bridge.models.code_confluence_parsing_models.unoplat_git_repository import (
    UnoplatGitRepository,
)
from src.code_confluence_flow_bridge.models.workflow.repo_workflow_base import (
    GitActivityEnvelope,
)


class GitActivity:
    """
    Temporal activity class for Git operations with GitHub
    """

    def __init__(self):
        self.github_helper = GithubHelper()

    @activity.defn
    def process_git_activity(
        self,
        envelope: GitActivityEnvelope,
    ) -> UnoplatGitRepository:
        """
        Process Git activity using GithubHelper

        Returns:
            UnoplatGitRepository containing processed git activity data
        """
        # Extract parameters from envelope
        repo_request = envelope.repo_request
        github_token = envelope.github_token
        trace_id = envelope.trace_id

        # Bind Loguru logger with the passed trace_id
        info: activity.Info = activity.info()
        
        workflow_id: str = info.workflow_id
        workflow_run_id: str = info.workflow_run_id
        activity_name: str = info.activity_type
        activity_id: str = info.activity_id
        log = seed_and_bind_logger_from_trace_id(
            trace_id=trace_id,
            workflow_id=workflow_id,
            workflow_run_id=workflow_run_id,
            activity_id=activity_id,
            activity_name=activity_name
        )

        try:
            # Get activity info for context
            log.debug(
                "Starting git activity processing | attempt={} | git_url={} | provider={}",
                info.attempt, repo_request.repository_git_url, repo_request.repository_provider.value
            )
            
            # Process GitHub repository
            log.info(
                "Processing GitHub repository | git_url={} | status=started",
                repo_request.repository_git_url
            )
            activity_data: UnoplatGitRepository = self.github_helper.clone_repository(
                repo_request, 
                github_token
            )
            
            log.debug(
                "Successfully processed git activity | git_url={} | provider={} | status=success",
                repo_request.repository_git_url, repo_request.repository_provider.value
            )
            return activity_data

        except Exception as e:
            if isinstance(e, ApplicationError):
                # Re-raise ApplicationError as is since it already contains detailed error info
                raise
            
            # For other exceptions, wrap in ApplicationError with basic info
            log.error(
                "Failed to process git activity | git_url={} | error_type={} | error_details={} | status=error",
                repo_request.repository_git_url, type(e).__name__, str(e)
            )
            
            # Capture the traceback string
            tb_str = traceback.format_exc()
            
            raise ApplicationError(
                "Failed to process git activity",
                {"repository": repo_request.repository_git_url},
                {"error": str(e)},
                {"error_type": type(e).__name__},
                {"traceback": tb_str},
                {"workflow_id": workflow_id or ""},
                {"workflow_run_id": workflow_run_id or ""},
                {"activity_name": activity_name or ""},
                {"activity_id": activity_id or ""},
                type="GIT_ACTIVITY_ERROR"
            )
