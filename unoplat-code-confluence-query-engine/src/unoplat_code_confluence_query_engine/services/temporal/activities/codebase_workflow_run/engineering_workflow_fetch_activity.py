"""Engineering workflow fetch activities for Temporal workflows."""

from __future__ import annotations

from loguru import logger
from src.unoplat_code_confluence_query_engine.models.output.engineering_workflow_output import (
    EngineeringWorkflow,
)
from temporalio import activity

from unoplat_code_confluence_query_engine.services.tracking.repository_agent_snapshot_service import (
    fetch_latest_completed_codebase_engineering_workflow,
)


class EngineeringWorkflowFetchActivity:
    """Activity for fetching previous engineering workflow state."""

    @activity.defn
    async def fetch_previous_engineering_workflow(
        self,
        repository_qualified_name: str,
        repository_workflow_run_id: str,
        codebase_name: str,
    ) -> EngineeringWorkflow | None:
        """Fetch latest previous structured engineering workflow for a codebase."""
        if "/" not in repository_qualified_name:
            logger.warning(
                "[engineering_workflow_fetch] Invalid repository_qualified_name: {}",
                repository_qualified_name,
            )
            return None

        owner_name, repo_name = repository_qualified_name.split("/", 1)
        return await fetch_latest_completed_codebase_engineering_workflow(
            owner_name=owner_name,
            repo_name=repo_name,
            codebase_name=codebase_name,
            exclude_repository_workflow_run_id=repository_workflow_run_id,
        )
