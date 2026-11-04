from __future__ import annotations

from datetime import timedelta
import traceback

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from loguru import logger

    from unoplat_code_confluence_query_engine.models.output.engineering_workflow_output import (
        ENGINEERING_WORKFLOW_FULL_OUTPUT,
        ENGINEERING_WORKFLOW_NO_CHANGE,
    )
    from unoplat_code_confluence_query_engine.models.repository.repository_ruleset_metadata import (
        CodebaseMetadata,
    )
    from unoplat_code_confluence_query_engine.models.runtime.agent_dependencies import (
        AgentDependencies,
        build_agent_run_metadata,
    )
    from unoplat_code_confluence_query_engine.models.statistics.agent_usage_statistics import (
        UsageStatistics,
    )
    from unoplat_code_confluence_query_engine.services.temporal.activities.codebase_workflow_run.engineering_workflow_completion_activity import (
        EngineeringWorkflowCompletionActivity,
    )
    from unoplat_code_confluence_query_engine.services.temporal.activities.codebase_workflow_run.engineering_workflow_fetch_activity import (
        EngineeringWorkflowFetchActivity,
    )
    from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.agents.user_prompts.build_user_prompt_development_workflow import (
        build_development_workflow_prompt,
    )
    from unoplat_code_confluence_query_engine.services.temporal.interceptors.agent_workflow import (
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


async def run_development_workflow_agent(
    temporal_agents: TemporalAgentRegistry,
    repository_qualified_name: str,
    codebase_metadata: CodebaseMetadata,
    repository_workflow_run_id: str,
    codebase_workflow_run_id: str,
    programming_language_metadata: dict[str, object],
    agent_stats: list[UsageStatistics],
    agent_errors: list[dict[str, object]],
) -> None:
    """Run the development workflow agent with direct AGENTS.md section ownership."""
    _ = programming_language_metadata
    development_workflow_agent = temporal_agents.development_workflow_guide
    if development_workflow_agent is None:
        logger.info(
            "[workflow] development_workflow_guide is disabled, skipping for {}",
            codebase_metadata.codebase_name,
        )
        agent_stats.append(create_zero_usage_statistics())
        return

    engineering_workflow_deps: AgentDependencies | None = None
    try:
        section_inspection = await workflow.execute_activity(
            EngineeringWorkflowFetchActivity.inspect_engineering_workflow_section,
            args=[codebase_metadata.codebase_path, None],
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=DB_ACTIVITY_RETRY_POLICY,
        )
        engineering_section_sha256 = section_inspection.section_sha256
        allow_no_change_output = engineering_section_sha256 is not None
        engineering_workflow_deps = AgentDependencies(
            repository_qualified_name=repository_qualified_name,
            codebase_metadata=codebase_metadata,
            repository_workflow_run_id=repository_workflow_run_id,
            codebase_workflow_run_id=codebase_workflow_run_id,
            agent_name="development_workflow_guide",
            engineering_section_sha256=engineering_section_sha256,
        )
        logger.info(
            "[workflow] Running development_workflow_guide for {}",
            codebase_metadata.codebase_name,
        )
        logger.debug("[workflow] Calling development_workflow_guide.run()...")
        workflow_result = await development_workflow_agent.run(
            build_development_workflow_prompt(
                codebase_path=codebase_metadata.codebase_path,
                programming_language=codebase_metadata.codebase_programming_language,
                package_manager=codebase_metadata.codebase_package_manager,
                allow_no_change_output=allow_no_change_output,
            ),
            deps=engineering_workflow_deps,
            usage_limits=get_cached_usage_limits(),
            metadata=build_agent_run_metadata(engineering_workflow_deps),
        )
        logger.debug("[workflow] development_workflow_guide.run() returned")

        development_workflow_stats = [extract_usage_statistics(workflow_result.usage)]
        agent_output = workflow_result.output
        if agent_output.status == ENGINEERING_WORKFLOW_FULL_OUTPUT:
            if not agent_output.commands:
                raise TypeError(
                    "development_workflow_guide returned full_output without commands"
                )
        elif agent_output.status == ENGINEERING_WORKFLOW_NO_CHANGE:
            if not allow_no_change_output:
                raise TypeError(
                    "development_workflow_guide returned no_change without a valid "
                    "existing Engineering Workflow section"
                )
            logger.info(
                "[workflow] development_workflow_guide kept the existing "
                "Engineering Workflow section for {}",
                codebase_metadata.codebase_name,
            )
        else:
            raise TypeError(
                "development_workflow_guide returned unsupported output status"
            )

        await workflow.execute_activity(
            EngineeringWorkflowCompletionActivity.emit_engineering_workflow_completion,
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
            "[workflow] development_workflow_guide completed for {}",
            codebase_metadata.codebase_name,
        )
        agent_stats.append(aggregate_usage_statistics(development_workflow_stats))

    except Exception as e:
        raise_if_temporal_cancellation(e)
        logger.error(
            "[workflow] development_workflow_guide failed for {}: {}",
            codebase_metadata.codebase_name,
            e,
        )
        logger.exception("[workflow] Full traceback:")
        engineering_error: dict[str, object] = {
            "agent": "development_workflow_guide",
            "codebase": codebase_metadata.codebase_name,
            "error": str(e),
            "traceback": traceback.format_exc(),
        }
        engineering_error = enrich_agent_error_with_model_details(
            engineering_error,
            e,
            "development_workflow_guide",
            codebase_metadata.codebase_name,
        )
        agent_errors.append(engineering_error)
        agent_stats.append(create_zero_usage_statistics())
    finally:
        if engineering_workflow_deps is not None:
            engineering_workflow_deps.release_backend()
