"""Agent metadata aggregator for building AgentMdOutput from multiple agent results."""

from typing import Optional

from loguru import logger

from unoplat_code_confluence_query_engine.models.agent_md_output import (
    AgentMdOutput,
    BusinessLogicDomain,
    CodebaseMetadataOutput,
    CodebaseType,
    DevelopmentWorkflow,
    FrameworkLibraryOutput,
    PackageManagerOutput,
    ProgrammingLanguageMetadataOutput,
    ProjectStructure,
)
from unoplat_code_confluence_query_engine.models.repository_ruleset_metadata import (
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
        self.project_structure: Optional[ProjectStructure] = None
        self.frameworks_libraries: Optional[list[FrameworkLibraryOutput]] = None
        self.development_workflow: Optional[DevelopmentWorkflow] = None
        self.business_logic: Optional[BusinessLogicDomain] = None
    
    def set_language_metadata(self, meta: Optional[ProgrammingLanguageMetadataOutput]) -> None:
        """Set programming language metadata from Neo4j.
        
        Args:
            meta: Programming language metadata or None if not found
        """
        self.language_metadata = meta
    
    def update_from_directory_agent(self, project_structure: ProjectStructure) -> None:
        """Update project structure from directory agent result.
        
        Args:
            project_structure: ProjectStructure BaseModel from directory agent
        """
        self.project_structure = project_structure
        logger.debug("Updated project structure for codebase: {}", self.codebase.codebase_name)
    
    def update_from_framework_explorer(self, frameworks: list[FrameworkLibraryOutput]) -> None:
        """Update frameworks and libraries from framework explorer agent result.
        
        Args:
            frameworks: List of FrameworkLibraryOutput BaseModels from framework explorer agent (post-processed)
        """
        self.frameworks_libraries = frameworks
        logger.debug("Updated frameworks/libraries for codebase: {}", self.codebase.codebase_name)
    
    def update_from_development_workflow(self, workflow: DevelopmentWorkflow) -> None:
        """Update development workflow from development workflow agent result.
        
        Args:
            workflow: DevelopmentWorkflow BaseModel from development workflow agent
        """
        self.development_workflow = workflow
        logger.debug("Updated development workflow for codebase: {}", self.codebase.codebase_name)
    
    def update_from_business_logic(self, business_logic: BusinessLogicDomain) -> None:
        """Update business logic domain from business logic domain agent result.
        
        Args:
            business_logic: BusinessLogicDomain BaseModel from business logic domain agent (post-processed)
        """
        self.business_logic = business_logic
        logger.debug("Updated business logic for codebase: {}", self.codebase.codebase_name)
    
    def to_final_model(self) -> AgentMdOutput:
        """Build final AgentMdOutput with defaults for missing fields.
        
        Returns:
            Complete AgentMdOutput with all required fields populated
        """
        # Build codebase metadata with defaults
        codebase_metadata = CodebaseMetadataOutput(
            name=self.codebase.codebase_name,
            description=f"Codebase {self.codebase.codebase_name} at {self.codebase.codebase_path}",
            # TODO: Implement robust codebase_type detection
            codebase_type=CodebaseType.APPLICATION
        )
        
        # Use fetched language metadata or create default
        if self.language_metadata:
            programming_language_metadata = self.language_metadata
        else:
            # Create default with primary language from codebase metadata
            default_package_manager = PackageManagerOutput(package_type="unknown")
            programming_language_metadata = ProgrammingLanguageMetadataOutput(
                primary_language=self.codebase.codebase_programming_language,
                package_manager=default_package_manager,
                version_requirement=None
            )
        
        # Use parsed project structure or create default
        project_structure = self.project_structure or ProjectStructure(
            key_directories=[],
            config_files=[]
        )
        
        # Use parsed frameworks/libraries or default to empty list
        major_frameworks_and_libraries = self.frameworks_libraries or []
        
        # Use parsed development workflow or create default
        development_workflow = self.development_workflow or DevelopmentWorkflow(
            commands=[]
        )
        
        # Use parsed business logic or create default
        if self.business_logic:
            critical_business_logic = self.business_logic
        else:
            # Create default business logic domain
            critical_business_logic = BusinessLogicDomain(
                description=f"Core business logic for {self.codebase.codebase_name}",
                core_files=[]
            )
        
        return AgentMdOutput(
            codebase_metadata=codebase_metadata,
            programming_language_metadata=programming_language_metadata,
            project_structure=project_structure,
            major_frameworks_and_libraries=major_frameworks_and_libraries,
            development_workflow=development_workflow,
            critical_business_logic=critical_business_logic
        )