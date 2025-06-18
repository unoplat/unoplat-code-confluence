from src.code_confluence_flow_bridge.logging.trace_utils import seed_and_bind_logger_from_trace_id
from src.code_confluence_flow_bridge.models.configuration.settings import EnvironmentSettings
from src.code_confluence_flow_bridge.models.workflow.repo_workflow_base import PackageManagerMetadataIngestionEnvelope
from src.code_confluence_flow_bridge.processor.db.graph_db.graph_context import graph_ingestion_ctx

import traceback

from loguru import logger
from temporalio import activity
from temporalio.exceptions import ApplicationError


class PackageManagerMetadataIngestion:
    """
    Temporal activity class for package manager metadata ingestion.
    Uses context manager to create fresh Neo4j sessions for each activity execution.
    """

    def __init__(self):
        self.env_settings = EnvironmentSettings()
        logger.debug(
            "Initialized PackageManagerMetadataIngestion - will create fresh Neo4j session per activity execution"
        )

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
        info = activity.info()
        workflow_id: str = info.workflow_id
        workflow_run_id: str = info.workflow_run_id
        activity_id: str = info.activity_id
        activity_name: str = info.activity_type
        log = seed_and_bind_logger_from_trace_id(
            trace_id=trace_id,
            workflow_id=workflow_id,
            workflow_run_id=workflow_run_id,
            activity_id=activity_id,
            activity_name=activity_name
        )
        try:
            log.debug(
                "Starting package manager metadata ingestion | codebase_name={} | programming_language={} | package_manager={}",
                codebase_qualified_name, package_manager_metadata.programming_language, package_manager_metadata.package_manager
            )
            
            # Use fresh Neo4j session for this activity execution
            async with graph_ingestion_ctx(self.env_settings) as graph:
                await graph.insert_code_confluence_codebase_package_manager_metadata(
                    codebase_qualified_name=codebase_qualified_name, 
                    package_manager_metadata=package_manager_metadata
                )

            log.debug(
                "Successfully ingested package manager metadata | codebase_name={} | status=success",
                codebase_qualified_name
            )

        except Exception as e:
            log.error(
                "Failed to ingest package manager metadata | codebase_name={} | error_type={} | error_details={} | status=error",
                codebase_qualified_name, type(e).__name__, str(e)
            )
            
            # Capture the traceback string
            tb_str = traceback.format_exc()
            
            raise ApplicationError(
                f"Failed to ingest package manager metadata for {codebase_qualified_name}",
                {"codebase": codebase_qualified_name},
                {"error": str(e)},
                {"error_type": type(e).__name__},
                {"traceback": tb_str},
                {"workflow_id": workflow_id},
                {"workflow_run_id": workflow_run_id},
                {"activity_name": activity_name},
                {"activity_id": activity_id},
                type="PACKAGE_METADATA_INGESTION_ERROR"
            )
