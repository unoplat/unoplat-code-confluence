from __future__ import annotations

from datetime import timedelta

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from loguru import logger

    from unoplat_code_confluence_query_engine.services.temporal.debug_timeouts import (
        debug_timeout,
    )

    from unoplat_code_confluence_query_engine.models.output.git_ref_info import (
        GitRefInfo,
    )
    from unoplat_code_confluence_query_engine.services.temporal.activities.repository_workflow_run.git_ref_resolution_activity import (
        GitRefResolutionActivity,
    )
    from unoplat_code_confluence_query_engine.services.temporal.interceptors.agent_workflow import (
        DB_ACTIVITY_RETRY_POLICY,
    )


async def resolve_repository_git_ref(
    repository_qualified_name: str,
) -> GitRefInfo | None:
    """Resolve repository git-ref info for freshness metadata."""
    owner_name, repo_name = repository_qualified_name.split("/", maxsplit=1)
    try:
        return await workflow.execute_activity(
            GitRefResolutionActivity.resolve_git_ref,
            args=[owner_name, repo_name],
            start_to_close_timeout=debug_timeout(
                timedelta(seconds=30),
                env_name="QUERY_ENGINE_TEMPORAL_DB_ACTIVITY_TIMEOUT_SECONDS",
            ),
            retry_policy=DB_ACTIVITY_RETRY_POLICY,
        )
    except Exception as e:
        logger.warning(
            "[workflow] Git ref resolution failed, proceeding without freshness metadata: {}",
            e,
        )
        return None
