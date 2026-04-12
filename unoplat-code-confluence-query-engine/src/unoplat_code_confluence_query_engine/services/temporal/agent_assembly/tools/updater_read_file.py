from __future__ import annotations

from pydantic_ai import Tool

from unoplat_code_confluence_query_engine.models.runtime.agent_dependencies import (
    AgentDependencies,
)
from unoplat_code_confluence_query_engine.tools.agents_md_updater_tools import (
    updater_read_file,
)


def build_updater_read_file_tool() -> Tool[AgentDependencies]:
    return Tool(updater_read_file, takes_ctx=True, max_retries=2)
