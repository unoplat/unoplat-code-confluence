from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from unoplat_code_confluence_query_engine.models.repository.repository_ruleset_metadata import (
    CodebaseMetadata,
)

if TYPE_CHECKING:
    from pydantic_ai_backends import DockerSandbox


@dataclass
class AgentDependencies:
    """
    Dependencies for Pydantic AI agents following best practices.

    Service objects and external connections are stored here for
    efficient access during agent execution.
    """

    repository_qualified_name: str
    codebase_metadata: CodebaseMetadata
    repository_workflow_run_id: str
    agent_name: str

    @property
    def backend(self) -> DockerSandbox:
        """Resolve the live per-run Docker sandbox from ServiceRegistry."""
        from unoplat_code_confluence_query_engine.services.temporal.service_registry import (  # noqa: PLC0415
            ServiceRegistry,
        )

        return ServiceRegistry.get_instance().get_development_workflow_backend(
            workflow_run_id=self.repository_workflow_run_id,
            agent_name=self.agent_name,
            metadata=self.codebase_metadata,
        )
