from __future__ import annotations

from pydantic_ai import Tool

from unoplat_code_confluence_query_engine.models.runtime.agent_dependencies import (
    AgentDependencies,
)
from unoplat_code_confluence_query_engine.tools.framework_feature_validation_tools import (
    upsert_framework_feature_validation_evidence,
)


def build_upsert_framework_feature_validation_evidence_tool() -> Tool[
    AgentDependencies
]:
    return Tool(
        upsert_framework_feature_validation_evidence,
        takes_ctx=True,
        max_retries=3,
        docstring_format="google",
        require_parameter_descriptions=True,
    )
