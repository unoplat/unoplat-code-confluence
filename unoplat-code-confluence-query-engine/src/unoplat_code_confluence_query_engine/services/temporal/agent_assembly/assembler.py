from __future__ import annotations

from collections.abc import Callable
from typing import Any

from pydantic_ai.durable_exec.temporal import TemporalAgent
from pydantic_ai.models import Model
from pydantic_ai.settings import ModelSettings

from unoplat_code_confluence_query_engine.services.temporal.activity_retry_config import (
    TemporalAgentRetryConfig,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.activity_policies import (
    ResolvedTemporalActivityConfig,
    create_temporal_activity_defaults,
    resolve_temporal_activity_config,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.catalog import (
    AgentType,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.runtime import (
    AgentAssemblyContext,
    AgentBuildResult,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.search import (
    SearchRuntimePolicy,
    resolve_search_runtime_policy,
)


def create_assembly_context(
    model: Model,
    retry_config: TemporalAgentRetryConfig,
    model_settings: ModelSettings | None = None,
    provider_key: str | None = None,
    exa_configured: bool = False,
) -> AgentAssemblyContext:
    """Build the shared context used by Temporal agent assembly."""

    return AgentAssemblyContext(
        model=model,
        model_settings=model_settings,
        search_policy=build_search_runtime_policy(
            provider_key=provider_key,
            exa_configured=exa_configured,
        ),
        activity_defaults=create_temporal_activity_defaults(retry_config),
    )


def build_search_runtime_policy(
    *,
    provider_key: str | None,
    exa_configured: bool,
) -> SearchRuntimePolicy:
    """Resolve the shared runtime search policy for this assembly pass."""

    return resolve_search_runtime_policy(
        provider_key=provider_key,
        exa_configured=exa_configured,
    )


def resolve_temporal_activity_bundle(
    *,
    build_result: AgentBuildResult[Any],
    context: AgentAssemblyContext,
) -> ResolvedTemporalActivityConfig:
    """Resolve the Temporal activity config bundle for one built agent."""

    toolset_ids = (context.default_function_toolset_id, *build_result.toolset_ids)
    return resolve_temporal_activity_config(
        function_tool_names=build_result.function_tool_names,
        toolset_ids=toolset_ids,
        default_function_toolset_id=context.default_function_toolset_id,
        defaults=context.activity_defaults,
        toolset_overrides={},
        tool_overrides={},
    )


def build_temporal_agent(
    *,
    build_result: AgentBuildResult[Any],
    activity_config: ResolvedTemporalActivityConfig,
) -> TemporalAgent[Any, Any]:
    """Build one TemporalAgent from a concrete built agent and config."""

    return TemporalAgent(
        build_result.agent,
        activity_config=activity_config.activity_config,
        model_activity_config=activity_config.model_activity_config,
        toolset_activity_config=activity_config.toolset_activity_config,
        tool_activity_config=activity_config.tool_activity_config,
    )


def assemble_temporal_agent(
    builder: Callable[[AgentAssemblyContext], AgentBuildResult[Any]],
    context: AgentAssemblyContext,
) -> TemporalAgent[Any, Any]:
    """Build one concrete agent for durable execution."""

    build_result = builder(context)
    activity_config = resolve_temporal_activity_bundle(
        build_result=build_result,
        context=context,
    )
    return build_temporal_agent(
        build_result=build_result,
        activity_config=activity_config,
    )


def assemble_enabled_temporal_agents(
    agent_builders: dict[
        AgentType,
        Callable[[AgentAssemblyContext], AgentBuildResult[Any]],
    ],
    context: AgentAssemblyContext,
) -> dict[AgentType, TemporalAgent[Any, Any]]:
    """Build all enabled agents from the concrete builder mapping."""

    return {
        agent_type: assemble_temporal_agent(builder, context)
        for agent_type, builder in agent_builders.items()
    }
