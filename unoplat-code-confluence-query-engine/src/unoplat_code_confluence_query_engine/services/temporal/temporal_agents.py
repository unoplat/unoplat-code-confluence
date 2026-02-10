"""Temporal durable agents with dynamic model configuration.

This module defines all agents wrapped with TemporalAgent for durable execution.
Uses ModelFactory to build models dynamically from database configuration.
"""

from datetime import timedelta
from enum import Enum
from typing import Any

from loguru import logger
from pydantic_ai import Agent, ModelRetry, Tool
from pydantic_ai.builtin_tools import AbstractBuiltinTool, WebSearchTool
from pydantic_ai.durable_exec.temporal import TemporalAgent
from pydantic_ai.models import Model
from pydantic_ai.settings import ModelSettings
from pydantic_ai.usage import UsageLimits
from temporalio.workflow import ActivityConfig

from unoplat_code_confluence_query_engine.agents.code_confluence_agents import (
    SEARCH_MODE_BUILTIN_WEB_SEARCH,
    SEARCH_MODE_EXA,
    get_engineering_citation_instructions,
    per_language_development_workflow_prompt,
)
from unoplat_code_confluence_query_engine.config.settings import EnvironmentSettings
from unoplat_code_confluence_query_engine.models.output.agent_md_output import (
    DependencyGuideEntry,
)
from unoplat_code_confluence_query_engine.models.output.engineering_workflow_output import (
    EngineeringWorkflow,
)
from unoplat_code_confluence_query_engine.models.runtime.agent_dependencies import (
    AgentDependencies,
)
from unoplat_code_confluence_query_engine.services.repository.engineering_workflow_service import (
    CONFIDENCE_THRESHOLD,
)
from unoplat_code_confluence_query_engine.services.temporal.activity_retry_config import (
    TemporalAgentRetryConfig,
)
from unoplat_code_confluence_query_engine.services.temporal.event_stream_handler import (
    event_stream_handler,
)
from unoplat_code_confluence_query_engine.services.temporal.service_registry import (
    get_mcp_server_manager,
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
from unoplat_code_confluence_query_engine.tools.search_across_codebase import (
    search_across_codebase,
)

EXA_MCP_SERVER_NAME = "exa"
WEB_SEARCH_BUILTIN_PROVIDER_KEYS = frozenset(
    {"codex_openai", "anthropic", "grok", "groq"}
)
SEARCH_MODE_NONE = "none"


def _get_exa_mcp_server(toolset_id: str):
    mcp_server = get_mcp_server_manager().get_server_by_name(
        EXA_MCP_SERVER_NAME, id_override=toolset_id
    )
    if not mcp_server:
        raise RuntimeError(
            f"Exa MCP server '{EXA_MCP_SERVER_NAME}' not configured in MCP servers config"
        )
    return mcp_server


class AgentType(Enum):
    """Enum for available agent types."""

    DEVELOPMENT_WORKFLOW = "development_workflow_guide"
    DEPENDENCY = "dependency_guide"
    BUSINESS_DOMAIN = "business_domain_guide"


def _get_web_search_builtin_tools(
    provider_key: str | None,
) -> list[AbstractBuiltinTool]:
    """Build provider-compatible built-in web-search tools."""
    if provider_key in WEB_SEARCH_BUILTIN_PROVIDER_KEYS:
        return [WebSearchTool()]
    return []


def _supports_builtin_web_search_with_function_tools(provider_key: str | None) -> bool:
    """Return whether provider can mix built-in web search with function tools."""
    return provider_key in WEB_SEARCH_BUILTIN_PROVIDER_KEYS


def _resolve_search_mode(provider_key: str | None, exa_configured: bool) -> str:
    """Resolve external search mode for agent prompts/tooling."""
    if exa_configured:
        return SEARCH_MODE_EXA
    if provider_key in WEB_SEARCH_BUILTIN_PROVIDER_KEYS:
        return SEARCH_MODE_BUILTIN_WEB_SEARCH
    return SEARCH_MODE_NONE


def _get_dependency_guide_instructions(search_mode: str) -> str:
    """Build dependency-guide instructions based on available web-search mode."""
    if search_mode == SEARCH_MODE_EXA:
        workflow_steps = """1. Use Exa MCP tools (web_search_exa/get_code_context_exa) to locate official documentation for the library/tool
2. Evaluate results:
   - If official documentation is found: synthesize purpose and usage from it
   - If NO official docs found (error message, empty response, or "not found"): mark as internal dependency
3. Return the DependencyGuideEntry"""
    elif search_mode == SEARCH_MODE_BUILTIN_WEB_SEARCH:
        workflow_steps = """1. Use built-in `web_search` to locate official documentation for the library/tool
2. Evaluate results:
   - If official documentation is found: synthesize purpose and usage from it
   - If NO official docs found (error message, empty response, or "not found"): mark as internal dependency
3. Return the DependencyGuideEntry"""
    else:
        workflow_steps = """1. Use available repository context to infer whether this is likely internal/private
2. If no official documentation source is available, mark as internal dependency
3. Return the DependencyGuideEntry"""

    return f"""You are the Dependency Guide.

Goal: Generate a concise documentation entry for a single library/package dependency.

<task>
Given a library name and programming language, produce a DependencyGuideEntry with:
1. name: The exact library name provided (do not modify it)
2. purpose: 1-2 lines describing what this library does (from official docs)
3. usage: Exactly 2 sentences describing core features and capabilities
</task>

<workflow>
{workflow_steps}
</workflow>

<handling_internal_dependencies>
IMPORTANT: If available search/documentation tools return an error, "not found", or empty/minimal info, this is likely an INTERNAL/PRIVATE dependency.

For internal dependencies, return:
- name: The exact library name provided
- purpose: "INTERNAL_DEPENDENCY_SKIP"
- usage: "INTERNAL_DEPENDENCY_SKIP"

This signals the system to skip this dependency in the final output.
</handling_internal_dependencies>

<output_requirements>
For PUBLIC dependencies with documentation:
- The 'name' field MUST match the provided library name exactly
- The 'purpose' field should be 1-2 lines (concise, from official docs)
- The 'usage' field MUST be exactly 2 sentences, each ending with a period

For INTERNAL/PRIVATE dependencies (no docs found):
- Set both 'purpose' and 'usage' to "INTERNAL_DEPENDENCY_SKIP"
</output_requirements>
"""


# Stable, per-agent Exa MCP toolset IDs for Temporal activity naming.
EXA_TOOLSET_IDS = {
    # Reuse the existing workflow Exa toolset ID so current MCP routing/credentials remain valid.
    AgentType.DEVELOPMENT_WORKFLOW: "exa__development_workflow_guide",
    AgentType.DEPENDENCY: "exa__dependency_guide",
}


# Toggle agents here - comment/uncomment to enable/disable
ENABLED_AGENTS: set[AgentType] = {
    AgentType.DEVELOPMENT_WORKFLOW,
    AgentType.DEPENDENCY,
    AgentType.BUSINESS_DOMAIN,
}


def validate_engineering_development_workflow_output(
    output: EngineeringWorkflow,
) -> EngineeringWorkflow:
    if not output.commands:
        raise ModelRetry(
            "engineering_workflow.commands is empty. Re-scan command sources "
            "(Taskfile/Makefile/package scripts/tool configs) and return commands."
        )

    for command in output.commands:
        if not command.command.strip():
            raise ModelRetry(
                "Found command with empty command string. Return non-empty runnable commands."
            )
        if command.config_file.startswith("/") or command.config_file.startswith("../"):
            raise ModelRetry(
                f"config_file '{command.config_file}' must be repo-relative without leading '/' or '../'. "
                "Use 'unknown' if no config file applies."
            )
        if command.confidence < 0.0 or command.confidence > 1.0:
            raise ModelRetry(
                f"confidence {command.confidence} for command '{command.command}' must be between 0.0 and 1.0."
            )
    if not any(command.confidence >= CONFIDENCE_THRESHOLD for command in output.commands):
        raise ModelRetry(
            "All engineering workflow commands are below confidence threshold "
            f"({CONFIDENCE_THRESHOLD}). Re-validate against official citations and return at least one command >= threshold."
        )
    return output


def validate_business_logic_domain_output(output: str) -> str:
    """Validate business logic domain output.

    Ensures the model returns a non-empty plain text description
    of the business domain (2-4 sentences as requested in the prompt).
    """
    if not output or not output.strip():
        raise ModelRetry(
            "Output is empty. Return a plain text description (2-4 sentences) "
            "summarizing the business logic domain based on the data models analyzed."
        )
    # Check if model returned JSON/structured content instead of plain text
    stripped = output.strip()
    if stripped.startswith("{") or stripped.startswith("["):
        raise ModelRetry(
            "Return ONLY plain text (2-4 sentences), NOT JSON or structured data. "
            "Summarize the business logic domain in natural language."
        )
    return output


# ──────────────────────────────────────────────
# Agent Definitions
# ──────────────────────────────────────────────


def create_engineering_development_workflow_agent(
    model: Model,
    model_settings: ModelSettings | None = None,
    builtin_tools: list[AbstractBuiltinTool] | None = None,
    include_exa_toolset: bool = True,
    search_mode: str = SEARCH_MODE_EXA,
) -> Agent[AgentDependencies, EngineeringWorkflow]:
    """Create canonical engineering development workflow agent.

    Args:
        model: Configured Model instance from ModelFactory
        model_settings: Optional model settings (temperature, etc.)
        builtin_tools: Optional built-in tools (e.g. WebSearchTool)
        include_exa_toolset: Whether to include Exa MCP toolset
        search_mode: Resolved search mode ('exa' or 'builtin_web_search')

    Returns:
        Engineering development workflow agent instance
    """
    citation_instructions = get_engineering_citation_instructions(search_mode)
    exa_id = EXA_TOOLSET_IDS[AgentType.DEVELOPMENT_WORKFLOW]
    tools = [
        Tool(get_directory_tree, takes_ctx=True, max_retries=3),
        Tool(read_file_content, takes_ctx=True, max_retries=3),
        Tool(search_across_codebase, takes_ctx=True, max_retries=3),
    ]

    agent = Agent(
        model,
        name="development_workflow_guide",
        instructions=f"<role>Engineering Workflow Synthesizer</role>\n{citation_instructions}",
        deps_type=AgentDependencies,
        toolsets=[_get_exa_mcp_server(exa_id)] if include_exa_toolset else [],
        tools=tools,
        builtin_tools=builtin_tools or [],
        output_type=EngineeringWorkflow,
        output_retries=2,
        model_settings=model_settings,
        event_stream_handler=event_stream_handler,
    )
    agent.output_validator(validate_engineering_development_workflow_output)
    # Attach dynamic per-language instructions (always enabled)
    agent.instructions(per_language_development_workflow_prompt)

    logger.debug("Dynamic instructions attached to development_workflow_guide")

    return agent


# Marker for internal/private dependencies that should be skipped
INTERNAL_DEPENDENCY_SKIP_MARKER = "INTERNAL_DEPENDENCY_SKIP"


def create_dependency_guide_agent(
    model: Model,
    model_settings: ModelSettings | None = None,
    builtin_tools: list[AbstractBuiltinTool] | None = None,
    include_exa_toolset: bool = True,
    search_mode: str = SEARCH_MODE_EXA,
) -> Agent[AgentDependencies, DependencyGuideEntry]:
    """Create dependency guide agent.

    This agent documents a single library/package dependency using official docs.

    Args:
        model: Configured Model instance from ModelFactory
        model_settings: Optional model settings (temperature, etc.)

    Returns:
        Dependency guide agent instance
    """
    # TODO: Add output validator for DependencyGuideEntry to ensure:
    # - purpose is 1-2 lines (not empty/too short)
    # - usage contains exactly 2 sentences
    # - name matches the input dependency name
    exa_id = EXA_TOOLSET_IDS[AgentType.DEPENDENCY]
    dependency_toolsets = [_get_exa_mcp_server(exa_id)] if include_exa_toolset else []
    agent = Agent(
        model,
        name="dependency_guide",
        instructions=_get_dependency_guide_instructions(search_mode),
        deps_type=AgentDependencies,
        toolsets=dependency_toolsets,
        tools=[],
        builtin_tools=builtin_tools or [],
        output_type=DependencyGuideEntry,
        output_retries=2,
        model_settings=model_settings,
        event_stream_handler=event_stream_handler,
    )

    return agent


def create_business_logic_domain_agent(
    model: Model,
    model_settings: ModelSettings | None = None,
    builtin_tools: list[AbstractBuiltinTool] | None = None,
) -> Agent[AgentDependencies, str]:
    """Create business logic domain agent.

    Args:
        model: Configured Model instance from ModelFactory
        model_settings: Optional model settings (temperature, etc.)

    Returns:
        Business logic domain agent instance
    """
    agent = Agent(
        model,
        name="business_domain_guide",
        instructions=r"""You are the Business Domain Guide.

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

<output_format>
IMPORTANT: Your final output must be PLAIN TEXT only (2-4 sentences).
- Do NOT return JSON, markdown, or structured data
- Do NOT wrap your response in quotes or code blocks
- Simply write the domain description as natural language text
</output_format>
""",
        deps_type=AgentDependencies,
        tools=[
            Tool(get_data_model_files, takes_ctx=True, max_retries=3),
            Tool(read_file_content, takes_ctx=True, max_retries=3),
        ],
        builtin_tools=builtin_tools or [],
        output_type=str,
        output_retries=3,
        model_settings=model_settings,
        event_stream_handler=event_stream_handler,
    )
    agent.output_validator(validate_business_logic_domain_output)
    return agent


# ──────────────────────────────────────────────
# TemporalAgent Wrappers
# ──────────────────────────────────────────────


def create_temporal_agents(
    model: Model,
    retry_config: TemporalAgentRetryConfig,
    model_settings: ModelSettings | None = None,
    provider_key: str | None = None,
    exa_configured: bool = False,
) -> dict[str, TemporalAgent[AgentDependencies, Any]]:
    """Create enabled agents wrapped with TemporalAgent for durable execution.

    Only creates agents that are listed in ENABLED_AGENTS.

    Args:
        model: Configured Model instance from ModelFactory
        retry_config: Retry policy configuration for activities
        model_settings: Optional model settings (temperature, etc.)
        provider_key: Provider identifier for built-in web-search compatibility
        exa_configured: Whether Exa tool credentials are configured for this worker

    Returns:
        Dictionary mapping agent names to TemporalAgent instances
    """
    agents: dict[str, TemporalAgent[AgentDependencies, Any]] = {}

    # Base activity configuration with bounded retry policy
    base_activity_config = ActivityConfig(
        start_to_close_timeout=timedelta(seconds=300),
        retry_policy=retry_config.base_retry_policy,
    )

    # Model activity configuration (higher retries for LLM calls)
    model_activity_config = ActivityConfig(
        start_to_close_timeout=timedelta(seconds=300),
        retry_policy=retry_config.model_retry_policy,
    )

    # Toolset activity configuration (moderate retries for tool operations)
    toolset_activity_config = ActivityConfig(
        start_to_close_timeout=timedelta(seconds=120),
        retry_policy=retry_config.toolset_retry_policy,
    )

    # Tool activity configuration (conservative retries for individual tools)
    tool_activity_config_base = ActivityConfig(
        start_to_close_timeout=timedelta(seconds=120),
        retry_policy=retry_config.tool_retry_policy,
    )

    # Pydantic AI names the default function toolset as "<agent>".
    # Use that exact ID when configuring activity overrides.
    default_toolset_id = "<agent>"
    search_mode = _resolve_search_mode(provider_key, exa_configured)
    supports_builtin_web_search = _supports_builtin_web_search_with_function_tools(
        provider_key
    )
    use_exa_tools = search_mode == SEARCH_MODE_EXA
    use_builtin_web_search = search_mode == SEARCH_MODE_BUILTIN_WEB_SEARCH
    builtin_web_search_tools = (
        _get_web_search_builtin_tools(provider_key) if use_builtin_web_search else []
    )
    logger.info(
        "Agent external search mode resolved: provider_key={}, exa_configured={}, supports_builtin_web_search={}, selected_search_mode={}",
        provider_key,
        exa_configured,
        supports_builtin_web_search,
        search_mode,
    )

    # Conditionally create agents based on ENABLED_AGENTS
    if AgentType.DEVELOPMENT_WORKFLOW in ENABLED_AGENTS:
        exa_toolset_id = EXA_TOOLSET_IDS[AgentType.DEVELOPMENT_WORKFLOW]
        engineering_agent = create_engineering_development_workflow_agent(
            model,
            model_settings,
            builtin_tools=builtin_web_search_tools if use_builtin_web_search else None,
            include_exa_toolset=use_exa_tools,
            search_mode=search_mode,
        )
        engineering_tool_activity_config = {
            "get_directory_tree": tool_activity_config_base,
            "read_file_content": tool_activity_config_base,
            "search_across_codebase": tool_activity_config_base,
        }
        engineering_toolset_activity_config = {default_toolset_id: toolset_activity_config}
        engineering_toolset_tool_activity_config = {
            default_toolset_id: engineering_tool_activity_config
        }
        if use_exa_tools:
            engineering_toolset_activity_config[exa_toolset_id] = toolset_activity_config
            engineering_toolset_tool_activity_config[exa_toolset_id] = {}
        agents[AgentType.DEVELOPMENT_WORKFLOW.value] = TemporalAgent(
            engineering_agent,
            activity_config=base_activity_config,
            model_activity_config=model_activity_config,
            toolset_activity_config=engineering_toolset_activity_config,
            tool_activity_config=engineering_toolset_tool_activity_config,
        )
        logger.info("Created development_workflow_guide")

    if AgentType.DEPENDENCY in ENABLED_AGENTS:
        exa_toolset_id = EXA_TOOLSET_IDS[AgentType.DEPENDENCY]
        include_exa_dependency_toolset = use_exa_tools
        dependency_guide_agent = create_dependency_guide_agent(
            model,
            model_settings,
            builtin_tools=builtin_web_search_tools if use_builtin_web_search else None,
            include_exa_toolset=include_exa_dependency_toolset,
            search_mode=search_mode,
        )
        dependency_toolset_activity_config = {default_toolset_id: toolset_activity_config}
        dependency_tool_activity_config = {default_toolset_id: {}}
        if include_exa_dependency_toolset:
            dependency_toolset_activity_config[exa_toolset_id] = toolset_activity_config
            dependency_tool_activity_config[exa_toolset_id] = {}

        agents[AgentType.DEPENDENCY.value] = TemporalAgent(
            dependency_guide_agent,
            activity_config=base_activity_config,
            model_activity_config=model_activity_config,
            toolset_activity_config=dependency_toolset_activity_config,
            tool_activity_config=dependency_tool_activity_config,
        )
        logger.info("Created dependency_guide")

    if AgentType.BUSINESS_DOMAIN in ENABLED_AGENTS:
        domain_agent = create_business_logic_domain_agent(
            model,
            model_settings,
            builtin_tools=builtin_web_search_tools if use_builtin_web_search else None,
        )
        agents[AgentType.BUSINESS_DOMAIN.value] = TemporalAgent(
            domain_agent,
            activity_config=base_activity_config,
            model_activity_config=model_activity_config,
            toolset_activity_config={default_toolset_id: toolset_activity_config},
            tool_activity_config={
                default_toolset_id: {
                    "get_data_model_files": tool_activity_config_base,
                    "read_file_content": tool_activity_config_base,
                }
            },
        )
        logger.info("Created business_domain_guide")

    logger.info("Enabled agents: {}", list(agents.keys()))
    return agents


# Default request_limit when user hasn't configured one explicitly.
# pydantic_ai's built-in default is 50, which is too low for larger codebases.
DEFAULT_REQUEST_LIMIT: int = 200

# Module-level cache for temporal agents singleton
_temporal_agents: dict[str, TemporalAgent[AgentDependencies, Any]] | None = None
_cached_model: Model | None = None
_cached_model_settings: ModelSettings | None = None
_cached_usage_limits: UsageLimits | None = None


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
    settings: EnvironmentSettings,
    model_settings: ModelSettings | None = None,
    provider_key: str | None = None,
    exa_configured: bool = False,
    request_limit: int | None = None,
) -> dict[str, TemporalAgent[AgentDependencies, Any]]:
    """Initialize temporal agents with the given model.

    This should be called once at worker startup after loading model from DB.

    Args:
        model: Configured Model instance from ModelFactory
        settings: Environment settings for retry configuration
        model_settings: Optional model settings (temperature, etc.)
        provider_key: Provider identifier for web search compatibility
        exa_configured: Whether Exa tool credentials are configured for this worker
        request_limit: Max LLM round-trips per Agent.run() call (None = DEFAULT_REQUEST_LIMIT)

    Returns:
        Dictionary of temporal agent instances
    """
    global _temporal_agents, _cached_model, _cached_model_settings, _cached_usage_limits

    retry_config = TemporalAgentRetryConfig(settings)

    effective_limit = request_limit if request_limit is not None else DEFAULT_REQUEST_LIMIT
    _cached_model = model
    _cached_model_settings = model_settings
    _cached_usage_limits = UsageLimits(request_limit=effective_limit)

    _temporal_agents = create_temporal_agents(
        model,
        retry_config,
        model_settings,
        provider_key=provider_key,
        exa_configured=exa_configured,
    )

    logger.info(
        "Temporal agents initialized with {} agents (request_limit={})",
        len(_temporal_agents),
        effective_limit,
    )
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


def get_cached_usage_limits() -> UsageLimits | None:
    """Get the cached usage limits.

    Returns:
        Cached UsageLimits (always set after initialization, defaults to 200)
    """
    return _cached_usage_limits
