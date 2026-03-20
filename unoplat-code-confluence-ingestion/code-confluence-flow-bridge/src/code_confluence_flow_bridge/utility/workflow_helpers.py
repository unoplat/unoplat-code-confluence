"""Workflow start, monitoring, and status helpers for Temporal workflows."""

from loguru import logger
from temporalio.client import Client, WorkflowHandle
from unoplat_code_confluence_commons.base_models import RepositoryWorkflowOperation
from unoplat_code_confluence_commons.workflow_models import JobStatus

from src.code_confluence_flow_bridge.models.code_confluence_parsing_models.unoplat_git_repository import (
    UnoplatGitRepository,
)
from src.code_confluence_flow_bridge.models.github.github_repo import (
    RepositoryRequestConfiguration,
)
from src.code_confluence_flow_bridge.models.workflow.repo_workflow_base import (
    RepoWorkflowRunEnvelope,
)
from src.code_confluence_flow_bridge.processor.repo_workflow import RepoWorkflow

CANCELLABLE_PARENT_WORKFLOW_OPERATIONS: set[RepositoryWorkflowOperation] = {
    RepositoryWorkflowOperation.AGENTS_GENERATION,
    RepositoryWorkflowOperation.AGENT_MD_UPDATE,
}

TERMINAL_PARENT_WORKFLOW_STATUSES: set[str] = {
    JobStatus.COMPLETED.value,
    JobStatus.FAILED.value,
    JobStatus.TIMED_OUT.value,
    JobStatus.ERROR.value,
    JobStatus.CANCELLED.value,
}


def is_parent_workflow_cancellable(
    operation: RepositoryWorkflowOperation,
    status: str,
) -> bool:
    """Return whether a parent workflow row can be canceled by UI users."""
    return (
        operation in CANCELLABLE_PARENT_WORKFLOW_OPERATIONS
        and status not in TERMINAL_PARENT_WORKFLOW_STATUSES
    )


async def start_workflow(
    temporal_client: Client,
    repo_request: RepositoryRequestConfiguration,
    github_token: str,
    workflow_id: str,
    trace_id: str,
) -> WorkflowHandle[RepoWorkflow, UnoplatGitRepository]:
    """
    Start a Temporal workflow for the given repository request and workflow id.
    """
    envelope = RepoWorkflowRunEnvelope(
        repo_request=repo_request, github_token=github_token, trace_id=trace_id
    )
    workflow_handle: WorkflowHandle[RepoWorkflow, UnoplatGitRepository] = (
        await temporal_client.start_workflow(
            RepoWorkflow.run,
            arg=envelope,
            id=workflow_id,
            task_queue="unoplat-code-confluence-repository-context-ingestion",
        )
    )
    logger.info(
        "Started workflow. Workflow ID: {}, RunID {}",
        workflow_handle.id,
        workflow_handle.result_run_id,
    )
    return workflow_handle


async def monitor_workflow(
    workflow_handle: WorkflowHandle[RepoWorkflow, UnoplatGitRepository],
) -> None:
    """Background task that awaits workflow completion and logs the outcome."""
    try:
        result = await workflow_handle.result()
        logger.info("Workflow completed with result: {}", result)
    except Exception as e:
        logger.error("Workflow failed: {}", e)
