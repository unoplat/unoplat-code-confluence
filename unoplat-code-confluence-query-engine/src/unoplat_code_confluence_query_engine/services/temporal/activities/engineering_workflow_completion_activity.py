"""Engineering workflow completion activity for Temporal workflows."""

from __future__ import annotations

from loguru import logger
from temporalio import activity

from unoplat_code_confluence_query_engine.services.temporal.event_stream_handler import (
    get_completion_namespaces,
)
from unoplat_code_confluence_query_engine.services.temporal.service_registry import (
    get_snapshot_writer,
)


class EngineeringWorkflowCompletionActivity:
    """Activity for emitting a single engineering workflow completion event."""

    @activity.defn
    async def emit_engineering_workflow_completion(
        self,
        repository_qualified_name: str,
        repository_workflow_run_id: str,
        codebase_name: str,
        programming_language: str,
    ) -> None:
        """Append a single completion event for development_workflow_guide."""
        if "/" not in repository_qualified_name:
            logger.warning(
                "[engineering_workflow_completion] Invalid repository_qualified_name: {}",
                repository_qualified_name,
            )
            return

        owner_name, repo_name = repository_qualified_name.split("/", 1)
        writer = get_snapshot_writer()

        await writer.append_event_atomic(
            owner_name=owner_name,
            repo_name=repo_name,
            codebase_name=codebase_name,
            agent_name="development_workflow_guide",
            phase="result",
            message="Development workflow guide completed",
            completion_namespaces=set(get_completion_namespaces(programming_language)),
            repository_workflow_run_id=repository_workflow_run_id,
        )

        logger.info(
            "[engineering_workflow_completion] Emitted completion event for {}/{} codebase={}",
            owner_name,
            repo_name,
            codebase_name,
        )
