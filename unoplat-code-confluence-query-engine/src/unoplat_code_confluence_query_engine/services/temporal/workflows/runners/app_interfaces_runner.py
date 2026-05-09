from __future__ import annotations

from datetime import timedelta
import traceback

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from loguru import logger

    from unoplat_code_confluence_query_engine.models.repository.repository_ruleset_metadata import (
        CodebaseMetadata,
    )
    from unoplat_code_confluence_query_engine.models.statistics.agent_usage_statistics import (
        UsageStatistics,
    )
    from unoplat_code_confluence_query_engine.services.temporal.activities.codebase_workflow_run.app_interfaces_activity import (
        AppInterfacesActivity,
    )
    from unoplat_code_confluence_query_engine.services.temporal.debug_timeouts import (
        debug_timeout,
    )
    from unoplat_code_confluence_query_engine.services.temporal.interceptors.agent_workflow import (
        DB_ACTIVITY_RETRY_POLICY,
    )
    from unoplat_code_confluence_query_engine.services.temporal.temporal_agents import (
        TemporalAgentRegistry,
    )
    from unoplat_code_confluence_query_engine.services.temporal.utils import (
        enrich_agent_error_with_model_details,
        raise_if_temporal_cancellation,
    )
    from unoplat_code_confluence_query_engine.services.temporal.workflows.runners.agent_snapshot_patch_runner import (
        persist_codebase_snapshot_patch,
    )
    from unoplat_code_confluence_query_engine.services.temporal.workflows.runners.call_expression_validation_runner import (
        run_call_expression_validation,
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
) -> None:
    """Build app interfaces and render the canonical reference file when supported."""
    _ = programming_language_metadata

    if not is_app_interfaces_supported(codebase_metadata.codebase_programming_language):
        logger.info(
            "[workflow] app_interfaces_agent skipped (language: {})",
            codebase_metadata.codebase_programming_language,
        )
        return

    try:
        candidate_payloads = await workflow.execute_activity(
            AppInterfacesActivity.fetch_low_confidence_call_expression_candidates,
            args=[
                codebase_metadata.codebase_path,
                codebase_metadata.codebase_programming_language,
            ],
            start_to_close_timeout=debug_timeout(
                timedelta(minutes=2),
                env_name="QUERY_ENGINE_TEMPORAL_DB_ACTIVITY_TIMEOUT_SECONDS",
            ),
            retry_policy=DB_ACTIVITY_RETRY_POLICY,
        )

        await run_call_expression_validation(
            temporal_agents=temporal_agents,
            codebase_metadata=codebase_metadata,
            repository_qualified_name=repository_qualified_name,
            repository_workflow_run_id=repository_workflow_run_id,
            codebase_workflow_run_id=codebase_workflow_run_id,
            candidate_payloads=candidate_payloads,
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
            start_to_close_timeout=debug_timeout(
                timedelta(minutes=2),
                env_name="QUERY_ENGINE_TEMPORAL_DB_ACTIVITY_TIMEOUT_SECONDS",
            ),
            retry_policy=DB_ACTIVITY_RETRY_POLICY,
        )
        await workflow.execute_activity(
            AppInterfacesActivity.write_app_interfaces,
            args=[
                codebase_metadata.codebase_path,
                app_interfaces_result,
            ],
            start_to_close_timeout=debug_timeout(
                timedelta(seconds=30),
                env_name="QUERY_ENGINE_TEMPORAL_DB_ACTIVITY_TIMEOUT_SECONDS",
            ),
            retry_policy=DB_ACTIVITY_RETRY_POLICY,
        )
        logger.info(
            "[workflow] app_interfaces.md render completed for {}",
            codebase_metadata.codebase_name,
        )

        await persist_codebase_snapshot_patch(
            repository_qualified_name=repository_qualified_name,
            repository_workflow_run_id=repository_workflow_run_id,
            codebase_name=codebase_metadata.codebase_name,
            codebase_patch={"app_interfaces": app_interfaces_result},
        )

        await workflow.execute_activity(
            AppInterfacesActivity.emit_app_interfaces_completion,
            args=[
                repository_qualified_name,
                repository_workflow_run_id,
                codebase_metadata.codebase_name,
                codebase_metadata.codebase_programming_language,
            ],
            start_to_close_timeout=debug_timeout(
                timedelta(seconds=30),
                env_name="QUERY_ENGINE_TEMPORAL_DB_ACTIVITY_TIMEOUT_SECONDS",
            ),
            retry_policy=DB_ACTIVITY_RETRY_POLICY,
        )

        logger.info(
            "[workflow] app_interfaces_agent completed for {}",
            codebase_metadata.codebase_name,
        )
    except Exception as e:
        raise_if_temporal_cancellation(e)
        logger.error(
            "[workflow] app_interfaces_agent failed for {}: {}",
            codebase_metadata.codebase_name,
            e,
        )
        logger.exception("[workflow] Full traceback:")
        app_interfaces_error: dict[str, object] = {
            "agent": "app_interfaces_agent",
            "codebase": codebase_metadata.codebase_name,
            "error": str(e),
            "traceback": traceback.format_exc(),
        }
        app_interfaces_error = enrich_agent_error_with_model_details(
            app_interfaces_error,
            e,
            "app_interfaces_agent",
            codebase_metadata.codebase_name,
        )
        agent_errors.append(app_interfaces_error)
