from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable

from pydantic_ai import Agent

from unoplat_code_confluence_query_engine.db.neo4j.connection_manager import (
    CodeConfluenceGraphQueryEngine,
)
from unoplat_code_confluence_query_engine.models.repository.repository_ruleset_metadata import (
    CodebaseMetadata,
)

if TYPE_CHECKING:
    from unoplat_code_confluence_query_engine.services.workflow.library_documentation_service import (
        LibraryDocumentationService,
    )


@dataclass
class AgentDependencies:
    """
    Dependencies for Pydantic AI agents following best practices.

    Service objects and external connections are stored here for
    efficient access during agent execution.
    """

    repository_qualified_name: str
    codebase_metadata: CodebaseMetadata
    neo4j_conn_manager: CodeConfluenceGraphQueryEngine
    # Use a factory so each tool call can create an isolated Context7 agent instance,
    # avoiding CancelScope leaks when tool calls run concurrently.
    context7_agent_factory: Callable[[], Agent]
    library_documentation_service: "LibraryDocumentationService"
