from __future__ import annotations

from collections.abc import Callable, Set as AbstractSet
from enum import Enum
from typing import Any

from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.agents.architecture import (
    build_architecture_agent,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.agents.business_domain import (
    build_business_domain_agent,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.agents.call_expression_discoverer import (
    build_call_expression_discoverer_agent,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.agents.dependency_guide import (
    build_dependency_guide_agent,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.agents.development_workflow import (
    build_development_workflow_agent,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.constants import (
    DEPENDENCY_GUIDE_EXA_TOOLSET_ID,
    DEVELOPMENT_WORKFLOW_EXA_TOOLSET_ID,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.runtime import (
    AgentAssemblyContext,
    AgentBuildResult,
)


class AgentType(str, Enum):
    ARCHITECTURE = "architecture"
    DEVELOPMENT_WORKFLOW = "development_workflow_guide"
    DEPENDENCY = "dependency_guide"
    BUSINESS_DOMAIN = "business_domain_guide"
    CALL_EXPRESSION_DISCOVERER = "call_expression_discoverer"


DEFAULT_ENABLED_AGENT_TYPES = frozenset(
    {
        AgentType.ARCHITECTURE,
        AgentType.DEVELOPMENT_WORKFLOW,
        AgentType.DEPENDENCY,
        AgentType.BUSINESS_DOMAIN,
        AgentType.CALL_EXPRESSION_DISCOVERER,
    }
)

EXA_TOOLSET_IDS: dict[AgentType, str] = {
    AgentType.DEVELOPMENT_WORKFLOW: DEVELOPMENT_WORKFLOW_EXA_TOOLSET_ID,
    AgentType.DEPENDENCY: DEPENDENCY_GUIDE_EXA_TOOLSET_ID,
}


AGENT_BUILDERS: dict[
    AgentType, Callable[[AgentAssemblyContext], AgentBuildResult[Any, Any]]
] = {
    AgentType.ARCHITECTURE: build_architecture_agent,
    AgentType.DEVELOPMENT_WORKFLOW: build_development_workflow_agent,
    AgentType.DEPENDENCY: build_dependency_guide_agent,
    AgentType.BUSINESS_DOMAIN: build_business_domain_agent,
    AgentType.CALL_EXPRESSION_DISCOVERER: build_call_expression_discoverer_agent,
}


def build_enabled_agent_builders(
    enabled_agents: AbstractSet[AgentType] | None = None,
) -> dict[AgentType, Callable[[AgentAssemblyContext], AgentBuildResult[Any, Any]]]:
    """Return the concrete builder mapping for each enabled agent type."""

    selected_agents = (
        DEFAULT_ENABLED_AGENT_TYPES
        if enabled_agents is None
        else frozenset(enabled_agents)
    )
    return {
        agent_type: builder
        for agent_type, builder in AGENT_BUILDERS.items()
        if agent_type in selected_agents
    }


def build_enabled_agent_specs(
    enabled_agents: AbstractSet[AgentType] | None = None,
) -> dict[AgentType, Callable[[AgentAssemblyContext], AgentBuildResult[Any, Any]]]:
    """Compatibility wrapper for the legacy builder-mapping helper name."""

    return build_enabled_agent_builders(enabled_agents)
