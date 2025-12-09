"""Service for triggering Temporal workflows from API endpoints."""

from __future__ import annotations

from typing import TYPE_CHECKING
import uuid

from loguru import logger

from unoplat_code_confluence_query_engine.models.repository.repository_ruleset_metadata import (
    RepositoryRulesetMetadata,
)
from unoplat_code_confluence_query_engine.services.temporal.service_registry import (
    get_snapshot_writer,
)
from unoplat_code_confluence_query_engine.services.temporal.temporal_worker import (
    TASK_QUEUE,
)
from unoplat_code_confluence_query_engine.services.temporal.temporal_workflows import (
    RepositoryAgentWorkflow,
)
from unoplat_code_confluence_query_engine.services.workflow.workflow_run_initializer import (
    ensure_workflow_run_exists,
)

if TYPE_CHECKING:
    from temporalio.client import Client


class TemporalWorkflowService:
    """Service for starting Temporal workflows.

    This service is used by the API endpoint to trigger Temporal workflows
    with trace_id from the API level. It handles:
    - Generating workflow IDs and run IDs
    - Ensuring DB records exist (Repository, RepositoryWorkflowRun)
    - Initializing snapshot tracking
    - Starting the Temporal workflow
    """

    def __init__(self, temporal_client: Client) -> None:
        """Initialize the workflow service.

        Args:
            temporal_client: Connected Temporal client instance
        """
        self._client = temporal_client

    async def start_workflow(
        self,
        *,
        ruleset_metadata: RepositoryRulesetMetadata,
        trace_id: str,
        repository_workflow_run_id: str | None = None,
    ) -> str:
        """Start a RepositoryAgentWorkflow for the given repository.

        Args:
            ruleset_metadata: Repository metadata with codebase information
            trace_id: Trace ID for distributed tracing (from API dependency)
            repository_workflow_run_id: Optional pre-generated workflow run ID.
                                       If not provided, a new UUID will be generated.

        Returns:
            The repository_workflow_run_id used for tracking

        Raises:
            Exception: If workflow fails to start
        """
        bound_logger = logger.bind(app_trace_id=trace_id)

        # Parse owner/repo from qualified name
        repository_qualified_name = ruleset_metadata.repository_qualified_name
        if "/" not in repository_qualified_name:
            raise ValueError(
                f"Invalid repository_qualified_name format: {repository_qualified_name}. "
                "Expected 'owner/repo'"
            )

        owner_name, repo_name = repository_qualified_name.split("/", maxsplit=1)

        # Generate workflow run ID if not provided
        if repository_workflow_run_id is None:
            repository_workflow_run_id = uuid.uuid4().hex

        bound_logger.info(
            "[workflow_service] Starting workflow for {}/{} with run_id={}",
            owner_name,
            repo_name,
            repository_workflow_run_id,
        )

        # Ensure parent records exist (Repository + RepositoryWorkflowRun)
        # This satisfies foreign key constraints for RepositoryAgentMdSnapshot
        await ensure_workflow_run_exists(
            owner_name=owner_name,
            repo_name=repo_name,
            repository_workflow_run_id=repository_workflow_run_id,
        )
        bound_logger.info(
            "[workflow_service] Ensured Repository and RepositoryWorkflowRun records exist"
        )

        # Initialize snapshot tracking with begin_run()
        codebase_names = [
            metadata.codebase_name for metadata in ruleset_metadata.codebase_metadata
        ]
        snapshot_writer = get_snapshot_writer()
        await snapshot_writer.begin_run(
            owner_name=owner_name,
            repo_name=repo_name,
            repository_qualified_name=repository_qualified_name,
            repository_workflow_run_id=repository_workflow_run_id,
            codebase_names=codebase_names,
        )
        bound_logger.info(
            "[workflow_service] Snapshot tracking initialized for {} codebases",
            len(codebase_names),
        )

        # Serialize codebase metadata for workflow args
        codebase_metadata_list = [
            metadata.model_dump() for metadata in ruleset_metadata.codebase_metadata
        ]

        # Generate workflow ID
        workflow_id = f"agent-{repository_qualified_name.replace('/', '-')}-{uuid.uuid4().hex[:8]}"

        bound_logger.info(
            "[workflow_service] Starting RepositoryAgentWorkflow with id={}, "
            "repository={}, codebases={}, trace_id={}",
            workflow_id,
            repository_qualified_name,
            len(codebase_metadata_list),
            trace_id,
        )

        # Start the workflow (non-blocking - returns immediately)
        await self._client.start_workflow(
            RepositoryAgentWorkflow.run,
            args=[
                repository_qualified_name,
                codebase_metadata_list,
                repository_workflow_run_id,
                trace_id,
            ],
            id=workflow_id,
            task_queue=TASK_QUEUE,
        )

        bound_logger.info(
            "[workflow_service] Workflow started successfully: workflow_id={}, run_id={}",
            workflow_id,
            repository_workflow_run_id,
        )

        return repository_workflow_run_id
