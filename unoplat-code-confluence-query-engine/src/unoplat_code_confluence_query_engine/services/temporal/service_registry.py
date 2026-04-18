"""Worker-level service registry for non-serializable dependencies.

Activities (tools) access services via this registry rather than through
AgentDependencies, since deps must be Pydantic-serializable for Temporal.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from loguru import logger
from pydantic_ai_backends import DockerSandbox, RuntimeConfig

from unoplat_code_confluence_query_engine.config.settings import EnvironmentSettings
from unoplat_code_confluence_query_engine.models.repository.repository_ruleset_metadata import (
    CodebaseMetadata,
)
from unoplat_code_confluence_query_engine.services.mcp.mcp_server_manager import (
    MCPServerManager,
)
from unoplat_code_confluence_query_engine.services.temporal.development_workflow_runtime import (
    resolve_development_workflow_repository_mounts,
    resolve_development_workflow_runtime,
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
        self._dev_workflow_backends: dict[str, DockerSandbox] = {}

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

    @staticmethod
    def _make_backend_key(
        workflow_run_id: str,
        agent_name: str,
        metadata: CodebaseMetadata,
    ) -> str:
        """Build a stable cache key for a per-run, per-codebase Docker sandbox."""
        codebase_hash = hashlib.sha1(metadata.codebase_path.encode()).hexdigest()[:12]
        return f"{workflow_run_id}:{agent_name}:{codebase_hash}"

    def _resolve_runtime(self, metadata: CodebaseMetadata) -> RuntimeConfig:
        """Resolve the Docker runtime for a development-workflow sandbox."""
        if not self._settings:
            raise RuntimeError("ServiceRegistry not initialized")
        return resolve_development_workflow_runtime(metadata, self._settings)

    @staticmethod
    def _resolve_repository_mounts(metadata: CodebaseMetadata) -> dict[str, str]:
        """Resolve the repository-scoped mount mapping for a sandbox."""
        return resolve_development_workflow_repository_mounts(metadata)

    def get_development_workflow_backend(
        self,
        *,
        workflow_run_id: str,
        agent_name: str,
        metadata: CodebaseMetadata,
    ) -> DockerSandbox:
        """Return (or create) an ephemeral Docker sandbox for a workflow run.

        The sandbox is cached by workflow run, agent name, and codebase path so
        repeated tool calls within the same codebase reuse the same container.
        Callers **must** invoke :meth:`release_development_workflow_backend`
        when the run completes.
        """
        if not self._settings:
            raise RuntimeError("ServiceRegistry not initialized")

        key = self._make_backend_key(workflow_run_id, agent_name, metadata)
        existing = self._dev_workflow_backends.get(key)
        if existing is not None:
            if existing.is_alive():
                return existing
            self.release_development_workflow_backend(
                workflow_run_id=workflow_run_id,
                agent_name=agent_name,
                metadata=metadata,
            )

        runtime = self._resolve_runtime(metadata)
        volumes = self._resolve_repository_mounts(metadata)
        backend = DockerSandbox(
            runtime=runtime,
            sandbox_id=key,
            idle_timeout=self._settings.dev_workflow_idle_timeout_seconds,
            network_mode=self._settings.dev_workflow_network_mode,
            volumes=volumes,
        )
        backend.start()
        self._dev_workflow_backends[key] = backend
        logger.info(
            "[service_registry] Created dev-workflow backend: key={}, runtime={}, work_dir={}, volumes={}",
            key,
            runtime.name,
            runtime.work_dir,
            volumes,
        )
        return backend

    def release_development_workflow_backend(
        self,
        workflow_run_id: str,
        agent_name: str,
        metadata: CodebaseMetadata,
    ) -> None:
        """Stop and remove the cached sandbox for a completed workflow run."""
        key = self._make_backend_key(workflow_run_id, agent_name, metadata)
        backend = self._dev_workflow_backends.pop(key, None)
        if backend is None:
            return
        try:
            backend.stop()
        except Exception:
            logger.opt(exception=True).warning(
                "[service_registry] Error stopping dev-workflow backend: key={}",
                key,
            )

    async def shutdown(self) -> None:
        """Cleanup services. Called by worker at shutdown."""
        # Stop all cached dev-workflow Docker sandboxes
        for key, backend in list(self._dev_workflow_backends.items()):
            try:
                backend.stop()
            except Exception:
                logger.opt(exception=True).warning(
                    "[service_registry] Error stopping dev-workflow backend during shutdown: key={}",
                    key,
                )
        self._dev_workflow_backends.clear()

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
