"""Ingestion parent lifecycle writes and cross-service checkout admission."""

import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from temporalio import activity
from temporalio.client import Client, WorkflowExecutionStatus
from temporalio.service import RPCError
from unoplat_code_confluence_commons.base_models import (
    CodebaseConfigSQLModel as CodebaseConfig,
)
from unoplat_code_confluence_commons.repository_checkout_coordination import (
    repository_lock_key,
    session_advisory_lock,
    update_repository_run_status,
)
from unoplat_code_confluence_commons.workflow_envelopes import (
    ParentWorkflowDbActivityEnvelope,
)
from unoplat_code_confluence_commons.workflow_models import JobStatus

from code_confluence_flow_bridge.processor.db.postgres.db import get_engine_for_loop

TEMPORAL_TERMINAL_STATUSES = {
    WorkflowExecutionStatus.COMPLETED: JobStatus.COMPLETED,
    WorkflowExecutionStatus.FAILED: JobStatus.FAILED,
    WorkflowExecutionStatus.CANCELED: JobStatus.CANCELLED,
    WorkflowExecutionStatus.TERMINATED: JobStatus.CANCELLED,
    WorkflowExecutionStatus.TIMED_OUT: JobStatus.TIMED_OUT,
}


class ParentWorkflowDbActivity:
    """Keep SUBMITTED parents queued until the repository slot is available."""

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
            return None
        if description.run_id != run_id or description.status is None:
            return None
        return TEMPORAL_TERMINAL_STATUSES.get(description.status)

    @activity.defn(name="update-repository-workflow-status")
    async def update_repository_workflow_status(
        self, envelope: ParentWorkflowDbActivityEnvelope
    ) -> bool:
        """Commit admission/status and codebase configuration before unlocking."""
        engine, _ = await get_engine_for_loop()
        async with session_advisory_lock(
            engine,
            repository_lock_key(
                envelope.repository_owner_name, envelope.repository_name
            ),
        ) as connection:
            async with AsyncSession(bind=connection, expire_on_commit=False) as session:
                async with session.begin():
                    admitted = await update_repository_run_status(
                        session, envelope, self._confirm_terminal
                    )
                    if admitted and envelope.status == JobStatus.RUNNING.value:
                        for metadata in envelope.repository_metadata or []:
                            config = await session.get(
                                CodebaseConfig,
                                (
                                    envelope.repository_name,
                                    envelope.repository_owner_name,
                                    metadata.codebase_folder,
                                ),
                            )
                            if config is None:
                                config = CodebaseConfig(
                                    repository_name=envelope.repository_name,
                                    repository_owner_name=envelope.repository_owner_name,
                                    codebase_folder=metadata.codebase_folder,
                                )
                                session.add(config)
                            config.root_packages = metadata.root_packages
                            config.programming_language_metadata = (
                                metadata.programming_language_metadata.model_dump()
                            )
                    return admitted
