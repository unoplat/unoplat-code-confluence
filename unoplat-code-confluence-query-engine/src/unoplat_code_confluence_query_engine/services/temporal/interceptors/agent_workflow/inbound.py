"""Temporal workflow interceptor for agent workflow status tracking."""

from __future__ import annotations

import asyncio
from datetime import timedelta
import traceback
from typing import Any, Optional

from temporalio import workflow
from temporalio.api.common.v1 import Payload
from temporalio.common import RetryPolicy
from temporalio.exceptions import ActivityError, ApplicationError, ChildWorkflowError
from temporalio.worker._interceptor import (
    ExecuteWorkflowInput,
    Interceptor,
    WorkflowInboundInterceptor,
)
from temporalio.workflow import Info

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
    from unoplat_code_confluence_commons.workflow_models import ErrorReport, JobStatus

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
        AgentSnapshotBeginRunEnvelope,
    )
    from unoplat_code_confluence_query_engine.utils.agent_error_logger import (
        extract_model_error_from_details,
        extract_model_error_from_exception,
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

WORKFLOW_EXECUTION_EXCEPTIONS: tuple[type[BaseException], ...] = (
    asyncio.CancelledError,
    Exception,
)


class AgentWorkflowStatusInterceptor(Interceptor):
    """Worker interceptor factory for agent workflow status tracking."""

    def workflow_interceptor_class(self, input: Any) -> type[WorkflowInboundInterceptor]:
        return AgentWorkflowStatusInboundInterceptor


class AgentWorkflowStatusInboundInterceptor(WorkflowInboundInterceptor):
    """Inbound interceptor for repository/codebase agent workflow status tracking."""

    def __init__(self, nxt: WorkflowInboundInterceptor) -> None:
        super().__init__(nxt)

    def init(self, outbound: Any) -> None:
        super().init(AgentWorkflowOutboundInterceptor(outbound))

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
        # Args: repository_qualified_name, codebase_metadata_list, trace_id
        repository_qualified_name: str = input.args[0]
        codebase_metadata_list: list[dict[str, Any]] = input.args[1]
        trace_id: str = input.args[2] if len(input.args) > 2 else ""

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
            "trace_id={}, workflow_id={}, run_id={}, repository={}",
            trace_id,
            workflow_id,
            repository_workflow_run_id,
            repository_qualified_name,
        )

        running_envelope = ParentWorkflowDbActivityEnvelope(
            repository_name=repo_name,
            repository_owner_name=owner_name,
            workflow_id=workflow_id,
            workflow_run_id=repository_workflow_run_id,
            status=JobStatus.RUNNING.value,
            operation=RepositoryWorkflowOperation.AGENTS_GENERATION,
            trace_id=trace_id,
        )
        await workflow.execute_activity(
            RepositoryWorkflowDbActivity.update_repository_workflow_status,
            args=[running_envelope],
            start_to_close_timeout=DB_ACTIVITY_TIMEOUT,
            retry_policy=DB_ACTIVITY_RETRY_POLICY,
        )
        bound_logger.debug(
            "[agent_workflow_interceptor] RUNNING status recorded for repository workflow"
        )

        status = JobStatus.COMPLETED.value
        error_report: Optional[ErrorReport] = None
        result: Any = None
        exc: Optional[BaseException] = None

        try:
            begin_envelope = AgentSnapshotBeginRunEnvelope(
                owner_name=owner_name,
                repo_name=repo_name,
                repository_qualified_name=repository_qualified_name,
                repository_workflow_run_id=repository_workflow_run_id,
                codebase_names=[
                    str(metadata.get("codebase_name", "unknown"))
                    for metadata in codebase_metadata_list
                ],
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
                bound_logger.info("[agent_workflow_interceptor] RepositoryAgentWorkflow cancelled")
            else:
                status = JobStatus.ERROR.value
                error_report = self._build_error_report(e)
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
                operation=RepositoryWorkflowOperation.AGENTS_GENERATION,
                error_report=error_report,
                trace_id=trace_id,
            )
            await workflow.execute_activity(
                RepositoryWorkflowDbActivity.update_repository_workflow_status,
                args=[final_envelope],
                start_to_close_timeout=DB_ACTIVITY_TIMEOUT,
                retry_policy=DB_ACTIVITY_RETRY_POLICY,
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
        trace_id: str = input.args[3] if len(input.args) > 3 else ""

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
                bound_logger.info("[agent_workflow_interceptor] CodebaseAgentWorkflow cancelled")
            else:
                status = JobStatus.ERROR.value
                error_report = self._build_error_report(e)
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

            if status == JobStatus.ERROR.value and repository_workflow_run_id:
                bound_logger.warning(
                    "[agent_workflow_interceptor] Codebase workflow failed, "
                    "marking parent repository workflow {} as ERROR",
                    repository_workflow_run_id,
                )
                parent_failed_envelope = ParentWorkflowDbActivityEnvelope(
                    repository_name=repo_name,
                    repository_owner_name=owner_name,
                    workflow_id=workflow_id,
                    workflow_run_id=repository_workflow_run_id,
                    status=JobStatus.ERROR.value,
                    operation=RepositoryWorkflowOperation.AGENTS_GENERATION,
                    error_report=None,
                    trace_id=trace_id,
                )
                await workflow.execute_activity(
                    RepositoryWorkflowDbActivity.update_repository_workflow_status,
                    args=[parent_failed_envelope],
                    start_to_close_timeout=DB_ACTIVITY_TIMEOUT,
                    retry_policy=DB_ACTIVITY_RETRY_POLICY,
                )
                bound_logger.info(
                    "[agent_workflow_interceptor] Parent repository workflow marked as ERROR"
                )

        if exc:
            raise exc
        return result

    def _build_error_report(self, exc: BaseException) -> ErrorReport:
        root: BaseException = exc
        if isinstance(exc, ActivityError) and exc.cause:
            root = exc.cause
        elif isinstance(exc, ChildWorkflowError) and exc.cause:
            root = exc.cause

        metadata: dict[str, Any] = {}

        if isinstance(root, ApplicationError):
            metadata = {
                "type": root.type,
                "details": root.details,
                "non_retryable": root.non_retryable,
                "next_retry_delay": (
                    root.next_retry_delay.total_seconds() if root.next_retry_delay else None
                ),
            }

        model_error_details = extract_model_error_from_exception(root)
        if not model_error_details and isinstance(root, ApplicationError):
            model_error_details = extract_model_error_from_details(root.details)
        if model_error_details:
            metadata["model_error"] = model_error_details

        return ErrorReport(
            error_message=str(root),
            stack_trace=traceback.format_exc(),
            metadata=metadata if metadata else None,
        )
