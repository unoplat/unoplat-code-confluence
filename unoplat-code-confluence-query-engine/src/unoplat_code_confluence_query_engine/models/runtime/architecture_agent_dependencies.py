from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property

from pydantic_ai_backends.protocol import BackendProtocol

from unoplat_code_confluence_query_engine.services.temporal.agent_backend_resolver import (
    release_architecture_backend,
    resolve_architecture_backend,
)


@dataclass
class ArchitectureAgentDependencies:
    """Repository-scoped dependencies for the single Architecture agent run."""

    repository_qualified_name: str
    repository_root: str
    repository_workflow_run_id: str
    agent_name: str = "architecture"

    @cached_property
    def backend(self) -> BackendProtocol:
        return resolve_architecture_backend(self.repository_root)

    def release_backend(self) -> None:
        if "backend" not in self.__dict__:
            return
        release_architecture_backend(self.repository_root)
        self.__dict__.pop("backend", None)


def build_architecture_run_metadata(
    deps: ArchitectureAgentDependencies,
) -> dict[str, str]:
    return {
        "repository_qualified_name": deps.repository_qualified_name,
        "repository_workflow_run_id": deps.repository_workflow_run_id,
        "agent_name": deps.agent_name,
    }
