from __future__ import annotations

from pydantic_ai.toolsets.abstract import AbstractToolset

from unoplat_code_confluence_query_engine.models.runtime.agent_dependencies import (
    AgentDependencies,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.constants import (
    DEPENDENCY_GUIDE_EXA_TOOLSET_ID,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.toolsets.exa import (
    get_exa_toolset,
)


def build_dependency_guide_exa_toolset() -> AbstractToolset[AgentDependencies]:
    return get_exa_toolset(DEPENDENCY_GUIDE_EXA_TOOLSET_ID)
