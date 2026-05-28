"""Repository operation idempotency helpers."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from unoplat_code_confluence_commons.base_models import (
    RepositoryWorkflowOperation,
    RepositoryWorkflowRun,
)
from unoplat_code_confluence_commons.workflow_models import JobStatus

ACTIVE_REPOSITORY_OPERATION_STATUSES: tuple[str, ...] = (
    JobStatus.SUBMITTED.value,
    JobStatus.RUNNING.value,
    JobStatus.RETRYING.value,
)

AGENT_UPDATE_BLOCKING_OPERATIONS: tuple[RepositoryWorkflowOperation, ...] = (
    RepositoryWorkflowOperation.INGESTION,
    RepositoryWorkflowOperation.AGENTS_GENERATION,
    RepositoryWorkflowOperation.AGENT_MD_UPDATE,
)


async def get_active_repository_operation(
    *,
    session: AsyncSession,
    repository_name: str,
    repository_owner_name: str,
    operations: tuple[RepositoryWorkflowOperation, ...] = AGENT_UPDATE_BLOCKING_OPERATIONS,
) -> RepositoryWorkflowRun | None:
    """Return a non-terminal repository workflow run that blocks a new operation."""
    stmt = (
        select(RepositoryWorkflowRun)
        .where(
            RepositoryWorkflowRun.repository_name == repository_name,
            RepositoryWorkflowRun.repository_owner_name == repository_owner_name,
            RepositoryWorkflowRun.status.in_(ACTIVE_REPOSITORY_OPERATION_STATUSES),
            RepositoryWorkflowRun.operation.in_(operations),
        )
        .order_by(RepositoryWorkflowRun.started_at.desc())
        .limit(1)
    )
    return (await session.execute(stmt)).scalar_one_or_none()
