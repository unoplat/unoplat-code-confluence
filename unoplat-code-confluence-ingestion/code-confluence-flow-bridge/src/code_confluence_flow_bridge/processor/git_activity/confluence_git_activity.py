from src.code_confluence_flow_bridge.confluence_git.github_helper import GithubHelper
from src.code_confluence_flow_bridge.confluence_git.local_git_helper import (
    LocalGitHelper,
)
from src.code_confluence_flow_bridge.logging.trace_utils import (
    seed_and_bind_logger_from_trace_id,
)
from src.code_confluence_flow_bridge.models.code_confluence_parsing_models.unoplat_git_repository import (
    UnoplatGitRepository,
)
from src.code_confluence_flow_bridge.models.workflow.repo_workflow_base import (
    GitActivityEnvelope,
)

import traceback

from temporalio import activity
from temporalio.exceptions import ApplicationError


class GitActivity:
    """
    Temporal activity class for Git operations supporting both GitHub and local repositories
    """

    def __init__(self):
        self.github_helper = GithubHelper()
        self.local_git_helper = LocalGitHelper()

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
            if repo_request.is_local:
                log.debug(
                    "Starting git activity processing | attempt={} | local_path={} | is_local={}",
                    info.attempt, repo_request.local_path, repo_request.is_local
                )
            else:
                log.debug(
                    "Starting git activity processing | attempt={} | git_url={} | is_local={}",
                    info.attempt, repo_request.repository_git_url, repo_request.is_local
                )
            activity_data: UnoplatGitRepository
            # Check if this is a local repository and process accordingly
            if repo_request.is_local and repo_request.local_path:
                log.info(
                    "Processing local repository | local_path={} | status=started",
                    repo_request.local_path
                )
                activity_data = self.local_git_helper.process_local_repository(
                    repo_request.local_path, 
                    repo_request
                )
            else:
                log.info(
                    "Processing GitHub repository | git_url={} | status=started",
                    repo_request.repository_git_url
                )
                activity_data = self.github_helper.clone_repository(
                    repo_request, 
                    github_token
                )
            
            if repo_request.is_local:
                log.debug(
                    "Successfully processed git activity | local_path={} | is_local={} | status=success",
                    repo_request.local_path, repo_request.is_local
                )
            else:
                log.debug(
                    "Successfully processed git activity | git_url={} | is_local={} | status=success",
                    repo_request.repository_git_url, repo_request.is_local
                )
            return activity_data

        except Exception as e:
            if isinstance(e, ApplicationError):
                # Re-raise ApplicationError as is since it already contains detailed error info
                raise
            
            # For other exceptions, wrap in ApplicationError with basic info
            if repo_request.is_local:
                log.error(
                    "Failed to process git activity | local_path={} | error_type={} | error_details={} | status=error",
                    repo_request.local_path, type(e).__name__, str(e)
                )
            else:
                log.error(
                    "Failed to process git activity | git_url={} | error_type={} | error_details={} | status=error",
                    repo_request.repository_git_url, type(e).__name__, str(e)
                )
            # Capture the traceback string
            tb_str = traceback.format_exc()
            
            # Use appropriate field for repository identification
            repository_identifier = repo_request.local_path if repo_request.is_local else repo_request.repository_git_url
            
            raise ApplicationError(
                "Failed to process git activity",
                {"repository": repository_identifier},
                {"error": str(e)},
                {"error_type": type(e).__name__},
                {"traceback": tb_str},
                {"workflow_id": workflow_id or ""},
                {"workflow_run_id": workflow_run_id or ""},
                {"activity_name": activity_name or ""},
                {"activity_id": activity_id or ""},
                type="GIT_ACTIVITY_ERROR"
            )
