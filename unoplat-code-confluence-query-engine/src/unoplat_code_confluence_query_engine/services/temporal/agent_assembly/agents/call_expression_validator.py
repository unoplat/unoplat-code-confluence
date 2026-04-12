from __future__ import annotations

from pydantic_ai import Agent, Tool
from pydantic_ai.builtin_tools import AbstractBuiltinTool
from pydantic_ai.toolsets.abstract import AbstractToolset

from unoplat_code_confluence_query_engine.models.repository.framework_feature_validation_models import (
    CallExpressionValidationAgentOutput,
)
from unoplat_code_confluence_query_engine.models.runtime.agent_dependencies import (
    AgentDependencies,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.agents.user_prompts.build_user_prompt_call_expression_validator import (
    build_call_expression_validator_instructions,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.constants import (
    CALL_EXPRESSION_VALIDATOR_EXA_TOOLSET_ID,
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
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.tools.read_file_content import (
    build_read_file_content_tool,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.tools.search_across_codebase import (
    build_search_across_codebase_tool,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.tools.set_framework_feature_validation_status import (
    build_set_framework_feature_validation_status_tool,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.tools.upsert_framework_feature_validation_evidence import (
    build_upsert_framework_feature_validation_evidence_tool,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.toolsets.call_expression_validator import (
    build_call_expression_validator_exa_toolset,
)
from unoplat_code_confluence_query_engine.services.temporal.event_stream_handler import (
    event_stream_handler,
)


def build_call_expression_validator_agent(
    context: AgentAssemblyContext,
) -> AgentBuildResult[CallExpressionValidationAgentOutput]:
    function_tools: list[Tool[AgentDependencies]] = [
        build_read_file_content_tool(),
        build_search_across_codebase_tool(),
        build_upsert_framework_feature_validation_evidence_tool(),
        build_set_framework_feature_validation_status_tool(),
    ]
    builtin_tools: tuple[AbstractBuiltinTool, ...] = resolve_builtin_search_tools(
        allow_builtin_web_search=True,
        runtime_policy=context.search_policy,
    )
    toolsets: list[AbstractToolset[AgentDependencies]] = []
    toolset_ids: list[str] = []

    if should_include_duckduckgo_search(context.search_policy):
        function_tools.append(build_duckduckgo_search_tool())

    if should_include_exa_toolsets(context.search_policy):
        exa_toolset = build_call_expression_validator_exa_toolset()
        if exa_toolset.id != CALL_EXPRESSION_VALIDATOR_EXA_TOOLSET_ID:
            raise ValueError(
                "Call expression validator Exa toolset ID does not match the catalog constant"
            )
        toolsets.append(exa_toolset)
        toolset_ids.append(CALL_EXPRESSION_VALIDATOR_EXA_TOOLSET_ID)

    agent = Agent(
        context.model,
        name="call_expression_validator",
        instructions=build_call_expression_validator_instructions(),
        deps_type=AgentDependencies,
        tools=tuple(function_tools),
        builtin_tools=builtin_tools,
        toolsets=tuple(toolsets),
        output_type=CallExpressionValidationAgentOutput,
        output_retries=2,
        model_settings=context.model_settings,
        event_stream_handler=event_stream_handler,
    )

    return AgentBuildResult(
        agent=agent,
        function_tool_names=tuple(tool.name for tool in function_tools),
        toolset_ids=tuple(toolset_ids),
    )
