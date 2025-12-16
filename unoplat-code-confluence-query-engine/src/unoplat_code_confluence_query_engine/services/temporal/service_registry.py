"""Worker-level service registry for non-serializable dependencies.

Activities (tools) access services via this registry rather than through
AgentDependencies, since deps must be Pydantic-serializable for Temporal.
"""

from pathlib import Path

from pydantic import BaseModel, ConfigDict
from pydantic_ai import Agent
from pydantic_ai.models import Model
from pydantic_ai.settings import ModelSettings

from unoplat_code_confluence_query_engine.config.settings import EnvironmentSettings
from unoplat_code_confluence_query_engine.db.neo4j.connection_manager import (
    CodeConfluenceGraphQueryEngine,
)
from unoplat_code_confluence_query_engine.services.mcp.mcp_server_manager import (
    MCPServerManager,
)
from unoplat_code_confluence_query_engine.services.tracking.repository_agent_snapshot_service import (
    RepositoryAgentSnapshotWriter,
)
from unoplat_code_confluence_query_engine.services.workflow.library_documentation_service import (
    LibraryDocumentationService,
)


class Context7AgentConfig(BaseModel):
    """Configuration for creating plain Context7 Agent on-demand.

    Stores the parameters needed to build a fresh Context7 agent per call,
    avoiding shared MCPServer lifecycle issues under concurrency.

    We use plain Agent (NOT TemporalAgent) for Context7 because TemporalAgent
    wraps MCP operations (get_tools, call_tool) in separate activities, causing
    cancel scope conflicts when the MCP exit stack is closed in a different
    task than it was created. Plain Agent executes MCP calls directly within
    the calling activity's async context, keeping cancel scopes in the same task.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    model: Model
    mcp_server_name: str
    model_settings: ModelSettings | None = None


class ServiceRegistry:
    """Holds non-serializable services for activity access."""

    _instance: "ServiceRegistry | None" = None
    _initialized: bool = False

    def __init__(self) -> None:
        self._neo4j_manager: CodeConfluenceGraphQueryEngine | None = None
        self._settings: EnvironmentSettings | None = None
        self._mcp_server_manager: MCPServerManager | None = None
        self._context7_agent: Agent[None, str] | None = None
        self._context7_agent_config: Context7AgentConfig | None = None
        self._library_documentation_service: LibraryDocumentationService | None = None
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
        self._neo4j_manager = CodeConfluenceGraphQueryEngine(self._settings)
        await self._neo4j_manager.connect()

        # Initialize MCP server manager
        self._mcp_server_manager = MCPServerManager()
        if mcp_config_path:
            await self._mcp_server_manager.load_config(mcp_config_path)

        # Initialize LibraryDocumentationService
        self._library_documentation_service = LibraryDocumentationService()

        # Initialize stateless snapshot writer
        self._snapshot_writer = RepositoryAgentSnapshotWriter()

        self._initialized = True

    async def shutdown(self) -> None:
        """Cleanup services. Called by worker at shutdown."""
        if self._neo4j_manager:
            await self._neo4j_manager.close()
        self._initialized = False

    @property
    def neo4j_manager(self) -> CodeConfluenceGraphQueryEngine:
        """Get Neo4j manager instance.

        Returns:
            Configured CodeConfluenceGraphQueryEngine instance.

        Raises:
            RuntimeError: If registry not initialized.
        """
        if not self._neo4j_manager:
            raise RuntimeError(
                "ServiceRegistry not initialized. Call initialize() first."
            )
        return self._neo4j_manager

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
    def context7_agent(self) -> Agent[None, str]:
        """Get plain Context7 Agent instance (non-durable).

        Raises:
            RuntimeError: If agent not configured.
        """

        if not self._context7_agent:
            raise RuntimeError("Context7 Agent not configured")
        return self._context7_agent

    @context7_agent.setter
    def context7_agent(self, agent: Agent[None, str]) -> None:
        """Set plain Context7 Agent instance."""

        self._context7_agent = agent

    @property
    def context7_agent_config(self) -> Context7AgentConfig:
        """Get Context7 agent configuration for on-demand creation.

        Returns:
            Configuration for creating Context7 agents on-demand.

        Raises:
            RuntimeError: If configuration not set.
        """
        if not self._context7_agent_config:
            raise RuntimeError("Context7AgentConfig not configured")
        return self._context7_agent_config

    @context7_agent_config.setter
    def context7_agent_config(self, config: Context7AgentConfig) -> None:
        """Set Context7 agent configuration.

        Args:
            config: Configuration for creating Context7 agents on-demand.
        """
        self._context7_agent_config = config

    @property
    def library_documentation_service(self) -> LibraryDocumentationService:
        """Get LibraryDocumentationService instance.

        Returns:
            Configured LibraryDocumentationService instance.

        Raises:
            RuntimeError: If service not initialized.
        """
        if not self._library_documentation_service:
            raise RuntimeError("LibraryDocumentationService not initialized")
        return self._library_documentation_service

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


def get_neo4j_manager() -> CodeConfluenceGraphQueryEngine:
    """Get Neo4j manager from registry.

    Use in activity/tool functions to access the shared Neo4j connection.

    Returns:
        CodeConfluenceGraphQueryEngine instance from the registry.
    """
    return ServiceRegistry.get_instance().neo4j_manager


def get_mcp_server_manager() -> MCPServerManager:
    """Get MCPServerManager from registry.

    Returns:
        MCPServerManager instance from the registry.
    """
    return ServiceRegistry.get_instance().mcp_server_manager


def get_context7_agent() -> Agent[None, str]:
    """Get plain Context7 Agent from registry.

    Returns:
        Agent instance for Context7.
    """

    return ServiceRegistry.get_instance().context7_agent


def get_context7_agent_config() -> Context7AgentConfig:
    """Get Context7AgentConfig from registry.

    Returns:
        Configuration for creating Context7 agents on-demand.
    """
    return ServiceRegistry.get_instance().context7_agent_config


def get_library_documentation_service() -> LibraryDocumentationService:
    """Get LibraryDocumentationService from registry.

    Returns:
        LibraryDocumentationService instance from the registry.
    """
    return ServiceRegistry.get_instance().library_documentation_service


def get_snapshot_writer() -> RepositoryAgentSnapshotWriter:
    """Get stateless RepositoryAgentSnapshotWriter from registry.

    Returns:
        RepositoryAgentSnapshotWriter instance from the registry.
    """
    return ServiceRegistry.get_instance().snapshot_writer
