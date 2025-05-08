from src.code_confluence_flow_bridge.logging.trace_utils import seed_and_bind_logger_from_trace_id
from src.code_confluence_flow_bridge.models.workflow.repo_workflow_base import PackageManagerMetadataIngestionEnvelope
from src.code_confluence_flow_bridge.processor.db.graph_db.code_confluence_graph_ingestion import CodeConfluenceGraphIngestion

from temporalio import activity
from temporalio.exceptions import ApplicationError


class PackageManagerMetadataIngestion:
    """
    Temporal activity class for package manager metadata ingestion
    """

    def __init__(self, code_confluence_graph_ingestion: CodeConfluenceGraphIngestion):
        self.code_confluence_graph_ingestion = code_confluence_graph_ingestion

    @activity.defn
    async def insert_package_manager_metadata(self, envelope: PackageManagerMetadataIngestionEnvelope) -> None:
        """
        Insert package manager metadata into graph database

        Args:
            codebase_qualified_name: Qualified name of the codebase
            package_manager_metadata: Package manager metadata to insert
        """
        # Extract parameters from envelope
        codebase_qualified_name = envelope.codebase_qualified_name
        package_manager_metadata = envelope.package_manager_metadata
        trace_id = envelope.trace_id
        
        # Bind Loguru logger with the passed trace_id
        log = seed_and_bind_logger_from_trace_id(trace_id, activity.info().workflow_id, activity.info().workflow_run_id, activity.info().activity_id)
        try:
            log.debug(
                "Starting package manager metadata ingestion | codebase_name={} | programming_language={} | package_manager={}",
                codebase_qualified_name, package_manager_metadata.programming_language, package_manager_metadata.package_manager
            )

            await self.code_confluence_graph_ingestion.insert_code_confluence_codebase_package_manager_metadata(codebase_qualified_name=codebase_qualified_name, package_manager_metadata=package_manager_metadata)

            log.debug(
                "Successfully ingested package manager metadata | codebase_name={} | status=success",
                codebase_qualified_name
            )

        except Exception as e:
            log.debug(
                "Failed to ingest package manager metadata | codebase_name={} | error_type={} | error_details={} | status=error",
                codebase_qualified_name, type(e).__name__, str(e)
            )
            raise ApplicationError(message=f"Failed to ingest package manager metadata for {codebase_qualified_name}", type="PACKAGE_METADATA_INGESTION_ERROR")
