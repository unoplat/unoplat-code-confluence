from __future__ import annotations

from pydantic_ai import Tool

from unoplat_code_confluence_query_engine.models.runtime.architecture_agent_dependencies import (
    ArchitectureAgentDependencies,
)
from unoplat_code_confluence_query_engine.tools.architecture_validation_tools import (
    validate_architecture,
)


def build_validate_architecture_tool() -> Tool[ArchitectureAgentDependencies]:
    """Build the Architecture agent's explicit final self-validation tool."""
    return Tool(
        validate_architecture,
        takes_ctx=True,
        max_retries=3,
        docstring_format="google",
        require_parameter_descriptions=True,
    )
