"""Single public entrypoint for agent backend acquisition and release.

Centralises backend-kind dispatch so that all agent-to-backend policy
is auditable in one mapping. Readonly/local agents are resolved
statelessly; Docker-backed agents delegate lifecycle operations to
``agent_backend_lifecycle`` and runtime selection to
``development_workflow_runtime``.

Shared path helpers are imported from ``agent_backend_paths`` and
re-exported here so callers can continue to use the resolver as the
public backend entrypoint without creating circular imports.
"""

from __future__ import annotations

from typing import Literal

from pydantic_ai_backends import DockerSandbox
from pydantic_ai_backends.backends.local import LocalBackend
from pydantic_ai_backends.permissions.presets import READONLY_RULESET
from pydantic_ai_backends.protocol import BackendProtocol

from unoplat_code_confluence_query_engine.models.repository.repository_ruleset_metadata import (
    CodebaseMetadata,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_backend_lifecycle import (
    AgentBackendLifecycle,
    make_backend_key,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_backend_paths import (
    resolve_repository_root,
    resolve_work_dir,
)
from unoplat_code_confluence_query_engine.services.temporal.development_workflow_runtime import (
    resolve_development_workflow_repository_mounts,
    resolve_development_workflow_runtime,
)

AgentBackendKind = Literal["readonly_local", "development_workflow_docker"]

_AGENT_BACKEND_KIND: dict[str, AgentBackendKind] = {
    "business_domain_guide": "readonly_local",
    "development_workflow_guide": "development_workflow_docker",
}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _resolve_agent_backend_kind(agent_name: str) -> AgentBackendKind:
    """Look up the backend kind for *agent_name*; raise on unknown agents."""
    kind = _AGENT_BACKEND_KIND.get(agent_name)
    if kind is None:
        raise ValueError(f"No backend resolution strategy for agent '{agent_name}'")
    return kind


def _build_readonly_local_backend(metadata: CodebaseMetadata) -> LocalBackend:
    """Build a read-only local-filesystem backend scoped to the repository."""
    work_dir = resolve_work_dir(metadata)
    repository_root = resolve_repository_root(metadata)
    return LocalBackend(
        root_dir=work_dir,
        allowed_directories=[repository_root],
        enable_execute=False,
        permissions=READONLY_RULESET,
    )


def _resolve_development_workflow_backend(
    *,
    agent_name: str,
    metadata: CodebaseMetadata,
    workflow_run_id: str,
) -> DockerSandbox:
    """Build or reuse a Docker sandbox for development-workflow agents."""
    lifecycle = AgentBackendLifecycle.get_instance()

    key = make_backend_key(workflow_run_id, agent_name, metadata)
    runtime = resolve_development_workflow_runtime(metadata, lifecycle.settings)
    volumes = resolve_development_workflow_repository_mounts(metadata)
    return lifecycle.get_or_start_docker_backend(
        key=key,
        runtime=runtime,
        volumes=volumes,
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def resolve_agent_backend(
    *,
    agent_name: str,
    metadata: CodebaseMetadata,
    workflow_run_id: str,
) -> BackendProtocol:
    """Resolve the correct backend implementation for the given agent.

    Business-domain agents get a read-only local backend.
    Development-workflow agents get a Docker sandbox via the lifecycle
    manager.  Unknown agents raise ``ValueError``.
    """
    kind = _resolve_agent_backend_kind(agent_name)
    if kind == "readonly_local":
        return _build_readonly_local_backend(metadata)
    return _resolve_development_workflow_backend(
        agent_name=agent_name,
        metadata=metadata,
        workflow_run_id=workflow_run_id,
    )


def release_agent_backend(
    *,
    agent_name: str,
    metadata: CodebaseMetadata,
    workflow_run_id: str,
) -> None:
    """Release the backend for the given agent.

    No-op for readonly local backends.  Stops and removes the Docker
    sandbox for development-workflow backends.
    """
    key = make_backend_key(workflow_run_id, agent_name, metadata)
    AgentBackendLifecycle.get_instance().release_backend(key=key)


# Shared path helpers are re-exported from agent_backend_paths.
