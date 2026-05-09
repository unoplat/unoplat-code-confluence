"""Single public entrypoint for agent backend acquisition and release.

All current agent backends resolve to local filesystem backends scoped to the
active repository. Readonly agents get inspection-only access; direct AGENTS.md
section owners get markdown-scoped editing for their owned sections, and the
development workflow agent also gets shell execution.
"""

from __future__ import annotations

from typing import Literal

from pydantic_ai_backends.backends.local import LocalBackend
from pydantic_ai_backends.permissions.types import PermissionRuleset
from pydantic_ai_backends.protocol import BackendProtocol
from pydantic_ai_backends.types import ExecuteResponse

from unoplat_code_confluence_query_engine.models.repository.repository_ruleset_metadata import (
    CodebaseMetadata,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.capabilities.readonly_console import (
    MARKDOWN_READ_WRITE_EXECUTE_RULESET,
    MARKDOWN_READ_WRITE_RULESET,
    READ_AND_EXECUTE_RULESET,
    READONLY_CONSOLE_RULESET,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_backend_paths import (
    resolve_repository_root,
    resolve_work_dir,
)

EXECUTE_TIMEOUT_SECONDS_CAP: int = 30


class ClampedTimeoutLocalBackend(LocalBackend):
    """LocalBackend variant that caps execute() timeout at 30 seconds.

    Upstream LocalBackend defaults to a 120-second subprocess timeout and will
    honor any caller-provided timeout. Allowed metadata/help executions for the
    development workflow agent must not be able to hang for two minutes or use
    an agent-supplied larger value, so we clamp every call to 30 seconds.
    """

    def execute(
        self, command: str, timeout: int | None = None
    ) -> ExecuteResponse:
        clamped = min(timeout or EXECUTE_TIMEOUT_SECONDS_CAP, EXECUTE_TIMEOUT_SECONDS_CAP)
        return super().execute(command, timeout=clamped)


AgentBackendKind = Literal[
    "readonly_local", "execute_local", "markdown_local", "markdown_execute_local"
]

_AGENT_BACKEND_KIND: dict[str, AgentBackendKind] = {
    "business_domain_guide": "markdown_local",
    "call_expression_validator": "readonly_local",
    "dependency_guide": "readonly_local",
    "dependency_guide_item": "readonly_local",
    "development_workflow_guide": "markdown_execute_local",
}


def _resolve_agent_backend_kind(agent_name: str) -> AgentBackendKind:
    """Look up the backend kind for *agent_name*; raise on unknown agents."""
    kind = _AGENT_BACKEND_KIND.get(agent_name)
    if kind is None:
        raise ValueError(f"No backend resolution strategy for agent '{agent_name}'")
    return kind


def _build_local_backend(
    metadata: CodebaseMetadata,
    *,
    enable_execute: bool,
    permissions: PermissionRuleset,
) -> LocalBackend:
    """Build a repository-scoped local backend with explicit permissions.

    When execute is enabled, return a ClampedTimeoutLocalBackend so that any
    permitted command runs under a hard 30-second timeout ceiling.
    """
    work_dir = resolve_work_dir(metadata)
    repository_root = resolve_repository_root(metadata)
    backend_cls = ClampedTimeoutLocalBackend if enable_execute else LocalBackend
    return backend_cls(
        root_dir=work_dir,
        allowed_directories=[repository_root],
        enable_execute=enable_execute,
        permissions=permissions,
        ask_fallback="deny",
    )


def resolve_agent_backend(
    *,
    agent_name: str,
    metadata: CodebaseMetadata,
    workflow_run_id: str,
) -> BackendProtocol:
    """Resolve the correct backend implementation for the given agent."""
    _ = workflow_run_id
    kind = _resolve_agent_backend_kind(agent_name)
    if kind == "readonly_local":
        return _build_local_backend(
            metadata,
            enable_execute=False,
            permissions=READONLY_CONSOLE_RULESET,
        )
    if kind == "execute_local":
        return _build_local_backend(
            metadata,
            enable_execute=True,
            permissions=READ_AND_EXECUTE_RULESET,
        )
    if kind == "markdown_execute_local":
        return _build_local_backend(
            metadata,
            enable_execute=True,
            permissions=MARKDOWN_READ_WRITE_EXECUTE_RULESET,
        )
    return _build_local_backend(
        metadata,
        enable_execute=False,
        permissions=MARKDOWN_READ_WRITE_RULESET,
    )


def release_agent_backend(
    *,
    agent_name: str,
    metadata: CodebaseMetadata,
    workflow_run_id: str,
) -> None:
    """Release the backend for the given agent.

    Local backends are process-local lightweight objects with no external
    lifecycle to tear down, so release is currently a no-op.
    """
    _ = (agent_name, metadata, workflow_run_id)


# Shared path helpers are re-exported from agent_backend_paths.
