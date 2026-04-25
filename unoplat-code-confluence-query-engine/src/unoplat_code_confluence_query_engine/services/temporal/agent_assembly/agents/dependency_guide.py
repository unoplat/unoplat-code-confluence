from __future__ import annotations

from pydantic_ai import Agent, Tool
from pydantic_ai.capabilities import AbstractCapability
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
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.capabilities.readonly_console import (
    build_readonly_console_capability,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.constants import (
    DEPENDENCY_GUIDE_CONSOLE_TOOLSET_ID,
    DEPENDENCY_GUIDE_EXA_TOOLSET_ID,
    DEPENDENCY_GUIDE_LOCAL_WEB_FETCH_TOOLSET_ID,
    DEPENDENCY_GUIDE_LOCAL_WEB_SEARCH_TOOLSET_ID,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.runtime import (
    AgentAssemblyContext,
    AgentBuildResult,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.search import (
    resolve_search_capability,
    should_include_exa_toolsets,
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
    search_capability = resolve_search_capability(
        allow_builtin_web_search=True,
        allow_builtin_web_fetch=True,
        local_web_search_toolset_id=DEPENDENCY_GUIDE_LOCAL_WEB_SEARCH_TOOLSET_ID,
        local_web_fetch_toolset_id=DEPENDENCY_GUIDE_LOCAL_WEB_FETCH_TOOLSET_ID,
    )
    toolsets: list[AbstractToolset[AgentDependencies]] = []
    toolset_ids: list[str] = []

    console_capability = build_readonly_console_capability(DEPENDENCY_GUIDE_CONSOLE_TOOLSET_ID)
    console_toolset = console_capability.get_toolset()
    if (
        console_toolset is None
        or console_toolset.id != DEPENDENCY_GUIDE_CONSOLE_TOOLSET_ID
    ):
        raise ValueError(
            "Dependency guide console capability must expose a Temporal-safe toolset ID"
        )

    if should_include_exa_toolsets(context.search_policy):
        exa_toolset = build_dependency_guide_exa_toolset()
        if exa_toolset.id != DEPENDENCY_GUIDE_EXA_TOOLSET_ID:
            raise ValueError(
                "Dependency guide Exa toolset ID does not match the catalog constant"
            )
        toolsets.append(exa_toolset)
        toolset_ids.append(DEPENDENCY_GUIDE_EXA_TOOLSET_ID)

    capabilities: list[AbstractCapability[AgentDependencies]] = [console_capability]
    if search_capability is not None:
        capabilities.append(search_capability)

    agent: Agent[AgentDependencies, DependencyGuideEntry] = Agent(
        context.model,
        name="dependency_guide",
        instructions=build_dependency_guide_instructions(),
        deps_type=AgentDependencies,
        tools=tuple(function_tools),
        toolsets=tuple(toolsets),
        capabilities=capabilities,
        output_type=DependencyGuideEntry,
        output_retries=2,
        model_settings=context.model_settings,
        event_stream_handler=event_stream_handler,
    )

    return AgentBuildResult(
        agent=agent,
        function_tool_names=tuple(tool.name for tool in function_tools),
        toolset_ids=(
            DEPENDENCY_GUIDE_CONSOLE_TOOLSET_ID,
            DEPENDENCY_GUIDE_LOCAL_WEB_SEARCH_TOOLSET_ID,
            DEPENDENCY_GUIDE_LOCAL_WEB_FETCH_TOOLSET_ID,
            *toolset_ids,
        ),
    )
