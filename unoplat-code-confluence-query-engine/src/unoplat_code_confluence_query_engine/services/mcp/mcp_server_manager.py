"""
MCP Server Manager Service

Manages the lifecycle of MCP servers using PydanticAI's MCPServerStdio and MCPServerHTTP.
"""

import json
from pathlib import Path
from typing import Any

from loguru import logger
from pydantic_ai.mcp import MCPServerSSE, MCPServerStdio

from unoplat_code_confluence_query_engine.models.mcp_config import (
    LocalMCPServerConfig,
    MCPServersConfig,
    MCPServerType,
    RemoteMCPServerConfig,
    load_mcp_config_from_dict,
)


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
        self, name: str, config: LocalMCPServerConfig
    ) -> MCPServerStdio:
        """Create a local MCP server instance."""
        if not config.command:
            raise ValueError(f"Command is required for local server {name}")

        logger.debug(
            "Creating local MCP server '{}' with command: {}", name, config.command
        )

        # Use tool_prefix if provided, otherwise use server name
        tool_prefix = config.tool_prefix or name

        try:
            server = MCPServerStdio(
                command=config.command[0],
                args=config.command[1:] + config.args,
                env=config.environment if config.environment else None,
                cwd=config.cwd,
                timeout=config.timeout,
                tool_prefix=tool_prefix,
            )

            logger.info(
                "Successfully created local MCP server '{}' with command: {}",
                name,
                config.command,
            )
            logger.debug(
                "Local MCP server '{}' - timeout: {}s, env: {}, cwd: {}",
                name,
                config.timeout,
                config.environment,
                config.cwd,
            )
            return server

        except Exception as e:
            logger.error("Failed to create local MCP server '{}': {}", name, e)
            raise

    def create_remote_server_instance(
        self, name: str, config: RemoteMCPServerConfig
    ) -> MCPServerSSE:
        """Create a remote MCP server instance."""
        logger.debug("Creating remote MCP server '{}' with URL: {}", name, config.url)

        # Use tool_prefix if provided, otherwise use server name
        tool_prefix = config.tool_prefix or name

        try:
            server = MCPServerSSE(
                url=config.url,
                headers=config.headers if config.headers else None,
                timeout=config.timeout,
                tool_prefix=tool_prefix,
            )

            logger.info(
                "Successfully created remote MCP server '{}' at URL: {}",
                name,
                config.url,
            )
            logger.debug(
                "Remote MCP server '{}' - timeout: {}s, headers count: {}",
                name,
                config.timeout,
                len(config.headers) if config.headers else 0,
            )
            return server

        except Exception as e:
            logger.error("Failed to create remote MCP server '{}': {}", name, e)
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

    def get_server_by_name(self, name: str) -> MCPServerStdio | MCPServerSSE | None:
        """Create a new MCP server instance from configuration.

        IMPORTANT: Caller is responsible for managing the server lifecycle.
        For agents, the server lifecycle is automatically managed by PydanticAI
        through async context managers when used in agent toolsets.

        Args:
            name: Name of the MCP server

        Returns:
            New MCP server instance if configuration exists, None otherwise
        """
        config = self.get_server_config(name)
        if not config:
            logger.warning("No configuration found for MCP server '{}'", name)
            return None

        match config.server_type:
            case MCPServerType.LOCAL:
                return self.create_local_server_instance(name, config)
            case MCPServerType.REMOTE:
                return self.create_remote_server_instance(name, config)
            case _:
                logger.error(
                    "Unknown server type for '{}': {}", name, config.server_type
                )
                return None
