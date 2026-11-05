import asyncio
import traceback

from temporalio import activity
from temporalio.exceptions import ApplicationError
from unoplat_code_confluence_commons.repository_checkout_coordination import (
    CheckoutAdmissionError,
    repository_capture_guard,
)

from code_confluence_flow_bridge.confluence_git.github_helper import GithubHelper
from code_confluence_flow_bridge.logging.trace_utils import (
    seed_and_bind_logger_from_trace_id,
)
from code_confluence_flow_bridge.models.code_confluence_parsing_models.unoplat_git_repository import (
    UnoplatGitRepository,
)
from code_confluence_flow_bridge.models.workflow.repo_workflow_base import (
    GitActivityEnvelope,
)
from code_confluence_flow_bridge.processor.db.postgres.db import get_engine_for_loop


class GitActivity:
    """
    Temporal activity class for Git operations with GitHub
    """

    def __init__(self):
        self.github_helper = GithubHelper()

    @activity.defn
    async def process_git_activity(
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

        if not info.workflow_id or not info.workflow_run_id:
            raise ApplicationError(
                "Checkout mutation requires a parent workflow execution",
                type="CheckoutAdmissionDenied",
                non_retryable=True,
            )
        workflow_id = info.workflow_id
        workflow_run_id = info.workflow_run_id
        activity_name: str = info.activity_type
        activity_id: str = info.activity_id
        log = seed_and_bind_logger_from_trace_id(
            trace_id=trace_id,
            workflow_id=workflow_id,
            workflow_run_id=workflow_run_id,
            activity_id=activity_id,
            activity_name=activity_name,
        )

        try:
            # Get activity info for context
            log.debug(
                "Starting git activity processing | attempt={} | git_url={} | provider={}",
                info.attempt,
                repo_request.repository_git_url,
                repo_request.provider_key.value,
            )

            # Process GitHub repository
            log.info(
                "Processing GitHub repository | git_url={} | status=started",
                repo_request.repository_git_url,
            )
            engine, _ = await get_engine_for_loop()
            async with repository_capture_guard(
                engine,
                repo_request.repository_owner_name,
                repo_request.repository_name,
                workflow_run_id,
            ):
                # Cancellation must not release the guard while a Git thread still
                # changes files. The workflow waits for activity cancellation too.
                clone_task = asyncio.create_task(
                    asyncio.to_thread(
                        self.github_helper.clone_repository, repo_request, github_token
                    )
                )
                try:
                    while not clone_task.done():
                        activity.heartbeat("git_checkout")
                        await asyncio.wait({clone_task}, timeout=5)
                    activity_data = await clone_task
                except BaseException:
                    # Any heartbeat error or repeated cancellation/shutdown must
                    # wait for the checkout thread before releasing the guard.
                    while not clone_task.done():
                        try:
                            await asyncio.shield(clone_task)
                        except (asyncio.CancelledError, Exception):
                            continue
                    if not clone_task.cancelled():
                        clone_task.exception()
                    raise

            log.debug(
                "Successfully processed git activity | git_url={} | provider={} | status=success",
                repo_request.repository_git_url,
                repo_request.provider_key.value,
            )
            return activity_data

        except CheckoutAdmissionError as e:
            raise ApplicationError(
                str(e), type="CheckoutAdmissionDenied", non_retryable=True
            ) from e
        except Exception as e:
            if isinstance(e, ApplicationError):
                # Re-raise ApplicationError as is since it already contains detailed error info
                raise

            # For other exceptions, wrap in ApplicationError with basic info
            log.error(
                "Failed to process git activity | git_url={} | error_type={} | error_details={} | status=error",
                repo_request.repository_git_url,
                type(e).__name__,
                str(e),
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
                type="GIT_ACTIVITY_ERROR",
            )
