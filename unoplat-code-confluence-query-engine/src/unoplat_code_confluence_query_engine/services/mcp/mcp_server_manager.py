"""
MCP Server Manager Service

Manages MCP servers using FastMCPToolset for local/remote transports.
"""

import json
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from loguru import logger
from pydantic_ai.toolsets.abstract import AbstractToolset
from pydantic_ai.toolsets.fastmcp import FastMCPToolset

from unoplat_code_confluence_query_engine.models.config.mcp_config import (
    LocalMCPServerConfig,
    MCPServerProtocol,
    MCPServersConfig,
    MCPServerType,
    RemoteMCPServerConfig,
    load_mcp_config_from_dict,
)

_SENSITIVE_QUERY_KEYS = {"exaApiKey", "api_key", "apikey", "token", "key"}


def _sanitize_url(url: str) -> str:
    parsed = urlparse(url)
    if not parsed.query:
        return url
    query = parse_qs(parsed.query, keep_blank_values=True)
    sanitized: dict[str, list[str]] = {}
    for key, values in query.items():
        if key in _SENSITIVE_QUERY_KEYS:
            sanitized[key] = ["***"]
        else:
            sanitized[key] = values
    return urlunparse(parsed._replace(query=urlencode(sanitized, doseq=True)))


class MCPServerManager:
    """Manages MCP server lifecycle using PydanticAI."""

    def __init__(self) -> None:
        self.config: MCPServersConfig | None = None

    async def load_config(self, config_path: str | Path) -> None:
        """Load MCP server configuration from JSON file."""
        config_file = Path(config_path).resolve()
        logger.debug("Loading MCP configuration from: {}", config_file)

        if not config_file.exists():
            logger.warning("MCP config file not found: {}", config_file)
            self.config = MCPServersConfig()
            return

        try:
            with config_file.open("r") as f:
                config_data = json.load(f)

            logger.debug("Raw MCP config data: {}", config_data)
            self.config = load_mcp_config_from_dict(config_data)
            logger.info(
                "Successfully loaded MCP configuration with {} servers",
                len(self.config.servers),
            )

            for name, server_config in self.config.servers.items():
                logger.debug(
                    "Configured MCP server '{}': {}", name, server_config.server_type
                )

        except Exception as e:
            logger.error("Failed to load MCP config from {}: {}", config_file, e)
            self.config = MCPServersConfig()

    def load_config_from_dict(self, config_data: dict[str, Any]) -> None:
        """Load MCP server configuration from dictionary."""
        try:
            logger.debug("Loading MCP config from dictionary: {}", config_data)
            self.config = load_mcp_config_from_dict(config_data)
            logger.info(
                "Successfully loaded MCP configuration from dict with {} servers",
                len(self.config.servers),
            )
        except Exception as e:
            logger.error("Failed to load MCP config from dictionary: {}", e)
            self.config = MCPServersConfig()

    def create_local_server_instance(
        self,
        name: str,
        config: LocalMCPServerConfig,
        *,
        id_override: str | None = None,
    ) -> AbstractToolset[Any]:
        """Create a local MCP server toolset via FastMCPToolset."""
        if not config.command:
            raise ValueError(f"Command is required for local server {name}")

        logger.debug(
            "Creating local MCP server '{}' with command: {}", name, config.command
        )

        # Use tool_prefix only when explicitly configured
        tool_prefix = config.tool_prefix if config.tool_prefix else None
        # Temporal requires stable toolset IDs; allow per-agent overrides.
        id_value = id_override or name

        try:
            # Build a FastMCP-compatible MCP config.
            stdio_config: dict[str, Any] = {
                "command": config.command[0],
                "args": config.command[1:] + config.args,
                "transport": "stdio",
                "timeout": config.timeout,
            }
            if config.environment:
                stdio_config["env"] = config.environment
            if config.cwd:
                stdio_config["cwd"] = config.cwd

            mcp_config = {"mcpServers": {name: stdio_config}}
            toolset: AbstractToolset[Any] = FastMCPToolset(mcp_config, id=id_value)

            # Apply tool prefix only when explicitly configured.
            if tool_prefix:
                toolset = toolset.prefixed(tool_prefix)

            logger.info(
                "Created local MCP toolset '{}' (id='{}') with command: {}",
                name,
                id_value,
                config.command[0],
            )
            logger.debug(
                "Local MCP toolset '{}' - timeout: {}s, env: {}, cwd: {}, tool_prefix: {}",
                name,
                config.timeout,
                config.environment,
                config.cwd,
                tool_prefix,
            )
            return toolset

        except Exception as e:
            logger.error("Failed to create local MCP toolset '{}': {}", name, e)
            raise

    def create_remote_server_instance(
        self,
        name: str,
        config: RemoteMCPServerConfig,
        *,
        id_override: str | None = None,
    ) -> AbstractToolset[Any]:
        """Create a remote MCP server toolset via FastMCPToolset."""
        logger.debug(
            "Creating remote MCP toolset '{}' with URL: {} (protocol: {})",
            name,
            _sanitize_url(config.url),
            config.protocol.value,
        )

        # Use tool_prefix only when explicitly configured
        tool_prefix = config.tool_prefix if config.tool_prefix else None
        # Temporal requires stable toolset IDs; allow per-agent overrides.
        id_value = id_override or name

        try:
            # Map protocol to FastMCP transport naming.
            transport = (
                "streamable-http"
                if config.protocol == MCPServerProtocol.HTTP
                else "sse"
            )

            remote_config: dict[str, Any] = {
                "url": config.url,
                "transport": transport,
                "timeout": config.timeout,
            }
            if config.headers:
                remote_config["headers"] = config.headers

            mcp_config = {"mcpServers": {name: remote_config}}
            toolset: AbstractToolset[Any] = FastMCPToolset(mcp_config, id=id_value)

            # Apply tool prefix only when explicitly configured.
            if tool_prefix:
                toolset = toolset.prefixed(tool_prefix)

            logger.info(
                "Created remote MCP toolset '{}' (id='{}') at URL: {} (protocol: {})",
                name,
                id_value,
                _sanitize_url(config.url),
                config.protocol.value,
            )
            logger.debug(
                "Remote MCP toolset '{}' - timeout: {}s, headers count: {}, tool_prefix: {}",
                name,
                config.timeout,
                len(config.headers) if config.headers else 0,
                tool_prefix,
            )
            return toolset

        except Exception as e:
            logger.error("Failed to create remote MCP toolset '{}': {}", name, e)
            raise

    def get_server_config(
        self, name: str
    ) -> LocalMCPServerConfig | RemoteMCPServerConfig | None:
        """Get configuration for a specific MCP server by name.

        Args:
            name: Name of the MCP server

        Returns:
            Server configuration if found, None otherwise
        """
        if not self.config:
            return None
        return self.config.servers.get(name)

    def has_server_config(self, name: str) -> bool:
        """Check if a server configuration exists.

        Args:
            name: Name of the MCP server

        Returns:
            True if configuration exists, False otherwise
        """
        return bool(self.get_server_config(name))

    def set_remote_server_query_param(
        self, name: str, param: str, value: str
    ) -> bool:
        """Update a remote server URL by setting a query parameter."""
        config = self.get_server_config(name)
        if not isinstance(config, RemoteMCPServerConfig):
            logger.warning(
                "Remote MCP server config not found for '{}'; cannot set query param",
                name,
            )
            return False

        parsed = urlparse(config.url)
        query = parse_qs(parsed.query, keep_blank_values=True)
        query[param] = [value]
        config.url = urlunparse(parsed._replace(query=urlencode(query, doseq=True)))
        logger.debug("Updated MCP server '{}' URL query param '{}'", name, param)
        return True

    def get_server_by_name(
        self, name: str, *, id_override: str | None = None
    ) -> AbstractToolset[Any] | None:
        """Create a new MCP toolset instance from configuration.

        IMPORTANT: Caller is responsible for managing the server lifecycle.
        For agents, the server lifecycle is automatically managed by PydanticAI
        through async context managers when used in agent toolsets.

        Args:
            name: Name of the MCP server

        Returns:
            New MCP toolset instance if configuration exists, None otherwise
        """
        config = self.get_server_config(name)
        if not config:
            logger.warning("No configuration found for MCP server '{}'", name)
            return None

        match config.server_type:
            case MCPServerType.LOCAL:
                return self.create_local_server_instance(
                    name, config, id_override=id_override
                )
            case MCPServerType.REMOTE:
                return self.create_remote_server_instance(
                    name, config, id_override=id_override
                )
