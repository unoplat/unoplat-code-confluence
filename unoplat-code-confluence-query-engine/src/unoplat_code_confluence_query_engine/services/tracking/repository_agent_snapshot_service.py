"""Helpers for writing repository agent snapshot events to Postgres."""

from __future__ import annotations

from collections.abc import Mapping, Sequence, Set
from datetime import datetime, timezone
from decimal import ROUND_HALF_UP, Decimal
from typing import TypedDict

from loguru import logger
from sqlalchemy import func, select, update
from sqlalchemy.dialects.postgresql import insert
from unoplat_code_confluence_commons.repo_models import (
    RepositoryAgentCodebaseProgress,
    RepositoryAgentEvent,
    RepositoryAgentMdSnapshot,
)

from unoplat_code_confluence_query_engine.db.postgres.db import get_startup_session
from unoplat_code_confluence_query_engine.models.events.agent_events import (
    AgentEventPhase,
    PersistedAgentEvent,
)

ZERO_DECIMAL = Decimal("0")
HUNDRED_DECIMAL = Decimal("100")
PERCENTAGE_QUANTIZER = Decimal("0.01")


class RepositoryAgentCodebaseProgressInsertRow(TypedDict):
    repository_owner_name: str
    repository_name: str
    repository_workflow_run_id: str
    codebase_name: str
    next_event_id: int
    latest_event_id: int | None
    event_count: int
    progress: Decimal
    completed_namespaces: list[str]
    latest_event_at: datetime | None


def _quantize_percentage(value: Decimal) -> Decimal:
    return value.quantize(PERCENTAGE_QUANTIZER, rounding=ROUND_HALF_UP)


def _compute_codebase_progress(
    completed_namespaces: Set[str],
    completion_namespaces: Set[str],
) -> Decimal:
    if not completion_namespaces:
        return ZERO_DECIMAL

    return _quantize_percentage(
        (Decimal(len(completed_namespaces)) / Decimal(len(completion_namespaces)))
        * HUNDRED_DECIMAL
    )


def _compute_overall_progress(
    *,
    codebase_progress_sum: Decimal,
    codebase_count: int,
    repository_activity_progress: Mapping[str, object],
) -> Decimal:
    """Average codebase pipelines and repository activities as top-level units."""
    repository_values = [
        Decimal(str(value)) for value in repository_activity_progress.values()
    ]
    unit_count = codebase_count + len(repository_values)
    if unit_count == 0:
        return ZERO_DECIMAL
    return _quantize_percentage(
        (codebase_progress_sum + sum(repository_values, ZERO_DECIMAL))
        / Decimal(unit_count)
    )


def _normalize_completed_namespaces(completed_namespaces: Set[str]) -> list[str]:
    return sorted(completed_namespaces)


class RepositoryAgentSnapshotWriter:
    """Persist agent lifecycle events and progress snapshots."""

    async def begin_run(
        self,
        *,
        owner_name: str,
        repo_name: str,
        repository_workflow_run_id: str,
        codebase_names: Sequence[str],
        repository_activity_names: Sequence[str] = (),
    ) -> None:
        """Initialize snapshot and normalized progress rows for a run."""
        async with get_startup_session() as session:
            snapshot_stmt = insert(RepositoryAgentMdSnapshot).values(
                repository_owner_name=owner_name,
                repository_name=repo_name,
                repository_workflow_run_id=repository_workflow_run_id,
                overall_progress=ZERO_DECIMAL,
                latest_event_at=None,
                repository_activity_progress={
                    name: 0 for name in repository_activity_names
                },
            )
            snapshot_stmt = snapshot_stmt.on_conflict_do_nothing(
                index_elements=[
                    RepositoryAgentMdSnapshot.repository_owner_name,
                    RepositoryAgentMdSnapshot.repository_name,
                    RepositoryAgentMdSnapshot.repository_workflow_run_id,
                ]
            )
            await session.execute(snapshot_stmt)

            if not codebase_names:
                return

            progress_rows: list[RepositoryAgentCodebaseProgressInsertRow] = [
                {
                    "repository_owner_name": owner_name,
                    "repository_name": repo_name,
                    "repository_workflow_run_id": repository_workflow_run_id,
                    "codebase_name": codebase_name,
                    "next_event_id": 1,
                    "latest_event_id": None,
                    "event_count": 0,
                    "progress": ZERO_DECIMAL,
                    "completed_namespaces": [],
                    "latest_event_at": None,
                }
                for codebase_name in codebase_names
            ]
            progress_stmt = insert(RepositoryAgentCodebaseProgress).values(
                progress_rows
            )
            progress_stmt = progress_stmt.on_conflict_do_nothing(
                index_elements=[
                    RepositoryAgentCodebaseProgress.repository_owner_name,
                    RepositoryAgentCodebaseProgress.repository_name,
                    RepositoryAgentCodebaseProgress.repository_workflow_run_id,
                    RepositoryAgentCodebaseProgress.codebase_name,
                ]
            )
            await session.execute(progress_stmt)

    async def append_event_atomic(
        self,
        *,
        owner_name: str,
        repo_name: str,
        codebase_name: str,
        agent_name: str,
        phase: AgentEventPhase,
        tool_name: str | None = None,
        tool_call_id: str | None = None,
        completion_namespaces: set[str],
        repository_workflow_run_id: str,
    ) -> int:
        """Atomically allocate an event id, persist the event, and update progress.

        Only ``PersistedAgentEvent`` fields reach the row. The legacy tool body
        columns are left NULL.
        """
        persisted_event = PersistedAgentEvent(
            agent_name=agent_name,
            phase=phase,
            tool_name=tool_name,
            tool_call_id=tool_call_id,
        )
        event_timestamp = datetime.now(timezone.utc)

        async with get_startup_session() as session:
            progress_stmt = (
                select(RepositoryAgentCodebaseProgress)
                .where(
                    RepositoryAgentCodebaseProgress.repository_owner_name == owner_name,
                    RepositoryAgentCodebaseProgress.repository_name == repo_name,
                    RepositoryAgentCodebaseProgress.repository_workflow_run_id
                    == repository_workflow_run_id,
                    RepositoryAgentCodebaseProgress.codebase_name == codebase_name,
                )
                .with_for_update()
            )
            progress_result = await session.execute(progress_stmt)
            progress_row = progress_result.scalar_one_or_none()

            if progress_row is None:
                logger.error(
                    "Progress row missing for %s/%s codebase=%s run_id=%s",
                    owner_name,
                    repo_name,
                    codebase_name,
                    repository_workflow_run_id,
                )
                raise ValueError(
                    f"Progress row not initialized for {owner_name}/{repo_name} "
                    f"codebase={codebase_name} run_id={repository_workflow_run_id}"
                )

            allocated_event_id = progress_row.next_event_id
            completed_namespaces = set(progress_row.completed_namespaces)
            if (
                persisted_event.phase == "result"
                and persisted_event.agent_name in completion_namespaces
            ):
                completed_namespaces.add(persisted_event.agent_name)

            normalized_completed_namespaces = _normalize_completed_namespaces(
                completed_namespaces
            )
            updated_progress = _compute_codebase_progress(
                completed_namespaces,
                completion_namespaces,
            )

            session.add(
                RepositoryAgentEvent(
                    repository_owner_name=owner_name,
                    repository_name=repo_name,
                    repository_workflow_run_id=repository_workflow_run_id,
                    codebase_name=codebase_name,
                    event_id=allocated_event_id,
                    event=persisted_event.agent_name,
                    phase=persisted_event.phase,
                    message=persisted_event.message,
                    tool_name=persisted_event.tool_name,
                    tool_call_id=persisted_event.tool_call_id,
                    created_at=event_timestamp,
                )
            )

            progress_row.next_event_id = allocated_event_id + 1
            progress_row.latest_event_id = allocated_event_id
            progress_row.event_count = progress_row.event_count + 1
            progress_row.progress = updated_progress
            progress_row.completed_namespaces = normalized_completed_namespaces
            progress_row.latest_event_at = event_timestamp
            progress_row.modified_at = event_timestamp

            await session.flush()

            snapshot_stmt = (
                select(RepositoryAgentMdSnapshot)
                .where(
                    RepositoryAgentMdSnapshot.repository_owner_name == owner_name,
                    RepositoryAgentMdSnapshot.repository_name == repo_name,
                    RepositoryAgentMdSnapshot.repository_workflow_run_id
                    == repository_workflow_run_id,
                )
                .with_for_update()
            )
            snapshot_result = await session.execute(snapshot_stmt)
            snapshot = snapshot_result.scalar_one_or_none()

            if snapshot is None:
                logger.error(
                    "Snapshot row missing for %s/%s codebase=%s run_id=%s",
                    owner_name,
                    repo_name,
                    codebase_name,
                    repository_workflow_run_id,
                )
                raise ValueError(
                    f"Snapshot row not found for {owner_name}/{repo_name} "
                    f"run_id={repository_workflow_run_id}"
                )

            activities = dict(snapshot.repository_activity_progress)
            codebase_count_result = await session.execute(
                select(func.count()).select_from(RepositoryAgentCodebaseProgress).where(
                    RepositoryAgentCodebaseProgress.repository_owner_name == owner_name,
                    RepositoryAgentCodebaseProgress.repository_name == repo_name,
                    RepositoryAgentCodebaseProgress.repository_workflow_run_id
                    == repository_workflow_run_id,
                )
            )
            codebase_count = int(codebase_count_result.scalar_one())
            codebase_sum_result = await session.execute(
                select(func.sum(RepositoryAgentCodebaseProgress.progress)).where(
                    RepositoryAgentCodebaseProgress.repository_owner_name == owner_name,
                    RepositoryAgentCodebaseProgress.repository_name == repo_name,
                    RepositoryAgentCodebaseProgress.repository_workflow_run_id
                    == repository_workflow_run_id,
                )
            )
            snapshot.overall_progress = _compute_overall_progress(
                codebase_progress_sum=Decimal(
                    codebase_sum_result.scalar_one_or_none() or 0
                ),
                codebase_count=codebase_count,
                repository_activity_progress=activities,
            )
            snapshot.latest_event_at = event_timestamp
            snapshot.modified_at = event_timestamp

            return allocated_event_id

    async def complete_repository_activity(
        self,
        *,
        owner_name: str,
        repo_name: str,
        repository_workflow_run_id: str,
        activity_name: str,
    ) -> None:
        """Atomically complete a named repository progress unit and recalculate total."""
        async with get_startup_session() as session:
            snapshot_result = await session.execute(
                select(RepositoryAgentMdSnapshot)
                .where(
                    RepositoryAgentMdSnapshot.repository_owner_name == owner_name,
                    RepositoryAgentMdSnapshot.repository_name == repo_name,
                    RepositoryAgentMdSnapshot.repository_workflow_run_id
                    == repository_workflow_run_id,
                )
                .with_for_update()
            )
            snapshot = snapshot_result.scalar_one()
            activities = dict(snapshot.repository_activity_progress)
            if activity_name not in activities:
                raise ValueError(
                    f"Repository activity was not initialized: {activity_name}"
                )
            activities[activity_name] = 100
            snapshot.repository_activity_progress = activities

            codebase_sum_result = await session.execute(
                select(func.sum(RepositoryAgentCodebaseProgress.progress)).where(
                    RepositoryAgentCodebaseProgress.repository_owner_name == owner_name,
                    RepositoryAgentCodebaseProgress.repository_name == repo_name,
                    RepositoryAgentCodebaseProgress.repository_workflow_run_id
                    == repository_workflow_run_id,
                )
            )
            codebase_rows = await session.execute(
                select(func.count()).select_from(RepositoryAgentCodebaseProgress).where(
                    RepositoryAgentCodebaseProgress.repository_owner_name == owner_name,
                    RepositoryAgentCodebaseProgress.repository_name == repo_name,
                    RepositoryAgentCodebaseProgress.repository_workflow_run_id
                    == repository_workflow_run_id,
                )
            )
            count = int(codebase_rows.scalar_one())
            snapshot.overall_progress = _compute_overall_progress(
                codebase_progress_sum=Decimal(
                    codebase_sum_result.scalar_one_or_none() or 0
                ),
                codebase_count=count,
                repository_activity_progress=activities,
            )
            snapshot.modified_at = datetime.now(timezone.utc)

    async def complete_run(
        self,
        *,
        owner_name: str,
        repo_name: str,
        repository_workflow_run_id: str,
        statistics_payload: dict[str, object] | None = None,
    ) -> None:
        """Persist final statistics for a repository run."""
        if statistics_payload:
            logger.info(
                "Persisting statistics for {}/{} run_id={}: {} keys, has_cost={}",
                owner_name,
                repo_name,
                repository_workflow_run_id,
                len(statistics_payload),
                "total_estimated_cost_usd" in statistics_payload,
            )
        else:
            logger.warning(
                "No statistics payload to persist for {}/{} run_id={}",
                owner_name,
                repo_name,
                repository_workflow_run_id,
            )

        async with get_startup_session() as session:
            stmt = (
                update(RepositoryAgentMdSnapshot)
                .where(
                    RepositoryAgentMdSnapshot.repository_owner_name == owner_name,
                    RepositoryAgentMdSnapshot.repository_name == repo_name,
                    RepositoryAgentMdSnapshot.repository_workflow_run_id
                    == repository_workflow_run_id,
                )
                .values(statistics=statistics_payload, modified_at=func.now())
            )
            await session.execute(stmt)


__all__ = ["RepositoryAgentSnapshotWriter"]
