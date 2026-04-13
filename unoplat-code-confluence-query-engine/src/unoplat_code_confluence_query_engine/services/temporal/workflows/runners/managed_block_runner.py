from __future__ import annotations

from datetime import timedelta

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from loguru import logger

    from unoplat_code_confluence_query_engine.models.output.agents_md_updater_output import (
        ManagedBlockRunRecord,
    )
    from unoplat_code_confluence_query_engine.models.output.git_ref_info import (
        GitRefInfo,
    )
    from unoplat_code_confluence_query_engine.models.repository.repository_ruleset_metadata import (
        CodebaseMetadata,
    )
    from unoplat_code_confluence_query_engine.services.temporal.activities.codebase_workflow_run.managed_block_activity import (
        ManagedBlockActivity,
    )
    from unoplat_code_confluence_query_engine.services.temporal.interceptors.agent_workflow_interceptor import (
        DB_ACTIVITY_RETRY_POLICY,
    )


async def run_managed_block_bootstrap(
    codebase_metadata: CodebaseMetadata,
    git_ref_info: GitRefInfo | None,
    updater_runs: list[dict[str, object]],
) -> None:
    """Bootstrap the managed block with markers and freshness metadata."""
    try:
        bootstrap_output = await workflow.execute_activity(
            ManagedBlockActivity.bootstrap,
            args=[
                codebase_metadata.codebase_path,
                git_ref_info.default_branch if git_ref_info else None,
                git_ref_info.head_commit_sha if git_ref_info else None,
            ],
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=DB_ACTIVITY_RETRY_POLICY,
        )
        bootstrap_record = ManagedBlockRunRecord(
            lifecycle_step="bootstrap",
            agent_name="managed_block_bootstrap",
            output=bootstrap_output,
        )
        updater_runs.append(bootstrap_record.model_dump(mode="json"))
    except Exception as e:
        logger.error("[workflow] Managed block bootstrap failed: {}", e)
