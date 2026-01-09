"""Temporal durable agents with dynamic model configuration.

This module defines all agents wrapped with TemporalAgent for durable execution.
Uses ModelFactory to build models dynamically from database configuration.
"""

from datetime import timedelta
from enum import Enum
from typing import Any

from loguru import logger
from pydantic_ai import Agent, ModelRetry, Tool
from pydantic_ai.durable_exec.temporal import TemporalAgent
from pydantic_ai.models import Model
from pydantic_ai.settings import ModelSettings
from temporalio.workflow import ActivityConfig

from unoplat_code_confluence_query_engine.agents.code_confluence_agents import (
    per_language_development_workflow_prompt,
    per_programming_language_configuration_prompt,
)
from unoplat_code_confluence_query_engine.config.settings import EnvironmentSettings
from unoplat_code_confluence_query_engine.models.output.agent_md_output import (
    DevelopmentWorkflow,
    ProjectConfiguration,
)
from unoplat_code_confluence_query_engine.models.runtime.agent_dependencies import (
    AgentDependencies,
)
from unoplat_code_confluence_query_engine.services.temporal.activity_retry_config import (
    TemporalAgentRetryConfig,
)
from unoplat_code_confluence_query_engine.services.temporal.event_stream_handler import (
    event_stream_handler,
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


def validate_project_configuration_output(
    output: ProjectConfiguration,
) -> ProjectConfiguration:
    if not output.config_files:
        raise ModelRetry(
            "config_files is empty. Re-scan and return all configuration files; do not omit any."
        )
    return output


def validate_development_workflow_output(
    output: DevelopmentWorkflow,
) -> DevelopmentWorkflow:
    if not output.commands:
        raise ModelRetry(
            "commands is empty. Extract build/dev/test/lint/type_check commands and return all applicable commands."
        )
    return output


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
            Tool(get_directory_tree, takes_ctx=True),
            Tool(read_file_content, takes_ctx=True),
            Tool(search_across_codebase, takes_ctx=True),
            Tool(get_lib_data),
        ],
        output_type=ProjectConfiguration,
        output_retries=2,
        model_settings=model_settings,
        event_stream_handler=event_stream_handler,
    )
    agent.output_validator(validate_project_configuration_output)
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
            Tool(get_directory_tree, takes_ctx=True),
            Tool(read_file_content, takes_ctx=True),
            Tool(get_lib_data),
        ],
        output_type=DevelopmentWorkflow,
        output_retries=2,
        model_settings=model_settings,
        event_stream_handler=event_stream_handler,
    )
    agent.output_validator(validate_development_workflow_output)
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
            Tool(get_data_model_files, takes_ctx=True),
            Tool(read_file_content, takes_ctx=True),
        ],
        output_type=str,
        model_settings=model_settings,
        event_stream_handler=event_stream_handler,
    )


# ──────────────────────────────────────────────
# TemporalAgent Wrappers
# ──────────────────────────────────────────────


def create_temporal_agents(
    model: Model,
    retry_config: TemporalAgentRetryConfig,
    model_settings: ModelSettings | None = None,
) -> dict[str, TemporalAgent[AgentDependencies, Any]]:
    """Create enabled agents wrapped with TemporalAgent for durable execution.

    Only creates agents that are listed in ENABLED_AGENTS.

    Args:
        model: Configured Model instance from ModelFactory
        retry_config: Retry policy configuration for activities
        model_settings: Optional model settings (temperature, etc.)

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

    # Conditionally create agents based on ENABLED_AGENTS
    if AgentType.PROJECT_CONFIGURATION in ENABLED_AGENTS:
        config_agent = create_project_configuration_agent(model, model_settings)
        agents[AgentType.PROJECT_CONFIGURATION.value] = TemporalAgent(
            config_agent,
            activity_config=base_activity_config,
            model_activity_config=model_activity_config,
            toolset_activity_config={default_toolset_id: toolset_activity_config},
            # Disable activity for get_lib_data since it calls Context7 TemporalAgent internally.
            # This avoids nested activity issues - get_lib_data runs in workflow,
            # while Context7 TemporalAgent handles its own activity execution.
            # Other tools use tool_activity_config_base for bounded retries.
            tool_activity_config={
                default_toolset_id: {
                    "get_lib_data": tool_activity_config_base,
                    "get_directory_tree": tool_activity_config_base,
                    "read_file_content": tool_activity_config_base,
                    "search_across_codebase": tool_activity_config_base,
                }
            },
        )
        logger.info("Created project_configuration_agent")

    if AgentType.DEVELOPMENT_WORKFLOW in ENABLED_AGENTS:
        workflow_agent = create_development_workflow_agent(model, model_settings)
        agents[AgentType.DEVELOPMENT_WORKFLOW.value] = TemporalAgent(
            workflow_agent,
            activity_config=base_activity_config,
            model_activity_config=model_activity_config,
            toolset_activity_config={default_toolset_id: toolset_activity_config},
            # Disable activity for get_lib_data since it calls
            # Context7 TemporalAgent internally.
            tool_activity_config={
                default_toolset_id: {
                    "get_lib_data": tool_activity_config_base,
                    "get_directory_tree": tool_activity_config_base,
                    "read_file_content": tool_activity_config_base,
                }
            },
        )
        logger.info("Created development_workflow_agent")

    if AgentType.BUSINESS_LOGIC_DOMAIN in ENABLED_AGENTS:
        domain_agent = create_business_logic_domain_agent(model, model_settings)
        agents[AgentType.BUSINESS_LOGIC_DOMAIN.value] = TemporalAgent(
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
    settings: EnvironmentSettings,
    model_settings: ModelSettings | None = None,
) -> dict[str, TemporalAgent[AgentDependencies, Any]]:
    """Initialize temporal agents with the given model.

    This should be called once at worker startup after loading model from DB.

    Args:
        model: Configured Model instance from ModelFactory
        settings: Environment settings for retry configuration
        model_settings: Optional model settings (temperature, etc.)

    Returns:
        Dictionary of temporal agent instances
    """
    global _temporal_agents, _cached_model, _cached_model_settings

    retry_config = TemporalAgentRetryConfig(settings)

    _cached_model = model
    _cached_model_settings = model_settings
    _temporal_agents = create_temporal_agents(model, retry_config, model_settings)

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
