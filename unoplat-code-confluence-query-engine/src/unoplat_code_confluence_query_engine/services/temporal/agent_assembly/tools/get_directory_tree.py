from __future__ import annotations

from pydantic_ai import Tool

from unoplat_code_confluence_query_engine.models.runtime.agent_dependencies import (
    AgentDependencies,
)
from unoplat_code_confluence_query_engine.tools.get_directory_tree import (
    get_directory_tree,
)


def build_get_directory_tree_tool() -> Tool[AgentDependencies]:
    return Tool(get_directory_tree, takes_ctx=True, max_retries=3)
