from dataclasses import dataclass
from typing import TYPE_CHECKING

from unoplat_code_confluence_query_engine.models.repository.repository_ruleset_metadata import (
    CodebaseMetadata,
)

if TYPE_CHECKING:
    pass


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
