from __future__ import annotations

from pydantic_ai import Agent, Tool

from unoplat_code_confluence_query_engine.models.runtime.agent_dependencies import (
    AgentDependencies,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.agents.user_prompts.build_user_prompt_business_domain import (
    build_business_domain_instructions,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.agents.validators.business_domain_validator import (
    validate_business_logic_domain_output,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.capabilities.readonly_console import (
    build_markdown_console_capability,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.constants import (
    BUSINESS_DOMAIN_CONSOLE_TOOLSET_ID,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.runtime import (
    AgentAssemblyContext,
    AgentBuildResult,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.tools.get_data_model_files import (
    build_get_data_model_files_tool,
)
from unoplat_code_confluence_query_engine.services.temporal.event_stream_handler import (
    event_stream_handler,
)


def configure_business_domain_agent(
    agent: Agent[AgentDependencies, str],
    context: AgentAssemblyContext,
) -> None:
    _ = context
    agent.output_validator(validate_business_logic_domain_output)


def build_business_domain_agent(
    context: AgentAssemblyContext,
) -> AgentBuildResult[str]:
    function_tools: list[Tool[AgentDependencies]] = [
        build_get_data_model_files_tool(),
    ]
    console_capability = build_markdown_console_capability(
        BUSINESS_DOMAIN_CONSOLE_TOOLSET_ID
    )

    agent: Agent[AgentDependencies, str] = Agent(
        context.model,
        name="business_domain_guide",
        instructions=build_business_domain_instructions(),
        deps_type=AgentDependencies,
        tools=tuple(function_tools),
        capabilities=[console_capability],
        output_type=str,
        output_retries=3,
        model_settings=context.model_settings,
        event_stream_handler=event_stream_handler,
    )
    configure_business_domain_agent(agent, context)

    return AgentBuildResult(
        agent=agent,
        function_tool_names=tuple(tool.name for tool in function_tools),
        toolset_ids=(BUSINESS_DOMAIN_CONSOLE_TOOLSET_ID,),
    )
