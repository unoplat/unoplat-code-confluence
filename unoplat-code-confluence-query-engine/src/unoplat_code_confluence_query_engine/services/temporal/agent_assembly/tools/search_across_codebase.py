from __future__ import annotations

from pydantic_ai import Tool

from unoplat_code_confluence_query_engine.models.runtime.agent_dependencies import (
    AgentDependencies,
)
from unoplat_code_confluence_query_engine.tools.search_across_codebase import (
    search_across_codebase,
)


def build_search_across_codebase_tool() -> Tool[AgentDependencies]:
    return Tool(search_across_codebase, takes_ctx=True, max_retries=3)
