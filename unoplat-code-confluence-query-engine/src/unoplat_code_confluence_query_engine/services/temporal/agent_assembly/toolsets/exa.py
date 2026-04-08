from __future__ import annotations

from typing import cast

from pydantic_ai.toolsets.abstract import AbstractToolset

from unoplat_code_confluence_query_engine.models.runtime.agent_dependencies import (
    AgentDependencies,
)
from unoplat_code_confluence_query_engine.services.temporal.service_registry import (
    get_mcp_server_manager,
)

EXA_MCP_SERVER_NAME = "exa"


def get_exa_toolset(toolset_id: str) -> AbstractToolset[AgentDependencies]:
    """Resolve a deterministic Exa MCP toolset ID for assembly."""

    mcp_server = get_mcp_server_manager().get_server_by_name(
        EXA_MCP_SERVER_NAME,
        id_override=toolset_id,
    )
    if mcp_server is None:
        raise RuntimeError(
            f"Exa MCP server '{EXA_MCP_SERVER_NAME}' not configured in MCP servers config"
        )
    return cast(AbstractToolset[AgentDependencies], mcp_server)
