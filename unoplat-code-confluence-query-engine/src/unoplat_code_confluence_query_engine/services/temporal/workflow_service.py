"""Service for triggering Temporal workflows from API endpoints."""

from __future__ import annotations

from typing import TYPE_CHECKING
import uuid

from loguru import logger

from unoplat_code_confluence_query_engine.models.repository.repository_ruleset_metadata import (
    RepositoryRulesetMetadata,
)
from unoplat_code_confluence_query_engine.services.temporal.temporal_worker_manager import (
    TASK_QUEUE,
)
from unoplat_code_confluence_query_engine.services.temporal.workflows import (
    RepositoryAgentWorkflow,
)

if TYPE_CHECKING:
    from temporalio.client import Client


class TemporalWorkflowService:
    """Service for starting Temporal workflows.

    The Temporal workflow ID is generated before start for lifecycle operations,
    while the repository workflow run ID returned to callers is Temporal's real
    ``result_run_id``. Initial DB/snapshot rows are created by workflow
    interceptors using ``workflow.info().run_id``.
    """

    def __init__(self, temporal_client: Client) -> None:
        self._client = temporal_client

    async def start_workflow(
        self,
        *,
        ruleset_metadata: RepositoryRulesetMetadata,
        trace_id: str,
    ) -> str:
        """Start a RepositoryAgentWorkflow and return Temporal's repository run ID."""
        bound_logger = logger.bind(app_trace_id=trace_id)

        repository_qualified_name = ruleset_metadata.repository_qualified_name
        if "/" not in repository_qualified_name:
            raise ValueError(
                f"Invalid repository_qualified_name format: {repository_qualified_name}. "
                "Expected 'owner/repo'"
            )

        owner_name, repo_name = repository_qualified_name.split("/", maxsplit=1)
        workflow_id = f"agent-{repository_qualified_name.replace('/', '-')}-{uuid.uuid4().hex[:8]}"

        codebase_metadata_list = [
            metadata.model_dump() for metadata in ruleset_metadata.codebase_metadata
        ]

        bound_logger.info(
            "[workflow_service] Starting RepositoryAgentWorkflow with id={}, "
            "repository={}/{}, codebases={}, trace_id={}",
            workflow_id,
            owner_name,
            repo_name,
            len(codebase_metadata_list),
            trace_id,
        )

        workflow_handle = await self._client.start_workflow(
            RepositoryAgentWorkflow.run,
            args=[
                repository_qualified_name,
                codebase_metadata_list,
                trace_id,
            ],
            id=workflow_id,
            task_queue=TASK_QUEUE,
        )

        repository_workflow_run_id = workflow_handle.result_run_id
        bound_logger.info(
            "[workflow_service] Workflow started successfully: workflow_id={}, temporal_run_id={}",
            workflow_handle.id,
            repository_workflow_run_id,
        )

        return repository_workflow_run_id
