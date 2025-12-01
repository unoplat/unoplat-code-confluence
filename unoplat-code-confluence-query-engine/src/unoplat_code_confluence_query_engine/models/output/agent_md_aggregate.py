"""Agent metadata aggregator for building AgentMdOutput from multiple agent results."""

from typing import Optional

from loguru import logger

from unoplat_code_confluence_query_engine.models.output.agent_md_output import (
    AgentMdOutput,
    BusinessLogicDomain,
    DevelopmentWorkflow,
    ProgrammingLanguageMetadataOutput,
    ProjectConfiguration,
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
        self.project_configuration: Optional[ProjectConfiguration] = None
        # self.frameworks_libraries: Optional[list[FrameworkLibraryOutput]] = None
        self.development_workflow: Optional[DevelopmentWorkflow] = None
        self.business_logic: Optional[BusinessLogicDomain] = None

    def set_language_metadata(
        self, meta: Optional[ProgrammingLanguageMetadataOutput]
    ) -> None:
        """Set programming language metadata from Neo4j.

        Args:
            meta: Programming language metadata or None if not found
        """
        self.language_metadata = meta

    def update_from_project_configuration_agent(
        self, project_structure: ProjectConfiguration
    ) -> None:
        """Update project structure from project configuration agent result.

        Args:
            project_structure: ProjectConfiguration BaseModel from project configuration agent
        """
        self.project_configuration = project_structure
        logger.debug(
            "Updated project structure for codebase: {}", self.codebase.codebase_name
        )

    # def update_from_framework_explorer(self, frameworks: list[FrameworkLibraryOutput]) -> None:
    #     """Update frameworks and libraries from framework explorer agent result.

    #     Args:
    #         frameworks: List of FrameworkLibraryOutput BaseModels from framework explorer agent (post-processed)
    #     """
    #     self.frameworks_libraries = frameworks
    #     logger.debug("Updated frameworks/libraries for codebase: {}", self.codebase.codebase_name)

    def update_from_development_workflow(self, workflow: DevelopmentWorkflow) -> None:
        """Update development workflow from development workflow agent result.

        Args:
            workflow: DevelopmentWorkflow BaseModel from development workflow agent
        """
        self.development_workflow = workflow
        logger.debug(
            "Updated development workflow for codebase: {}", self.codebase.codebase_name
        )

    def update_from_business_logic(self, business_logic: BusinessLogicDomain) -> None:
        """Update business logic domain from business logic domain agent result.

        Args:
            business_logic: BusinessLogicDomain BaseModel from business logic domain agent (post-processed)
        """
        self.business_logic = business_logic
        logger.debug(
            "Updated business logic for codebase: {}", self.codebase.codebase_name
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
            project_configuration=self.project_configuration
            or ProjectConfiguration(config_files=[]),
            development_workflow=self.development_workflow
            or DevelopmentWorkflow(commands=[]),
            business_logic=self.business_logic
            or BusinessLogicDomain(
                description=f"Core business logic for {self.codebase.codebase_name} could not be performed due to an error",
                data_models=[],
            ),
        )
