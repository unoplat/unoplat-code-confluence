from src.code_confluence_flow_bridge.logging.trace_utils import seed_and_bind_logger_from_trace_id
from src.code_confluence_flow_bridge.models.github.github_repo import ErrorReport, JobStatus
from src.code_confluence_flow_bridge.models.workflow.repo_workflow_base import CodebaseWorkflowDbActivityEnvelope
from src.code_confluence_flow_bridge.processor.db.postgres.db import get_session_cm
from src.code_confluence_flow_bridge.processor.db.postgres.repository_data import CodebaseConfig, CodebaseWorkflowRun, RepositoryWorkflowRun

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from temporalio import activity
from temporalio.exceptions import ApplicationError


class ChildWorkflowDbActivity:
    """Activity for database operations related to child workflow status tracking."""

    @activity.defn(name="update-codebase-workflow-status")
    async def update_codebase_workflow_status(
        self,
        envelope: CodebaseWorkflowDbActivityEnvelope
    ) -> None:
        """Update the repository with child workflow status information.

        Args:
            envelope: Envelope containing all necessary parameters for updating codebase workflow status
        """
        # Extract parameters from envelope
        repository_name: str = envelope.repository_name
        repository_owner_name: str = envelope.repository_owner_name
        root_package: str = envelope.root_package
        workflow_id: str = envelope.codebase_workflow_id
        workflow_run_id: str = envelope.codebase_workflow_run_id
        parent_workflow_run_id: str = envelope.repository_workflow_run_id
        trace_id: str = envelope.trace_id
        status: JobStatus = JobStatus(envelope.status)  # Convert string to JobStatus enum
        error_report: Optional[ErrorReport] = envelope.error_report
        
        activity_id: str = "update_codebase_workflow_status"
        log = seed_and_bind_logger_from_trace_id(
            trace_id=trace_id,
            workflow_id=workflow_id,
            workflow_run_id=workflow_run_id,
            activity_id=activity_id
        )
        
        try:
            async with get_session_cm() as session:
                # First check if the parent workflow run exists
                parent_workflow_run = await self._get_parent_workflow_run(session, repository_name, repository_owner_name, parent_workflow_run_id)
                if not parent_workflow_run:
                    error_msg = f"Parent workflow run not found: {parent_workflow_run_id} for {repository_name}/{repository_owner_name}"
                    log.error(error_msg)
                    raise ApplicationError(
                        error_msg,
                        type="ParentWorkflowRunNotFound",
                        non_retryable=True,
                        details={
                            "workflow_id": workflow_id,
                            "workflow_run_id": workflow_run_id,
                            "activity_id": activity_id,
                            "activity_name": "update_codebase_workflow_status"
                        }
                    )
                
                # Check if codebase config exists
                codebase_config = await session.get(CodebaseConfig, (repository_name, repository_owner_name, root_package))
                if not codebase_config:
                    error_msg = f"Codebase config not found for {repository_name}/{repository_owner_name}/{root_package}"
                    log.error(error_msg)
                    raise ApplicationError(
                        error_msg,
                        type="CodebaseConfigNotFound",
                        non_retryable=True,
                        details={
                            "workflow_id": workflow_id,
                            "workflow_run_id": workflow_run_id,
                            "activity_id": activity_id,
                            "activity_name": "update_codebase_workflow_status"
                        }
                    )
                
                # Check if workflow run exists
                workflow_run = await self._get_workflow_run(session, repository_name, repository_owner_name, root_package, workflow_run_id)
                
                now = datetime.now(timezone.utc)
                if not workflow_run:
                    # Create a new workflow run
                    workflow_run = CodebaseWorkflowRun(
                        repository_name=repository_name,
                        repository_owner_name=repository_owner_name,
                        root_package=root_package,
                        codebase_workflow_run_id=workflow_run_id,
                        codebase_workflow_id=workflow_id,
                        repository_workflow_run_id=parent_workflow_run_id,
                        status=status.value,
                        error_report=error_report.model_dump() if error_report else None,
                        started_at=now
                    )
                    
                    # Add and commit the new workflow run
                    session.add(workflow_run)
                    await session.commit()
                    await session.refresh(workflow_run)
                    log.info(f"Created codebase workflow run: {workflow_run_id} for {repository_name}/{repository_owner_name}/{root_package}")
                else:
                    # Update existing workflow run
                    workflow_run.status = status.value
                    
                    if error_report:
                        workflow_run.error_report = error_report.model_dump()
                    
                    if status == JobStatus.COMPLETED or status == JobStatus.FAILED:
                        workflow_run.completed_at = now
                    
                    # Add and commit the updated workflow run
                    session.add(workflow_run)
                    await session.commit()
                    await session.refresh(workflow_run)
                    log.info(f"Updated codebase workflow run: {workflow_run_id} for {repository_name}/{repository_owner_name}/{root_package} with status {status.value}")
                    
        except ApplicationError:
            # Re-raise without wrapping to preserve error context
            raise
        except Exception as e:
            error_msg = f"Failed to update codebase workflow status: {e}"
            log.error(error_msg)
            raise ApplicationError(
                error_msg,
                type="CodebaseStatusUpdateError",
                non_retryable=False,  # Allow retries
                details={
                    "workflow_id": workflow_id,
                    "workflow_run_id": workflow_run_id,
                    "activity_id": activity_id,
                    "activity_name": "update_codebase_workflow_status",
                    "error": str(e)
                }
            )
    
    async def _get_parent_workflow_run(self, session: AsyncSession, repository_name: str, repository_owner_name: str, workflow_run_id: str) -> Optional[RepositoryWorkflowRun]:
        """Get a parent workflow run by its keys."""
        return await session.get(RepositoryWorkflowRun, (repository_name, repository_owner_name, workflow_run_id))
    
    async def _get_workflow_run(self, session: AsyncSession, repository_name: str, repository_owner_name: str, root_package: str, workflow_run_id: str) -> Optional[CodebaseWorkflowRun]:
        """Get a codebase workflow run by its keys."""
        return await session.get(CodebaseWorkflowRun, (repository_name, repository_owner_name, root_package, workflow_run_id))