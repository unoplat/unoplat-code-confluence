"""Worker-level service registry for non-serializable dependencies.

Activities (tools) access services via this registry rather than through
AgentDependencies, since deps must be Pydantic-serializable for Temporal.
"""

from pathlib import Path

from unoplat_code_confluence_query_engine.config.settings import EnvironmentSettings
from unoplat_code_confluence_query_engine.services.mcp.mcp_server_manager import (
    MCPServerManager,
)
from unoplat_code_confluence_query_engine.services.tracking.repository_agent_snapshot_service import (
    RepositoryAgentSnapshotWriter,
)


class ServiceRegistry:
    """Holds non-serializable services for activity access."""

    _instance: "ServiceRegistry | None" = None
    _initialized: bool = False

    def __init__(self) -> None:
        self._settings: EnvironmentSettings | None = None
        self._mcp_server_manager: MCPServerManager | None = None
        self._snapshot_writer: RepositoryAgentSnapshotWriter | None = None

    @classmethod
    def get_instance(cls) -> "ServiceRegistry":
        """Get or create singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def initialize(
        self,
        settings: EnvironmentSettings | None = None,
        mcp_config_path: str | Path | None = None,
    ) -> None:
        """Initialize services. Called by worker at startup.

        Args:
            settings: Optional environment settings. Uses defaults if not provided.
            mcp_config_path: Optional path to MCP servers config JSON file.
        """
        if self._initialized:
            return

        self._settings = settings or EnvironmentSettings()

        # Initialize MCP server manager
        self._mcp_server_manager = MCPServerManager()
        if mcp_config_path:
            await self._mcp_server_manager.load_config(mcp_config_path)

        # Initialize stateless snapshot writer
        self._snapshot_writer = RepositoryAgentSnapshotWriter()

        self._initialized = True

    async def shutdown(self) -> None:
        """Cleanup services. Called by worker at shutdown."""
        self._initialized = False

    @property
    def mcp_server_manager(self) -> MCPServerManager:
        """Get MCP server manager instance.

        Returns:
            Configured MCPServerManager instance.

        Raises:
            RuntimeError: If registry not initialized.
        """
        if not self._mcp_server_manager:
            raise RuntimeError("MCPServerManager not initialized")
        return self._mcp_server_manager

    @property
    def snapshot_writer(self) -> RepositoryAgentSnapshotWriter:
        """Get stateless RepositoryAgentSnapshotWriter instance.

        Returns:
            Stateless RepositoryAgentSnapshotWriter instance.

        Raises:
            RuntimeError: If service not initialized.
        """
        if not self._snapshot_writer:
            raise RuntimeError("RepositoryAgentSnapshotWriter not initialized")
        return self._snapshot_writer


def get_mcp_server_manager() -> MCPServerManager:
    """Get MCPServerManager from registry.

    Returns:
        MCPServerManager instance from the registry.
    """
    return ServiceRegistry.get_instance().mcp_server_manager


def get_snapshot_writer() -> RepositoryAgentSnapshotWriter:
    """Get stateless RepositoryAgentSnapshotWriter from registry.

    Returns:
        RepositoryAgentSnapshotWriter instance from the registry.
    """
    return ServiceRegistry.get_instance().snapshot_writer
