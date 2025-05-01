from src.code_confluence_flow_bridge.logging.trace_utils import seed_and_bind_logger_from_trace_id
from src.code_confluence_flow_bridge.models.github.github_repo import (
    CodebaseStatus,
    CodebaseStatusList,
    GithubRepoStatus,
    WorkflowRun,
    WorkflowStatus,
)
from src.code_confluence_flow_bridge.processor.db.postgres.db import get_session_cm
from src.code_confluence_flow_bridge.processor.db.postgres.repository_data import RepositoryData

from datetime import datetime, timezone
from typing import Optional

from temporalio import activity


class ChildWorkflowDbActivity:
    """Activity for database operations related to workflow status tracking."""

    @activity.defn
    async def update_codebase_workflow_status(
        self,
        repository_name: str,
        repository_owner_name: str,
        codebase_name: str,
        workflow_id: str,
        workflow_run_id: str,
        trace_id: str
    ) -> None:
        """Update the repository with child workflow status information.

        Args:
            repository_name: Name of the repository
            repository_owner_name: Name of the repository owner
            codebase_name: Name of the codebase (root package)
            workflow_id: ID of the child workflow
            workflow_run_id: Run ID of the child workflow
            trace_id: Trace ID for logging
        """
        # Set up logging context
        log = seed_and_bind_logger_from_trace_id(trace_id, workflow_id, workflow_run_id, "update_codebase_workflow_status")
        
        try:
            async with get_session_cm() as session:
                # Get the repository data from the database
                repository_data: Optional[RepositoryData] = await session.get(
                    RepositoryData,
                    (repository_name, repository_owner_name)
                )
                
                #TODO: handle application failure. do not return false
                if not repository_data:
                    log.error(f"Repository data not found for {repository_name}/{repository_owner_name}")
                    raise ValueError(f"Repository data not found for {repository_name}/{repository_owner_name}")
                
                # Parse the current repository workflow status
                current_status_data = repository_data.repository_workflow_status
            
                try:
                    current_status = GithubRepoStatus.model_validate(current_status_data)
                except Exception as e:
                    log.error(f"Failed to parse repository workflow status: {e}")
                    raise ValueError(f"Failed to parse repository workflow status: {e}")
                
                # Create or update the codebase status list
                if not current_status.status:
                    current_status.status = CodebaseStatusList(codebases=[])
                
                # Create a new workflow run
                now = datetime.now(timezone.utc)
                workflow_run = WorkflowRun(
                    workflowRunId=workflow_run_id,
                    started_at=now
                )
                
                # Create a new workflow status
                child_workflow_status = WorkflowStatus(
                    workflowId=workflow_id,
                    workflowRuns=[workflow_run]
                )
                
                # Find or create the codebase status
                codebase_found = False
                for codebase in current_status.status.codebases:
                    if codebase.root_package == codebase_name:
                        codebase.workflows.append(child_workflow_status)
                        codebase_found = True
                        break
                
                if not codebase_found:
                    # Create a new codebase status
                    new_codebase_status = CodebaseStatus(
                        root_package=codebase_name,
                        workflows=[child_workflow_status]
                    )
                    current_status.status.codebases.append(new_codebase_status)
                
                # Update the repository data
                repository_data.repository_workflow_status = current_status.model_dump(mode="json")
                session.add(repository_data)
                await session.commit()
                log.success(f"Updated codebase workflow status for {repository_name}/{repository_owner_name}/{codebase_name}")
        except Exception as e:
            log.error(f"Failed to update codebase workflow status: {e}")
            raise