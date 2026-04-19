from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property

from pydantic_ai_backends.protocol import BackendProtocol

from unoplat_code_confluence_query_engine.models.repository.repository_ruleset_metadata import (
    CodebaseMetadata,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_backend_resolver import (
    release_agent_backend,
    resolve_agent_backend,
)


@dataclass
class AgentDependencies:
    """Dependencies for Pydantic AI agents following best practices.

    Service objects and external connections are stored here for
    efficient access during agent execution.

    The ``backend`` cached property lazily resolves the correct backend
    implementation (LocalBackend, DockerSandbox, etc.) based on
    ``agent_name``, satisfying the ``ConsoleDeps`` protocol that
    console toolsets require without storing backend state as a dataclass
    field that Pydantic would try to schema-generate.
    """

    repository_qualified_name: str
    codebase_metadata: CodebaseMetadata
    repository_workflow_run_id: str
    agent_name: str

    @cached_property
    def backend(self) -> BackendProtocol:
        return resolve_agent_backend(
            agent_name=self.agent_name,
            metadata=self.codebase_metadata,
            workflow_run_id=self.repository_workflow_run_id,
        )

    def release_backend(self) -> None:
        """Release the backend and clear the cached reference.

        Safe to call even if no backend was ever resolved.
        """
        if "backend" not in self.__dict__:
            return

        release_agent_backend(
            agent_name=self.agent_name,
            metadata=self.codebase_metadata,
            workflow_run_id=self.repository_workflow_run_id,
        )
        self.__dict__.pop("backend", None)
