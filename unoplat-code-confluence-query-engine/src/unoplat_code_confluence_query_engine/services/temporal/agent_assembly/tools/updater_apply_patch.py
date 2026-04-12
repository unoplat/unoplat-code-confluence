from __future__ import annotations

from pydantic_ai import Tool

from unoplat_code_confluence_query_engine.models.runtime.agent_dependencies import (
    AgentDependencies,
)
from unoplat_code_confluence_query_engine.tools.agents_md_updater_tools import (
    updater_apply_patch,
)


def build_updater_apply_patch_tool() -> Tool[AgentDependencies]:
    return Tool(
        updater_apply_patch,
        takes_ctx=True,
        max_retries=4,
        docstring_format="google",
    )
