from datetime import timedelta

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_codebase import UnoplatCodebase
    from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_package_manager_metadata import UnoplatPackageManagerMetadata
    from src.code_confluence_flow_bridge.models.configuration.settings import PackageManagerType, ProgrammingLanguage, ProgrammingLanguageMetadata
    from src.code_confluence_flow_bridge.processor.package_metadata_activity.package_manager_metadata_activity import PackageMetadataActivity
    

@workflow.defn(name="child-codebase-workflow")
class CodebaseChildWorkflow:
    
    def __init__(self):
        self.package_metadata_activity = PackageMetadataActivity()
    
    @workflow.run
    async def run(self, unoplat_codebase: UnoplatCodebase) -> UnoplatCodebase:
        """
        Execute the repository activity workflow
        
        Args:
            repository_settings: Repository configuration
            app_settings: Application settings including GitHub token
            
        Returns:
            RepoActivityResult containing the processing outcome
        """
        programming_language_metadata = ProgrammingLanguageMetadata(
            language=ProgrammingLanguage(unoplat_codebase.package_manager_metadata.programming_language.lower()),
            package_manager=PackageManagerType(unoplat_codebase.package_manager_metadata.package_manager.lower()),
            language_version=unoplat_codebase.package_manager_metadata.programming_language_version
        )
        # Execute git activity with retry policy
        package_metadata: UnoplatPackageManagerMetadata = await workflow.execute_activity(
            activity=PackageMetadataActivity.run,
            args=(unoplat_codebase.local_path, programming_language_metadata),
            start_to_close_timeout=timedelta(minutes=10)
        )
        unoplat_codebase.package_manager_metadata = package_metadata
        
        return unoplat_codebase
