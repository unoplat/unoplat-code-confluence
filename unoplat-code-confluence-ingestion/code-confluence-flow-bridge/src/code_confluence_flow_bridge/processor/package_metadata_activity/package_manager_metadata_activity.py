# Standard Library

# Third Party
from loguru import logger
from temporalio import activity
from temporalio.exceptions import ApplicationError

# First Party
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_package_manager_metadata import UnoplatPackageManagerMetadata
from src.code_confluence_flow_bridge.models.configuration.settings import ProgrammingLanguageMetadata
from src.code_confluence_flow_bridge.parser.package_manager.package_manager_parser import PackageManagerParser


class PackageMetadataActivity:
    
    def __init__(self):
        self.package_manager_parser = PackageManagerParser()
    
    @activity.defn
    def run(self, local_path: str, programming_language_metadata: ProgrammingLanguageMetadata) -> UnoplatPackageManagerMetadata:
        """
        Process package manager specific metadata
        
        Args:
            local_path: Local path to the codebase
            programming_language_metadata: Programming language metadata
            
        Returns:
            UnoplatPackageManagerMetadata: Processed package manager metadata
        """
        try:
            info = activity.info()
            logger.info(
                "Processing package metadata",
                workflow_id=info.workflow_id,
                activity_id=info.activity_id,
                local_path=local_path,
                language=programming_language_metadata.language.value
            )
            
            package_metadata = self.package_manager_parser.parse_package_metadata(
                local_workspace_path=local_path,
                programming_language_metadata=programming_language_metadata
            )
            
            logger.success(
                "Successfully processed package metadata",
                workflow_id=info.workflow_id,
                activity_id=info.activity_id,
                local_path=local_path
            )
            return package_metadata
            
        except Exception as e:
            logger.error(
                "Failed to process package metadata",
                workflow_id=activity.info().workflow_id,
                activity_id=activity.info().activity_id,
                error=str(e),
                local_path=local_path
            )
            raise ApplicationError(
                message=f"Failed to process package metadata for {local_path}",
                type="PACKAGE_METADATA_ERROR"
            )
        
        
