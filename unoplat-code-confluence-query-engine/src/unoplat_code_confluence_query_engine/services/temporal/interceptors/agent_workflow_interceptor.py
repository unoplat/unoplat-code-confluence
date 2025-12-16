"""Temporal workflow interceptor for agent workflow status tracking.

This module provides the inbound interceptor that:
- Extracts trace_id from workflow arguments
- Sets up headers for propagation to activities and child workflows
- Tracks workflow status (RUNNING/COMPLETED/FAILED) in PostgreSQL
- Implements cascade failure (child fails → parent marked FAILED)
- Preserves FAILED status (never overwritten with COMPLETED)
"""

from __future__ import annotations

from datetime import timedelta
import traceback
from typing import Any, Optional
import uuid

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

with workflow.unsafe.imports_passed_through():
    from loguru import logger
    from unoplat_code_confluence_commons.workflow_envelopes import (
        CodebaseWorkflowDbActivityEnvelope,
        ParentWorkflowDbActivityEnvelope,
    )
    from unoplat_code_confluence_commons.workflow_models import ErrorReport, JobStatus

    from unoplat_code_confluence_query_engine.services.temporal.activities.codebase_workflow_db_activity import (
        CodebaseWorkflowDbActivity,
    )
    from unoplat_code_confluence_query_engine.services.temporal.activities.repository_workflow_db_activity import (
        RepositoryWorkflowDbActivity,
    )
    from unoplat_code_confluence_query_engine.services.temporal.interceptors.agent_workflow_outbound_interceptor import (
        AgentWorkflowOutboundInterceptor,
        workflow_headers_var,
    )
    from unoplat_code_confluence_query_engine.utils.trace_utils import (
        seed_and_bind_logger,
    )


# Default retry policy for DB activities
DB_ACTIVITY_RETRY_POLICY = RetryPolicy(
    initial_interval=timedelta(seconds=1),
    backoff_coefficient=2.0,
    maximum_attempts=3,
    maximum_interval=timedelta(seconds=10),
)


class AgentWorkflowStatusInterceptor(Interceptor):
    """Worker interceptor factory for agent workflow status tracking.

    This interceptor creates inbound interceptors for workflows that track
    their status in PostgreSQL and propagate context via headers.
    """

    def workflow_interceptor_class(
        self,
        input: Any,  # Interceptor.WorkflowInterceptorClassInput (not typed in SDK)
    ) -> type[WorkflowInboundInterceptor]:
        """Return the inbound interceptor class for workflows.

        Args:
            input: Interceptor class input containing workflow info

        Returns:
            The AgentWorkflowStatusInboundInterceptor class
        """
        return AgentWorkflowStatusInboundInterceptor


class AgentWorkflowStatusInboundInterceptor(WorkflowInboundInterceptor):
    """Inbound interceptor for workflows to track RUNNING/COMPLETED/FAILED status.

    This interceptor handles:
    - RepositoryAgentWorkflow: Main workflow for repository-level agent execution
    - CodebaseAgentWorkflow: Child workflow for codebase-level agent execution

    Features:
    - Extracts trace_id from workflow args[3]
    - Sets up headers for propagation to activities/children
    - Records RUNNING status at workflow start
    - Records COMPLETED/FAILED status at workflow end
    - Captures ErrorReport for failures (error_message, stack_trace, ApplicationError metadata)
    - Cascade failure: When child fails, parent is marked FAILED
    """

    def __init__(self, nxt: WorkflowInboundInterceptor) -> None:
        """Initialize the inbound interceptor.

        Args:
            nxt: Next interceptor in the chain
        """
        super().__init__(nxt)

    def init(self, outbound: Any) -> None:
        """Wrap outbound interceptor to forward headers to activities.

        Args:
            outbound: Original outbound interceptor
        """
        super().init(AgentWorkflowOutboundInterceptor(outbound))

    async def execute_workflow(self, input: ExecuteWorkflowInput) -> Any:
        """Execute the workflow with status tracking.

        Routes to appropriate handler based on workflow type:
        - RepositoryAgentWorkflow: _handle_repository_workflow
        - CodebaseAgentWorkflow: _handle_codebase_workflow
        - Other workflows: Pass through unchanged

        Args:
            input: Workflow execution input

        Returns:
            Workflow result
        """
        info: Info = workflow.info()
        workflow_type = info.workflow_type

        if workflow_type == "RepositoryAgentWorkflow":
            return await self._handle_repository_workflow(input, info)
        elif workflow_type == "CodebaseAgentWorkflow":
            return await self._handle_codebase_workflow(input, info)
        else:
            # Unknown workflow type, pass through
            logger.debug(
                "[agent_workflow_interceptor] Unknown workflow type {}, passing through",
                workflow_type,
            )
            return await self.next.execute_workflow(input)

    async def _handle_repository_workflow(
        self, input: ExecuteWorkflowInput, info: Info
    ) -> Any:
        """Handle RepositoryAgentWorkflow execution with status tracking.

        Args:
            input: Workflow execution input
            info: Workflow info

        Returns:
            Workflow result
        """
        # Extract args: args[0]=repository_qualified_name, args[1]=codebase_metadata_list,
        #               args[2]=repository_workflow_run_id, args[3]=trace_id
        repository_qualified_name: str = input.args[0]
        repository_workflow_run_id: str = input.args[2]
        trace_id: str = input.args[3] if len(input.args) > 3 else ""

        workflow_id = info.workflow_id
        workflow_run_id = info.run_id

        # Parse owner/repo from qualified name
        if "/" in repository_qualified_name:
            owner_name, repo_name = repository_qualified_name.split("/", maxsplit=1)
        else:
            owner_name = ""
            repo_name = repository_qualified_name

        # Set up headers for propagation
        input.headers = {
            "trace_id": Payload(data=trace_id.encode("utf-8")),
            "repository_name": Payload(data=repo_name.encode("utf-8")),
            "repository_owner_name": Payload(data=owner_name.encode("utf-8")),
            "workflow_run_id": Payload(data=workflow_run_id.encode("utf-8")),
            "repository_workflow_run_id": Payload(
                data=repository_workflow_run_id.encode("utf-8")
            ),
        }
        workflow_headers_var.set(input.headers)

        # Set up bound logger
        bound_logger = seed_and_bind_logger(
            trace_id=trace_id,
            workflow_id=workflow_id,
            workflow_run_id=workflow_run_id,
        )

        bound_logger.info(
            "[agent_workflow_interceptor] Starting RepositoryAgentWorkflow: "
            "trace_id={}, workflow_id={}, repository={}",
            trace_id,
            workflow_id,
            repository_qualified_name,
        )

        # Record RUNNING status
        running_envelope = ParentWorkflowDbActivityEnvelope(
            repository_name=repo_name,
            repository_owner_name=owner_name,
            workflow_id=workflow_id,
            workflow_run_id=repository_workflow_run_id,
            status=JobStatus.RUNNING.value,
            trace_id=trace_id,
        )
        await workflow.execute_activity(
            RepositoryWorkflowDbActivity.update_repository_workflow_status,
            args=[running_envelope],
            start_to_close_timeout=timedelta(minutes=1),
            retry_policy=DB_ACTIVITY_RETRY_POLICY,
        )
        bound_logger.debug(
            "[agent_workflow_interceptor] RUNNING status recorded for repository workflow"
        )

        # Execute workflow and track final status
        status = JobStatus.COMPLETED.value
        error_report: Optional[ErrorReport] = None
        result: Any = None
        exc: Optional[BaseException] = None

        try:
            result = await self.next.execute_workflow(input)
            bound_logger.info(
                "[agent_workflow_interceptor] RepositoryAgentWorkflow completed successfully"
            )
        except (ActivityError, ChildWorkflowError, ApplicationError, Exception) as e:
            exc = e
            status = JobStatus.ERROR.value
            error_report = self._build_error_report(e)
            bound_logger.error(
                "[agent_workflow_interceptor] RepositoryAgentWorkflow failed: {}",
                str(e),
            )
        finally:
            # Record final status
            final_envelope = ParentWorkflowDbActivityEnvelope(
                repository_name=repo_name,
                repository_owner_name=owner_name,
                workflow_id=workflow_id,
                workflow_run_id=repository_workflow_run_id,
                status=status,
                error_report=error_report,
                trace_id=trace_id,
            )
            await workflow.execute_activity(
                RepositoryWorkflowDbActivity.update_repository_workflow_status,
                args=[final_envelope],
                start_to_close_timeout=timedelta(minutes=1),
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
        """Handle CodebaseAgentWorkflow execution with status tracking.

        Args:
            input: Workflow execution input
            info: Workflow info

        Returns:
            Workflow result
        """
        # Extract args: args[0]=repository_qualified_name, args[1]=codebase_metadata_dict,
        #               args[2]=repository_workflow_run_id, args[3]=trace_id
        repository_qualified_name: str = input.args[0]
        codebase_metadata_dict: dict[str, Any] = input.args[1]
        repository_workflow_run_id: str = input.args[2]
        trace_id: str = input.args[3] if len(input.args) > 3 else ""

        workflow_id = info.workflow_id
        workflow_run_id = info.run_id

        # Extract codebase folder from metadata
        codebase_folder = codebase_metadata_dict.get("codebase_name", "unknown")

        # Parse owner/repo from qualified name
        if "/" in repository_qualified_name:
            owner_name, repo_name = repository_qualified_name.split("/", maxsplit=1)
        else:
            owner_name = ""
            repo_name = repository_qualified_name

        # Generate unique codebase workflow run ID
        codebase_workflow_run_id = uuid.uuid4().hex

        # Set up headers for propagation
        input.headers = {
            "trace_id": Payload(data=trace_id.encode("utf-8")),
            "repository_name": Payload(data=repo_name.encode("utf-8")),
            "repository_owner_name": Payload(data=owner_name.encode("utf-8")),
            "codebase_folder": Payload(data=codebase_folder.encode("utf-8")),
            "workflow_run_id": Payload(data=workflow_run_id.encode("utf-8")),
            "repository_workflow_run_id": Payload(
                data=repository_workflow_run_id.encode("utf-8")
            ),
            "codebase_workflow_run_id": Payload(
                data=codebase_workflow_run_id.encode("utf-8")
            ),
        }
        workflow_headers_var.set(input.headers)

        # Set up bound logger
        bound_logger = seed_and_bind_logger(
            trace_id=trace_id,
            workflow_id=workflow_id,
            workflow_run_id=workflow_run_id,
        )

        bound_logger.info(
            "[agent_workflow_interceptor] Starting CodebaseAgentWorkflow: "
            "trace_id={}, workflow_id={}, codebase={}",
            trace_id,
            workflow_id,
            codebase_folder,
        )

        # Record RUNNING status
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
            start_to_close_timeout=timedelta(minutes=1),
            retry_policy=DB_ACTIVITY_RETRY_POLICY,
        )
        bound_logger.debug(
            "[agent_workflow_interceptor] RUNNING status recorded for codebase workflow"
        )

        # Execute workflow and track final status
        status = JobStatus.COMPLETED.value
        error_report: Optional[ErrorReport] = None
        result: Any = None
        exc: Optional[BaseException] = None

        try:
            result = await self.next.execute_workflow(input)
            bound_logger.info(
                "[agent_workflow_interceptor] CodebaseAgentWorkflow completed successfully"
            )
        except (ActivityError, ChildWorkflowError, ApplicationError, Exception) as e:
            exc = e
            status = JobStatus.ERROR.value
            error_report = self._build_error_report(e)
            bound_logger.error(
                "[agent_workflow_interceptor] CodebaseAgentWorkflow failed: {}",
                str(e),
            )
        finally:
            # Record final status for codebase workflow
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
                start_to_close_timeout=timedelta(minutes=1),
                retry_policy=DB_ACTIVITY_RETRY_POLICY,
            )
            bound_logger.debug(
                "[agent_workflow_interceptor] Final status {} recorded for codebase workflow",
                status,
            )

            # CASCADE FAILURE: If codebase workflow failed, mark parent as ERROR too
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
                    error_report=None,
                    trace_id=trace_id,
                )
                await workflow.execute_activity(
                    RepositoryWorkflowDbActivity.update_repository_workflow_status,
                    args=[parent_failed_envelope],
                    start_to_close_timeout=timedelta(minutes=1),
                    retry_policy=DB_ACTIVITY_RETRY_POLICY,
                )
                bound_logger.info(
                    "[agent_workflow_interceptor] Parent repository workflow marked as ERROR"
                )

        if exc:
            raise exc
        return result

    def _build_error_report(self, exc: BaseException) -> ErrorReport:
        """Build an ErrorReport from an exception.

        Handles ActivityError, ChildWorkflowError, and ApplicationError specially
        to capture rich context from their cause/details.

        Args:
            exc: The exception to build a report from

        Returns:
            ErrorReport with error details
        """
        # Get root cause for activity/child workflow errors
        root = exc
        if isinstance(exc, (ActivityError, ChildWorkflowError)) and getattr(
            exc, "cause", None
        ):
            root = exc.cause  # type: ignore[assignment]

        # Build metadata for ApplicationError
        metadata: Optional[dict[str, Any]] = None
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

        return ErrorReport(
            error_message=str(root),
            stack_trace=traceback.format_exc() if root is not None else "",
            metadata=metadata,
        )
