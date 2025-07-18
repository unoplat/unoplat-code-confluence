from src.code_confluence_flow_bridge.logging.trace_utils import (
    activity_id_var,
    activity_name_var,
    seed_and_bind_logger_from_trace_id,
    workflow_id_var,
    workflow_run_id_var,
)
from src.code_confluence_flow_bridge.models.configuration.settings import (
    EnvironmentSettings,
)
from src.code_confluence_flow_bridge.models.workflow.parent_child_clone_metadata import (
    ParentChildCloneMetadata,
)
from src.code_confluence_flow_bridge.models.workflow.repo_workflow_base import (
    ConfluenceGitGraphEnvelope,
)
from src.code_confluence_flow_bridge.processor.db.graph_db.code_confluence_graph_ingestion import (
    CodeConfluenceGraphIngestion,
)

import traceback

from loguru import logger
from temporalio import activity
from temporalio.exceptions import ApplicationError


class ConfluenceGitGraph:
    """
    Temporal activity class for GitHub operations.
    Uses global Neo4j connection managed at application startup.
    """

    def __init__(self) -> None:
        self.env_settings = EnvironmentSettings()
        logger.debug(
            "Initialized ConfluenceGitGraph - using global Neo4j connection"
        )

    @activity.defn
    async def insert_git_repo_into_graph_db(self, envelope: "ConfluenceGitGraphEnvelope") -> ParentChildCloneMetadata:
        """
        Insert a git repository into the graph database

        Args:
            envelope: ConfluenceGitGraphEnvelope containing git repository data and trace id

        Returns:
            ParentChildCloneMetadata containing the qualified name of the git repository and the codebase qualified names
        """
        # Use envelope model
        
        # Extract parameters from envelope
        git_repo = envelope.git_repo
        trace_id = envelope.trace_id
        
        # Bind a Loguru logger with the provided trace_id
        info: activity.Info = activity.info()
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
                "Starting graph db insertion for repo: {} ",
                git_repo.repository_url
            )
            
            # Use global Neo4j connection
            graph = CodeConfluenceGraphIngestion(code_confluence_env=self.env_settings)
            parent_child_clone_metadata = await graph.insert_code_confluence_git_repo(git_repo=git_repo)
            
            log.debug(
                "Successfully inserted git repo into graph db: {} ",
                git_repo.repository_url
            )
            return parent_child_clone_metadata

        except Exception as e:
            if isinstance(e, ApplicationError):
                # Re-raise ApplicationError as is since it already contains detailed error info
                raise
                
            # For other exceptions, wrap in ApplicationError with detailed info
            error_msg = f"Failed to insert git repo into graph db: {git_repo.repository_url}"
            log.error(
                "{} | error_type={} | error={} | status=failed",
                error_msg, type(e).__name__, str(e)
            )
            
            # Capture the traceback string
            tb_str = traceback.format_exc()
            
            raise ApplicationError(
                error_msg,
                {"repository": git_repo.repository_url},
                {"error": str(e)},
                {"error_type": type(e).__name__},
                {"traceback": tb_str},
                {"workflow_id": workflow_id_var.get("") },
                {"workflow_run_id": workflow_run_id_var.get("")},
                {"activity_name": activity_name_var.get("")},
                {"activity_id": activity_id_var.get("")},
                type="GRAPH_INGESTION_ERROR"
            )
