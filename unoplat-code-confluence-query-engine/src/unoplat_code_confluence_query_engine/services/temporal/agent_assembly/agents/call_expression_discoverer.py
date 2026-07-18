from __future__ import annotations

from pydantic_ai import Agent, Tool

from unoplat_code_confluence_query_engine.models.repository.framework_feature_validation_models import (
    DiscoveredFrameworkFeatureUsagesUpsertResult,
)
from unoplat_code_confluence_query_engine.models.runtime.agent_dependencies import (
    AgentDependencies,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.agents.user_prompts.build_user_prompt_call_expression_discoverer import (
    build_call_expression_discoverer_instructions,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.capabilities.readonly_console import (
    build_readonly_console_capability,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.constants import (
    CALL_EXPRESSION_DISCOVERER_CONSOLE_TOOLSET_ID,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.runtime import (
    AgentAssemblyContext,
    AgentBuildResult,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.tools.upsert_discovered_framework_feature_usages import (
    build_upsert_discovered_framework_feature_usages_tool,
)
from unoplat_code_confluence_query_engine.services.temporal.event_stream_handler import (
    event_stream_handler,
)


def build_call_expression_discoverer_agent(
    context: AgentAssemblyContext,
) -> AgentBuildResult[DiscoveredFrameworkFeatureUsagesUpsertResult]:
    """Build the readonly, discovery-only call-expression agent."""
    function_tools: list[Tool[AgentDependencies]] = [
        build_upsert_discovered_framework_feature_usages_tool()
    ]
    console_capability = build_readonly_console_capability(
        CALL_EXPRESSION_DISCOVERER_CONSOLE_TOOLSET_ID
    )
    console_toolset = console_capability.get_toolset()
    if (
        console_toolset is None
        or console_toolset.id != CALL_EXPRESSION_DISCOVERER_CONSOLE_TOOLSET_ID
    ):
        raise ValueError(
            "Call expression discoverer console capability must expose a "
            "Temporal-safe toolset ID"
        )

    agent = Agent(
        context.model,
        name="call_expression_discoverer",
        instructions=build_call_expression_discoverer_instructions(),
        deps_type=AgentDependencies,
        tools=tuple(function_tools),
        capabilities=[console_capability],
        output_type=DiscoveredFrameworkFeatureUsagesUpsertResult,
        retries={"output": 2},
        end_strategy="early",
        model_settings=context.model_settings,
    )
    return AgentBuildResult(
        agent=agent,
        function_tool_names=tuple(tool.name for tool in function_tools),
        event_stream_handler=event_stream_handler,
        toolset_ids=(CALL_EXPRESSION_DISCOVERER_CONSOLE_TOOLSET_ID,),
    )
