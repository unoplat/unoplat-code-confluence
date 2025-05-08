# Standard Library

# Third Party
# First Party
from src.code_confluence_flow_bridge.logging.trace_utils import seed_and_bind_logger_from_trace_id
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_package_manager_metadata import UnoplatPackageManagerMetadata
from src.code_confluence_flow_bridge.models.workflow.repo_workflow_base import PackageMetadataActivityEnvelope
from src.code_confluence_flow_bridge.parser.package_manager.package_manager_parser import PackageManagerParser

from temporalio import activity
from temporalio.exceptions import ApplicationError


class PackageMetadataActivity:
    def __init__(self):
        self.package_manager_parser = PackageManagerParser()

    @activity.defn
    def get_package_metadata(self, envelope: PackageMetadataActivityEnvelope) -> UnoplatPackageManagerMetadata:
        """
        Process package manager specific metadata

        Args:
            local_path: Local path to the codebase
            programming_language_metadata: Programming language metadata

        Returns:
            UnoplatPackageManagerMetadata: Processed package manager metadata
        """
        # Extract parameters from envelope
        local_path = envelope.local_path
        programming_language_metadata = envelope.programming_language_metadata
        trace_id = envelope.trace_id
        
        # Bind Loguru logger with the passed trace_id
        info = activity.info()
        log = seed_and_bind_logger_from_trace_id(trace_id, info.workflow_id, info.workflow_run_id, info.activity_id)
        try:
            log.debug(
                "Processing package metadata | codebase_path={} | programming_language={} | language_version={} | package_manager={}",
                local_path, programming_language_metadata.language.value, programming_language_metadata.language_version, programming_language_metadata.package_manager.value
            )

            package_metadata = self.package_manager_parser.parse_package_metadata(local_workspace_path=local_path, programming_language_metadata=programming_language_metadata)

            log.debug(
                "Successfully processed package metadata | codebase_path={} | status=success",
                local_path
            )
            return package_metadata

        except Exception as e:
            log.debug(
                "Failed to process package metadata | codebase_path={} | error_type={} | error_details={} | status=error",
                local_path, type(e).__name__, str(e)
            )
            raise ApplicationError(message=f"Failed to process package metadata for {local_path}", type="PACKAGE_METADATA_ERROR")
