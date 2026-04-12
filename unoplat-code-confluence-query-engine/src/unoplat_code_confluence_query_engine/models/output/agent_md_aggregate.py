"""Agent metadata aggregator for building AgentMdOutput from multiple agent results."""

from typing import Optional

from loguru import logger

from unoplat_code_confluence_query_engine.models.output.agent_md_output import (
    AgentMdOutput,
    BusinessLogicDomain,
    ProgrammingLanguageMetadataOutput,
)
from unoplat_code_confluence_query_engine.models.output.engineering_workflow_output import (
    EngineeringWorkflow,
)
from unoplat_code_confluence_query_engine.models.repository.repository_ruleset_metadata import (
    CodebaseMetadata,
)


class AgentMdAggregate:
    """Builder class to accumulate agent results and produce final AgentMdOutput."""

    def __init__(self, codebase: CodebaseMetadata) -> None:
        """Initialize aggregator for a specific codebase.

        Args:
            codebase: Codebase metadata containing name, path, and programming language
        """
        self.codebase = codebase
        self.language_metadata: Optional[ProgrammingLanguageMetadataOutput] = None
        self.engineering_workflow: Optional[EngineeringWorkflow] = None
        self.business_logic: Optional[BusinessLogicDomain] = None

    def set_language_metadata(
        self, meta: Optional[ProgrammingLanguageMetadataOutput]
    ) -> None:
        """Set programming language metadata from PostgreSQL.

        Args:
            meta: Programming language metadata or None if not found
        """
        self.language_metadata = meta

    def update_from_engineering_workflow(self, workflow: EngineeringWorkflow) -> None:
        """Update canonical engineering workflow from single workflow agent result."""
        self.engineering_workflow = workflow
        logger.debug(
            "Updated engineering workflow for codebase: {}", self.codebase.codebase_name
        )

    def update_from_business_logic(self, business_logic: BusinessLogicDomain) -> None:
        """Update business logic domain from business logic domain agent result.

        Args:
            business_logic: BusinessLogicDomain BaseModel from business logic domain agent (post-processed)
        """
        self.business_logic = business_logic
        logger.debug(
            f"Updated business logic for codebase: {self.codebase.codebase_name}"
        )

    def to_final_model(self) -> AgentMdOutput:
        """Build final AgentMdOutput with defaults for missing fields.

        Returns:
            Complete AgentMdOutput with all required fields populated
        """

        return AgentMdOutput(
            programming_language_metadata=self.language_metadata
            or ProgrammingLanguageMetadataOutput(
                primary_language=self.codebase.codebase_programming_language,
                package_manager="unknown",
            ),
            engineering_workflow=self.engineering_workflow or EngineeringWorkflow(),
            business_logic=self.business_logic
            or BusinessLogicDomain(
                description=f"Core business logic for {self.codebase.codebase_name} could not be performed due to an error",
                data_models=[],
            ),
        )
