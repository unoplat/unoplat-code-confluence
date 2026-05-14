from __future__ import annotations

from datetime import timedelta
import traceback

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from loguru import logger

    from unoplat_code_confluence_query_engine.models.output.engineering_workflow_output import (
        ENGINEERING_WORKFLOW_NO_CHANGE,
        EngineeringWorkflow,
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
    from unoplat_code_confluence_query_engine.services.temporal.workflows.runners.agent_snapshot_patch_runner import (
        persist_codebase_snapshot_patch,
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

    engineering_workflow_deps = AgentDependencies(
        repository_qualified_name=repository_qualified_name,
        codebase_metadata=codebase_metadata,
        repository_workflow_run_id=repository_workflow_run_id,
        codebase_workflow_run_id=codebase_workflow_run_id,
        agent_name="development_workflow_guide",
    )
    try:
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
            ),
            deps=engineering_workflow_deps,
            usage_limits=get_cached_usage_limits(),
            metadata=build_agent_run_metadata(engineering_workflow_deps),
        )
        logger.debug("[workflow] development_workflow_guide.run() returned")

        development_workflow_stats = [extract_usage_statistics(workflow_result.usage())]
        agent_output = workflow_result.output
        if isinstance(agent_output, EngineeringWorkflow):
            engineering_workflow_output = agent_output.model_dump()
        elif agent_output == ENGINEERING_WORKFLOW_NO_CHANGE:
            previous_engineering_workflow = await workflow.execute_activity(
                EngineeringWorkflowFetchActivity.fetch_previous_engineering_workflow,
                args=[
                    repository_qualified_name,
                    repository_workflow_run_id,
                    codebase_metadata.codebase_name,
                ],
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=DB_ACTIVITY_RETRY_POLICY,
            )
            if previous_engineering_workflow is None:
                logger.info(
                    "[workflow] development_workflow_guide reported no change for {}, "
                    "but the latest previous snapshot has no engineering_workflow "
                    "to carry forward; rerunning for full output",
                    codebase_metadata.codebase_name,
                )
                full_output_prompt = (
                    build_development_workflow_prompt(
                        codebase_path=codebase_metadata.codebase_path,
                        programming_language=codebase_metadata.codebase_programming_language,
                        package_manager=codebase_metadata.codebase_package_manager,
                    )
                    + " Previous structured engineering_workflow data is unavailable "
                    "in the latest completed snapshot. Do not return "
                    "NO_CHANGE_REQUIRED; re-validate the repository evidence and "
                    "return the full EngineeringWorkflow JSON model."
                )
                workflow_result = await development_workflow_agent.run(
                    full_output_prompt,
                    deps=engineering_workflow_deps,
                    usage_limits=get_cached_usage_limits(),
                    metadata=build_agent_run_metadata(engineering_workflow_deps),
                )
                development_workflow_stats.append(
                    extract_usage_statistics(workflow_result.usage())
                )
                agent_output = workflow_result.output
                if not isinstance(agent_output, EngineeringWorkflow):
                    raise TypeError(
                        "development_workflow_guide returned NO_CHANGE_REQUIRED "
                        "or an unsupported output after full-output rerun"
                    )
                engineering_workflow_output = agent_output.model_dump()
            else:
                engineering_workflow_output = previous_engineering_workflow
                logger.info(
                    "[workflow] development_workflow_guide reported no change for {}; "
                    "carried forward previous engineering_workflow",
                    codebase_metadata.codebase_name,
                )
        else:
            raise TypeError(
                "development_workflow_guide returned unsupported output type/value"
            )

        await persist_codebase_snapshot_patch(
            repository_qualified_name=repository_qualified_name,
            repository_workflow_run_id=repository_workflow_run_id,
            codebase_name=codebase_metadata.codebase_name,
            codebase_patch={"engineering_workflow": engineering_workflow_output},
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
        engineering_workflow_deps.release_backend()
