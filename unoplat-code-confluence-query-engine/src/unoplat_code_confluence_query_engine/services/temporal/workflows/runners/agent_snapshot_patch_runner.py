from __future__ import annotations

from datetime import timedelta
from typing import Any

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from unoplat_code_confluence_query_engine.services.temporal.interceptors.agent_workflow.activity.repository_agent_snapshot_activity import (
        RepositoryAgentSnapshotActivity,
    )
    from unoplat_code_confluence_query_engine.services.temporal.debug_timeouts import (
        debug_timeout,
    )
    from unoplat_code_confluence_query_engine.services.temporal.interceptors.agent_workflow import (
        DB_ACTIVITY_RETRY_POLICY,
    )
    from unoplat_code_confluence_query_engine.services.temporal.workflow_envelopes import (
        AgentSnapshotCodebasePatchEnvelope,
    )


async def persist_codebase_snapshot_patch(
    *,
    repository_qualified_name: str,
    repository_workflow_run_id: str,
    codebase_name: str,
    codebase_patch: dict[str, Any],
) -> None:
    """Persist a partial codebase snapshot patch through a Temporal activity."""
    owner_name, repo_name = repository_qualified_name.split("/", maxsplit=1)
    patch_envelope = AgentSnapshotCodebasePatchEnvelope(
        owner_name=owner_name,
        repo_name=repo_name,
        repository_workflow_run_id=repository_workflow_run_id,
        codebase_name=codebase_name,
        codebase_patch=codebase_patch,
    )
    await workflow.execute_activity(
        RepositoryAgentSnapshotActivity.persist_agent_snapshot_codebase_patch,
        args=[patch_envelope],
        start_to_close_timeout=debug_timeout(
            timedelta(minutes=2),
            env_name="QUERY_ENGINE_TEMPORAL_DB_ACTIVITY_TIMEOUT_SECONDS",
        ),
        retry_policy=DB_ACTIVITY_RETRY_POLICY,
    )
