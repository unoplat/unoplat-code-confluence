from __future__ import annotations

from datetime import timedelta

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from loguru import logger

    from unoplat_code_confluence_query_engine.models.output.agent_md_output import (
        Interfaces,
    )
    from unoplat_code_confluence_query_engine.models.repository.repository_ruleset_metadata import (
        CodebaseMetadata,
    )
    from unoplat_code_confluence_query_engine.models.statistics.agent_usage_statistics import (
        UsageStatistics,
    )
    from unoplat_code_confluence_query_engine.services.temporal.activities.codebase_workflow_run.app_interfaces_activity import (
        AppInterfacesActivity,
    )
    from unoplat_code_confluence_query_engine.services.temporal.interceptors.agent_workflow import (
        DB_ACTIVITY_RETRY_POLICY,
    )
    from unoplat_code_confluence_query_engine.services.temporal.temporal_agents import (
        TemporalAgentRegistry,
    )
    from unoplat_code_confluence_query_engine.services.temporal.utils import (
        raise_if_temporal_cancellation,
        summarize_agent_failure,
    )
    from unoplat_code_confluence_query_engine.services.temporal.workflows.runners.call_expression_discovery_runner import (
        run_call_expression_discovery,
    )
    from unoplat_code_confluence_query_engine.utils.framework_feature_language_support import (
        is_app_interfaces_supported,
    )


async def run_app_interfaces_agent(
    temporal_agents: TemporalAgentRegistry,
    repository_qualified_name: str,
    codebase_metadata: CodebaseMetadata,
    repository_workflow_run_id: str,
    codebase_workflow_run_id: str,
    programming_language_metadata: dict[str, object],
    agent_stats: list[UsageStatistics],
    agent_errors: list[dict[str, object]],
) -> Interfaces | None:
    """Build, render, and return app interfaces when the language is supported."""
    _ = programming_language_metadata

    if not is_app_interfaces_supported(codebase_metadata.codebase_programming_language):
        logger.info(
            "[workflow] app_interfaces_agent skipped (language: {})",
            codebase_metadata.codebase_programming_language,
        )
        return

    try:
        discovery_targets = await workflow.execute_activity(
            AppInterfacesActivity.fetch_call_expression_discovery_targets,
            args=[
                codebase_metadata.codebase_path,
                codebase_metadata.codebase_programming_language,
            ],
            start_to_close_timeout=timedelta(minutes=2),
            retry_policy=DB_ACTIVITY_RETRY_POLICY,
        )

        await run_call_expression_discovery(
            temporal_agents=temporal_agents,
            codebase_metadata=codebase_metadata,
            repository_qualified_name=repository_qualified_name,
            repository_workflow_run_id=repository_workflow_run_id,
            codebase_workflow_run_id=codebase_workflow_run_id,
            targets=discovery_targets,
            agent_stats=agent_stats,
            agent_errors=agent_errors,
        )

        logger.info(
            "[workflow] Running app_interfaces_agent for {}",
            codebase_metadata.codebase_name,
        )
        app_interfaces_result = await workflow.execute_activity(
            AppInterfacesActivity.build_app_interfaces,
            args=[
                codebase_metadata.codebase_path,
                codebase_metadata.codebase_programming_language,
            ],
            start_to_close_timeout=timedelta(minutes=2),
            retry_policy=DB_ACTIVITY_RETRY_POLICY,
        )
        await workflow.execute_activity(
            AppInterfacesActivity.write_app_interfaces,
            args=[
                codebase_metadata.codebase_path,
                app_interfaces_result,
            ],
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=DB_ACTIVITY_RETRY_POLICY,
        )
        logger.info(
            "[workflow] app_interfaces.md render completed for {}",
            codebase_metadata.codebase_name,
        )

        await workflow.execute_activity(
            AppInterfacesActivity.emit_app_interfaces_completion,
            args=[
                repository_qualified_name,
                repository_workflow_run_id,
                codebase_metadata.codebase_name,
                codebase_metadata.codebase_programming_language,
            ],
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=DB_ACTIVITY_RETRY_POLICY,
        )

        logger.info(
            "[workflow] app_interfaces_agent completed for {}",
            codebase_metadata.codebase_name,
        )
        return app_interfaces_result
    except Exception as e:
        raise_if_temporal_cancellation(e)
        logger.error(
            "[workflow] app_interfaces_agent failed for {}: {}",
            codebase_metadata.codebase_name,
            e,
        )
        logger.exception("[workflow] Full traceback:")
        agent_errors.append(
            summarize_agent_failure(
                e,
                agent_name="app_interfaces_agent",
                codebase_name=codebase_metadata.codebase_name,
            )
        )
        return None
