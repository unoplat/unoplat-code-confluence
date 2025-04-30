# Standard Library

# Third Party
# First Party
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_package_manager_metadata import UnoplatPackageManagerMetadata
from src.code_confluence_flow_bridge.models.configuration.settings import ProgrammingLanguageMetadata
from src.code_confluence_flow_bridge.parser.package_manager.package_manager_parser import PackageManagerParser

from src.code_confluence_flow_bridge.logging.trace_utils import seed_and_bind_logger_from_trace_id
from temporalio import activity
from temporalio.exceptions import ApplicationError


class PackageMetadataActivity:
    def __init__(self):
        self.package_manager_parser = PackageManagerParser()

    @activity.defn
    def get_package_metadata(self, local_path: str, programming_language_metadata: ProgrammingLanguageMetadata, trace_id: str) -> UnoplatPackageManagerMetadata:
        """
        Process package manager specific metadata

        Args:
            local_path: Local path to the codebase
            programming_language_metadata: Programming language metadata

        Returns:
            UnoplatPackageManagerMetadata: Processed package manager metadata
        """
        # Bind Loguru logger with the passed trace_id
        log = seed_and_bind_logger_from_trace_id(trace_id)
        try:
            info = activity.info()
            log.debug(
                "Processing package metadata | workflow_id={} | activity_id={} | codebase_path={} | programming_language={} | language_version={} | package_manager={}",
                info.workflow_id, info.activity_id, local_path, programming_language_metadata.language.value, programming_language_metadata.language_version, programming_language_metadata.package_manager.value
            )

            package_metadata = self.package_manager_parser.parse_package_metadata(local_workspace_path=local_path, programming_language_metadata=programming_language_metadata)

            log.debug(
                "Successfully processed package metadata | workflow_id={} | activity_id={} | codebase_path={} | status=success",
                info.workflow_id, info.activity_id, local_path
            )
            return package_metadata

        except Exception as e:
            info = activity.info()
            log.debug(
                "Failed to process package metadata | workflow_id={} | activity_id={} | codebase_path={} | error_type={} | error_details={} | status=error",
                info.workflow_id, info.activity_id, local_path, type(e).__name__, str(e)
            )
            raise ApplicationError(message=f"Failed to process package metadata for {local_path}", type="PACKAGE_METADATA_ERROR")
