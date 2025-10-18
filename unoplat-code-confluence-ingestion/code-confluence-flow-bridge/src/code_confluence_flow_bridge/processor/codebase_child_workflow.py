from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from datetime import timedelta

    from unoplat_code_confluence_commons.programming_language_metadata import (
        PackageManagerType,
        ProgrammingLanguage,
        ProgrammingLanguageMetadata,
    )

    from src.code_confluence_flow_bridge.logging.trace_utils import (
        seed_and_bind_logger_from_trace_id,
    )
    from src.code_confluence_flow_bridge.models.code_confluence_parsing_models.unoplat_package_manager_metadata import (
        UnoplatPackageManagerMetadata,
    )
    from src.code_confluence_flow_bridge.models.workflow.repo_workflow_base import (
        CodebaseChildWorkflowEnvelope,
        CodebaseProcessingActivityEnvelope,
        PackageManagerMetadataIngestionEnvelope,
        PackageMetadataActivityEnvelope,
    )
    from src.code_confluence_flow_bridge.processor.activity_retries_config import (
        ActivityRetriesConfig,
    )
    from src.code_confluence_flow_bridge.processor.generic_codebase_processing_activity import (
        GenericCodebaseProcessingActivity,
    )
    from src.code_confluence_flow_bridge.processor.package_metadata_activity.package_manager_metadata_activity import (
        PackageMetadataActivity,
    )
    from src.code_confluence_flow_bridge.processor.package_metadata_activity.package_manager_metadata_ingestion import (
        PackageManagerMetadataIngestion,
    )


@workflow.defn(name="child-codebase-workflow")
class CodebaseChildWorkflow:

    @workflow.run
    async def run(
        self,
        envelope: CodebaseChildWorkflowEnvelope,
    ) -> None:
        """Execute the codebase workflow"""
        # Use envelope model
        
        # Extract parameters from envelope
        repository_qualified_name = envelope.repository_qualified_name
        codebase_qualified_name = envelope.codebase_qualified_name
        root_packages = envelope.root_packages
        codebase_path = envelope.codebase_path
        package_manager_metadata = envelope.package_manager_metadata
        trace_id = envelope.trace_id
    
        
        # Seed ContextVar and bind Loguru logger with trace_id
        info = workflow.info()
        workflow_id: str = info.workflow_id
        workflow_run_id: str = info.run_id
        log = seed_and_bind_logger_from_trace_id(
            trace_id=trace_id,
            workflow_id=workflow_id,
            workflow_run_id=workflow_run_id,
            codebase_local_path=codebase_path
        )

        log.info(f"Starting codebase workflow for {codebase_qualified_name}")
        
        # 1. Parse package metadata
        log.info(f"Creating programming language metadata for {package_manager_metadata.programming_language}")
        programming_language_metadata = ProgrammingLanguageMetadata(
            language=ProgrammingLanguage(package_manager_metadata.programming_language.lower()),
            package_manager=PackageManagerType(package_manager_metadata.package_manager.lower()),
            language_version=package_manager_metadata.programming_language_version,
        )

        log.info("Parsing package metadata")
        # Create PackageMetadataActivityEnvelope
        package_metadata_envelope = PackageMetadataActivityEnvelope(
            codebase_path=codebase_path,
            programming_language_metadata=programming_language_metadata,
            trace_id=trace_id
        )
        parsed_metadata: UnoplatPackageManagerMetadata = await workflow.execute_activity(
            activity=PackageMetadataActivity.get_package_metadata, 
            args=[package_metadata_envelope], 
            start_to_close_timeout=timedelta(minutes=10), 
            retry_policy=ActivityRetriesConfig.DEFAULT
        )

        # 2. Ingest package metadata into graph
        log.info("Ingesting package metadata into graph")
        # Create PackageManagerMetadataIngestionEnvelope
        package_manager_metadata_envelope = PackageManagerMetadataIngestionEnvelope(
            codebase_qualified_name=codebase_qualified_name,
            package_manager_metadata=parsed_metadata,
            trace_id=trace_id
        )
        await workflow.execute_activity(
            activity=PackageManagerMetadataIngestion.insert_package_manager_metadata, 
            args=[package_manager_metadata_envelope], 
            start_to_close_timeout=timedelta(minutes=10), 
            retry_policy=ActivityRetriesConfig.DEFAULT
        )
        
        programming_language_metadata.language_version = parsed_metadata.programming_language_version

        # 3. Process codebase with the generic parser (AST generation, parsing)
        log.info("Processing codebase using generic parser (AST generation and parsing)")

        codebase_processing_envelope = CodebaseProcessingActivityEnvelope(
            root_packages=root_packages,
            codebase_path=codebase_path,
            repository_qualified_name=repository_qualified_name,
            codebase_qualified_name=codebase_qualified_name,
            dependencies=list(parsed_metadata.dependencies.keys()),
            programming_language_metadata=programming_language_metadata,
            trace_id=trace_id,
        )

        await workflow.execute_activity(
            activity=GenericCodebaseProcessingActivity.process_codebase_generic,
            args=[codebase_processing_envelope],
            start_to_close_timeout=timedelta(weeks=1),
            retry_policy=ActivityRetriesConfig.DEFAULT,
        )

        log.info(f"Codebase workflow completed successfully for {codebase_qualified_name}")
        