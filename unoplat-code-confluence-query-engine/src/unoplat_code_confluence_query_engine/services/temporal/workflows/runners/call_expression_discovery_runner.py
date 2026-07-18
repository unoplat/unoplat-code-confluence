from __future__ import annotations

import traceback

from pydantic_ai.durable_exec.temporal import TemporalAgent
from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from loguru import logger

    from unoplat_code_confluence_query_engine.models.repository.framework_feature_validation_models import (
        CallExpressionDiscoveryTarget,
        DiscoveredFrameworkFeatureUsagesUpsertResult,
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
    from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.agents.user_prompts.build_user_prompt_call_expression_discoverer import (
        build_call_expression_discoverer_prompt,
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

_DISCOVERY_LANGUAGES: frozenset[str] = frozenset({"python", "typescript"})


def is_call_expression_discovery_supported(programming_language: str) -> bool:
    """Return whether a language has repository-tracing instructions."""
    return programming_language.lower() in _DISCOVERY_LANGUAGES


async def run_call_expression_discovery(
    *,
    temporal_agents: TemporalAgentRegistry,
    codebase_metadata: CodebaseMetadata,
    repository_qualified_name: str,
    repository_workflow_run_id: str,
    codebase_workflow_run_id: str,
    targets: list[CallExpressionDiscoveryTarget],
    agent_stats: list[UsageStatistics],
    agent_errors: list[dict[str, object]],
) -> None:
    """Run exactly one isolated discoverer invocation per eligible operation."""
    if (
        not is_call_expression_discovery_supported(
            codebase_metadata.codebase_programming_language
        )
        or not targets
    ):
        return
    discoverer_agent: (
        TemporalAgent[AgentDependencies, DiscoveredFrameworkFeatureUsagesUpsertResult]
        | None
    ) = temporal_agents.call_expression_discoverer
    if discoverer_agent is None:
        agent_stats.append(create_zero_usage_statistics())
        return

    for capability in targets:
        for operation in capability.operations:
            deps = AgentDependencies(
                repository_qualified_name=repository_qualified_name,
                codebase_metadata=codebase_metadata,
                repository_workflow_run_id=repository_workflow_run_id,
                codebase_workflow_run_id=codebase_workflow_run_id,
                agent_name="call_expression_discoverer",
            )
            try:
                result = await discoverer_agent.run(
                    build_call_expression_discoverer_prompt(
                        codebase_metadata.codebase_path, capability, operation
                    ),
                    deps=deps,
                    usage_limits=get_cached_usage_limits(),
                    metadata=build_agent_run_metadata(deps),
                )
                agent_stats.append(extract_usage_statistics(result.usage))
            except Exception as error:
                raise_if_temporal_cancellation(error)
                logger.error(
                    "[workflow] call_expression_discoverer failed for {}:{}:{}:{}: {}",
                    capability.feature_language,
                    capability.feature_library,
                    capability.feature_capability_key,
                    operation.feature_operation_key,
                    error,
                )
                entry: dict[str, object] = {
                    "agent": "call_expression_discoverer",
                    "codebase": codebase_metadata.codebase_name,
                    "error": str(error),
                    "traceback": traceback.format_exc(),
                    "operation_identity": {
                        "feature_language": capability.feature_language,
                        "feature_library": capability.feature_library,
                        "feature_capability_key": capability.feature_capability_key,
                        "feature_operation_key": operation.feature_operation_key,
                    },
                }
                agent_errors.append(
                    enrich_agent_error_with_model_details(
                        entry,
                        error,
                        "call_expression_discoverer",
                        codebase_metadata.codebase_name,
                    )
                )
                agent_stats.append(create_zero_usage_statistics())
