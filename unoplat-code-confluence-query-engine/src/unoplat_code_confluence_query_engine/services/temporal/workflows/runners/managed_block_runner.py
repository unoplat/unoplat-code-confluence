from __future__ import annotations

from datetime import timedelta

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from loguru import logger

    from unoplat_code_confluence_query_engine.models.output.git_ref_info import (
        GitRefInfo,
    )
    from unoplat_code_confluence_query_engine.models.repository.repository_ruleset_metadata import (
        CodebaseMetadata,
    )
    from unoplat_code_confluence_query_engine.services.temporal.activities.codebase_workflow_run.managed_block_activity import (
        ManagedBlockActivity,
    )
    from unoplat_code_confluence_query_engine.services.temporal.interceptors.agent_workflow import (
        DB_ACTIVITY_RETRY_POLICY,
    )
    from unoplat_code_confluence_query_engine.services.temporal.utils import (
        raise_if_temporal_cancellation,
    )


async def run_managed_block_bootstrap(
    codebase_metadata: CodebaseMetadata,
    git_ref_info: GitRefInfo | None,
) -> None:
    """Bootstrap the managed block with markers and freshness metadata."""
    try:
        changed = await workflow.execute_activity(
            ManagedBlockActivity.bootstrap,
            args=[
                codebase_metadata.codebase_path,
                git_ref_info.default_branch if git_ref_info else None,
                git_ref_info.head_commit_sha if git_ref_info else None,
            ],
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=DB_ACTIVITY_RETRY_POLICY,
        )
        logger.info(
            "[workflow] Managed block bootstrap finished for {} changed={}",
            codebase_metadata.codebase_name,
            changed,
        )
    except Exception as e:
        raise_if_temporal_cancellation(e)
        logger.error("[workflow] Managed block bootstrap failed: {}", e)
