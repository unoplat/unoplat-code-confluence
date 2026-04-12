from __future__ import annotations

from pydantic_ai import Tool

from unoplat_code_confluence_query_engine.models.runtime.agent_dependencies import (
    AgentDependencies,
)
from unoplat_code_confluence_query_engine.tools.get_data_model_files import (
    get_data_model_files,
)


def build_get_data_model_files_tool() -> Tool[AgentDependencies]:
    return Tool(get_data_model_files, takes_ctx=True, max_retries=3)
