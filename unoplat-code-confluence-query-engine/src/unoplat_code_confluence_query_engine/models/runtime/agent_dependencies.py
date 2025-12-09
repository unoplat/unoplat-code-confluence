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
    # neo4j_conn_manager: CodeConfluenceGraphQueryEngine
    # # Use a factory so each tool call can create an isolated Context7 agent instance,
    # # avoiding CancelScope leaks when tool calls run concurrently.
    # context7_agent_factory: Callable[[], Agent]
    # library_documentation_service: "LibraryDocumentationService"
