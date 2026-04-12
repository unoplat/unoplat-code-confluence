from __future__ import annotations

from pydantic_ai.toolsets.abstract import AbstractToolset

from unoplat_code_confluence_query_engine.models.runtime.agent_dependencies import (
    AgentDependencies,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.constants import (
    CALL_EXPRESSION_VALIDATOR_EXA_TOOLSET_ID,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.toolsets.exa import (
    get_exa_toolset,
)


def build_call_expression_validator_exa_toolset() -> AbstractToolset[AgentDependencies]:
    return get_exa_toolset(CALL_EXPRESSION_VALIDATOR_EXA_TOOLSET_ID)
