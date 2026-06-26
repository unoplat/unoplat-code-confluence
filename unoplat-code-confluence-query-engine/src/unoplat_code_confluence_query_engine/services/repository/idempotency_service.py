"""Repository workflow idempotency helpers."""

from __future__ import annotations

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from unoplat_code_confluence_commons.repo_models import (
    RepositoryAgentMdSnapshot,
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


async def get_latest_completed_agent_snapshot(
    *,
    session: AsyncSession,
    repository_name: str,
    repository_owner_name: str,
) -> RepositoryAgentMdSnapshot | None:
    """Return the latest completed AGENTS.md snapshot for a repository, if any."""
    stmt = (
        select(RepositoryAgentMdSnapshot)
        .join(
            RepositoryWorkflowRun,
            and_(
                RepositoryWorkflowRun.repository_owner_name
                == RepositoryAgentMdSnapshot.repository_owner_name,
                RepositoryWorkflowRun.repository_name
                == RepositoryAgentMdSnapshot.repository_name,
                RepositoryWorkflowRun.repository_workflow_run_id
                == RepositoryAgentMdSnapshot.repository_workflow_run_id,
            ),
        )
        .where(
            RepositoryAgentMdSnapshot.repository_owner_name == repository_owner_name,
            RepositoryAgentMdSnapshot.repository_name == repository_name,
            RepositoryWorkflowRun.status == JobStatus.COMPLETED.value,
            RepositoryWorkflowRun.operation.in_(AGENT_WORKFLOW_OPERATIONS),
        )
        .order_by(
            RepositoryWorkflowRun.completed_at.desc().nulls_last(),
            RepositoryWorkflowRun.started_at.desc(),
            RepositoryWorkflowRun.repository_workflow_run_id.desc(),
        )
        .limit(1)
    )
    return (await session.execute(stmt)).scalar_one_or_none()


async def resolve_agent_workflow_operation(
    *,
    session: AsyncSession,
    repository_name: str,
    repository_owner_name: str,
) -> RepositoryWorkflowOperation:
    """Resolve whether a repository agent run is initial generation or update."""
    latest_completed_snapshot = await get_latest_completed_agent_snapshot(
        session=session,
        repository_name=repository_name,
        repository_owner_name=repository_owner_name,
    )
    if latest_completed_snapshot is None:
        return RepositoryWorkflowOperation.AGENTS_GENERATION
    return RepositoryWorkflowOperation.AGENT_MD_UPDATE
