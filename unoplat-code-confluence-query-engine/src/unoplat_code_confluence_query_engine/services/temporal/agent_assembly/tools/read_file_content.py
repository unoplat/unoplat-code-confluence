from __future__ import annotations

from pydantic_ai import Tool

from unoplat_code_confluence_query_engine.models.runtime.agent_dependencies import (
    AgentDependencies,
)
from unoplat_code_confluence_query_engine.tools.get_content_file import (
    read_file_content,
)


def build_read_file_content_tool() -> Tool[AgentDependencies]:
    return Tool(read_file_content, takes_ctx=True, max_retries=3)
