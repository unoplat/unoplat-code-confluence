from __future__ import annotations

import traceback

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from loguru import logger

    from unoplat_code_confluence_query_engine.models.output.agents_md_updater_output import (
        SectionId,
    )
    from unoplat_code_confluence_query_engine.models.repository.repository_ruleset_metadata import (
        CodebaseMetadata,
    )
    from unoplat_code_confluence_query_engine.models.runtime.agent_dependencies import (
        AgentDependencies,
    )
    from unoplat_code_confluence_query_engine.models.statistics.agent_usage_statistics import (
        UsageStatistics,
    )
    from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.agents.user_prompts.build_user_prompt_agents_md_updater import (
        SECTION_UPDATER_AGENT_NAMES,
        build_section_updater_prompt,
    )
    from unoplat_code_confluence_query_engine.services.temporal.statistics_helpers import (
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


async def run_section_updater(
    temporal_agents: TemporalAgentRegistry,
    section_id: SectionId,
    codebase_metadata: CodebaseMetadata,
    repository_qualified_name: str,
    repository_workflow_run_id: str,
    programming_language_metadata: dict[str, object],
    section_data: object,
    agent_stats: list[UsageStatistics],
    agent_errors: list[dict[str, object]],
    updater_runs: list[dict[str, object]],
) -> None:
    """Run agents_md_updater for a specific section after its guide completes."""
    updater_agent = temporal_agents.agents_md_updater
    if updater_agent is None:
        agent_stats.append(create_zero_usage_statistics())
        return

    updater_agent_name = SECTION_UPDATER_AGENT_NAMES[section_id]
    try:
        logger.info(
            "[workflow] Running {} for {}",
            updater_agent_name,
            codebase_metadata.codebase_name,
        )
        updater_deps = AgentDependencies(
            repository_qualified_name=repository_qualified_name,
            codebase_metadata=codebase_metadata,
            repository_workflow_run_id=repository_workflow_run_id,
            agent_name=updater_agent_name,
        )
        updater_prompt = build_section_updater_prompt(
            section_id=section_id,
            codebase_path=codebase_metadata.codebase_path,
            programming_language_metadata=programming_language_metadata,
            section_data=section_data,
        )
        updater_result = await updater_agent.run(
            updater_prompt,
            deps=updater_deps,
            usage_limits=get_cached_usage_limits(),
        )
        output_dict = updater_result.output.model_dump(mode="json")
        updater_runs.append(
            {
                "section_id": section_id.value,
                "agent_name": updater_agent_name,
                "output": output_dict,
            }
        )
        agent_stats.append(extract_usage_statistics(updater_result.usage()))
        logger.info(
            "[workflow] {} completed for {}",
            updater_agent_name,
            codebase_metadata.codebase_name,
        )
    except Exception as e:
        raise_if_temporal_cancellation(e)
        logger.error(
            "[workflow] {} failed for {}: {}",
            updater_agent_name,
            codebase_metadata.codebase_name,
            e,
        )
        logger.exception("[workflow] Full traceback:")
        error_entry: dict[str, object] = {
            "agent": updater_agent_name,
            "codebase": codebase_metadata.codebase_name,
            "error": str(e),
            "traceback": traceback.format_exc(),
        }
        error_entry = enrich_agent_error_with_model_details(
            error_entry,
            e,
            updater_agent_name,
            codebase_metadata.codebase_name,
        )
        agent_errors.append(error_entry)
        agent_stats.append(create_zero_usage_statistics())
