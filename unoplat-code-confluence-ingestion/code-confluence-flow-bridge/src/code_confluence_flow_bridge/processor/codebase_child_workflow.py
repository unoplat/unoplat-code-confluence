from datetime import timedelta
from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_package_manager_metadata import UnoplatPackageManagerMetadata
    from src.code_confluence_flow_bridge.models.configuration.settings import PackageManagerType, ProgrammingLanguage, ProgrammingLanguageMetadata
    from src.code_confluence_flow_bridge.processor.package_metadata_activity.package_manager_metadata_activity import PackageMetadataActivity
    from src.code_confluence_flow_bridge.processor.package_metadata_activity.package_manager_metadata_ingestion import PackageManagerMetadataIngestion

@workflow.defn(name="child-codebase-workflow")
class CodebaseChildWorkflow:
    
    def __init__(self):
        self.package_metadata_activity = PackageMetadataActivity()
    
    @workflow.run
    async def run(
        self,
        repository_qualified_name: str,
        codebase_qualified_name: str,
        local_path: str,
        package_manager_metadata: UnoplatPackageManagerMetadata
    ) -> None:
        """Execute the codebase workflow"""
        
        # 1. Parse package metadata
        programming_language_metadata = ProgrammingLanguageMetadata(
            language=ProgrammingLanguage(package_manager_metadata.programming_language.lower()),
            package_manager=PackageManagerType(package_manager_metadata.package_manager.lower()),
            language_version=package_manager_metadata.programming_language_version
        )
        
        parsed_metadata: UnoplatPackageManagerMetadata = await workflow.execute_activity(
            activity=PackageMetadataActivity.get_package_metadata,
            args=[local_path, programming_language_metadata],
            start_to_close_timeout=timedelta(minutes=10)
        )
        
        # 2. Ingest package metadata into graph
        await workflow.execute_activity(
            activity=PackageManagerMetadataIngestion.insert_package_manager_metadata,
            args=[codebase_qualified_name, parsed_metadata],
            start_to_close_timeout=timedelta(minutes=10)
        )
