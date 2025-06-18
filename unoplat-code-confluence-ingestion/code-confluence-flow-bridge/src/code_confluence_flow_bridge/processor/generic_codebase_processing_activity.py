"""
Generic codebase processing activity for Temporal workflows.

This activity replaces the legacy CodebaseProcessingActivity with a new language-agnostic
approach that uses TreeSitterStructuralSignatureExtractor and optimized Neo4j streaming ingestion.
"""

from src.code_confluence_flow_bridge.logging.trace_utils import seed_and_bind_logger_from_trace_id
from src.code_confluence_flow_bridge.models.workflow.repo_workflow_base import CodebaseProcessingActivityEnvelope
from src.code_confluence_flow_bridge.parser.generic_codebase_parser import GenericCodebaseParser
from src.code_confluence_flow_bridge.parser.linters.linter_parser import LinterParser

import traceback

from temporalio import activity
from temporalio.exceptions import ApplicationError


class GenericCodebaseProcessingActivity:
    """
    New Temporal activity for processing codebases with streaming Neo4j insertion.
    
    Uses the revamped architecture with language-agnostic parsing and optimized
    batch operations for high-performance, memory-efficient processing.
    """

    def __init__(self):
        pass

    @activity.defn
    async def process_codebase_generic(self, envelope: CodebaseProcessingActivityEnvelope) -> None:
        """
        Process a codebase using the new generic parser with direct Neo4j insertion.
        
        Args:
            envelope: Activity envelope containing codebase processing parameters
            
        Raises:
            ApplicationError: If processing fails with full context for Temporal retry
        """
        # Extract parameters from envelope
        codebase_path = envelope.codebase_path
        codebase_qualified_name = envelope.codebase_qualified_name
        programming_language_metadata = envelope.programming_language_metadata
        trace_id = envelope.trace_id
        
        # Set up logger with trace context
        info = activity.info()
        workflow_id: str = info.workflow_id
        workflow_run_id: str = info.workflow_run_id
        activity_id: str = info.activity_id
        activity_name: str = info.activity_type
        log = seed_and_bind_logger_from_trace_id(
            trace_id=trace_id,
            workflow_id=workflow_id,
            workflow_run_id=workflow_run_id,
            activity_id=activity_id,
            activity_name=activity_name,
            codebase_local_path=codebase_path
        )
        
        try:
            log.info(
                "Starting generic codebase processing | codebase_qualified_name={} | codebase_path={} | programming_language={}",
                codebase_qualified_name, codebase_path, programming_language_metadata.language.value
            )

            # 1. Lint the codebase using existing LinterParser for consistency
            await self._lint_codebase(envelope, log)

            # 2. Process codebase with new parser (direct Neo4j insertion, no return)
            await self._process_codebase_with_parser(envelope, log)

            log.info(
                "Generic codebase processing completed successfully | codebase_qualified_name={}",
                codebase_qualified_name
            )

        except Exception as e:
            log.error(
                "Generic codebase processing failed | codebase_qualified_name={} | codebase_path={} | error={} | traceback={}",
                codebase_qualified_name, codebase_path, str(e), traceback.format_exc()
            )
            
            raise ApplicationError(
                f"Codebase processing failed for {codebase_qualified_name}",
                {
                    "trace_id": trace_id,
                    "codebase_qualified_name": codebase_qualified_name,
                    "codebase_path": codebase_path,
                    "repository_qualified_name": envelope.repository_qualified_name,
                    "programming_language": programming_language_metadata.language.value,
                    "error": str(e),
                    "activity_name": "process_codebase_generic",
                    "traceback": traceback.format_exc()
                }
            )

    async def _lint_codebase(self, envelope: CodebaseProcessingActivityEnvelope, log) -> None:
        """
        Lint the codebase using existing LinterParser for consistency.
        
        Args:
            envelope: Activity envelope with codebase parameters
        """
        try:
            log.info(
                "Starting linting for codebase | codebase_qualified_name={} | programming_language={}",
                envelope.codebase_qualified_name, envelope.programming_language_metadata.language.value
            )

            linter = LinterParser()
            lint_success = linter.lint_codebase(
                envelope.codebase_path,
                envelope.dependencies,
                envelope.programming_language_metadata
            )

            if lint_success:
                log.info(
                    "Linting completed successfully | codebase_qualified_name={}",
                    envelope.codebase_qualified_name
                )
            else:
                log.warning(
                    "Linting completed with issues | codebase_qualified_name={}",
                    envelope.codebase_qualified_name
                )

        except Exception as e:
            # Log warning but don't fail the entire processing
            log.warning(
                "Linting failed, continuing with parsing | codebase_qualified_name={} | error={}",
                envelope.codebase_qualified_name, str(e)
            )

    async def _process_codebase_with_parser(self, envelope: CodebaseProcessingActivityEnvelope, log) -> None:
        """
        Process codebase using GenericCodebaseParser with streaming Neo4j insertion.
        
        Args:
            envelope: Activity envelope with codebase parameters
        """
        try:
            log.info(
                "Starting generic parser processing | codebase_qualified_name={} | root_packages={} | programming_language={}",
                envelope.codebase_qualified_name, envelope.root_packages, envelope.programming_language_metadata.language.value
            )

            # Create parser instance
            parser = GenericCodebaseParser(
                codebase_name=envelope.codebase_qualified_name,
                codebase_path=envelope.codebase_path,
                root_packages=envelope.root_packages,
                programming_language_metadata=envelope.programming_language_metadata,
                trace_id=envelope.trace_id
            )

            # Process with transaction boundaries for consistency
            try:
                async with adb.transaction:
                    await parser.process_and_insert_codebase()
                    
                log.info(
                    "Parser processing completed successfully | codebase_qualified_name={} | files_processed={} | packages_created={} | neo4j_retries={}",
                    envelope.codebase_qualified_name, 
                    getattr(parser, 'files_processed', 0),
                    getattr(parser, 'packages_created', 0),
                    getattr(parser, 'neo4j_retries', 0)
                )
                
            except Exception as e:
                # Transaction rollback is handled automatically by neomodel
                log.error(
                    "Parser processing failed, transaction rolled back | codebase_qualified_name={} | error={} | files_processed={} | packages_created={} | neo4j_retries={}",
                    envelope.codebase_qualified_name, str(e),
                    getattr(parser, 'files_processed', 0) if 'parser' in locals() else 0,
                    getattr(parser, 'packages_created', 0) if 'parser' in locals() else 0,
                    getattr(parser, 'neo4j_retries', 0) if 'parser' in locals() else 0
                )
                raise

        except Exception as e:
            log.error(
                "Failed to initialize or run generic parser | codebase_qualified_name={} | error={}",
                envelope.codebase_qualified_name, str(e)
            )
            raise


# Activity instance for registration
generic_codebase_processing_activity = GenericCodebaseProcessingActivity()


# Export the activity function for Temporal worker registration
process_codebase_generic = generic_codebase_processing_activity.process_codebase_generic