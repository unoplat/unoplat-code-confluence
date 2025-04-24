from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_package_manager_metadata import UnoplatPackageManagerMetadata
from src.code_confluence_flow_bridge.processor.db.graph_db.code_confluence_graph_ingestion import CodeConfluenceGraphIngestion

from temporalio import activity
from temporalio.exceptions import ApplicationError
from loguru import logger


class PackageManagerMetadataIngestion:
    """
    Temporal activity class for package manager metadata ingestion
    """

    def __init__(self, code_confluence_graph_ingestion: CodeConfluenceGraphIngestion):
        self.code_confluence_graph_ingestion = code_confluence_graph_ingestion
        logger.debug("Initialized PackageManagerMetadataIngestion")

    @activity.defn
    async def insert_package_manager_metadata(self, codebase_qualified_name: str, package_manager_metadata: UnoplatPackageManagerMetadata) -> None:
        """
        Insert package manager metadata into graph database

        Args:
            codebase_qualified_name: Qualified name of the codebase
            package_manager_metadata: Package manager metadata to insert
        """
        try:
            info = activity.info()
            logger.debug(
                "Starting package manager metadata ingestion | workflow_id={} | activity_id={} | codebase_name={} | programming_language={} | package_manager={}",
                info.workflow_id, info.activity_id, codebase_qualified_name, package_manager_metadata.programming_language, package_manager_metadata.package_manager
            )

            await self.code_confluence_graph_ingestion.insert_code_confluence_codebase_package_manager_metadata(codebase_qualified_name=codebase_qualified_name, package_manager_metadata=package_manager_metadata)

            logger.debug(
                "Successfully ingested package manager metadata | workflow_id={} | activity_id={} | codebase_name={} | status=success",
                info.workflow_id, info.activity_id, codebase_qualified_name
            )

        except Exception as e:
            info = activity.info()
            logger.debug(
                "Failed to ingest package manager metadata | workflow_id={} | activity_id={} | codebase_name={} | error_type={} | error_details={} | status=error",
                info.workflow_id, info.activity_id, codebase_qualified_name, type(e).__name__, str(e)
            )
            raise ApplicationError(message=f"Failed to ingest package manager metadata for {codebase_qualified_name}", type="PACKAGE_METADATA_INGESTION_ERROR")
