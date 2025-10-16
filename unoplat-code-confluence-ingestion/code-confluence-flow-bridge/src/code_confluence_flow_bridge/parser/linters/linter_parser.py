
from typing import Dict, List, Optional

from loguru import logger
from unoplat_code_confluence_commons.programming_language_metadata import (
    ProgrammingLanguage,
    ProgrammingLanguageMetadata,
)

from src.code_confluence_flow_bridge.models.workflow.code_confluence_linter import (
    LinterType,
)
from src.code_confluence_flow_bridge.parser.linters.linter_factory import (
    LinterStrategyFactory,
)

# Centralized mapping of programming languages to their default linters
# TODO: Add TypeScript → ESLint mapping when TypeScript linting support is implemented
# TODO: Add Java → Checkstyle/SpotBugs mapping for future Java support
# TODO: Add Go → golangci-lint mapping for future Go support
DEFAULT_LINTER_BY_LANGUAGE: Dict[ProgrammingLanguage, LinterType] = {
    ProgrammingLanguage.PYTHON: LinterType.RUFF,
}


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
            dependencies: List of dependencies
            programming_language_metadata: Metadata about programming language

        Returns:
            bool: True if linting was successful, False if linting was skipped
        """
        # Look up linter type from centralized mapping
        linter_type = DEFAULT_LINTER_BY_LANGUAGE.get(programming_language_metadata.language)

        if linter_type is None:
            # No linter configured for this language - skip linting
            logger.warning(
                "No linter configured for language={}, skipping linting",
                programming_language_metadata.language.value
            )
            return False

        # Get linter strategy from factory (may raise UnsupportedLinterError)
        linter_strategy = LinterStrategyFactory.get_strategy(
            programming_language=programming_language_metadata.language,
            linter_type=linter_type
        )

        return linter_strategy.lint_codebase(
            local_workspace_path=local_workspace_path,
            dependencies=dependencies,
            programming_language_version=programming_language_metadata.language_version #type: ignore
        ) 