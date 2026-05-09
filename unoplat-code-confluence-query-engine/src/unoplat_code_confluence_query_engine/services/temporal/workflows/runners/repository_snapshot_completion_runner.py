from __future__ import annotations

from datetime import timedelta

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from loguru import logger

    from unoplat_code_confluence_query_engine.services.temporal.interceptors.agent_workflow import (
        DB_ACTIVITY_RETRY_POLICY,
    )
    from unoplat_code_confluence_query_engine.services.temporal.interceptors.agent_workflow.activity.repository_agent_snapshot_activity import (
        RepositoryAgentSnapshotActivity,
    )
    from unoplat_code_confluence_query_engine.services.temporal.workflow_envelopes import (
        AgentSnapshotCompleteEnvelope,
    )


async def persist_repository_snapshot_completion(
    repository_qualified_name: str,
    repository_workflow_run_id: str,
    statistics_payload: dict[str, object],
) -> None:
    """Persist final repository workflow statistics without overwriting output."""
    owner_name, repo_name = repository_qualified_name.split("/", maxsplit=1)
    complete_envelope = AgentSnapshotCompleteEnvelope(
        owner_name=owner_name,
        repo_name=repo_name,
        repository_workflow_run_id=repository_workflow_run_id,
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
