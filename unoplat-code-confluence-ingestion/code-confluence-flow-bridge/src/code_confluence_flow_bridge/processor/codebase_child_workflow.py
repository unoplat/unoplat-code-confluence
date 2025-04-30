from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_package_manager_metadata import UnoplatPackageManagerMetadata
    from src.code_confluence_flow_bridge.models.configuration.settings import PackageManagerType, ProgrammingLanguage, ProgrammingLanguageMetadata
    from src.code_confluence_flow_bridge.processor.codebase_processing.codebase_processing_activity import CodebaseProcessingActivity
    from src.code_confluence_flow_bridge.processor.package_metadata_activity.package_manager_metadata_activity import PackageMetadataActivity
    from src.code_confluence_flow_bridge.processor.package_metadata_activity.package_manager_metadata_ingestion import PackageManagerMetadataIngestion

    from loguru import logger
    from src.code_confluence_flow_bridge.logging.trace_utils import seed_and_bind_logger_from_trace_id

    from datetime import timedelta

    
    


@workflow.defn(name="child-codebase-workflow")
class  CodebaseChildWorkflow:
    def __init__(self):
        self.package_metadata_activity = PackageMetadataActivity()

    @workflow.run
    async def run(
        self,
        repository_qualified_name: str,
        codebase_qualified_name: str,
        local_path: str,
        source_directory: str,
        package_manager_metadata: UnoplatPackageManagerMetadata,
        trace_id: str,
    ) -> None:
        """Execute the codebase workflow"""
        # Seed ContextVar and bind Loguru logger with trace_id
        log = seed_and_bind_logger_from_trace_id(trace_id)

        log.info(f"Starting codebase workflow for {codebase_qualified_name}")

        # 1. Parse package metadata
        log.info(f"Creating programming language metadata for {package_manager_metadata.programming_language}")
        programming_language_metadata = ProgrammingLanguageMetadata(language=ProgrammingLanguage(package_manager_metadata.programming_language.lower()), package_manager=PackageManagerType(package_manager_metadata.package_manager.lower()), language_version=package_manager_metadata.programming_language_version)

        log.info("Parsing package metadata")
        parsed_metadata: UnoplatPackageManagerMetadata = await workflow.execute_activity(activity=PackageMetadataActivity.get_package_metadata, args=[source_directory, programming_language_metadata, trace_id], start_to_close_timeout=timedelta(minutes=10))

        # 2. Ingest package metadata into graph
        log.info("Ingesting package metadata into graph")
        await workflow.execute_activity(activity=PackageManagerMetadataIngestion.insert_package_manager_metadata, args=[codebase_qualified_name, parsed_metadata, trace_id], start_to_close_timeout=timedelta(minutes=10))
        
        programming_language_metadata.language_version = parsed_metadata.programming_language_version
         
        # 3. Process codebase (linting, AST generation, parsing)
        log.info("Processing codebase")
        log.debug(
            "Starting codebase processing with args: local_path='{}', source_directory='{}', repository_qualified_name='{}', codebase_qualified_name='{}', dependencies={}, programming_language_metadata={}",
            local_path,
            source_directory,
            repository_qualified_name,
            codebase_qualified_name,
            parsed_metadata.dependencies,
            programming_language_metadata
        )
        await workflow.execute_activity(
            activity=CodebaseProcessingActivity.process_codebase,
            args=[
                local_path,
                source_directory,
                repository_qualified_name,
                codebase_qualified_name,
                parsed_metadata.dependencies,
                programming_language_metadata,
                trace_id,
            ],
            start_to_close_timeout=timedelta(minutes=30)
        )

        log.info(f"Codebase workflow completed successfully for {codebase_qualified_name}")
        
        
