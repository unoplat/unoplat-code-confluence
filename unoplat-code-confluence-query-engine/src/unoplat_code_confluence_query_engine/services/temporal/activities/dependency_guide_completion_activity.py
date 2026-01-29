"""Dependency guide completion activity for Temporal workflows."""

from __future__ import annotations

from loguru import logger
from temporalio import activity

from unoplat_code_confluence_query_engine.services.temporal.event_stream_handler import (
    COMPLETION_NAMESPACES,
)
from unoplat_code_confluence_query_engine.services.temporal.service_registry import (
    get_snapshot_writer,
)


class DependencyGuideCompletionActivity:
    """Activity for emitting a single dependency_guide_agent completion event."""

    @activity.defn
    async def emit_dependency_guide_completion(
        self,
        repository_qualified_name: str,
        repository_workflow_run_id: str,
        codebase_name: str,
    ) -> None:
        """Append a single completion event for dependency_guide_agent."""
        if "/" not in repository_qualified_name:
            logger.warning(
                "[dependency_guide_completion] Invalid repository_qualified_name: {}",
                repository_qualified_name,
            )
            return

        owner_name, repo_name = repository_qualified_name.split("/", 1)
        writer = get_snapshot_writer()

        await writer.append_event_atomic(
            owner_name=owner_name,
            repo_name=repo_name,
            codebase_name=codebase_name,
            agent_name="dependency_guide_agent",
            phase="result",
            message="Dependency guide completed",
            completion_namespaces=set(COMPLETION_NAMESPACES),
            repository_workflow_run_id=repository_workflow_run_id,
        )

        logger.info(
            "[dependency_guide_completion] Emitted completion event for {}/{} codebase={}",
            owner_name,
            repo_name,
            codebase_name,
        )
