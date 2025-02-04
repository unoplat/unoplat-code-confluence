
from src.code_confluence_flow_bridge.models.configuration.settings import (
    ProgrammingLanguageMetadata,
)
from src.code_confluence_flow_bridge.models.workflow.code_confluence_linter import (
    LinterType,
)
from src.code_confluence_flow_bridge.parser.linters.linter_factory import (
    LinterStrategyFactory,
)

from typing import List, Optional


class LinterParser:
    def lint_codebase(
        self,
        local_workspace_path: str,
        dependencies: Optional[List[str]],
        programming_language_metadata: ProgrammingLanguageMetadata
    ) -> bool:
        """
        Run linting on the codebase using appropriate linter strategy.

        Args:
            local_workspace_path: Path to the local workspace
            programming_language_metadata: Metadata about programming language
            programming_language_version: Version of programming language

        Returns:
            bool: True if linting was successful
        """
        
        
        # Select linter type based on programming language
        linter_type: LinterType
        if programming_language_metadata.language == "python":
            linter_type = LinterType.RUFF
        else:
            linter_type = LinterType.RUFF  # Default to Ruff for now
            
        linter_strategy = LinterStrategyFactory.get_strategy(
            programming_language=programming_language_metadata.language,
            linter_type=linter_type
        )
        return linter_strategy.lint_codebase(
            local_workspace_path=local_workspace_path,
            dependencies=dependencies,
            programming_language_version=programming_language_metadata.language_version #type: ignore
        ) 