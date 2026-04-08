from __future__ import annotations

from pydantic_ai import Agent, Tool
from pydantic_ai.builtin_tools import AbstractBuiltinTool

from unoplat_code_confluence_query_engine.models.output.agents_md_updater_output import (
    AgentsMdUpdaterOutput,
)
from unoplat_code_confluence_query_engine.models.runtime.agent_dependencies import (
    AgentDependencies,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.agents.user_prompts.build_user_prompt_agents_md_updater import (
    build_agents_md_updater_instructions,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.agents.validators.agents_md_updater_validator import (
    validate_agents_md_updater_output,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.runtime import (
    AgentAssemblyContext,
    AgentBuildResult,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.search import (
    resolve_builtin_search_tools,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.tools.updater_apply_patch import (
    build_updater_apply_patch_tool,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.tools.updater_edit_file import (
    build_updater_edit_file_tool,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.tools.updater_read_file import (
    build_updater_read_file_tool,
)
from unoplat_code_confluence_query_engine.services.temporal.event_stream_handler import (
    event_stream_handler,
)


def configure_agents_md_updater_agent(
    agent: Agent[AgentDependencies, AgentsMdUpdaterOutput],
    context: AgentAssemblyContext,
) -> None:
    _ = context
    agent.output_validator(validate_agents_md_updater_output)


def build_agents_md_updater_agent(
    context: AgentAssemblyContext,
) -> AgentBuildResult[AgentsMdUpdaterOutput]:
    function_tools: list[Tool[AgentDependencies]] = [
        build_updater_read_file_tool(),
        build_updater_edit_file_tool(),
        build_updater_apply_patch_tool(),
    ]
    builtin_tools: tuple[AbstractBuiltinTool, ...] = resolve_builtin_search_tools(
        allow_builtin_web_search=False,
        runtime_policy=context.search_policy,
    )

    agent = Agent(
        context.model,
        name="agents_md_updater",
        instructions=build_agents_md_updater_instructions(),
        deps_type=AgentDependencies,
        tools=tuple(function_tools),
        builtin_tools=builtin_tools,
        output_type=AgentsMdUpdaterOutput,
        output_retries=2,
        model_settings=context.model_settings,
        event_stream_handler=event_stream_handler,
    )
    configure_agents_md_updater_agent(agent, context)

    return AgentBuildResult(
        agent=agent,
        function_tool_names=tuple(tool.name for tool in function_tools),
    )
