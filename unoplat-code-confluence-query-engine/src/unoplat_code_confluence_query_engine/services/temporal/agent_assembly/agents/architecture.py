"""Pydantic AI agent assembly for the repository architecture artifact."""

from __future__ import annotations

from collections.abc import AsyncIterable

from pydantic_ai import Agent, AgentStreamEvent, RunContext, Tool
from pydantic_ai.capabilities import AbstractCapability, ProcessHistory
from pydantic_ai.messages import ToolCallPart
from pydantic_ai.toolsets.abstract import AbstractToolset
from pydantic_ai_harness.compaction import (
    ClearToolResults,
    DeduplicateFileReads,
    SummarizingCompaction,
    TieredCompaction,
)

from unoplat_code_confluence_query_engine.models.runtime.architecture_agent_dependencies import (
    ArchitectureAgentDependencies,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.agents.user_prompts.build_user_prompt_architecture import (
    build_architecture_instructions,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.capabilities.history_compaction import (
    compact_temporal_agent_history,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.capabilities.readonly_console import (
    build_architecture_console_capability,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.constants import (
    ARCHITECTURE_CONSOLE_TOOLSET_ID,
    ARCHITECTURE_SKILL_TOOLSET_ID,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.runtime import (
    AgentAssemblyContext,
    AgentBuildResult,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.tools.validate_architecture import (
    build_validate_architecture_tool,
)
from unoplat_code_confluence_query_engine.skills.architecture_diagrams_skill import (
    create_architecture_diagrams_toolset,
)

ARCHITECTURE_COMPACTION_TARGET_TOKENS = 80_000
ARCHITECTURE_COMPACTION_KEEP_PAIRS = 3
ARCHITECTURE_COMPACTION_KEEP_MESSAGES = 20


def architecture_read_file_key(call: ToolCallPart) -> str | None:
    """Map console read_file tool calls to a stable path key for dedupe."""
    if call.tool_name != "read_file":
        return None
    path = call.args_as_dict().get("path")
    return path if isinstance(path, str) else None


async def architecture_event_stream_handler(
    _ctx: RunContext[ArchitectureAgentDependencies],
    _event_stream: AsyncIterable[AgentStreamEvent],
) -> None:
    """Enable required model streaming without codebase-scoped event persistence.

    The Temporal model consumes the stream after this handler returns. Repository
    Architecture progress is tracked as a repository activity rather than through
    codebase event records.
    """


def build_architecture_agent(
    context: AgentAssemblyContext,
) -> AgentBuildResult[ArchitectureAgentDependencies, str]:
    """Build the Architecture agent with scoped authoring and validation tools."""
    function_tools: list[Tool[ArchitectureAgentDependencies]] = [
        build_validate_architecture_tool(),
    ]
    console_capability = build_architecture_console_capability(
        ARCHITECTURE_CONSOLE_TOOLSET_ID
    )
    console_toolset = console_capability.get_toolset()
    if console_toolset is None or console_toolset.id != ARCHITECTURE_CONSOLE_TOOLSET_ID:
        raise ValueError(
            "Architecture console capability must expose a Temporal-safe toolset ID"
        )

    architecture_skill_toolset = create_architecture_diagrams_toolset(
        ARCHITECTURE_SKILL_TOOLSET_ID
    )
    if architecture_skill_toolset.id != ARCHITECTURE_SKILL_TOOLSET_ID:
        raise ValueError(
            "Architecture skill toolset ID does not match the catalog constant"
        )

    capabilities: list[AbstractCapability[ArchitectureAgentDependencies]] = [
        console_capability,
        ProcessHistory(compact_temporal_agent_history),
        TieredCompaction(
            tiers=[
                DeduplicateFileReads(file_key=architecture_read_file_key),
                ClearToolResults(
                    max_tokens=1,
                    keep_pairs=ARCHITECTURE_COMPACTION_KEEP_PAIRS,
                ),
                SummarizingCompaction(
                    model=None,
                    max_messages=1,
                    keep_messages=ARCHITECTURE_COMPACTION_KEEP_MESSAGES,
                    incremental=True,
                    preserve_first_user_message=True,
                ),
            ],
            target_tokens=ARCHITECTURE_COMPACTION_TARGET_TOKENS,
        ),
    ]
    toolsets: list[AbstractToolset[ArchitectureAgentDependencies]] = [
        architecture_skill_toolset
    ]
    agent: Agent[ArchitectureAgentDependencies, str] = Agent(
        context.model,
        name="architecture",
        instructions=build_architecture_instructions(),
        deps_type=ArchitectureAgentDependencies,
        tools=tuple(function_tools),
        toolsets=tuple(toolsets),
        capabilities=capabilities,
        output_type=str,
        retries={"output": 3},
        end_strategy="early",
        model_settings=context.model_settings,
    )

    return AgentBuildResult(
        agent=agent,
        function_tool_names=tuple(tool.name for tool in function_tools),
        event_stream_handler=architecture_event_stream_handler,
        toolset_ids=(
            ARCHITECTURE_CONSOLE_TOOLSET_ID,
            ARCHITECTURE_SKILL_TOOLSET_ID,
        ),
    )
