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
    from unoplat_code_confluence_query_engine.models.statistics.agent_usage_statistics import (
        UsageStatistics,
    )
    from unoplat_code_confluence_query_engine.services.temporal.activities.codebase_workflow_run.business_logic_post_process_activity import (
        BusinessLogicPostProcessActivity,
    )
    from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.agents.user_prompts.build_user_prompt_business_domain import (
        build_business_domain_prompt,
    )
    from unoplat_code_confluence_query_engine.services.temporal.interceptors.agent_workflow_interceptor import (
        DB_ACTIVITY_RETRY_POLICY,
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


async def run_business_domain_agent(
    temporal_agents: TemporalAgentRegistry,
    repository_qualified_name: str,
    codebase_metadata: CodebaseMetadata,
    repository_workflow_run_id: str,
    programming_language_metadata: dict[str, object],
    results: dict[str, Any],
    agent_stats: list[UsageStatistics],
    agent_errors: list[dict[str, object]],
) -> None:
    """Run the business-domain agent and deterministic reference post-processing."""
    _ = programming_language_metadata
    business_domain_agent = temporal_agents.business_domain_guide
    if business_domain_agent is None:
        logger.info(
            "[workflow] business_domain_guide is disabled, skipping for {}",
            codebase_metadata.codebase_name,
        )
        agent_stats.append(create_zero_usage_statistics())
        return

    try:
        logger.info(
            "[workflow] Running business_domain_guide for {}",
            codebase_metadata.codebase_name,
        )
        business_logic_deps = AgentDependencies(
            repository_qualified_name=repository_qualified_name,
            codebase_metadata=codebase_metadata,
            repository_workflow_run_id=repository_workflow_run_id,
            agent_name="business_domain_guide",
        )
        logger.debug("[workflow] Calling business_domain_guide.run()...")
        domain_result = await business_domain_agent.run(
            build_business_domain_prompt(codebase_metadata.codebase_path),
            deps=business_logic_deps,
            usage_limits=get_cached_usage_limits(),
        )
        logger.debug("[workflow] business_domain_guide.run() returned")
        
        # Append stats before fallible activity to preserve real usage data
        agent_stats.append(extract_usage_statistics(domain_result.usage()))
        
        business_logic_result = await workflow.execute_activity(
            BusinessLogicPostProcessActivity.post_process_business_logic,
            args=[
                domain_result.output,
                codebase_metadata.codebase_path,
                codebase_metadata.codebase_programming_language,
            ],
            start_to_close_timeout=timedelta(minutes=1),
            retry_policy=DB_ACTIVITY_RETRY_POLICY,
        )
        results["business_logic_domain"] = business_logic_result
        logger.info(
            "[workflow] business_domain_guide completed for {}",
            codebase_metadata.codebase_name,
        )

        logger.debug(
            "[workflow] business_domain_guide directly owns AGENTS.md / ## Business Domain / ### Description; "
            "business_domain_references.md was rendered during post-processing"
        )
    except Exception as e:
        raise_if_temporal_cancellation(e)
        logger.error(
            "[workflow] business_domain_guide failed for {}: {}",
            codebase_metadata.codebase_name,
            e,
        )
        logger.exception("[workflow] Full traceback:")
        business_logic_error: dict[str, object] = {
            "agent": "business_domain_guide",
            "codebase": codebase_metadata.codebase_name,
            "error": str(e),
            "traceback": traceback.format_exc(),
        }
        business_logic_error = enrich_agent_error_with_model_details(
            business_logic_error,
            e,
            "business_domain_guide",
            codebase_metadata.codebase_name,
        )
        agent_errors.append(business_logic_error)
        agent_stats.append(create_zero_usage_statistics())
