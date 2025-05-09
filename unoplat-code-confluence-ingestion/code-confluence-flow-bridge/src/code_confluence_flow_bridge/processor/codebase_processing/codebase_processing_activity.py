from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_package import UnoplatPackage
from src.code_confluence_flow_bridge.models.configuration.settings import ProgrammingLanguageMetadata
from src.code_confluence_flow_bridge.parser.codebase_parser import CodebaseParser
from src.code_confluence_flow_bridge.parser.linters.linter_parser import LinterParser
from src.code_confluence_flow_bridge.processor.archguard.arc_guard_handler import ArchGuardHandler
from src.code_confluence_flow_bridge.processor.db.graph_db.code_confluence_graph_ingestion import CodeConfluenceGraphIngestion

import os
import json
from typing import List, Optional

from loguru import logger
from temporalio import activity


class CodebaseProcessingActivity:
    """Activity for processing codebase through linting, AST generation and parsing."""
   
    def __init__(self, code_confluence_graph_ingestion: CodeConfluenceGraphIngestion):
        self.code_confluence_graph_ingestion = code_confluence_graph_ingestion

    @activity.defn
    async def process_codebase(
        self,
        local_workspace_path: str,
        source_directory: str,
        repository_qualified_name: str,
        codebase_qualified_name: str,
        dependencies: Optional[List[str]],
        programming_language_metadata: ProgrammingLanguageMetadata,
    ) -> None:
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
        log = logger.bind(codebase_qualified_name=codebase_qualified_name)
        log.info("Starting codebase processing")
        log.info("Programming language metadata: {}", programming_language_metadata.language.value)
        
        linter_parser = LinterParser()
        lint_result = linter_parser.lint_codebase(
            local_workspace_path=local_workspace_path,
            dependencies=[],
            programming_language_metadata=programming_language_metadata
        )
        
        if not lint_result:
            log.exception("Linting process completed with warnings")

        # 2. Generate AST using ArchGuard
        jar_env: str = os.getenv("SCANNER_JAR_PATH", "/app/jars/scanner_cli-2.2.8-all.jar")
        if jar_env:
            scanner_jar_path: str = jar_env
        
        log.debug(
            "Initializing ArchGuardHandler with args: jar_path='{}', language='{}', codebase_path='{}', codebase_name='{}', output_path='{}', extension='{}'",
            scanner_jar_path,
            programming_language_metadata.language.value,
            local_workspace_path,
            codebase_qualified_name,
            local_workspace_path,
            ".py"
        )
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
        
        await self.code_confluence_graph_ingestion.insert_code_confluence_package(codebase_qualified_name=codebase_qualified_name, packages=list_packages)

        log.info("Completed codebase processing")
        
