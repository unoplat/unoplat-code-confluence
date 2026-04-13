from __future__ import annotations

from typing import cast

from pydantic_ai import Tool
from pydantic_ai.common_tools.duckduckgo import (
    duckduckgo_search_tool,  # pyright: ignore[reportUnknownVariableType]
)

from unoplat_code_confluence_query_engine.models.runtime.agent_dependencies import (
    AgentDependencies,
)


def build_duckduckgo_search_tool() -> Tool[AgentDependencies]:
    """Build the shared DuckDuckGo fallback tool."""

    return cast(Tool[AgentDependencies], duckduckgo_search_tool(max_results=5))
