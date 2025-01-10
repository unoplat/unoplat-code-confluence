from loguru import logger
from temporalio import activity
from temporalio.exceptions import ApplicationError

from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_package_manager_metadata import UnoplatPackageManagerMetadata
from src.code_confluence_flow_bridge.processor.db.graph_db.code_confluence_graph_ingestion import CodeConfluenceGraphIngestion


class PackageManagerMetadataIngestion:
    """
    Temporal activity class for package manager metadata ingestion
    """
    def __init__(self, code_confluence_graph_ingestion: CodeConfluenceGraphIngestion):
        self.code_confluence_graph_ingestion = code_confluence_graph_ingestion
        logger.info("Initialized PackageManagerMetadataIngestion")

    @activity.defn
    async def insert_package_manager_metadata(
        self,
        codebase_qualified_name: str,
        package_manager_metadata: UnoplatPackageManagerMetadata
    ) -> None:
        """
        Insert package manager metadata into graph database
        
        Args:
            codebase_qualified_name: Qualified name of the codebase
            package_manager_metadata: Package manager metadata to insert
        """
        try:
            info = activity.info()
            logger.info(
                "Starting package manager metadata ingestion",
                workflow_id=info.workflow_id,
                activity_id=info.activity_id,
                codebase=codebase_qualified_name
            )
            
            await self.code_confluence_graph_ingestion.insert_code_confluence_codebase_package_manager_metadata(
                codebase_qualified_name=codebase_qualified_name,
                package_manager_metadata=package_manager_metadata
            )
            
            logger.success(
                "Successfully ingested package manager metadata",
                workflow_id=info.workflow_id,
                activity_id=info.activity_id,
                codebase=codebase_qualified_name
            )
            
        except Exception as e:
            logger.error(
                "Failed to ingest package manager metadata",
                workflow_id=activity.info().workflow_id,
                activity_id=activity.info().activity_id,
                error=str(e),
                codebase=codebase_qualified_name
            )
            raise ApplicationError(
                message=f"Failed to ingest package manager metadata for {codebase_qualified_name}",
                type="PACKAGE_METADATA_INGESTION_ERROR"
            )
