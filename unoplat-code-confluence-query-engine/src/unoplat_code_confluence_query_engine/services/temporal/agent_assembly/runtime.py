from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

from pydantic_ai import Agent
from pydantic_ai.models import Model
from pydantic_ai.settings import ModelSettings

from unoplat_code_confluence_query_engine.models.runtime.agent_dependencies import (
    AgentDependencies,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.activity_policies import (
    TemporalActivityDefaults,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.search import (
    SearchRuntimePolicy,
)

OutputT = TypeVar("OutputT")


@dataclass(frozen=True, slots=True)
class AgentAssemblyContext:
    """Shared runtime inputs for one agent-assembly pass."""

    model: Model
    model_settings: ModelSettings | None
    search_policy: SearchRuntimePolicy
    activity_defaults: TemporalActivityDefaults
    default_function_toolset_id: str = "<agent>"


@dataclass(frozen=True, slots=True)
class AgentBuildResult(Generic[OutputT]):
    """Concrete agent plus the metadata Temporal wrapping still needs."""

    agent: Agent[AgentDependencies, OutputT]
    function_tool_names: tuple[str, ...]
    toolset_ids: tuple[str, ...] = ()

