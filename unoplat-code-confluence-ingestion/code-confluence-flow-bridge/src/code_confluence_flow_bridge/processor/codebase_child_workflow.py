from datetime import timedelta

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_package_manager_metadata import UnoplatPackageManagerMetadata
    from src.code_confluence_flow_bridge.models.configuration.settings import PackageManagerType, ProgrammingLanguage, ProgrammingLanguageMetadata
    from src.code_confluence_flow_bridge.processor.codebase_processing.codebase_processing_activity import CodebaseProcessingActivity
    from src.code_confluence_flow_bridge.processor.package_metadata_activity.package_manager_metadata_activity import PackageMetadataActivity
    from src.code_confluence_flow_bridge.processor.package_metadata_activity.package_manager_metadata_ingestion import PackageManagerMetadataIngestion


@workflow.defn(name="child-codebase-workflow")
class  CodebaseChildWorkflow:
    def __init__(self):
        self.package_metadata_activity = PackageMetadataActivity()

    @workflow.run
    async def run(self, repository_qualified_name: str, codebase_qualified_name: str, local_path: str, source_directory: str, package_manager_metadata: UnoplatPackageManagerMetadata) -> None:
        """Execute the codebase workflow"""
        workflow.logger.info(f"Starting codebase workflow for {codebase_qualified_name}")

        # 1. Parse package metadata
        workflow.logger.info(f"Creating programming language metadata for {package_manager_metadata.programming_language}")
        programming_language_metadata = ProgrammingLanguageMetadata(language=ProgrammingLanguage(package_manager_metadata.programming_language.lower()), package_manager=PackageManagerType(package_manager_metadata.package_manager.lower()), language_version=package_manager_metadata.programming_language_version)

        workflow.logger.info(f"Parsing package metadata for {codebase_qualified_name}")
        parsed_metadata: UnoplatPackageManagerMetadata = await workflow.execute_activity(activity=PackageMetadataActivity.get_package_metadata, args=[source_directory, programming_language_metadata], start_to_close_timeout=timedelta(minutes=10))

        # 2. Ingest package metadata into graph
        workflow.logger.info(f"Ingesting package metadata for {codebase_qualified_name} into graph")
        await workflow.execute_activity(activity=PackageManagerMetadataIngestion.insert_package_manager_metadata, args=[codebase_qualified_name, parsed_metadata], start_to_close_timeout=timedelta(minutes=10))
        
        programming_language_metadata.language_version = parsed_metadata.programming_language_version
         
        # 3. Process codebase (linting, AST generation, parsing)
        workflow.logger.info(f"Processing codebase for {codebase_qualified_name}")
        await workflow.execute_activity(
            activity=CodebaseProcessingActivity.process_codebase,
            args=[
                local_path,
                source_directory,
                repository_qualified_name,
                codebase_qualified_name,
                parsed_metadata.dependencies,
                programming_language_metadata
            ],
            start_to_close_timeout=timedelta(minutes=30)
        )

        workflow.logger.info(f"Codebase workflow completed successfully for {codebase_qualified_name}")
        
        
