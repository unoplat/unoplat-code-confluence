"""Temporal workflow interceptor for agent workflow status tracking."""

from __future__ import annotations

import asyncio
from datetime import timedelta
from typing import Any, Optional, override

from temporalio import workflow
from temporalio.api.common.v1 import Payload
from temporalio.common import RetryPolicy
from temporalio.exceptions import (
    ActivityError,
    ApplicationError,
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

from unoplat_code_confluence_query_engine.services.temporal.cancellation_helpers import (
    is_temporal_cancellation_exception,
)

with workflow.unsafe.imports_passed_through():
    from loguru import logger
    from unoplat_code_confluence_commons.repo_models import RepositoryWorkflowOperation
    from unoplat_code_confluence_commons.workflow_envelopes import (
        CodebaseWorkflowDbActivityEnvelope,
        ParentWorkflowDbActivityEnvelope,
    )
    from unoplat_code_confluence_commons.workflow_models import (
        ErrorReport,
        JobStatus,
        error_report_from_exception,
    )

    from unoplat_code_confluence_query_engine.services.temporal.interceptors.agent_workflow.activity import (
        CodebaseWorkflowDbActivity,
        RepositoryAgentSnapshotActivity,
        RepositoryWorkflowDbActivity,
    )
    from unoplat_code_confluence_query_engine.services.temporal.interceptors.agent_workflow.outbound import (
        AgentWorkflowOutboundInterceptor,
        workflow_headers_var,
    )
    from unoplat_code_confluence_query_engine.services.temporal.workflow_envelopes import (
        REPOSITORY_ACTIVITY_NAMES,
        AgentSnapshotBeginRunEnvelope,
    )
    from unoplat_code_confluence_query_engine.utils.trace_utils import (
        seed_and_bind_logger,
    )


DB_ACTIVITY_RETRY_POLICY = RetryPolicy(
    initial_interval=timedelta(seconds=1),
    backoff_coefficient=2.0,
    maximum_attempts=3,
    maximum_interval=timedelta(seconds=10),
)
DB_ACTIVITY_TIMEOUT = timedelta(minutes=1)
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


async def wait_for_checkout_admission(
    envelope: ParentWorkflowDbActivityEnvelope,
) -> None:
    """Queue without occupying a checkout slot; wait outside DB transactions."""
    deadline = workflow.now() + ADMISSION_TIMEOUT
    try:
        await workflow.execute_activity(
            RepositoryWorkflowDbActivity.update_repository_workflow_status,
            args=[envelope.model_copy(update={"status": JobStatus.SUBMITTED.value})],
            start_to_close_timeout=DB_ACTIVITY_TIMEOUT,
            schedule_to_close_timeout=ADMISSION_TIMEOUT,
            retry_policy=ADMISSION_RETRY_POLICY,
            cancellation_type=ActivityCancellationType.WAIT_CANCELLATION_COMPLETED,
        )
        while workflow.now() < deadline:
            admitted = await workflow.execute_activity(
                RepositoryWorkflowDbActivity.update_repository_workflow_status,
                args=[envelope],
                start_to_close_timeout=DB_ACTIVITY_TIMEOUT,
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
        # Exhausted admission infrastructure retries also report TIMED_OUT.
        # Cancellation errors must propagate even at the deadline.
    raise ApplicationError(
        "Checkout admission timed out",
        type="CheckoutAdmissionTimeout",
        non_retryable=True,
    )


WORKFLOW_EXECUTION_EXCEPTIONS: tuple[type[BaseException], ...] = (
    asyncio.CancelledError,
    Exception,
)


class AgentWorkflowStatusInterceptor(Interceptor):
    """Worker interceptor factory for agent workflow status tracking."""

    @override
    def workflow_interceptor_class(
        self, input: WorkflowInterceptorClassInput
    ) -> type[WorkflowInboundInterceptor]:
        return AgentWorkflowStatusInboundInterceptor


class AgentWorkflowStatusInboundInterceptor(WorkflowInboundInterceptor):
    """Inbound interceptor for repository/codebase agent workflow status tracking."""

    def __init__(self, nxt: WorkflowInboundInterceptor) -> None:
        super().__init__(nxt)

    @override
    def init(self, outbound: WorkflowOutboundInterceptor) -> None:
        super().init(AgentWorkflowOutboundInterceptor(outbound))

    @override
    async def execute_workflow(self, input: ExecuteWorkflowInput) -> Any:
        info: Info = workflow.info()
        workflow_type = info.workflow_type

        if workflow_type == "RepositoryAgentWorkflow":
            return await self._handle_repository_workflow(input, info)
        if workflow_type == "CodebaseAgentWorkflow":
            return await self._handle_codebase_workflow(input, info)

        logger.debug(
            "[agent_workflow_interceptor] Unknown workflow type {}, passing through",
            workflow_type,
        )
        return await self.next.execute_workflow(input)

    async def _handle_repository_workflow(
        self, input: ExecuteWorkflowInput, info: Info
    ) -> Any:
        # Args: repository_qualified_name, codebase_metadata_list, trace_id, operation
        repository_qualified_name: str = input.args[0]
        codebase_metadata_list: list[dict[str, Any]] = input.args[1]
        trace_id: str = input.args[2]
        operation = RepositoryWorkflowOperation(input.args[3])

        workflow_id = info.workflow_id
        repository_workflow_run_id = info.run_id

        if "/" in repository_qualified_name:
            owner_name, repo_name = repository_qualified_name.split("/", maxsplit=1)
        else:
            owner_name = ""
            repo_name = repository_qualified_name

        input.headers = {
            "trace_id": Payload(data=trace_id.encode("utf-8")),
            "repository_name": Payload(data=repo_name.encode("utf-8")),
            "repository_owner_name": Payload(data=owner_name.encode("utf-8")),
            "workflow_run_id": Payload(data=repository_workflow_run_id.encode("utf-8")),
            "repository_workflow_run_id": Payload(
                data=repository_workflow_run_id.encode("utf-8")
            ),
        }
        workflow_headers_var.set(input.headers)

        bound_logger = seed_and_bind_logger(
            trace_id=trace_id,
            workflow_id=workflow_id,
            workflow_run_id=repository_workflow_run_id,
        )
        bound_logger.info(
            "[agent_workflow_interceptor] Starting RepositoryAgentWorkflow: "
            "trace_id={}, workflow_id={}, run_id={}, repository={}, operation={}",
            trace_id,
            workflow_id,
            repository_workflow_run_id,
            repository_qualified_name,
            operation.value,
        )

        running_envelope = ParentWorkflowDbActivityEnvelope(
            repository_name=repo_name,
            repository_owner_name=owner_name,
            workflow_id=workflow_id,
            workflow_run_id=repository_workflow_run_id,
            status=JobStatus.RUNNING.value,
            operation=operation,
            trace_id=trace_id,
        )
        status = JobStatus.COMPLETED.value
        error_report: Optional[ErrorReport] = None
        result: Any = None
        exc: Optional[BaseException] = None

        try:
            await wait_for_checkout_admission(running_envelope)
            begin_envelope = AgentSnapshotBeginRunEnvelope(
                owner_name=owner_name,
                repo_name=repo_name,
                repository_workflow_run_id=repository_workflow_run_id,
                codebase_names=[
                    str(metadata.get("codebase_name", "unknown"))
                    for metadata in codebase_metadata_list
                ],
                repository_activity_names=list(REPOSITORY_ACTIVITY_NAMES),
            )
            await workflow.execute_activity(
                RepositoryAgentSnapshotActivity.persist_agent_snapshot_begin_run,
                args=[begin_envelope],
                start_to_close_timeout=DB_ACTIVITY_TIMEOUT,
                retry_policy=DB_ACTIVITY_RETRY_POLICY,
            )
            bound_logger.debug(
                "[agent_workflow_interceptor] Snapshot begin-run recorded for repository workflow"
            )

            result = await self.next.execute_workflow(input)
            bound_logger.info(
                "[agent_workflow_interceptor] RepositoryAgentWorkflow completed successfully"
            )
        except WORKFLOW_EXECUTION_EXCEPTIONS as e:
            exc = e
            if is_temporal_cancellation_exception(e):
                status = JobStatus.CANCELLED.value
                error_report = None
                bound_logger.info(
                    "[agent_workflow_interceptor] RepositoryAgentWorkflow cancelled"
                )
            else:
                status = (
                    JobStatus.TIMED_OUT.value
                    if isinstance(e, ApplicationError)
                    and e.type == "CheckoutAdmissionTimeout"
                    else JobStatus.ERROR.value
                )
                error_report = error_report_from_exception(e)
                bound_logger.error(
                    "[agent_workflow_interceptor] RepositoryAgentWorkflow failed: {}",
                    str(e),
                )
        finally:
            final_envelope = ParentWorkflowDbActivityEnvelope(
                repository_name=repo_name,
                repository_owner_name=owner_name,
                workflow_id=workflow_id,
                workflow_run_id=repository_workflow_run_id,
                status=status,
                operation=operation,
                error_report=error_report,
                trace_id=trace_id,
            )
            # Cleanup must survive queued/running cancellation and transient DB outages.
            await asyncio.shield(
                workflow.execute_activity(
                    RepositoryWorkflowDbActivity.update_repository_workflow_status,
                    args=[final_envelope],
                    start_to_close_timeout=DB_ACTIVITY_TIMEOUT,
                    retry_policy=TERMINAL_RETRY_POLICY,
                    cancellation_type=ActivityCancellationType.WAIT_CANCELLATION_COMPLETED,
                )
            )
            bound_logger.debug(
                "[agent_workflow_interceptor] Final status {} recorded for repository workflow",
                status,
            )

        if exc:
            raise exc
        return result

    async def _handle_codebase_workflow(
        self, input: ExecuteWorkflowInput, info: Info
    ) -> Any:
        # Args: repository_qualified_name, codebase_metadata_dict,
        #       parent repository_workflow_run_id, trace_id, git_ref_info
        repository_qualified_name: str = input.args[0]
        codebase_metadata_dict: dict[str, Any] = input.args[1]
        repository_workflow_run_id: str = input.args[2]
        trace_id: str = input.args[3]

        workflow_id = info.workflow_id
        codebase_workflow_run_id = info.run_id
        codebase_folder = codebase_metadata_dict.get("codebase_name", "unknown")

        if "/" in repository_qualified_name:
            owner_name, repo_name = repository_qualified_name.split("/", maxsplit=1)
        else:
            owner_name = ""
            repo_name = repository_qualified_name

        input.headers = {
            "trace_id": Payload(data=trace_id.encode("utf-8")),
            "repository_name": Payload(data=repo_name.encode("utf-8")),
            "repository_owner_name": Payload(data=owner_name.encode("utf-8")),
            "codebase_folder": Payload(data=codebase_folder.encode("utf-8")),
            "workflow_run_id": Payload(data=codebase_workflow_run_id.encode("utf-8")),
            "repository_workflow_run_id": Payload(
                data=repository_workflow_run_id.encode("utf-8")
            ),
            "codebase_workflow_run_id": Payload(
                data=codebase_workflow_run_id.encode("utf-8")
            ),
        }
        workflow_headers_var.set(input.headers)

        bound_logger = seed_and_bind_logger(
            trace_id=trace_id,
            workflow_id=workflow_id,
            workflow_run_id=codebase_workflow_run_id,
        )
        bound_logger.info(
            "[agent_workflow_interceptor] Starting CodebaseAgentWorkflow: "
            "trace_id={}, workflow_id={}, run_id={}, codebase={}",
            trace_id,
            workflow_id,
            codebase_workflow_run_id,
            codebase_folder,
        )

        running_envelope = CodebaseWorkflowDbActivityEnvelope(
            repository_name=repo_name,
            repository_owner_name=owner_name,
            codebase_folder=codebase_folder,
            codebase_workflow_id=workflow_id,
            codebase_workflow_run_id=codebase_workflow_run_id,
            repository_workflow_run_id=repository_workflow_run_id,
            status=JobStatus.RUNNING.value,
            trace_id=trace_id,
        )
        await workflow.execute_activity(
            CodebaseWorkflowDbActivity.update_codebase_workflow_status,
            args=[running_envelope],
            start_to_close_timeout=DB_ACTIVITY_TIMEOUT,
            retry_policy=DB_ACTIVITY_RETRY_POLICY,
        )
        bound_logger.debug(
            "[agent_workflow_interceptor] RUNNING status recorded for codebase workflow"
        )

        status = JobStatus.COMPLETED.value
        error_report: Optional[ErrorReport] = None
        result: Any = None
        exc: Optional[BaseException] = None

        try:
            result = await self.next.execute_workflow(input)
            bound_logger.info(
                "[agent_workflow_interceptor] CodebaseAgentWorkflow completed successfully"
            )
        except WORKFLOW_EXECUTION_EXCEPTIONS as e:
            exc = e
            if is_temporal_cancellation_exception(e):
                status = JobStatus.CANCELLED.value
                error_report = None
                bound_logger.info(
                    "[agent_workflow_interceptor] CodebaseAgentWorkflow cancelled"
                )
            else:
                status = JobStatus.ERROR.value
                error_report = error_report_from_exception(e)
                bound_logger.error(
                    "[agent_workflow_interceptor] CodebaseAgentWorkflow failed: {}",
                    str(e),
                )
        finally:
            final_envelope = CodebaseWorkflowDbActivityEnvelope(
                repository_name=repo_name,
                repository_owner_name=owner_name,
                codebase_folder=codebase_folder,
                codebase_workflow_id=workflow_id,
                codebase_workflow_run_id=codebase_workflow_run_id,
                repository_workflow_run_id=repository_workflow_run_id,
                status=status,
                error_report=error_report,
                trace_id=trace_id,
            )
            await workflow.execute_activity(
                CodebaseWorkflowDbActivity.update_codebase_workflow_status,
                args=[final_envelope],
                start_to_close_timeout=DB_ACTIVITY_TIMEOUT,
                retry_policy=DB_ACTIVITY_RETRY_POLICY,
            )
            bound_logger.debug(
                "[agent_workflow_interceptor] Final status {} recorded for codebase workflow",
                status,
            )

            # Only the parent releases admission, after all sibling work has stopped.

        if exc:
            raise exc
        return result
