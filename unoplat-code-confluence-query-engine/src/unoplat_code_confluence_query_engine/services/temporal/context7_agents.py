"""Context7 agent factories for plain Agent execution.

This module provides factories for creating Context7 Agents that execute MCP
operations directly within the calling async context. We use plain Agent (NOT
TemporalAgent) because TemporalAgent wraps MCP operations in separate activities,
causing cancel scope conflicts when the MCP exit stack is closed in a different
task than it was created.

This module is intentionally separated from `temporal_agents.py` to avoid circular
imports between agent definitions and tools (e.g., `get_lib_data`).
"""

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerSSE, MCPServerStdio, MCPServerStreamableHTTP
from pydantic_ai.models import Model
from pydantic_ai.settings import ModelSettings

from unoplat_code_confluence_query_engine.services.mcp.mcp_server_manager import (
    MCPServerManager,
)


def _build_context7_agent(
    model: Model,
    mcp_server: MCPServerStdio | MCPServerSSE | MCPServerStreamableHTTP | None = None,
    model_settings: ModelSettings | None = None,
) -> Agent[None, str]:
    """Create a plain Context7 Agent (non-durable).

    Shared between durable and non-durable variants to ensure identical prompts
    and tool wiring.
    """
    toolsets = [mcp_server] if mcp_server else []

    return Agent(
        model,
        name="context7_agent",  # REQUIRED for stable activity names
        system_prompt=r"""You are the Context7 Library Documentation Agent.

Your role is to provide concise, accurate documentation summaries for libraries, frameworks, and developer tools using Context7 tools.

Workflow:
1. Use resolve-library-id to get the correct library identifier
2. Use get-library-docs to retrieve comprehensive documentation
3. Provide a unified 5-line response format

Response Format (exactly 5 lines):
- Line 1: Library/tool type and primary purpose
- Line 2: Primary use case, commands, or when to use it
- Line 3: Key features or config files
- Line 4: Installation or setup
- Line 5: Usage patterns or grep-ready regex patterns

Always provide exactly 5 lines maximum. Keep responses factual and based on official documentation only.
""",
        toolsets=toolsets,  # type: ignore
        output_type=str,
        model_settings=model_settings,
        retries=3,
    )


def create_context7_agent(
    model: Model,
    mcp_server: MCPServerStdio | MCPServerSSE | MCPServerStreamableHTTP | None = None,
    model_settings: ModelSettings | None = None,
) -> Agent[None, str]:
    """Create plain Context7 Agent for in-activity use (non-durable)."""
    return _build_context7_agent(model, mcp_server, model_settings)


def create_context7_agent_fresh_mcp(
    model: Model,
    mcp_server_manager: MCPServerManager,
    mcp_server_name: str,
    model_settings: ModelSettings | None = None,
) -> Agent[None, str]:
    """Create plain Context7 Agent bound to a fresh MCPServer instance.

    This factory creates a new MCPServer per call, ensuring each invocation
    gets its own connection. Unlike TemporalAgent, the plain Agent executes
    MCP calls directly within the calling async context, avoiding cross-task
    cancel scope conflicts entirely.

    Use this for Context7 calls inside Temporal activities where the MCP
    lifecycle must stay within a single async task. TemporalAgent cannot
    disable activity wrapping for MCP tools (they require I/O), so plain
    Agent is the only way to avoid cancel scope conflicts.

    Args:
        model: Configured Model instance (can be reused)
        mcp_server_manager: Manager to create fresh MCP server instances
        mcp_server_name: Name of MCP server config (e.g., "context7")
        model_settings: Optional model settings

    Returns:
        Plain Context7 Agent with fresh MCPServer binding
    """
    mcp_server = mcp_server_manager.get_server_by_name(mcp_server_name)
    return create_context7_agent(model, mcp_server, model_settings)

