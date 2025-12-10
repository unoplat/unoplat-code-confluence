"""Temporal durable agents with dynamic model configuration.

This module defines all agents wrapped with TemporalAgent for durable execution.
Uses ModelFactory to build models dynamically from database configuration.
"""

from collections.abc import AsyncIterable
from datetime import timedelta
from enum import Enum
from typing import Any

from loguru import logger
from pydantic_ai import Agent, AgentStreamEvent, RunContext, Tool
from pydantic_ai.durable_exec.temporal import TemporalAgent
from pydantic_ai.mcp import MCPServerSSE, MCPServerStdio
from pydantic_ai.messages import (
    FinalResultEvent,
    FunctionToolCallEvent,
    FunctionToolResultEvent,
)
from pydantic_ai.models import Model
from pydantic_ai.settings import ModelSettings
from temporalio.workflow import ActivityConfig

from unoplat_code_confluence_query_engine.agents.code_confluence_agents import (
    per_language_development_workflow_prompt,
    per_programming_language_configuration_prompt,
)
from unoplat_code_confluence_query_engine.models.output.agent_md_output import (
    DevelopmentWorkflow,
    ProjectConfiguration,
)
from unoplat_code_confluence_query_engine.models.runtime.agent_dependencies import (
    AgentDependencies,
)
from unoplat_code_confluence_query_engine.tools.get_content_file import (
    read_file_content,
)
from unoplat_code_confluence_query_engine.tools.get_data_model_files import (
    get_data_model_files,
)
from unoplat_code_confluence_query_engine.tools.get_directory_tree import (
    get_directory_tree,
)
from unoplat_code_confluence_query_engine.tools.get_lib_data import get_lib_data
from unoplat_code_confluence_query_engine.tools.search_across_codebase import (
    search_across_codebase,
)


class AgentType(Enum):
    """Enum for available agent types."""

    PROJECT_CONFIGURATION = "project_configuration_agent"
    DEVELOPMENT_WORKFLOW = "development_workflow_agent"
    BUSINESS_LOGIC_DOMAIN = "business_logic_domain_agent"


# Toggle agents here - comment/uncomment to enable/disable
ENABLED_AGENTS: set[AgentType] = {
    AgentType.PROJECT_CONFIGURATION,
    AgentType.DEVELOPMENT_WORKFLOW,
    AgentType.BUSINESS_LOGIC_DOMAIN,
}


# ──────────────────────────────────────────────
# Event Stream Handler
# ──────────────────────────────────────────────

# Agent names that contribute to progress calculation
COMPLETION_NAMESPACES: frozenset[str] = frozenset(
    {
        "project_configuration_agent",
        "development_workflow_agent",
        "business_logic_domain_agent",
    }
)


def _map_event_to_phase(event: AgentStreamEvent) -> str | None:
    """Map PydanticAI stream event to DB phase string.

    Args:
        event: The stream event to map

    Returns:
        Phase string or None if event should be skipped
    """
    if isinstance(event, FunctionToolCallEvent):
        return "tool.call"
    if isinstance(event, FunctionToolResultEvent):
        return "tool.result"
    if isinstance(event, FinalResultEvent):
        return "result"
    return None


def _extract_event_message(event: AgentStreamEvent) -> str | None:
    """Extract human-readable message from stream event.

    Args:
        event: The stream event

    Returns:
        Message string or None
    """
    if isinstance(event, FunctionToolCallEvent):
        return f"Calling {event.part.tool_name}"
    if isinstance(event, FunctionToolResultEvent):
        preview = str(event.result.content)[:100]
        return f"Tool result: {preview}"
    if isinstance(event, FinalResultEvent):
        return (
            f"Final result via {event.tool_name}" if event.tool_name else "Final result"
        )
    return None


async def event_stream_handler(
    ctx: RunContext[AgentDependencies],
    event_stream: AsyncIterable[AgentStreamEvent],
) -> None:
    """Handle streaming events with DB-first stateless tracking.

    This handler runs in the Temporal activity process.
    Persists events to PostgreSQL via atomic CTEs for progress tracking.
    Falls back to logging-only if deps are not properly configured.
    """
    # Import here to avoid circular imports
    from unoplat_code_confluence_query_engine.services.temporal.service_registry import (  # noqa: PLC0415
        get_snapshot_writer,
    )

    deps = ctx.deps
    codebase = deps.codebase_metadata.codebase_name if deps else "unknown"

    # Check if DB tracking is configured
    db_tracking_enabled = bool(
        deps
        and deps.repository_workflow_run_id
        and deps.agent_name
        and deps.repository_qualified_name
    )

    # Parse owner/repo for DB persistence
    owner_name: str | None = None
    repo_name: str | None = None
    if db_tracking_enabled and deps:
        qualified = deps.repository_qualified_name
        if "/" in qualified:
            parts = qualified.split("/", 1)
            owner_name = parts[0]
            repo_name = parts[1]
        else:
            logger.warning(
                "[{}] Invalid repository_qualified_name format: {}",
                codebase,
                qualified,
            )
            db_tracking_enabled = False

    async for event in event_stream:
        phase = _map_event_to_phase(event)
        if phase is None:
            continue

        message = _extract_event_message(event)

        # Always log for observability
        if isinstance(event, FunctionToolCallEvent):
            logger.info(
                f"[{codebase}] TOOL CALL: name={event.part.tool_name}, args={event.part.args}, id={event.part.tool_call_id}"
            )
        elif isinstance(event, FunctionToolResultEvent):
            result_preview = str(event.result.content)[:200]
            logger.info(
                "[{}] TOOL RESULT: id={}, result_preview={}",
                codebase,
                event.tool_call_id,
                result_preview,
            )
        elif isinstance(event, FinalResultEvent):
            logger.info(f"[{codebase}] FINAL RESULT: tool_name={event.tool_name}")

        # Persist to DB if tracking is enabled
        if db_tracking_enabled and deps and owner_name and repo_name:
            try:
                writer = get_snapshot_writer()
                await writer.append_event_atomic(
                    owner_name=owner_name,
                    repo_name=repo_name,
                    codebase_name=codebase,
                    agent_name=deps.agent_name,
                    phase=phase,
                    message=message,
                    completion_namespaces=set(COMPLETION_NAMESPACES),
                    repository_workflow_run_id=deps.repository_workflow_run_id,
                )
            except Exception as e:
                # Log but don't crash - event tracking is non-critical
                logger.error(
                    "[{}] Failed to persist event to DB: {} - {}",
                    codebase,
                    type(e).__name__,
                    str(e),
                )


# ──────────────────────────────────────────────
# Agent Definitions
# ──────────────────────────────────────────────


def create_project_configuration_agent(
    model: Model,
    model_settings: ModelSettings | None = None,
) -> Agent[AgentDependencies, ProjectConfiguration]:
    """Create project configuration agent.

    Args:
        model: Configured Model instance from ModelFactory
        model_settings: Optional model settings (temperature, etc.)

    Returns:
        Project configuration agent instance
    """
    agent = Agent(
        model,
        name="project_configuration_agent",
        system_prompt="<role> Build/CI/Test/Lint/Type Configuration Locator</role>",
        deps_type=AgentDependencies,
        tools=[
            Tool(get_directory_tree, takes_ctx=True, max_retries=5),
            Tool(read_file_content, takes_ctx=True, max_retries=5),
            Tool(search_across_codebase, takes_ctx=True, max_retries=5),
            Tool(get_lib_data, takes_ctx=True, max_retries=5),
        ],
        output_type=ProjectConfiguration,
        retries=6,
        model_settings=model_settings,
        event_stream_handler=event_stream_handler,
    )
    # Attach dynamic per-language system prompt (always enabled)
    agent.system_prompt(per_programming_language_configuration_prompt)
    logger.debug("Dynamic system prompt attached to project_configuration_agent")
    return agent


def create_development_workflow_agent(
    model: Model,
    model_settings: ModelSettings | None = None,
) -> Agent[AgentDependencies, DevelopmentWorkflow]:
    """Create development workflow agent.

    Args:
        model: Configured Model instance from ModelFactory
        model_settings: Optional model settings (temperature, etc.)

    Returns:
        Development workflow agent instance
    """
    agent = Agent(
        model,
        name="development_workflow_agent",
        system_prompt="<role> Development Workflow Synthesizer</role>",
        deps_type=AgentDependencies,
        tools=[
            Tool(get_directory_tree, takes_ctx=True, max_retries=5),
            Tool(read_file_content, takes_ctx=True, max_retries=5),
            Tool(get_lib_data, takes_ctx=True, max_retries=5),
        ],
        output_type=DevelopmentWorkflow,
        retries=6,
        model_settings=model_settings,
        event_stream_handler=event_stream_handler,
    )
    # Attach dynamic per-language system prompt (always enabled)
    agent.system_prompt(per_language_development_workflow_prompt)
    logger.debug("Dynamic system prompt attached to development_workflow_agent")
    return agent


def create_business_logic_domain_agent(
    model: Model,
    model_settings: ModelSettings | None = None,
) -> Agent[AgentDependencies, str]:
    """Create business logic domain agent.

    Args:
        model: Configured Model instance from ModelFactory
        model_settings: Optional model settings (temperature, etc.)

    Returns:
        Business logic domain agent instance
    """
    return Agent(
        model,
        name="business_logic_domain_agent",
        system_prompt=r"""You are the Business Logic Domain Agent.

Goal: Analyze data models across this codebase and return a 2-4 sentence description of the dominant business logic domain.

<file_path_requirements>
CRITICAL: When calling read_file_content or any tool that accepts file paths:
- ALWAYS use ABSOLUTE paths starting with / (e.g., /opt/unoplat/repositories/my-repo/src/models.py)
- NEVER use relative paths (e.g., models.py, src/models.py, ./file.py)
- The file_path values returned by get_data_model_files are already absolute - use them exactly as provided
</file_path_requirements>

Strict workflow:
1) Call get_data_model_files to retrieve all data model file paths and their (start_line, end_line) spans
2) Create a coverage checklist from ALL returned (file_path, model_identifier) pairs and process UNTIL NONE REMAIN
3) After inspecting ALL spans, synthesize the overall business domain they represent
4) Return ONLY a plain text description (2-4 sentences) summarizing the domain
""",
        deps_type=AgentDependencies,
        tools=[
            Tool(get_data_model_files, takes_ctx=True, max_retries=5),
            Tool(read_file_content, takes_ctx=True, max_retries=5),
        ],
        output_type=str,
        retries=6,
        model_settings=model_settings,
        event_stream_handler=event_stream_handler,
    )


def _build_context7_agent(
    model: Model,
    mcp_server: MCPServerStdio | MCPServerSSE | None = None,
    model_settings: ModelSettings | None = None,
) -> Agent[None, str]:
    """Create a plain Context7 Agent (non-durable).

    Shared between durable and non-durable variants to ensure identical prompts
    and tool wiring.
    """

    toolsets = [mcp_server] if mcp_server else []

    return Agent(
        model,
        name="context7_agent",  # REQUIRED for stable activity names
        system_prompt=r"""You are the Context7 Library Documentation Agent.

Your role is to provide concise, accurate documentation summaries for libraries, frameworks, and developer tools using Context7 tools.

Workflow:
1. Use resolve-library-id to get the correct library identifier
2. Use get-library-docs to retrieve comprehensive documentation
3. Provide a unified 5-line response format

Response Format (exactly 5 lines):
- Line 1: Library/tool type and primary purpose
- Line 2: Primary use case, commands, or when to use it
- Line 3: Key features or config files
- Line 4: Installation or setup
- Line 5: Usage patterns or grep-ready regex patterns

Always provide exactly 5 lines maximum. Keep responses factual and based on official documentation only.
""",
        toolsets=toolsets,  # type: ignore
        output_type=str,
        retries=6,
        model_settings=model_settings,
    )


def create_context7_agent(
    model: Model,
    mcp_server: MCPServerStdio | MCPServerSSE | None = None,
    model_settings: ModelSettings | None = None,
) -> Agent[None, str]:
    """Create plain Context7 Agent for in-activity use (non-durable)."""

    return _build_context7_agent(model, mcp_server, model_settings)


def create_context7_temporal_agent(
    model: Model,
    mcp_server: MCPServerStdio | MCPServerSSE | None = None,
    model_settings: ModelSettings | None = None,
) -> TemporalAgent[None, str]:
    """Create Context7 agent wrapped with TemporalAgent for durable execution.

    With Temporal, each agent.run() executes in an isolated activity,
    eliminating CancelScope conflicts without needing a factory pattern.
    """

    context7_agent = _build_context7_agent(model, mcp_server, model_settings)

    return TemporalAgent(
        context7_agent,
        activity_config=ActivityConfig(
            start_to_close_timeout=timedelta(seconds=300),  # 5 minutes for network calls
        ),
    )


# ──────────────────────────────────────────────
# TemporalAgent Wrappers
# ──────────────────────────────────────────────


def create_temporal_agents(
    model: Model,
    model_settings: ModelSettings | None = None,
) -> dict[str, TemporalAgent[AgentDependencies, Any]]:
    """Create enabled agents wrapped with TemporalAgent for durable execution.

    Only creates agents that are listed in ENABLED_AGENTS.

    Args:
        model: Configured Model instance from ModelFactory
        model_settings: Optional model settings (temperature, etc.)

    Returns:
        Dictionary mapping agent names to TemporalAgent instances
    """
    agents: dict[str, TemporalAgent[AgentDependencies, Any]] = {}

    # Default activity configuration
    default_activity_config = ActivityConfig(
        start_to_close_timeout=timedelta(seconds=300),  # 5 minutes for LLM operations
    )

    # Conditionally create agents based on ENABLED_AGENTS
    if AgentType.PROJECT_CONFIGURATION in ENABLED_AGENTS:
        config_agent = create_project_configuration_agent(model, model_settings)
        # Pydantic AI names the default function toolset as
        # "agent__{agent_name}__toolset". Use that exact ID when disabling
        # activities for specific tools; otherwise the override is ignored and
        # tools still execute inside activities (triggering nested Temporal calls).
        config_toolset_id = "<agent>"
        agents[AgentType.PROJECT_CONFIGURATION.value] = TemporalAgent(
            config_agent,
            activity_config=default_activity_config,
            # Disable activity for get_lib_data since it calls Context7 TemporalAgent internally.
            # This avoids nested activity issues - get_lib_data runs in workflow,
            # while Context7 TemporalAgent handles its own activity execution.
            tool_activity_config={
                config_toolset_id: {
                    "get_lib_data": False,
                }
            },
        )
        logger.info("Created project_configuration_agent")

    if AgentType.DEVELOPMENT_WORKFLOW in ENABLED_AGENTS:
        workflow_agent = create_development_workflow_agent(model, model_settings)
        workflow_toolset_id = "<agent>"
        agents[AgentType.DEVELOPMENT_WORKFLOW.value] = TemporalAgent(
            workflow_agent,
            activity_config=default_activity_config,
            # Disable activity for get_lib_data since it calls Context7 TemporalAgent internally.
            # This avoids nested activity issues - get_lib_data runs in workflow,
            # while Context7 TemporalAgent handles its own activity execution.
            tool_activity_config={
                workflow_toolset_id: {
                    "get_lib_data": False,
                }
            },
        )
        logger.info("Created development_workflow_agent")

    if AgentType.BUSINESS_LOGIC_DOMAIN in ENABLED_AGENTS:
        domain_agent = create_business_logic_domain_agent(model, model_settings)
        agents[AgentType.BUSINESS_LOGIC_DOMAIN.value] = TemporalAgent(
            domain_agent,
            activity_config=default_activity_config,
        )
        logger.info("Created business_logic_domain_agent")

    logger.info("Enabled agents: {}", list(agents.keys()))
    return agents


# Module-level cache for temporal agents singleton
_temporal_agents: dict[str, TemporalAgent[AgentDependencies, Any]] | None = None
_cached_model: Model | None = None
_cached_model_settings: ModelSettings | None = None


def get_temporal_agents() -> dict[str, TemporalAgent[AgentDependencies, Any]]:
    """Get cached temporal agents singleton.

    Returns:
        Dictionary of temporal agent instances

    Raises:
        RuntimeError: If agents not initialized (call initialize_temporal_agents first)
    """
    global _temporal_agents
    if _temporal_agents is None:
        raise RuntimeError(
            "Temporal agents not initialized. Call initialize_temporal_agents() first."
        )
    return _temporal_agents


def initialize_temporal_agents(
    model: Model,
    model_settings: ModelSettings | None = None,
) -> dict[str, TemporalAgent[AgentDependencies, Any]]:
    """Initialize temporal agents with the given model.

    This should be called once at worker startup after loading model from DB.

    Args:
        model: Configured Model instance from ModelFactory
        model_settings: Optional model settings (temperature, etc.)

    Returns:
        Dictionary of temporal agent instances
    """
    global _temporal_agents, _cached_model, _cached_model_settings

    _cached_model = model
    _cached_model_settings = model_settings
    _temporal_agents = create_temporal_agents(model, model_settings)

    logger.info(f"Temporal agents initialized with {len(_temporal_agents)} agents")
    return _temporal_agents


def get_cached_model() -> Model:
    """Get the cached model instance used for agents.

    Returns:
        Cached Model instance

    Raises:
        RuntimeError: If agents not initialized
    """
    if _cached_model is None:
        raise RuntimeError(
            "Model not initialized. Call initialize_temporal_agents() first."
        )
    return _cached_model


def get_cached_model_settings() -> ModelSettings | None:
    """Get the cached model settings.

    Returns:
        Cached ModelSettings or None
    """
    return _cached_model_settings
