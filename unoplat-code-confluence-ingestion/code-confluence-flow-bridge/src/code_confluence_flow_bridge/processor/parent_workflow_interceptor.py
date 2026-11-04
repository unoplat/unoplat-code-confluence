import asyncio
from datetime import timedelta
import json
import traceback
from typing import Any, Optional, override

from temporalio import workflow
from temporalio.api.common.v1 import Payload
from temporalio.common import RetryPolicy
from temporalio.exceptions import (
    ActivityError,
    ApplicationError,
    CancelledError,
    ChildWorkflowError,
    FailureError,
    TimeoutError as TemporalTimeoutError,
)
from temporalio.worker._interceptor import (
    ExecuteWorkflowInput,
    Interceptor,
    WorkflowInboundInterceptor,
    WorkflowInterceptorClassInput,
    WorkflowOutboundInterceptor,
)
from temporalio.workflow import ActivityCancellationType, Info

with workflow.unsafe.imports_passed_through():
    from unoplat_code_confluence_commons.workflow_envelopes import (
        CodebaseWorkflowDbActivityEnvelope,
        ParentWorkflowDbActivityEnvelope,
    )
    from unoplat_code_confluence_commons.workflow_models import (
        ErrorReport,
        JobStatus,
    )

    from code_confluence_flow_bridge.models.workflow.repo_workflow_base import (
        CodebaseChildWorkflowEnvelope,
        RepoWorkflowRunEnvelope,
    )
    from code_confluence_flow_bridge.processor.activity_retries_config import (
        ActivityRetriesConfig,
    )
    from code_confluence_flow_bridge.processor.db.postgres.child_workflow_db_activity import (
        ChildWorkflowDbActivity,
    )
    from code_confluence_flow_bridge.processor.db.postgres.parent_workflow_db_activity import (
        ParentWorkflowDbActivity,
    )

    # Bring in the outbound interceptor and shared headers ContextVar
    from code_confluence_flow_bridge.processor.workflow_outbound_interceptor import (
        ParentWorkflowOutboundInterceptor,
        workflow_headers_var,
    )


ADMISSION_TIMEOUT = timedelta(hours=6)
ADMISSION_POLL_INTERVAL = timedelta(seconds=5)
ADMISSION_RETRY_POLICY = RetryPolicy(
    initial_interval=timedelta(seconds=1),
    maximum_interval=timedelta(seconds=30),
    maximum_attempts=0,
)
TERMINAL_RETRY_POLICY = RetryPolicy(
    initial_interval=timedelta(seconds=1),
    maximum_interval=timedelta(seconds=30),
    maximum_attempts=0,
)


def is_cancellation(exception: BaseException) -> bool:
    for _ in range(8):
        if isinstance(exception, (asyncio.CancelledError, CancelledError)):
            return True
        if isinstance(exception, FailureError) and exception.cause is not None:
            exception = exception.cause
        else:
            return False
    return False


async def wait_for_checkout_admission(
    envelope: ParentWorkflowDbActivityEnvelope,
) -> None:
    """Keep waiting parents SUBMITTED without holding a connection or lock."""
    deadline = workflow.now() + ADMISSION_TIMEOUT
    try:
        await workflow.execute_activity(
            ParentWorkflowDbActivity.update_repository_workflow_status,
            args=[envelope.model_copy(update={"status": JobStatus.SUBMITTED.value})],
            start_to_close_timeout=timedelta(minutes=1),
            schedule_to_close_timeout=ADMISSION_TIMEOUT,
            retry_policy=ADMISSION_RETRY_POLICY,
            cancellation_type=ActivityCancellationType.WAIT_CANCELLATION_COMPLETED,
        )
        while workflow.now() < deadline:
            admitted = await workflow.execute_activity(
                ParentWorkflowDbActivity.update_repository_workflow_status,
                args=[envelope],
                start_to_close_timeout=timedelta(minutes=1),
                schedule_to_close_timeout=deadline - workflow.now(),
                retry_policy=ADMISSION_RETRY_POLICY,
                cancellation_type=ActivityCancellationType.WAIT_CANCELLATION_COMPLETED,
            )
            if admitted:
                return
            remaining = deadline - workflow.now()
            if remaining <= timedelta():
                break
            await workflow.sleep(min(ADMISSION_POLL_INTERVAL, remaining))
    except ActivityError as exc:
        if not isinstance(exc.cause, TemporalTimeoutError):
            raise
    raise ApplicationError(
        "Checkout admission timed out",
        type="CheckoutAdmissionTimeout",
        non_retryable=True,
    )


class ParentWorkflowStatusInterceptor(Interceptor):
    """Worker interceptor to update parent workflow status in the DB."""

    @override
    def workflow_interceptor_class(
        self, input: WorkflowInterceptorClassInput
    ) -> type[WorkflowInboundInterceptor]:
        return ParentWorkflowStatusInboundInterceptor


class ParentWorkflowStatusInboundInterceptor(WorkflowInboundInterceptor):
    """Inbound interceptor for parent workflows to mark RUNNING/COMPLETED/FAILED."""

    def __init__(self, nxt: WorkflowInboundInterceptor) -> None:
        super().__init__(nxt)

    # ------------------------------------------------------------------
    # Interceptor chain initialization
    # ------------------------------------------------------------------
    @override
    def init(self, outbound: WorkflowOutboundInterceptor) -> None:
        """Wrap outbound interceptor to forward headers to activities."""
        super().init(ParentWorkflowOutboundInterceptor(outbound))

    @override
    async def execute_workflow(self, input: ExecuteWorkflowInput) -> Any:
        # Unpack envelope and workflow info
        info: Info = workflow.info()
        workflow_type = info.workflow_type
        workflow_id: str = info.workflow_id
        workflow_run_id: str = info.run_id

        if workflow_type == "repo-activity-workflow":
            envelope: RepoWorkflowRunEnvelope = input.args[0]
            trace_id: str = envelope.trace_id

            # Prepare codebase configurations for headers with complete metadata
            codebase_configs = [
                {
                    "root_packages": config.root_packages,
                    "codebase_folder": config.codebase_folder,
                    "programming_language_metadata": config.programming_language_metadata.model_dump(),
                }
                for config in (envelope.repo_request.repository_metadata or [])
            ]

            # Set headers with trace_id and codebase configs as Payload messages
            input.headers = {
                "trace_id": Payload(data=trace_id.encode("utf-8")),
                "repository_name": Payload(
                    data=envelope.repo_request.repository_name.encode("utf-8")
                ),
                "repository_owner_name": Payload(
                    data=envelope.repo_request.repository_owner_name.encode("utf-8")
                ),
                "codebases": Payload(data=json.dumps(codebase_configs).encode("utf-8")),
                "workflow_run_id": Payload(data=workflow_run_id.encode("utf-8")),
            }

            # Store headers in contextvar for forwarding to activities
            workflow_headers_var.set(input.headers)

            workflow.logger.debug(
                "Starting execute_workflow with trace_id=%s, workflow_id=%s, workflow_run_id=%s",
                trace_id,
                workflow_id,
                workflow_run_id,
            )

            # Admission records SUBMITTED before attempting RUNNING.
            running_env = ParentWorkflowDbActivityEnvelope(
                repository_name=envelope.repo_request.repository_name,
                repository_owner_name=envelope.repo_request.repository_owner_name,
                workflow_id=info.workflow_id,
                workflow_run_id=info.run_id,
                trace_id=envelope.trace_id,
                repository_metadata=envelope.repo_request.repository_metadata,
                status=JobStatus.RUNNING.value,
                provider_key=envelope.repo_request.provider_key,
            )
            status = JobStatus.COMPLETED.value
            error_report: Optional[ErrorReport] = None
            result: Any = None
            exc: Optional[BaseException] = None
            try:
                await wait_for_checkout_admission(running_env)
                # Execute the workflow logic
                workflow.logger.debug("Invoking next interceptor execute_workflow")
                result = await self.next.execute_workflow(input)
                workflow.logger.debug(
                    "Workflow logic executed successfully, result: %s", result
                )
            except (asyncio.CancelledError, Exception) as e:
                exc = e
                workflow.logger.debug(
                    "Exception occurred during workflow execution: %s", e
                )

                # Build error report
                root = (
                    e.cause
                    if isinstance(e, (ActivityError, ChildWorkflowError))
                    and getattr(e, "cause", None)
                    else e
                )
                # If the root is an ApplicationError, capture its rich context
                if isinstance(root, ApplicationError):
                    metadata = {
                        "type": root.type,
                        "details": root.details,
                        "non_retryable": root.non_retryable,
                        "next_retry_delay": (
                            root.next_retry_delay.total_seconds()
                            if root.next_retry_delay
                            else None
                        ),
                    }
                else:
                    metadata = None
                error_report = ErrorReport(
                    error_message=str(root),
                    stack_trace=traceback.format_exc() if root is not None else "",
                    metadata=metadata,
                )

                if is_cancellation(e):
                    status = JobStatus.CANCELLED.value
                    error_report = None
                elif (
                    isinstance(e, ApplicationError)
                    and e.type == "CheckoutAdmissionTimeout"
                ):
                    status = JobStatus.TIMED_OUT.value
                else:
                    status = JobStatus.FAILED.value
            finally:
                workflow.logger.debug("Setting final status %s in DB", status)
                # Final status write
                final_env = ParentWorkflowDbActivityEnvelope(
                    repository_name=envelope.repo_request.repository_name,
                    repository_owner_name=envelope.repo_request.repository_owner_name,
                    workflow_id=info.workflow_id,
                    workflow_run_id=info.run_id,
                    trace_id=envelope.trace_id,
                    repository_metadata=envelope.repo_request.repository_metadata,
                    status=status,
                    error_report=error_report,
                    provider_key=envelope.repo_request.provider_key,
                )
                await asyncio.shield(
                    workflow.execute_activity(
                        activity=ParentWorkflowDbActivity.update_repository_workflow_status,
                        args=[final_env],
                        start_to_close_timeout=timedelta(minutes=1),
                        retry_policy=TERMINAL_RETRY_POLICY,
                        cancellation_type=ActivityCancellationType.WAIT_CANCELLATION_COMPLETED,
                    )
                )
                workflow.logger.debug("Final status written to DB")

            if exc:
                workflow.logger.debug(
                    "Propagating exception to Temporal for retry/failure"
                )
                # Propagate exception to let Temporal retry or fail the workflow
                raise exc
            return result

        elif workflow_type == "child-codebase-workflow":
            child_envelope: CodebaseChildWorkflowEnvelope = input.args[0]
            child_trace_id: str = child_envelope.trace_id
            # Extract codebase folder from envelope (use relative path, not absolute)
            codebase_folder: str = child_envelope.codebase_folder
            parent_workflow_run_id: str = child_envelope.parent_workflow_run_id  # type: ignore

            # Parse repository_name and repository_owner_name from trace_id
            repository_name, repository_owner_name = child_trace_id.split("__")

            # Set headers with trace_id and parent workflow context
            input.headers = {
                "trace_id": Payload(data=child_trace_id.encode("utf-8")),
                "repository_name": Payload(data=repository_name.encode("utf-8")),
                "repository_owner_name": Payload(
                    data=repository_owner_name.encode("utf-8")
                ),
                "codebase_folder": Payload(data=codebase_folder.encode("utf-8")),
                "workflow_run_id": Payload(data=workflow_run_id.encode("utf-8")),
            }

            # Add parent_workflow_run_id header if available
            if child_envelope.parent_workflow_run_id:
                input.headers["parent_workflow_run_id"] = Payload(
                    data=child_envelope.parent_workflow_run_id.encode("utf-8")
                )

            # Store headers in contextvar for forwarding to activities
            workflow_headers_var.set(input.headers)

            workflow.logger.debug(
                "Child workflow: Starting execute_workflow with trace_id=%s, workflow_id=%s, workflow_run_id=%s",
                child_trace_id,
                workflow_id,
                workflow_run_id,
            )

            # Initial RUNNING status for child workflow
            running_child_env = CodebaseWorkflowDbActivityEnvelope(
                repository_name=repository_name,
                repository_owner_name=repository_owner_name,
                codebase_folder=codebase_folder,
                codebase_workflow_id=workflow_id,
                codebase_workflow_run_id=workflow_run_id,
                repository_workflow_run_id=parent_workflow_run_id,
                trace_id=child_trace_id,
                status=JobStatus.RUNNING.value,
            )
            await workflow.execute_activity(
                activity=ChildWorkflowDbActivity.update_codebase_workflow_status,
                args=[running_child_env],
                start_to_close_timeout=timedelta(minutes=1),
                retry_policy=ActivityRetriesConfig.DEFAULT,
            )
            workflow.logger.debug(
                "Initial RUNNING status recorded for child workflow %s for codebase %s",
                workflow_run_id,
                codebase_folder,
            )

            child_status = JobStatus.COMPLETED.value
            child_error_report: Optional[ErrorReport] = None
            child_result: Any = None
            child_exc: Optional[BaseException] = None
            try:
                # Execute the workflow logic
                workflow.logger.debug(
                    "Invoking next interceptor execute_workflow for child workflow"
                )
                child_result = await self.next.execute_workflow(input)
                workflow.logger.debug(
                    "Child workflow logic executed successfully, result: %s",
                    child_result,
                )
            except (
                ActivityError,
                ChildWorkflowError,
                ApplicationError,
                Exception,
            ) as e:
                child_exc = e
                workflow.logger.debug(
                    "Exception occurred during child workflow execution: %s", e
                )

                # Build error report
                root = (
                    e.cause
                    if isinstance(e, (ActivityError, ChildWorkflowError))
                    and getattr(e, "cause", None)
                    else e
                )
                # If the root is an ApplicationError, capture its rich context
                if isinstance(root, ApplicationError):
                    metadata = {
                        "type": root.type,
                        "details": root.details,
                        "non_retryable": root.non_retryable,
                        "next_retry_delay": (
                            root.next_retry_delay.total_seconds()
                            if root.next_retry_delay
                            else None
                        ),
                    }
                else:
                    metadata = None
                child_error_report = ErrorReport(
                    error_message=str(root),
                    stack_trace=traceback.format_exc() if root is not None else "",
                    metadata=metadata,
                )

                # Decide between RETRYING and FAILED
                child_status = JobStatus.FAILED.value
            finally:
                workflow.logger.debug(
                    "Setting final status %s in DB for child workflow", child_status
                )
                # Final status write
                final_child_env = CodebaseWorkflowDbActivityEnvelope(
                    repository_name=repository_name,
                    repository_owner_name=repository_owner_name,
                    codebase_folder=codebase_folder,
                    codebase_workflow_id=workflow_id,
                    codebase_workflow_run_id=workflow_run_id,
                    repository_workflow_run_id=parent_workflow_run_id,
                    trace_id=child_trace_id,
                    status=child_status,
                    error_report=child_error_report,
                )
                await workflow.execute_activity(
                    activity=ChildWorkflowDbActivity.update_codebase_workflow_status,
                    args=[final_child_env],
                    start_to_close_timeout=timedelta(minutes=1),
                    retry_policy=ActivityRetriesConfig.DEFAULT,
                )
                workflow.logger.debug("Final status written to DB for child workflow")

                # The parent retains admission until all sibling work has stopped.

            if child_exc:
                workflow.logger.debug(
                    "Propagating exception to Temporal for retry/failure of child workflow"
                )
                # Propagate exception to let Temporal retry or fail the workflow
                raise child_exc
            return child_result

        else:
            workflow.logger.debug(
                "Skipping execute_workflow for workflow_type: %s", workflow_type
            )
            return await self.next.execute_workflow(input)
