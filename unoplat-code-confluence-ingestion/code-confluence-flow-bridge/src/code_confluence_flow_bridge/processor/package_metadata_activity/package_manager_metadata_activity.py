# Standard Library

# Third Party
# First Party
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_package_manager_metadata import UnoplatPackageManagerMetadata
from src.code_confluence_flow_bridge.models.configuration.settings import ProgrammingLanguageMetadata
from src.code_confluence_flow_bridge.parser.package_manager.package_manager_parser import PackageManagerParser

from loguru import logger
from temporalio import activity
from temporalio.exceptions import ApplicationError


class PackageMetadataActivity:
    def __init__(self):
        self.package_manager_parser = PackageManagerParser()

    @activity.defn
    def get_package_metadata(self, local_path: str, programming_language_metadata: ProgrammingLanguageMetadata) -> UnoplatPackageManagerMetadata:
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
                extra={
                    "temporal_workflow_id": info.workflow_id,
                    "temporal_activity_id": info.activity_id,
                    "codebase_path": local_path,
                    "programming_language": programming_language_metadata.language.value,
                    "language_version": programming_language_metadata.language_version,
                    "package_manager": programming_language_metadata.package_manager.value,
                },
            )

            package_metadata = self.package_manager_parser.parse_package_metadata(local_workspace_path=local_path, programming_language_metadata=programming_language_metadata)

            logger.info("Successfully processed package metadata", extra={"temporal_workflow_id": info.workflow_id, "temporal_activity_id": info.activity_id, "codebase_path": local_path, "status": "success"})
            return package_metadata

        except Exception as e:
            logger.error("Failed to process package metadata", extra={"temporal_workflow_id": activity.info().workflow_id, "temporal_activity_id": activity.info().activity_id, "error_type": type(e).__name__, "error_details": str(e), "codebase_path": local_path, "status": "error"})
            raise ApplicationError(message=f"Failed to process package metadata for {local_path}", type="PACKAGE_METADATA_ERROR")
