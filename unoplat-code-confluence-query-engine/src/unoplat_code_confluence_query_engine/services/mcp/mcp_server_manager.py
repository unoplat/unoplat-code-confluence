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
        self.servers: dict[str, MCPServerStdio | MCPServerSSE] = {}
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

    def _create_local_server(
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

    def _create_remote_server(
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

    async def start_servers(self) -> None:
        """Start all configured MCP servers."""
        if not self.config:
            logger.warning("No MCP configuration loaded")
            return

        logger.info("Starting {} MCP servers", len(self.config.servers))

        for name, server_config in self.config.servers.items():
            try:
                # Use discriminator field instead of isinstance
                match server_config.server_type:
                    case MCPServerType.LOCAL:
                        server = self._create_local_server(name, server_config)
                    case MCPServerType.REMOTE:
                        server = self._create_remote_server(name, server_config)
                    case _:
                        logger.error(
                            "Unknown server type for '{}': {}",
                            name,
                            server_config.server_type,
                        )
                        continue

                self.servers[name] = server
                logger.info("Started MCP server '{}'", name)

            except Exception as e:
                logger.error("Failed to start MCP server '{}': {}", name, e)

    async def stop_servers(self) -> None:
        """Stop all MCP servers."""
        if not self.servers:
            logger.debug("No MCP servers to stop")
            return

        logger.info("Stopping {} MCP servers", len(self.servers))

        for name in list(self.servers.keys()):
            try:
                # MCP servers are managed via context managers in PydanticAI
                # Cleanup happens automatically when the server instances are destroyed
                logger.info("Stopped MCP server '{}'", name)
            except Exception as e:
                logger.error("Error stopping MCP server '{}': {}", name, e)

        self.servers.clear()

    def get_servers(self) -> list[MCPServerStdio | MCPServerSSE]:
        """Get list of all active MCP servers for agent integration."""
        return list(self.servers.values())

    def get_server_by_name(self, name: str) -> MCPServerStdio | MCPServerSSE | None:
        """Get a specific MCP server by name."""
        return self.servers.get(name)
