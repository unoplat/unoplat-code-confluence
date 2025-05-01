from src.code_confluence_flow_bridge.logging.trace_utils import seed_and_bind_logger_from_trace_id
from src.code_confluence_flow_bridge.models.github.github_repo import CodebaseConfig, GithubRepoStatus, WorkflowRun, WorkflowStatus
from src.code_confluence_flow_bridge.processor.db.postgres.db import get_session_cm
from src.code_confluence_flow_bridge.processor.db.postgres.repository_data import RepositoryData

from datetime import datetime, timezone
from typing import List

from temporalio import activity


class ParentWorkflowDbActivity:
    """Activity for database operations related to parent workflow status tracking."""

    @activity.defn
    async def update_repository_workflow_status(
        self,
        repository_name: str,
        repository_owner_name: str,
        workflow_id: str,
        workflow_run_id: str,
        trace_id: str,
        repository_metadata: List[CodebaseConfig]
    ) -> None:
        """Update the repository with parent workflow status information.

        Args:
            repository_name: Name of the repository
            repository_owner_name: Name of the repository owner
            workflow_id: ID of the parent workflow
            workflow_run_id: Run ID of the parent workflow
            trace_id: Trace ID for logging
            repository_metadata: Metadata for the repository
        """
        log = seed_and_bind_logger_from_trace_id(trace_id, workflow_id, workflow_run_id, "update_repository_workflow_status")
        try:
            async with get_session_cm() as session:
                repo_data = await session.get(RepositoryData, (repository_name, repository_owner_name))
                now = datetime.now(timezone.utc)
                workflow_run = WorkflowRun(workflowRunId=workflow_run_id, started_at=now)
                if not repo_data:
                    # Initial insert
                    parent_status = WorkflowStatus(workflowId=workflow_id, workflowRuns=[workflow_run])
                    github_status = GithubRepoStatus(
                        repository_workflow_status=parent_status,
                        status=None
                    )
                    new_data = RepositoryData(
                        repository_name=repository_name,
                        repository_owner_name=repository_owner_name,
                        repository_workflow_status=github_status.model_dump(mode="json"),
                        repository_metadata=[config.model_dump(mode="json") for config in repository_metadata]
                    )
                    session.add(new_data)
                    await session.commit()
                    log.success(f"Created repository data for {repository_name}/{repository_owner_name}")
                    return

                # Update existing record
                current_status_data = repo_data.repository_workflow_status
                try:
                    current_status = GithubRepoStatus.model_validate(current_status_data)
                except Exception as e:
                    log.error(f"Failed to parse repository workflow status: {e}")
                    raise ValueError(f"Failed to parse repository workflow status: {e}")

                if not current_status.repository_workflow_status:
                    parent_status = WorkflowStatus(workflowId=workflow_id, workflowRuns=[workflow_run])
                    current_status.repository_workflow_status = parent_status
                else:
                    current_status.repository_workflow_status.workflowRuns.append(workflow_run)

                repo_data.repository_workflow_status = current_status.model_dump(mode="json")
                session.add(repo_data)
                await session.commit()
                log.success(f"Updated repository workflow status for {repository_name}/{repository_owner_name}")
        except Exception as e:
            log.error(f"Failed to update repository workflow status: {e}")
            raise