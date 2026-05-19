"""Repository workflow idempotency helpers."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from unoplat_code_confluence_commons.repo_models import (
    RepositoryWorkflowOperation,
    RepositoryWorkflowRun,
)
from unoplat_code_confluence_commons.workflow_models import JobStatus


ACTIVE_AGENT_WORKFLOW_STATUSES: tuple[str, ...] = (
    JobStatus.SUBMITTED.value,
    JobStatus.RUNNING.value,
    JobStatus.RETRYING.value,
)

AGENT_WORKFLOW_OPERATIONS: tuple[RepositoryWorkflowOperation, ...] = (
    RepositoryWorkflowOperation.AGENTS_GENERATION,
    RepositoryWorkflowOperation.AGENT_MD_UPDATE,
)


async def get_active_agent_workflow_run(
    *,
    session: AsyncSession,
    repository_name: str,
    repository_owner_name: str,
) -> RepositoryWorkflowRun | None:
    """Return an active AGENTS.md-related workflow for a repository, if any."""
    stmt = (
        select(RepositoryWorkflowRun)
        .where(
            RepositoryWorkflowRun.repository_name == repository_name,
            RepositoryWorkflowRun.repository_owner_name == repository_owner_name,
            RepositoryWorkflowRun.status.in_(ACTIVE_AGENT_WORKFLOW_STATUSES),
            RepositoryWorkflowRun.operation.in_(AGENT_WORKFLOW_OPERATIONS),
        )
        .order_by(RepositoryWorkflowRun.started_at.desc())
        .limit(1)
    )
    return (await session.execute(stmt)).scalar_one_or_none()
