from __future__ import annotations

from datetime import timedelta
import traceback
from typing import Any

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from loguru import logger

    from unoplat_code_confluence_query_engine.models.repository.repository_ruleset_metadata import (
        CodebaseMetadata,
    )
    from unoplat_code_confluence_query_engine.models.runtime.agent_dependencies import (
        AgentDependencies,
    )
    from unoplat_code_confluence_query_engine.models.runtime.dependency_guide_target import (
        DependencyGuideTarget,
    )
    from unoplat_code_confluence_query_engine.models.statistics.agent_usage_statistics import (
        UsageStatistics,
    )
    from unoplat_code_confluence_query_engine.services.temporal.activities.codebase_workflow_run.dependency_guide_completion_activity import (
        DependencyGuideCompletionActivity,
    )
    from unoplat_code_confluence_query_engine.services.temporal.activities.codebase_workflow_run.dependency_guide_fetch_activity import (
        DependencyGuideFetchActivity,
    )
    from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.agents.user_prompts.build_user_prompt_dependency_guide import (
        build_dependency_guide_prompt,
    )
    from unoplat_code_confluence_query_engine.services.temporal.interceptors.agent_workflow_interceptor import (
        DB_ACTIVITY_RETRY_POLICY,
    )
    from unoplat_code_confluence_query_engine.services.temporal.statistics_helpers import (
        aggregate_usage_statistics,
        create_zero_usage_statistics,
        extract_usage_statistics,
    )
    from unoplat_code_confluence_query_engine.services.temporal.temporal_agents import (
        TemporalAgentRegistry,
        get_cached_usage_limits,
    )
    from unoplat_code_confluence_query_engine.services.temporal.utils import (
        enrich_agent_error_with_model_details,
        raise_if_temporal_cancellation,
    )


async def run_dependency_guide_agent(
    temporal_agents: TemporalAgentRegistry,
    repository_qualified_name: str,
    codebase_metadata: CodebaseMetadata,
    repository_workflow_run_id: str,
    programming_language_metadata: dict[str, object],
    results: dict[str, Any],
    agent_stats: list[UsageStatistics],
    agent_errors: list[dict[str, object]],
) -> None:
    """Run dependency-guide target fetch, agent synthesis, and artifact write."""
    _ = programming_language_metadata

    dependency_guide_agent = temporal_agents.dependency_guide
    if dependency_guide_agent is None:
        logger.info(
            "[workflow] dependency_guide is disabled, skipping for {}",
            codebase_metadata.codebase_name,
        )
        agent_stats.append(create_zero_usage_statistics())
        return

    try:
        dependency_targets: list[DependencyGuideTarget] = await workflow.execute_activity(
            DependencyGuideFetchActivity.fetch_codebase_dependencies,
            args=[
                codebase_metadata.codebase_path,
                codebase_metadata.codebase_programming_language,
                codebase_metadata.codebase_package_manager,
            ],
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=DB_ACTIVITY_RETRY_POLICY,
        )

        logger.info(
            "[workflow] Found {} dependency-guide targets for {}",
            len(dependency_targets),
            codebase_metadata.codebase_name,
        )

        dependency_entries: list[dict[str, Any]] = []
        dependency_agent_stats: list[UsageStatistics] = []

        for dependency_target in dependency_targets:
            deps = AgentDependencies(
                repository_qualified_name=repository_qualified_name,
                codebase_metadata=codebase_metadata,
                repository_workflow_run_id=repository_workflow_run_id,
                agent_name="dependency_guide_item",
            )
            try:
                result = await dependency_guide_agent.run(
                    build_dependency_guide_prompt(
                        dependency_target=dependency_target,
                        programming_language=codebase_metadata.codebase_programming_language,
                    ),
                    deps=deps,
                    usage_limits=get_cached_usage_limits(),
                )

                entry_dict = result.output.model_dump()
                dependency_entries.append(entry_dict)
                dependency_agent_stats.append(
                    extract_usage_statistics(result.usage())
                )
            except Exception as dep_error:
                raise_if_temporal_cancellation(dep_error)
                logger.warning(
                    "[workflow] Failed to document dependency '{}': {}",
                    dependency_target.name,
                    dep_error,
                )
                dependency_agent_stats.append(create_zero_usage_statistics())

        results["dependency_guide"] = {"dependencies": dependency_entries}

        # Append stats before fallible activities to preserve real usage data
        if dependency_agent_stats:
            agent_stats.append(aggregate_usage_statistics(dependency_agent_stats))
        else:
            agent_stats.append(create_zero_usage_statistics())

        await workflow.execute_activity(
            DependencyGuideCompletionActivity.write_dependency_overview,
            args=[
                codebase_metadata.codebase_path,
                dependency_entries,
                codebase_metadata.codebase_package_manager,
            ],
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=DB_ACTIVITY_RETRY_POLICY,
        )

        await workflow.execute_activity(
            DependencyGuideCompletionActivity.emit_dependency_guide_completion,
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
            "[workflow] dependency_guide completed for {}: {} entries",
            codebase_metadata.codebase_name,
            len(dependency_entries),
        )
    except Exception as e:
        raise_if_temporal_cancellation(e)
        logger.error(
            "[workflow] dependency_guide failed for {}: {}",
            codebase_metadata.codebase_name,
            e,
        )
        logger.exception("[workflow] Full traceback:")
        dependency_error: dict[str, object] = {
            "agent": "dependency_guide",
            "codebase": codebase_metadata.codebase_name,
            "error": str(e),
            "traceback": traceback.format_exc(),
        }
        dependency_error = enrich_agent_error_with_model_details(
            dependency_error,
            e,
            "dependency_guide",
            codebase_metadata.codebase_name,
        )
        agent_errors.append(dependency_error)
        agent_stats.append(create_zero_usage_statistics())
