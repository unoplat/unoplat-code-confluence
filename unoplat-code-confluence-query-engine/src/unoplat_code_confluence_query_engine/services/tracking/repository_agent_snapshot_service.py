"""Helpers for writing repository agent snapshot events to Postgres."""

from __future__ import annotations

from collections.abc import Mapping, Sequence, Set
from datetime import datetime, timezone
from decimal import ROUND_HALF_UP, Decimal
from typing import TypedDict

from loguru import logger
from sqlalchemy import and_, bindparam, func, select, text, update
from sqlalchemy.dialects.postgresql import JSONB, insert
from unoplat_code_confluence_commons.repo_models import (
    RepositoryAgentCodebaseProgress,
    RepositoryAgentEvent,
    RepositoryAgentMdSnapshot,
    RepositoryWorkflowOperation,
    RepositoryWorkflowRun,
)
from unoplat_code_confluence_commons.workflow_models import JobStatus

from unoplat_code_confluence_query_engine.db.postgres.db import get_startup_session
from unoplat_code_confluence_query_engine.models.output.agent_md_output import (
    RepositoryAgentMdOutputSnapshot,
)
from unoplat_code_confluence_query_engine.models.output.engineering_workflow_output import (
    EngineeringWorkflow,
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


def _normalize_completed_namespaces(completed_namespaces: Set[str]) -> list[str]:
    return sorted(completed_namespaces)


def _normalize_tool_args(
    tool_args: Mapping[str, object] | None,
) -> dict[str, object] | None:
    if tool_args is None:
        return None
    return dict(tool_args)


def _extract_engineering_workflow_payload(
    repository_agent_md_snapshot: RepositoryAgentMdOutputSnapshot,
    codebase_name: str,
) -> EngineeringWorkflow | None:
    """Return the engineering workflow for one codebase from a repository snapshot."""
    codebase_snapshot = repository_agent_md_snapshot.codebases.get(codebase_name)
    if codebase_snapshot is None:
        return None
    return codebase_snapshot.engineering_workflow


async def fetch_latest_completed_codebase_engineering_workflow(
    *,
    owner_name: str,
    repo_name: str,
    codebase_name: str,
    exclude_repository_workflow_run_id: str,
) -> EngineeringWorkflow | None:
    """Fetch the latest previous structured engineering workflow for carry-forward.

    Only the newest completed repository snapshot is considered. If that snapshot
    does not contain this codebase or its engineering workflow, historical rows
    are intentionally ignored and ``None`` is returned.
    """
    async with get_startup_session() as session:
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
                RepositoryAgentMdSnapshot.repository_owner_name == owner_name,
                RepositoryAgentMdSnapshot.repository_name == repo_name,
                RepositoryAgentMdSnapshot.repository_workflow_run_id
                != exclude_repository_workflow_run_id,
                RepositoryWorkflowRun.status == JobStatus.COMPLETED.value,
                RepositoryWorkflowRun.operation.in_(
                    (
                        RepositoryWorkflowOperation.AGENTS_GENERATION,
                        RepositoryWorkflowOperation.AGENT_MD_UPDATE,
                    )
                ),
            )
            .order_by(
                RepositoryWorkflowRun.completed_at.desc().nulls_last(),
                RepositoryWorkflowRun.started_at.desc(),
                RepositoryWorkflowRun.repository_workflow_run_id.desc(),
            )
        )
        result = await session.execute(stmt.limit(1))
        snapshot = result.scalar_one_or_none()
        if snapshot is None:
            return None

        repository_agent_md_snapshot: RepositoryAgentMdOutputSnapshot = (
            RepositoryAgentMdOutputSnapshot.model_validate(snapshot.agent_md_output)
        )
        engineering_workflow_payload = _extract_engineering_workflow_payload(
            repository_agent_md_snapshot,
            codebase_name,
        )
        if engineering_workflow_payload is None:
            return None

        try:
            return EngineeringWorkflow.model_validate(engineering_workflow_payload)
        except Exception as validation_error:
            logger.error(
                "Invalid previous engineering_workflow for {}/{} codebase={} run_id={}: {}",
                owner_name,
                repo_name,
                codebase_name,
                snapshot.repository_workflow_run_id,
                validation_error,
            )
            raise validation_error

    return None


class RepositoryAgentSnapshotWriter:
    """Persist agent lifecycle events and progress snapshots."""

    async def begin_run(
        self,
        *,
        owner_name: str,
        repo_name: str,
        repository_qualified_name: str,
        repository_workflow_run_id: str,
        codebase_names: Sequence[str],
    ) -> None:
        """Initialize snapshot and normalized progress rows for a run."""
        async with get_startup_session() as session:
            snapshot_stmt = insert(RepositoryAgentMdSnapshot).values(
                repository_owner_name=owner_name,
                repository_name=repo_name,
                repository_workflow_run_id=repository_workflow_run_id,
                overall_progress=ZERO_DECIMAL,
                latest_event_at=None,
                agent_md_output={
                    "repository": repository_qualified_name,
                    "codebases": {},
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
        phase: str,
        message: str | None,
        tool_name: str | None = None,
        tool_call_id: str | None = None,
        tool_args: Mapping[str, object] | None = None,
        tool_result_content: str | None = None,
        completion_namespaces: set[str],
        repository_workflow_run_id: str,
    ) -> int:
        """Atomically allocate an event id, persist the event, and update progress."""
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
            if phase == "result" and agent_name in completion_namespaces:
                completed_namespaces.add(agent_name)

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
                    event=agent_name,
                    phase=phase,
                    message=message,
                    tool_name=tool_name,
                    tool_call_id=tool_call_id,
                    tool_args=_normalize_tool_args(tool_args),
                    tool_result_content=tool_result_content,
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

            overall_progress_stmt = select(
                func.avg(RepositoryAgentCodebaseProgress.progress)
            ).where(
                RepositoryAgentCodebaseProgress.repository_owner_name == owner_name,
                RepositoryAgentCodebaseProgress.repository_name == repo_name,
                RepositoryAgentCodebaseProgress.repository_workflow_run_id
                == repository_workflow_run_id,
            )
            overall_progress_result = await session.execute(overall_progress_stmt)
            overall_progress_raw = overall_progress_result.scalar_one_or_none()
            overall_progress = _quantize_percentage(
                Decimal(overall_progress_raw)
                if overall_progress_raw is not None
                else ZERO_DECIMAL
            )

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

            snapshot.overall_progress = overall_progress
            snapshot.latest_event_at = event_timestamp
            snapshot.modified_at = event_timestamp

            return allocated_event_id

    async def patch_codebase_output(
        self,
        *,
        owner_name: str,
        repo_name: str,
        repository_workflow_run_id: str,
        codebase_name: str,
        codebase_patch: dict[str, object],
    ) -> None:
        """Atomically merge a patch into one codebase's agent_md_output object."""
        async with get_startup_session() as session:
            stmt = text(
                """
                UPDATE repository_agent_md_snapshot
                SET agent_md_output = jsonb_set(
                    agent_md_output,
                    ARRAY['codebases', :codebase_name]::text[],
                    COALESCE(
                        agent_md_output #> ARRAY['codebases', :codebase_name]::text[],
                        '{}'::jsonb
                    ) || :codebase_patch,
                    true
                ),
                modified_at = NOW()
                WHERE repository_owner_name = :owner_name
                  AND repository_name = :repo_name
                  AND repository_workflow_run_id = :repository_workflow_run_id
                """
            ).bindparams(bindparam("codebase_patch", type_=JSONB))
            connection = await session.connection()
            result = await connection.execute(
                stmt,
                {
                    "owner_name": owner_name,
                    "repo_name": repo_name,
                    "repository_workflow_run_id": repository_workflow_run_id,
                    "codebase_name": codebase_name,
                    "codebase_patch": codebase_patch,
                },
            )

            if result.rowcount == 0:
                logger.error(
                    "Snapshot row missing while patching {}/{} codebase={} run_id={}",
                    owner_name,
                    repo_name,
                    codebase_name,
                    repository_workflow_run_id,
                )
                raise ValueError(
                    f"Snapshot row not found for {owner_name}/{repo_name} "
                    f"run_id={repository_workflow_run_id}"
                )

    async def complete_run(
        self,
        *,
        owner_name: str,
        repo_name: str,
        repository_workflow_run_id: str,
        final_payload: dict[str, object] | None = None,
        statistics_payload: dict[str, object] | None = None,
    ) -> None:
        """Persist final statistics and optionally a legacy final agent output."""
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

        values: dict[str, object] = {
            "statistics": statistics_payload,
            "modified_at": func.now(),
        }
        if final_payload is not None:
            values["agent_md_output"] = final_payload

        async with get_startup_session() as session:
            stmt = (
                update(RepositoryAgentMdSnapshot)
                .where(
                    RepositoryAgentMdSnapshot.repository_owner_name == owner_name,
                    RepositoryAgentMdSnapshot.repository_name == repo_name,
                    RepositoryAgentMdSnapshot.repository_workflow_run_id
                    == repository_workflow_run_id,
                )
                .values(**values)
            )
            await session.execute(stmt)


__all__ = [
    "RepositoryAgentSnapshotWriter",
    "fetch_latest_completed_codebase_engineering_workflow",
]
