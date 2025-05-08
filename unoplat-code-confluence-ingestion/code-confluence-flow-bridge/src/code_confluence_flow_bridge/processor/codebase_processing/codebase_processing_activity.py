from src.code_confluence_flow_bridge.logging.trace_utils import seed_and_bind_logger_from_trace_id
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_package import UnoplatPackage
from src.code_confluence_flow_bridge.models.workflow.repo_workflow_base import CodebaseProcessingActivityEnvelope
from src.code_confluence_flow_bridge.parser.codebase_parser import CodebaseParser
from src.code_confluence_flow_bridge.parser.linters.linter_parser import LinterParser
from src.code_confluence_flow_bridge.processor.archguard.arc_guard_handler import ArchGuardHandler
from src.code_confluence_flow_bridge.processor.db.graph_db.code_confluence_graph_ingestion import CodeConfluenceGraphIngestion

import os
import json
from typing import List

from temporalio import activity


class CodebaseProcessingActivity:
    """Activity for processing codebase through linting, AST generation and parsing."""
   
    def __init__(self, code_confluence_graph_ingestion: CodeConfluenceGraphIngestion):
        self.code_confluence_graph_ingestion = code_confluence_graph_ingestion

    @activity.defn
    async def process_codebase(
        self,
        envelope: CodebaseProcessingActivityEnvelope,
    ) -> None:
        """
        Process codebase through linting, AST generation, and parsing.

        Args:
            envelope: CodebaseProcessingActivityEnvelope containing parameters

        Returns:
            UnoplatCodebase: Parsed codebase data
        """
        # Extract parameters from envelope
        local_workspace_path = envelope.local_workspace_path
        source_directory = envelope.source_directory
        codebase_qualified_name = envelope.codebase_qualified_name
        programming_language_metadata = envelope.programming_language_metadata
        trace_id = envelope.trace_id
        
        info : activity.Info = activity.info()
        workflow_id = info.workflow_id
        workflow_run_id = info.workflow_run_id
        activity_id = info.activity_id
        log = seed_and_bind_logger_from_trace_id(trace_id, workflow_id, workflow_run_id, activity_id)
        
        log.info("Starting codebase processing")
        log.info("Programming language metadata: {}", programming_language_metadata.language.value)
        
        linter_parser = LinterParser()
        lint_result = linter_parser.lint_codebase(
            local_workspace_path=local_workspace_path,
            dependencies=[],
            programming_language_metadata=programming_language_metadata
        )
        
        if not lint_result:
            log.warning("Linting completed with warnings")
        else:
            log.info("Linting completed successfully")

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

        log.info("ArchGuard scan completed, JSON path: {}", chapi_json_path)

        # 3. Parse the codebase using CodebaseParser
        with open(chapi_json_path, 'r') as f:
            json_data = json.load(f)

        log.debug("Loaded AST JSON data, size {} bytes", len(json_data))

        parser = CodebaseParser()
        list_packages: List[UnoplatPackage] = parser.parse_codebase(
            codebase_name=codebase_qualified_name,
            json_data=json_data,
            local_workspace_path=local_workspace_path,
            source_directory=source_directory,
            programming_language_metadata=programming_language_metadata
        )
        
        log.debug("Parsed {} packages from codebase", len(list_packages))
        
        await self.code_confluence_graph_ingestion.insert_code_confluence_package(codebase_qualified_name=codebase_qualified_name, packages=list_packages)

        log.debug("Inserted {} packages into graph DB", len(list_packages))

        log.success("Completed codebase processing successfully")
        
