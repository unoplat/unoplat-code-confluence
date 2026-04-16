"""Temporal durable agent registry and workflow-facing helpers."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from loguru import logger
from pydantic import BaseModel, ConfigDict
from pydantic_ai.durable_exec.temporal import TemporalAgent
from pydantic_ai.models import Model
from pydantic_ai.settings import ModelSettings
from pydantic_ai.usage import UsageLimits

from unoplat_code_confluence_query_engine.config.settings import EnvironmentSettings
from unoplat_code_confluence_query_engine.models.output.agent_md_output import (
    DependencyGuideEntry,
)
from unoplat_code_confluence_query_engine.models.output.agents_md_updater_output import (
    AgentsMdUpdaterOutput,
)
from unoplat_code_confluence_query_engine.models.output.engineering_workflow_output import (
    EngineeringWorkflow,
)
from unoplat_code_confluence_query_engine.models.repository.framework_feature_validation_models import (
    CallExpressionValidationAgentOutput,
)
from unoplat_code_confluence_query_engine.models.runtime.agent_dependencies import (
    AgentDependencies,
)
from unoplat_code_confluence_query_engine.services.temporal.activity_retry_config import (
    TemporalAgentRetryConfig,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.assembler import (
    assemble_enabled_temporal_agents,
    create_assembly_context,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.catalog import (
    DEFAULT_ENABLED_AGENT_TYPES,
    AgentType,
    build_enabled_agent_builders,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.search import (
    provider_supports_builtin_web_fetch,
    provider_supports_builtin_web_search,
)


class TemporalAgentRegistry(BaseModel):
    """Precise registry model for enabled Temporal agents."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    development_workflow_guide: (
        TemporalAgent[AgentDependencies, EngineeringWorkflow] | None
    ) = None
    dependency_guide: TemporalAgent[AgentDependencies, DependencyGuideEntry] | None = (
        None
    )
    business_domain_guide: TemporalAgent[AgentDependencies, str] | None = None
    agents_md_updater: TemporalAgent[AgentDependencies, AgentsMdUpdaterOutput] | None = (
        None
    )
    call_expression_validator: (
        TemporalAgent[AgentDependencies, CallExpressionValidationAgentOutput] | None
    ) = None

    def iter_agents(self) -> Iterator[TemporalAgent[AgentDependencies, Any]]:
        """Yield all enabled temporal agents."""
        for field_name in type(self).model_fields:
            agent = getattr(self, field_name)
            if agent is not None:
                yield agent

    def iter_agent_names(self) -> Iterator[str]:
        """Yield field names for all enabled temporal agents."""
        for field_name in type(self).model_fields:
            if getattr(self, field_name) is not None:
                yield field_name

    def enabled_agent_names(self) -> list[str]:
        """Return enabled temporal agent names in declaration order."""
        return list(self.iter_agent_names())

    def enabled_agent_count(self) -> int:
        """Return the number of enabled temporal agents."""
        return len(self.enabled_agent_names())


ENABLED_AGENTS: frozenset[AgentType] = DEFAULT_ENABLED_AGENT_TYPES


def create_temporal_agents(
    model: Model,
    retry_config: TemporalAgentRetryConfig,
    model_settings: ModelSettings | None = None,
    provider_key: str | None = None,
    exa_configured: bool = False,
) -> TemporalAgentRegistry:
    """Create enabled agents wrapped with TemporalAgent for durable execution.

    Only creates agents that are listed in ENABLED_AGENTS.
    """
    assembly_context = create_assembly_context(
        model=model,
        retry_config=retry_config,
        model_settings=model_settings,
        provider_key=provider_key,
        exa_configured=exa_configured,
    )
    logger.info(
        "Agent external web-tool wiring resolved: provider_key={}, exa_configured={}, supports_builtin_web_search={}, supports_builtin_web_fetch={}, use_exa_toolsets={}, use_prepared_builtin_web_search={}, use_prepared_builtin_web_fetch={}",
        provider_key,
        exa_configured,
        provider_supports_builtin_web_search(provider_key),
        provider_supports_builtin_web_fetch(provider_key),
        assembly_context.search_policy.include_exa_toolsets,
        assembly_context.search_policy.include_prepared_builtin_web_search,
        assembly_context.search_policy.include_prepared_builtin_web_fetch,
    )
    assembled_agents = assemble_enabled_temporal_agents(
        agent_builders=build_enabled_agent_builders(ENABLED_AGENTS),
        context=assembly_context,
    )
    agents = TemporalAgentRegistry.model_validate(
        {
            agent_type.value: temporal_agent
            for agent_type, temporal_agent in assembled_agents.items()
        }
    )
    for agent_name in agents.iter_agent_names():
        logger.info("Created {}", agent_name)
    logger.info("Enabled agents: {}", agents.enabled_agent_names())
    return agents


# Default request_limit when user hasn't configured one explicitly.
# pydantic_ai's built-in default is 50, which is too low for larger codebases.
DEFAULT_REQUEST_LIMIT: int = 200

# Module-level cache for temporal agents singleton
_temporal_agents: TemporalAgentRegistry | None = None
_cached_model: Model | None = None
_cached_model_settings: ModelSettings | None = None
_cached_usage_limits: UsageLimits | None = None


def get_temporal_agents() -> TemporalAgentRegistry:
    """Get cached temporal agents singleton."""
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
) -> TemporalAgentRegistry:
    """Initialize temporal agents with the given model."""
    global _temporal_agents, _cached_model, _cached_model_settings, _cached_usage_limits

    retry_config = TemporalAgentRetryConfig(settings)

    effective_limit = (
        request_limit if request_limit is not None else DEFAULT_REQUEST_LIMIT
    )
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
        _temporal_agents.enabled_agent_count(),
        effective_limit,
    )
    return _temporal_agents


def get_cached_model() -> Model:
    """Get the cached model instance used for agents."""
    if _cached_model is None:
        raise RuntimeError(
            "Model not initialized. Call initialize_temporal_agents() first."
        )
    return _cached_model


def get_cached_model_settings() -> ModelSettings | None:
    """Get the cached model settings."""
    return _cached_model_settings


def get_cached_usage_limits() -> UsageLimits | None:
    """Get the cached usage limits."""
    return _cached_usage_limits
