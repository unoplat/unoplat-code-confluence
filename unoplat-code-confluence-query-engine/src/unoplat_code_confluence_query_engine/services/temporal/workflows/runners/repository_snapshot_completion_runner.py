from __future__ import annotations

from datetime import timedelta
from typing import Any

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from loguru import logger

    from unoplat_code_confluence_query_engine.services.temporal.activities.repository_workflow_run.repository_agent_snapshot_activity import (
        RepositoryAgentSnapshotActivity,
    )
    from unoplat_code_confluence_query_engine.services.temporal.interceptors.agent_workflow_interceptor import (
        DB_ACTIVITY_RETRY_POLICY,
    )
    from unoplat_code_confluence_query_engine.services.temporal.workflow_envelopes import (
        AgentSnapshotCompleteEnvelope,
    )


async def persist_repository_snapshot_completion(
    repository_qualified_name: str,
    repository_workflow_run_id: str,
    results: dict[str, Any],
    statistics_payload: dict[str, Any],
) -> None:
    """Persist the final repository workflow snapshot output."""
    owner_name, repo_name = repository_qualified_name.split("/", maxsplit=1)
    complete_envelope = AgentSnapshotCompleteEnvelope(
        owner_name=owner_name,
        repo_name=repo_name,
        repository_workflow_run_id=repository_workflow_run_id,
        final_payload=results,
        statistics_payload=statistics_payload,
    )
    await workflow.execute_activity(
        RepositoryAgentSnapshotActivity.persist_agent_snapshot_complete,
        args=[complete_envelope],
        start_to_close_timeout=timedelta(minutes=2),
        retry_policy=DB_ACTIVITY_RETRY_POLICY,
    )
    logger.info(
        "[workflow] Agent snapshot output persisted for {}",
        repository_qualified_name,
    )
