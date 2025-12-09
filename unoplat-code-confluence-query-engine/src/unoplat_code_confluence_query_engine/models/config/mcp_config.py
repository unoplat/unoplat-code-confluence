"""
MCP Server Configuration Models

This implementation is inspired by OpenCode.ai's MCP server configuration:
https://opencode.ai/docs/mcp-servers/
"""

from enum import Enum
from typing import Annotated, Any, Literal, Union

from pydantic import BaseModel, Field, field_validator


class MCPServerType(str, Enum):
    """MCP server type enumeration."""

    LOCAL = "local"
    REMOTE = "remote"


class MCPServerProtocol(str, Enum):
    SSE = "sse"
    HTTP = "http"


class LocalMCPServerConfig(BaseModel):
    """Configuration for local MCP servers using stdio transport."""

    server_type: Literal[MCPServerType.LOCAL] = MCPServerType.LOCAL
    command: list[str] = Field(..., description="Command to run the MCP server")
    args: list[str] = Field(
        default_factory=list, description="Additional arguments for the command"
    )
    environment: dict[str, str] = Field(
        default_factory=dict, description="Environment variables for the server"
    )
    cwd: str | None = Field(
        default=None, description="Working directory for the server process"
    )
    timeout: int = Field(
        default=5, description="Timeout in seconds for server initialization"
    )
    tool_prefix: str | None = Field(
        default=None, description="Prefix for tool names from this server"
    )

    @field_validator("command")
    @classmethod
    def validate_command(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("Command cannot be empty")
        return v


class RemoteMCPServerConfig(BaseModel):
    """Configuration for remote MCP servers using HTTP SSE transport."""

    server_type: Literal[MCPServerType.REMOTE] = MCPServerType.REMOTE
    url: str = Field(..., description="SSE endpoint URL for the MCP server")
    headers: dict[str, str] = Field(
        default_factory=dict, description="HTTP headers for authentication"
    )
    timeout: int = Field(default=5, description="Initial connection timeout in seconds")
    tool_prefix: str | None = Field(
        default=None, description="Prefix for tool names from this server"
    )
    protocol: MCPServerProtocol = Field(
        default=MCPServerProtocol.SSE, description="Protocol to use for communication"
    )

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        if not v.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        return v


MCPServerConfigUnion = Annotated[
    Union[LocalMCPServerConfig, RemoteMCPServerConfig],
    Field(discriminator="server_type"),
]


class MCPServersConfig(BaseModel):
    """Configuration for multiple MCP servers."""

    servers: dict[str, MCPServerConfigUnion] = Field(
        default_factory=dict, description="Named MCP server configurations"
    )

    def get_local_servers(self) -> dict[str, LocalMCPServerConfig]:
        """Get all local MCP server configurations."""
        return {
            name: config
            for name, config in self.servers.items()
            if config.server_type == MCPServerType.LOCAL
        }

    def get_remote_servers(self) -> dict[str, RemoteMCPServerConfig]:
        """Get all remote MCP server configurations."""
        return {
            name: config
            for name, config in self.servers.items()
            if config.server_type == MCPServerType.REMOTE
        }


def load_mcp_config_from_dict(config_data: dict[str, Any]) -> MCPServersConfig:
    """Load MCP configuration from a dictionary using Pydantic discriminated unions."""
    return MCPServersConfig.model_validate({"servers": config_data})
