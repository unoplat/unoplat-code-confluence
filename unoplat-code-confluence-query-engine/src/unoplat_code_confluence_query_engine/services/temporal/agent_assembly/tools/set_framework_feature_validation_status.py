from __future__ import annotations

from pydantic_ai import Tool

from unoplat_code_confluence_query_engine.models.runtime.agent_dependencies import (
    AgentDependencies,
)
from unoplat_code_confluence_query_engine.tools.framework_feature_validation_tools import (
    set_framework_feature_validation_status,
)


def build_set_framework_feature_validation_status_tool() -> Tool[AgentDependencies]:
    return Tool(
        set_framework_feature_validation_status,
        takes_ctx=True,
        max_retries=3,
        docstring_format="google",
        require_parameter_descriptions=True,
    )
