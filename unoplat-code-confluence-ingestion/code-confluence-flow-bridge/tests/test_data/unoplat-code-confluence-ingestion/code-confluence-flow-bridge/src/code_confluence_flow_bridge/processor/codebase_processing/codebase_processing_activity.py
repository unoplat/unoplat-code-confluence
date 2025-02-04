from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_package import (
    UnoplatPackage,
)
from src.code_confluence_flow_bridge.models.configuration.settings import (
    ProgrammingLanguageMetadata,
)
from src.code_confluence_flow_bridge.parser.codebase_parser import CodebaseParser
from src.code_confluence_flow_bridge.parser.linters.linter_parser import LinterParser
from src.code_confluence_flow_bridge.processor.archguard.arc_guard_handler import (
    ArchGuardHandler,
)

import json
from pathlib import Path
from typing import List, Optional

from temporalio import activity


class CodebaseProcessingActivity:
    """Activity for processing codebase through linting, AST generation and parsing."""

    @activity.defn  
    async def process_codebase(
        self,
        local_workspace_path: str,
        source_directory: str,
        repository_qualified_name: str,
        codebase_qualified_name: str,
        dependencies: Optional[List[str]],
        programming_language_metadata: ProgrammingLanguageMetadata,
    ) -> List[UnoplatPackage]:
        """
        Process codebase through linting, AST generation, and parsing.

        Args:
            local_workspace_path: Path to the local workspace
            codebase_name: Name of the codebase
            dependencies: List of project dependencies
            programming_language_metadata: Metadata about the programming language

        Returns:
            UnoplatCodebase: Parsed codebase data
        """
        activity.logger.info(f"Starting codebase processing for {codebase_qualified_name}")

        
        linter_parser = LinterParser()
        lint_result = linter_parser.lint_codebase(
            local_workspace_path=local_workspace_path,
            dependencies=[],
            programming_language_metadata=programming_language_metadata
        )
        
        if not lint_result:
            activity.logger.exception("Linting process completed with warnings")

        # 2. Generate AST using ArchGuard
        scanner_jar_path = str(Path(__file__).parent.parent.parent.parent.parent / "assets" / "scanner_cli-2.2.8-all.jar")
        
        arch_guard = ArchGuardHandler(
            jar_path=scanner_jar_path,
            language=programming_language_metadata.language.value,
            codebase_path=local_workspace_path,
            codebase_name=codebase_qualified_name,
            output_path=local_workspace_path,
            extension=".py"  # For Python files
        )
        
        chapi_json_path = arch_guard.run_scan()

        # 3. Parse the codebase using CodebaseParser
        with open(chapi_json_path, 'r') as f:
            json_data = json.load(f)

        parser = CodebaseParser()
        list_packages: List[UnoplatPackage] = parser.parse_codebase(
            codebase_name=codebase_qualified_name,
            json_data=json_data,
            local_workspace_path=local_workspace_path,
            source_directory=source_directory,
            programming_language_metadata=programming_language_metadata
        )

        activity.logger.info(f"Completed codebase processing for {codebase_qualified_name}")
        return list_packages 
