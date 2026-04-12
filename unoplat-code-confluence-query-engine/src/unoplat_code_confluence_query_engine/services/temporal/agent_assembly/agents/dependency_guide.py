from __future__ import annotations

from pydantic_ai import Agent, Tool
from pydantic_ai.builtin_tools import AbstractBuiltinTool
from pydantic_ai.toolsets.abstract import AbstractToolset

from unoplat_code_confluence_query_engine.models.output.agent_md_output import (
    DependencyGuideEntry,
)
from unoplat_code_confluence_query_engine.models.runtime.agent_dependencies import (
    AgentDependencies,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.agents.user_prompts.build_user_prompt_dependency_guide import (
    build_dependency_guide_instructions,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.constants import (
    DEPENDENCY_GUIDE_EXA_TOOLSET_ID,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.runtime import (
    AgentAssemblyContext,
    AgentBuildResult,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.search import (
    resolve_builtin_search_tools,
    should_include_duckduckgo_search,
    should_include_exa_toolsets,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.tools.duckduckgo_search import (
    build_duckduckgo_search_tool,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.toolsets.dependency_guide import (
    build_dependency_guide_exa_toolset,
)
from unoplat_code_confluence_query_engine.services.temporal.event_stream_handler import (
    event_stream_handler,
)


def build_dependency_guide_agent(
    context: AgentAssemblyContext,
) -> AgentBuildResult[DependencyGuideEntry]:
    function_tools: list[Tool[AgentDependencies]] = []
    builtin_tools: tuple[AbstractBuiltinTool, ...] = resolve_builtin_search_tools(
        allow_builtin_web_search=True,
        runtime_policy=context.search_policy,
    )
    toolsets: list[AbstractToolset[AgentDependencies]] = []
    toolset_ids: list[str] = []

    if should_include_duckduckgo_search(context.search_policy):
        function_tools.append(build_duckduckgo_search_tool())

    if should_include_exa_toolsets(context.search_policy):
        exa_toolset = build_dependency_guide_exa_toolset()
        if exa_toolset.id != DEPENDENCY_GUIDE_EXA_TOOLSET_ID:
            raise ValueError(
                "Dependency guide Exa toolset ID does not match the catalog constant"
            )
        toolsets.append(exa_toolset)
        toolset_ids.append(DEPENDENCY_GUIDE_EXA_TOOLSET_ID)

    agent: Agent[AgentDependencies, DependencyGuideEntry] = Agent(
        context.model,
        name="dependency_guide",
        instructions=build_dependency_guide_instructions(),
        deps_type=AgentDependencies,
        tools=tuple(function_tools),
        builtin_tools=builtin_tools,
        toolsets=tuple(toolsets),
        output_type=DependencyGuideEntry,
        output_retries=2,
        model_settings=context.model_settings,
        event_stream_handler=event_stream_handler,
    )

    return AgentBuildResult(
        agent=agent,
        function_tool_names=tuple(tool.name for tool in function_tools),
        toolset_ids=tuple(toolset_ids),
    )
