"""Docker-only mutable backend lifecycle manager.

Owns the keyed cache of running ``DockerSandbox`` instances and exposes
a focused API for starting, reusing, releasing, and shutting down
sandboxes.  This module is deliberately backend-policy-free: it does
not know which agents receive Docker backends or how runtimes are
selected — that logic belongs in ``agent_backend_resolver`` and
``development_workflow_runtime`` respectively.
"""

from __future__ import annotations

import hashlib

from loguru import logger
from pydantic_ai_backends import DockerSandbox, RuntimeConfig

from unoplat_code_confluence_query_engine.config.settings import EnvironmentSettings
from unoplat_code_confluence_query_engine.models.repository.repository_ruleset_metadata import (
    CodebaseMetadata,
)


def make_backend_key(
    workflow_run_id: str,
    agent_name: str,
    metadata: CodebaseMetadata,
) -> str:
    """Build a stable cache key for a per-run, per-codebase Docker sandbox."""
    codebase_hash = hashlib.sha1(metadata.codebase_path.encode()).hexdigest()[:12]
    return f"{workflow_run_id}:{agent_name}:{codebase_hash}"


class AgentBackendLifecycle:
    """Singleton lifecycle manager for Docker sandbox backends."""

    _instance: AgentBackendLifecycle | None = None

    def __init__(self) -> None:
        self._settings: EnvironmentSettings | None = None
        self._backends: dict[str, DockerSandbox] = {}

    @classmethod
    def get_instance(cls) -> AgentBackendLifecycle:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def initialize(self, settings: EnvironmentSettings) -> None:
        """Store worker-level settings needed when constructing sandboxes.

        Safe to call more than once; subsequent calls are no-ops.
        """
        if self._settings is not None:
            return
        self._settings = settings

    @property
    def settings(self) -> EnvironmentSettings:
        """Validated access to the worker-level settings."""
        if self._settings is None:
            raise RuntimeError("AgentBackendLifecycle not initialized — call initialize() first")
        return self._settings

    def get_or_start_docker_backend(
        self,
        *,
        key: str,
        runtime: RuntimeConfig,
        volumes: dict[str, str],
    ) -> DockerSandbox:
        """Return a running sandbox for *key*, creating one if necessary.

        If a cached sandbox exists but is no longer alive it is released
        first and a fresh one is started.
        """
        settings = self.settings

        existing = self._backends.get(key)
        if existing is not None:
            if existing.is_alive():
                return existing
            self.release_backend(key=key)

        backend = DockerSandbox(
            runtime=runtime,
            sandbox_id=key,
            idle_timeout=settings.dev_workflow_idle_timeout_seconds,
            network_mode=settings.dev_workflow_network_mode,
            volumes=volumes,
        )
        backend.start()
        self._backends[key] = backend
        logger.info(
            "[agent_backend_lifecycle] Started Docker backend: key={}, runtime={}, work_dir={}, volumes={}",
            key,
            runtime.name,
            runtime.work_dir,
            volumes,
        )
        return backend

    def release_backend(self, *, key: str) -> None:
        """Stop and remove a single cached sandbox by key.  No-op if absent."""
        backend = self._backends.pop(key, None)
        if backend is None:
            return
        try:
            backend.stop()
        except Exception:
            logger.opt(exception=True).warning(
                "[agent_backend_lifecycle] Error stopping Docker backend: key={}",
                key,
            )

    def shutdown(self) -> None:
        """Stop all cached sandboxes.  Called during worker shutdown."""
        for key, backend in list(self._backends.items()):
            try:
                backend.stop()
            except Exception:
                logger.opt(exception=True).warning(
                    "[agent_backend_lifecycle] Error stopping Docker backend during shutdown: key={}",
                    key,
                )
        self._backends.clear()
        logger.info("[agent_backend_lifecycle] All Docker backends shut down")
