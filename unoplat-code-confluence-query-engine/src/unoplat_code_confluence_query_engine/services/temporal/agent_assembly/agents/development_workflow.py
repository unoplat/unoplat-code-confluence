from __future__ import annotations

from pydantic_ai import Agent
from pydantic_ai.capabilities import AbstractCapability
from pydantic_ai.toolsets.abstract import AbstractToolset

from unoplat_code_confluence_query_engine.models.output.engineering_workflow_output import (
    EngineeringWorkflow,
    EngineeringWorkflowAgentOutput,
)
from unoplat_code_confluence_query_engine.models.runtime.agent_dependencies import (
    AgentDependencies,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.agents.user_prompts.build_user_prompt_development_workflow import (
    build_development_workflow_instructions,
    build_per_language_development_workflow_instructions,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.agents.validators.development_workflow_validator import (
    validate_engineering_development_workflow_output,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.capabilities.readonly_console import (
    build_markdown_execute_console_capability,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.constants import (
    DEVELOPMENT_WORKFLOW_CONSOLE_TOOLSET_ID,
    DEVELOPMENT_WORKFLOW_EXA_TOOLSET_ID,
    DEVELOPMENT_WORKFLOW_LOCAL_WEB_FETCH_TOOLSET_ID,
    DEVELOPMENT_WORKFLOW_LOCAL_WEB_SEARCH_TOOLSET_ID,
    TS_MONOREPO_DYNAMIC_TOOLSET_ID,
    TS_MONOREPO_TOOLSET_ID,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.runtime import (
    AgentAssemblyContext,
    AgentBuildResult,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.search import (
    resolve_search_capability,
    should_include_exa_toolsets,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.toolsets.development_workflow import (
    build_development_workflow_exa_toolset,
    maybe_get_typescript_monorepo_instructions,
    maybe_get_typescript_monorepo_toolset,
)
from unoplat_code_confluence_query_engine.services.temporal.event_stream_handler import (
    event_stream_handler,
)


def configure_engineering_workflow_agent(
    agent: Agent[AgentDependencies, EngineeringWorkflowAgentOutput],
    context: AgentAssemblyContext,
) -> None:
    _ = context
    agent.output_validator(validate_engineering_development_workflow_output)
    agent.instructions(build_per_language_development_workflow_instructions())
    toolset_registrar = agent.toolset(
        id=TS_MONOREPO_DYNAMIC_TOOLSET_ID,
        per_run_step=False,
    )
    toolset_registrar(maybe_get_typescript_monorepo_toolset)
    agent.instructions(maybe_get_typescript_monorepo_instructions)


def build_development_workflow_agent(
    context: AgentAssemblyContext,
) -> AgentBuildResult[EngineeringWorkflowAgentOutput]:
    console_capability = build_markdown_execute_console_capability(
        DEVELOPMENT_WORKFLOW_CONSOLE_TOOLSET_ID
    )
    console_toolset = console_capability.get_toolset()
    if (
        console_toolset is None
        or console_toolset.id != DEVELOPMENT_WORKFLOW_CONSOLE_TOOLSET_ID
    ):
        raise ValueError(
            "Development workflow console capability must expose a Temporal-safe toolset ID"
        )

    search_capability = resolve_search_capability(
        allow_builtin_web_search=True,
        allow_builtin_web_fetch=True,
        local_web_search_toolset_id=DEVELOPMENT_WORKFLOW_LOCAL_WEB_SEARCH_TOOLSET_ID,
        local_web_fetch_toolset_id=DEVELOPMENT_WORKFLOW_LOCAL_WEB_FETCH_TOOLSET_ID,
    )
    capabilities: list[AbstractCapability[AgentDependencies]] = [console_capability]
    if search_capability is not None:
        capabilities.append(search_capability)
    toolsets: list[AbstractToolset[AgentDependencies]] = []
    toolset_ids: list[str] = []

    if should_include_exa_toolsets(context.search_policy):
        exa_toolset = build_development_workflow_exa_toolset()
        if exa_toolset.id != DEVELOPMENT_WORKFLOW_EXA_TOOLSET_ID:
            raise ValueError(
                "Development workflow Exa toolset ID does not match the catalog constant"
            )
        toolsets.append(exa_toolset)
        toolset_ids.append(DEVELOPMENT_WORKFLOW_EXA_TOOLSET_ID)

    agent = Agent(
        context.model,
        name="development_workflow_guide",
        instructions=build_development_workflow_instructions(),
        deps_type=AgentDependencies,
        toolsets=tuple(toolsets),
        capabilities=capabilities,
        output_type=[EngineeringWorkflow, str],
        output_retries=2,
        model_settings=context.model_settings,
        event_stream_handler=event_stream_handler,
    )
    configure_engineering_workflow_agent(agent, context)

    return AgentBuildResult(
        agent=agent,
        function_tool_names=(),
        toolset_ids=(
            DEVELOPMENT_WORKFLOW_CONSOLE_TOOLSET_ID,
            DEVELOPMENT_WORKFLOW_LOCAL_WEB_SEARCH_TOOLSET_ID,
            DEVELOPMENT_WORKFLOW_LOCAL_WEB_FETCH_TOOLSET_ID,
            *toolset_ids,
            TS_MONOREPO_DYNAMIC_TOOLSET_ID,
            TS_MONOREPO_TOOLSET_ID,
        ),
    )
