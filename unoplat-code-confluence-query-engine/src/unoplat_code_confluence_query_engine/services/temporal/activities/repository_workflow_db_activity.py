"""Temporal activity for updating RepositoryWorkflowRun status in PostgreSQL."""

from datetime import datetime, timezone

from loguru import logger
from sqlalchemy import select
from temporalio import activity
from unoplat_code_confluence_commons.repo_models import RepositoryWorkflowRun
from unoplat_code_confluence_commons.workflow_envelopes import (
    ParentWorkflowDbActivityEnvelope,
)
from unoplat_code_confluence_commons.workflow_models import JobStatus

from unoplat_code_confluence_query_engine.db.postgres.db import get_startup_session


class RepositoryWorkflowDbActivity:
    """Activity class for repository workflow status database operations."""

    @activity.defn(name="update-repository-agent-workflow-status")
    async def update_repository_workflow_status(
        self, envelope: ParentWorkflowDbActivityEnvelope
    ) -> None:
        """Update or create RepositoryWorkflowRun status in PostgreSQL.

        Logic:
        1. Query for existing record by (repo_name, repo_owner, run_id)
        2. If not exists: CREATE with status, started_at=now()
        3. If exists:
           - If current status is FAILED and new status is COMPLETED: DO NOT update
           - Otherwise: UPDATE status, set completed_at if COMPLETED/FAILED
        4. Store error_report if provided

        Args:
            envelope: Repository workflow DB envelope with status and metadata
        """
        logger.info(
            "[repository_workflow_db_activity] Updating status for {}/{} run_id={} to {}",
            envelope.repository_owner_name,
            envelope.repository_name,
            envelope.workflow_run_id,
            envelope.status,
        )

        async with get_startup_session() as session:
            # Query for existing record
            stmt = select(RepositoryWorkflowRun).where(
                RepositoryWorkflowRun.repository_name == envelope.repository_name,
                RepositoryWorkflowRun.repository_owner_name
                == envelope.repository_owner_name,
                RepositoryWorkflowRun.repository_workflow_run_id
                == envelope.workflow_run_id,
            )
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()

            now = datetime.now(timezone.utc)

            if existing is None:
                # CREATE new record
                logger.debug(
                    "[repository_workflow_db_activity] Creating new RepositoryWorkflowRun record"
                )
                new_record = RepositoryWorkflowRun(
                    repository_name=envelope.repository_name,
                    repository_owner_name=envelope.repository_owner_name,
                    repository_workflow_run_id=envelope.workflow_run_id,
                    repository_workflow_id=envelope.workflow_id,
                    operation=envelope.operation,
                    status=envelope.status,
                    started_at=now,
                    error_report=(
                        envelope.error_report.model_dump()
                        if envelope.error_report
                        else None
                    ),
                )
                session.add(new_record)
            else:
                # UPDATE existing record
                # Status preservation: FAILED/ERROR status should never be overwritten with COMPLETED
                if existing.status in (
                    JobStatus.FAILED.value,
                    JobStatus.ERROR.value,
                ) and envelope.status == JobStatus.COMPLETED.value:
                    logger.warning(
                        "[repository_workflow_db_activity] Preserving {} status - "
                        "ignoring COMPLETED update for {}/{} run_id={}",
                        existing.status,
                        envelope.repository_owner_name,
                        envelope.repository_name,
                        envelope.workflow_run_id,
                    )
                    return

                logger.debug(
                    "[repository_workflow_db_activity] Updating existing record from {} to {}",
                    existing.status,
                    envelope.status,
                )
                existing.status = envelope.status

                # Set completed_at for terminal states
                if envelope.status in (
                    JobStatus.COMPLETED.value,
                    JobStatus.FAILED.value,
                    JobStatus.TIMED_OUT.value,
                    JobStatus.ERROR.value,
                ):
                    existing.completed_at = now

                # Store error report if provided
                if envelope.error_report:
                    existing.error_report = envelope.error_report.model_dump()

        logger.info(
            "[repository_workflow_db_activity] Successfully updated status for {}/{} run_id={}",
            envelope.repository_owner_name,
            envelope.repository_name,
            envelope.workflow_run_id,
        )
