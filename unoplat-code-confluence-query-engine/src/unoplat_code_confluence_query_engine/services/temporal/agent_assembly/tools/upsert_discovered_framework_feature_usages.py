from __future__ import annotations

from pydantic_ai import Tool

from unoplat_code_confluence_query_engine.models.runtime.agent_dependencies import (
    AgentDependencies,
)
from unoplat_code_confluence_query_engine.tools.framework_feature_validation_tools import (
    upsert_discovered_framework_feature_usages,
)


def build_upsert_discovered_framework_feature_usages_tool() -> Tool[AgentDependencies]:
    """Build the discovery tool for one-to-many confirmed usage persistence."""
    return Tool(
        upsert_discovered_framework_feature_usages,
        takes_ctx=True,
        max_retries=3,
        docstring_format="google",
        require_parameter_descriptions=True,
    )
