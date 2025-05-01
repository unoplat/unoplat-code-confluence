from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from src.code_confluence_flow_bridge.logging.trace_utils import seed_and_bind_logger_from_trace_id
    from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_package_manager_metadata import UnoplatPackageManagerMetadata
    from src.code_confluence_flow_bridge.models.configuration.settings import PackageManagerType, ProgrammingLanguage, ProgrammingLanguageMetadata
    from src.code_confluence_flow_bridge.processor.activity_retries_config import ActivityRetriesConfig
    from src.code_confluence_flow_bridge.processor.codebase_processing.codebase_processing_activity import CodebaseProcessingActivity
    from src.code_confluence_flow_bridge.processor.db.postgres.child_workflow_db_activity import ChildWorkflowDbActivity
    from src.code_confluence_flow_bridge.processor.package_metadata_activity.package_manager_metadata_activity import PackageMetadataActivity
    from src.code_confluence_flow_bridge.processor.package_metadata_activity.package_manager_metadata_ingestion import PackageManagerMetadataIngestion

    from datetime import timedelta


@workflow.defn(name="child-codebase-workflow")
class  CodebaseChildWorkflow:

    @workflow.run
    async def run(
        self,
        repository_qualified_name: str,
        codebase_qualified_name: str,
        local_path: str,
        source_directory: str,
        package_manager_metadata: UnoplatPackageManagerMetadata,
        trace_id: str,
        root_package: str,
    ) -> None:
        """Execute the codebase workflow"""
        # Seed ContextVar and bind Loguru logger with trace_id
        info = workflow.info()
        workflow_id = info.workflow_id
        workflow_run_id = info.run_id
        log = seed_and_bind_logger_from_trace_id(trace_id, workflow_id, workflow_run_id)

        log.info(f"Starting codebase workflow for {codebase_qualified_name}")
        
        # #TODO: repository_name: str,
        # repository_owner_name: str,
        # codebase_name: str,
        # workflow_id: str,
        # workflow_run_id: str,
        # trace_id: str
        
        repository_name, repository_owner_name = trace_id.split("__")
        
        await workflow.execute_activity(activity=ChildWorkflowDbActivity.update_codebase_workflow_status, args=[repository_name, repository_owner_name, root_package, workflow_id, workflow_run_id, trace_id], start_to_close_timeout=timedelta(minutes=10), retry_policy=ActivityRetriesConfig.DEFAULT) 
         
        # 1. Parse package metadata
        log.info(f"Creating programming language metadata for {package_manager_metadata.programming_language}")
        programming_language_metadata = ProgrammingLanguageMetadata(language=ProgrammingLanguage(package_manager_metadata.programming_language.lower()), package_manager=PackageManagerType(package_manager_metadata.package_manager.lower()), language_version=package_manager_metadata.programming_language_version)

        log.info("Parsing package metadata")
        parsed_metadata: UnoplatPackageManagerMetadata = await workflow.execute_activity(activity=PackageMetadataActivity.get_package_metadata, args=[source_directory, programming_language_metadata, trace_id], start_to_close_timeout=timedelta(minutes=10), retry_policy=ActivityRetriesConfig.DEFAULT)

        # 2. Ingest package metadata into graph
        log.info("Ingesting package metadata into graph")
        await workflow.execute_activity(activity=PackageManagerMetadataIngestion.insert_package_manager_metadata, args=[codebase_qualified_name, parsed_metadata, trace_id], start_to_close_timeout=timedelta(minutes=10), retry_policy=ActivityRetriesConfig.DEFAULT)
        
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
            start_to_close_timeout=timedelta(minutes=30),
            retry_policy=ActivityRetriesConfig.DEFAULT        
            )

        log.info(f"Codebase workflow completed successfully for {codebase_qualified_name}")
        