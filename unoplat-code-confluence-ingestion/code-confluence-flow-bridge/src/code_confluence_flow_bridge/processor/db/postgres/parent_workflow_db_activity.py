from src.code_confluence_flow_bridge.logging.trace_utils import seed_and_bind_logger_from_trace_id
from src.code_confluence_flow_bridge.models.github.github_repo import ErrorReport, JobStatus
from src.code_confluence_flow_bridge.models.workflow.repo_workflow_base import ParentWorkflowDbActivityEnvelope
from src.code_confluence_flow_bridge.processor.db.postgres.db import get_session_cm
from src.code_confluence_flow_bridge.processor.db.postgres.repository_data import (
    CodebaseConfig,
    Repository,
    RepositoryWorkflowRun,
)

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from temporalio import activity


class ParentWorkflowDbActivity:
    """Activity for database operations related to parent workflow status tracking."""

    @activity.defn(name="update-repository-workflow-status")
    async def update_repository_workflow_status(
        self,
        envelope: ParentWorkflowDbActivityEnvelope
    ) -> None:
        """Update the repository with parent workflow status information.

        Args:
            envelope: Envelope containing all necessary parameters for updating repository workflow status
        """
        # Extract parameters from envelope
        repository_name: str = envelope.repository_name
        repository_owner_name: str = envelope.repository_owner_name
        workflow_id: str = envelope.workflow_id
        workflow_run_id: str = envelope.workflow_run_id
        trace_id: str = envelope.trace_id
        status: JobStatus = JobStatus(envelope.status)  # Convert string to JobStatus enum
        error_report: Optional[ErrorReport] = envelope.error_report
        
        activity_id: str = "update_repository_workflow_status"
        log = seed_and_bind_logger_from_trace_id(
            trace_id=trace_id,
            workflow_id=workflow_id,
            workflow_run_id=workflow_run_id,
            activity_id=activity_id
        )
        try:
            log.debug(
                "Starting update repository workflow status | repository={}/{} | workflow_run_id={} | status={} | error_report_present={}",
                repository_name, repository_owner_name, workflow_run_id, status.value, bool(error_report)
            )
            async with get_session_cm() as session:
                # First check if repository exists, if not create it
                _ = await self._get_or_create_repository(session, repository_name, repository_owner_name)
            
                for cm in envelope.repository_metadata:
                    existing_config = await session.get(CodebaseConfig, (repository_name, repository_owner_name, cm.root_package))
                    source_directory = cm.codebase_folder or cm.root_package
                    plm = cm.programming_language_metadata.model_dump()
                    if not existing_config:
                        config = CodebaseConfig(
                            repository_name=repository_name,
                            repository_owner_name=repository_owner_name,
                            root_package=cm.root_package,
                            source_directory=source_directory,
                            programming_language_metadata=plm,
                        )
                        session.add(config)
                        await session.commit()
                        await session.refresh(config)
                    else:
                        #Todo: Revisit this later
                        existing_config.source_directory = source_directory
                        existing_config.programming_language_metadata = plm
                        session.add(existing_config)
                        await session.commit()
                        await session.refresh(existing_config)
            
                # Then check if workflow run exists
                workflow_run = await self._get_workflow_run(session, repository_name, repository_owner_name, workflow_run_id)
                
                now = datetime.now(timezone.utc)
                if not workflow_run:
                    # Create a new workflow run
                    workflow_run = RepositoryWorkflowRun(
                        repository_name=repository_name,
                        repository_owner_name=repository_owner_name,
                        repository_workflow_run_id=workflow_run_id,
                        repository_workflow_id=workflow_id,
                        status=status.value,
                        error_report=error_report.model_dump() if error_report else None,
                        started_at=now
                    )
                    if status == JobStatus.COMPLETED:
                        workflow_run.completed_at = now
                    
                    # Add and commit the new workflow run
                    session.add(workflow_run)
                    await session.commit()
                    await session.refresh(workflow_run)
                    log.success(f"Created workflow run: {workflow_run_id} for {repository_name}/{repository_owner_name}")
                    log.debug(
                        "Created workflow run: {} for {}/{}",
                        workflow_run_id, repository_name, repository_owner_name
                    )
                else:
                    # Update existing workflow run
                    workflow_run.status = status.value
                    
                    if error_report:
                        workflow_run.error_report = error_report.model_dump()
                    
                    if status == JobStatus.COMPLETED:
                        workflow_run.completed_at = now
                    
                    # Add and commit the updated workflow run
                    session.add(workflow_run)
                    await session.commit()
                    await session.refresh(workflow_run)
                    log.success(f"Updated workflow run: {workflow_run_id} for {repository_name}/{repository_owner_name}")
                    log.debug(
                        "Updated workflow run: {} for {}/{} with status={}",
                        workflow_run_id, repository_name, repository_owner_name, status.value
                    )
                    
        except Exception as e:
            log.error(f"Failed to update repository workflow status: {e}")
            raise
        
    async def _get_or_create_repository(self, session: AsyncSession, repository_name: str, repository_owner_name: str) -> Repository:
        """Get or create a repository record."""
        repository = await session.get(Repository, (repository_name, repository_owner_name))
        
        if not repository:
            # Create a new repository
            repository = Repository(
                repository_name=repository_name,
                repository_owner_name=repository_owner_name
            )
            session.add(repository)
            await session.commit()
            await session.refresh(repository)
            
        return repository
        
    async def _get_workflow_run(self, session: AsyncSession, repository_name: str, repository_owner_name: str, workflow_run_id: str) -> Optional[RepositoryWorkflowRun]:
        """Get a workflow run by its keys."""
        return await session.get(RepositoryWorkflowRun, (repository_name, repository_owner_name, workflow_run_id))