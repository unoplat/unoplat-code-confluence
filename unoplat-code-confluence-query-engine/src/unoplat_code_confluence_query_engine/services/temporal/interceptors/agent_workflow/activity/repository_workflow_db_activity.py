"""Repository parent lifecycle writes and cross-service checkout admission."""

import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from temporalio import activity
from temporalio.client import Client, WorkflowExecutionStatus
from temporalio.service import RPCError
from unoplat_code_confluence_commons.repository_checkout_coordination import (
    repository_lock_key,
    session_advisory_lock,
    update_repository_run_status,
)
from unoplat_code_confluence_commons.workflow_envelopes import (
    ParentWorkflowDbActivityEnvelope,
)
from unoplat_code_confluence_commons.workflow_models import JobStatus

from unoplat_code_confluence_query_engine.db.postgres import db

TEMPORAL_TERMINAL_STATUSES = {
    WorkflowExecutionStatus.COMPLETED: JobStatus.COMPLETED,
    WorkflowExecutionStatus.FAILED: JobStatus.FAILED,
    WorkflowExecutionStatus.CANCELED: JobStatus.CANCELLED,
    WorkflowExecutionStatus.TERMINATED: JobStatus.CANCELLED,
    WorkflowExecutionStatus.TIMED_OUT: JobStatus.TIMED_OUT,
}


class RepositoryWorkflowDbActivity:
    """Serialize parent status writes with ingestion and artifact capture."""

    def __init__(self, temporal_client: Client | None = None) -> None:
        self._temporal_client = temporal_client

    async def _confirm_terminal(
        self, workflow_id: str, run_id: str
    ) -> JobStatus | None:
        if self._temporal_client is None:
            return None
        try:
            description = await asyncio.wait_for(
                self._temporal_client.get_workflow_handle(
                    workflow_id, run_id=run_id
                ).describe(),
                timeout=10,
            )
        except (RPCError, TimeoutError):
            # Missing history or an unreachable server is not proof of termination.
            return None
        if description.run_id != run_id or description.status is None:
            return None
        return TEMPORAL_TERMINAL_STATUSES.get(description.status)

    @activity.defn(name="update-repository-agent-workflow-status")
    async def update_repository_workflow_status(
        self, envelope: ParentWorkflowDbActivityEnvelope
    ) -> bool:
        """Return False for a queued admission request; commit before unlocking."""
        if db.async_engine is None:
            raise RuntimeError("Database connections not initialized")
        async with session_advisory_lock(
            db.async_engine,
            repository_lock_key(
                envelope.repository_owner_name, envelope.repository_name
            ),
        ) as connection:
            async with AsyncSession(bind=connection, expire_on_commit=False) as session:
                async with session.begin():
                    return await update_repository_run_status(
                        session, envelope, self._confirm_terminal
                    )
