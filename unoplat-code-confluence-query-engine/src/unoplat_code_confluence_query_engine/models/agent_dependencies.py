from dataclasses import dataclass
from typing import TYPE_CHECKING

from pydantic_ai import Agent

from unoplat_code_confluence_query_engine.db.neo4j.connection_manager import (
    CodeConfluenceGraphQueryEngine,
)
from unoplat_code_confluence_query_engine.models.repository_ruleset_metadata import (
    CodebaseMetadata,
)

if TYPE_CHECKING:
    from unoplat_code_confluence_query_engine.services.library_documentation_service import (
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
    context7_agent: Agent
    library_documentation_service: "LibraryDocumentationService"
