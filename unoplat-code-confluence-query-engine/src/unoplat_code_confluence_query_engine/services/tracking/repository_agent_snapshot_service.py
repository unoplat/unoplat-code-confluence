"""Helpers for writing repository agent snapshot events to Postgres."""

from __future__ import annotations

from decimal import Decimal
from typing import Any, Sequence

from loguru import logger
from sqlalchemy import func, select, text, update
from sqlalchemy.dialects.postgresql import insert
from unoplat_code_confluence_commons.repo_models import (
    RepoAgentSnapshotStatus,
    RepositoryAgentMdSnapshot,
)

from unoplat_code_confluence_query_engine.db.postgres.db import get_startup_session
from unoplat_code_confluence_query_engine.models.events.agent_events import (
    RepositoryAgentEventDelta,
)


class RepositoryAgentSnapshotWriter:
    """Persist agent lifecycle events and progress snapshots.

    This service is stateless - all identifying attributes (owner_name, repo_name)
    are passed as method parameters to avoid unnecessary instance allocation.
    """

    async def begin_run(
        self,
        *,
        owner_name: str,
        repo_name: str,
        repository_qualified_name: str,
        repository_workflow_run_id: str,
        codebase_names: Sequence[str],
    ) -> None:
        """Initialize the snapshot row with zeroed progress and empty event lists."""
        codebases: list[dict[str, Any]] = [
            {
                "codebase_name": codebase_name,
                "progress": 0.0,
                "events": [],
            }
            for codebase_name in codebase_names
        ]
        events_payload: dict[str, Any] = {
            "repository_name": repository_qualified_name,
            "repository_workflow_run_id": repository_workflow_run_id,
            "overall_progress": 0.0,
            "codebases": codebases,
        }

        # Initialize event_counters for each codebase
        event_counters = {name: {"next_id": 1} for name in codebase_names}

        # Initialize codebase_progress for each codebase
        codebase_progress: dict[str, dict[str, Any]] = {
            name: {"progress": 0.0, "completed_namespaces": []}
            for name in codebase_names
        }

        async with get_startup_session() as session:
            stmt = insert(RepositoryAgentMdSnapshot).values(
                repository_owner_name=owner_name,
                repository_name=repo_name,
                repository_workflow_run_id=repository_workflow_run_id,
                status=RepoAgentSnapshotStatus.RUNNING,
                events=events_payload,
                event_counters=event_counters,
                codebase_progress=codebase_progress,
                overall_progress=Decimal("0"),
                agent_md_output={},
            )

            stmt = stmt.on_conflict_do_update(
                index_elements=[
                    RepositoryAgentMdSnapshot.repository_owner_name,
                    RepositoryAgentMdSnapshot.repository_name,
                    RepositoryAgentMdSnapshot.repository_workflow_run_id,
                ],
                set_={
                    "status": RepoAgentSnapshotStatus.RUNNING,
                    "events": stmt.excluded.events,
                    "event_counters": stmt.excluded.event_counters,
                    "codebase_progress": stmt.excluded.codebase_progress,
                    "overall_progress": stmt.excluded.overall_progress,
                    "agent_md_output": stmt.excluded.agent_md_output,
                    "modified_at": func.now(),
                },
            )

            await session.execute(stmt)

    async def get_active_run_id(
        self,
        *,
        owner_name: str,
        repo_name: str,
    ) -> str | None:
        """Return the currently running workflow ID if a run is in progress."""
        async with get_startup_session() as session:
            stmt = (
                select(
                    RepositoryAgentMdSnapshot.status,
                    RepositoryAgentMdSnapshot.events,
                )
                .where(
                    RepositoryAgentMdSnapshot.repository_owner_name == owner_name,
                    RepositoryAgentMdSnapshot.repository_name == repo_name,
                )
                .limit(1)
            )

            result = await session.execute(stmt)
            row = result.first()
            if row is None:
                return None

            status, events_payload = row
            if status != RepoAgentSnapshotStatus.RUNNING:
                return None

            if not isinstance(events_payload, dict):
                return None

            events_dict: dict[str, Any] = events_payload
            run_id: str | None = events_dict.get("repository_workflow_run_id")
            if isinstance(run_id, str) and run_id:
                return run_id

            return None

    async def append_event(
        self,
        *,
        owner_name: str,
        repo_name: str,
        delta: RepositoryAgentEventDelta,
    ) -> None:
        """Append a new event and update progress metrics atomically."""
        event_payload = delta.codebase_delta.new_event.model_dump_json()

        query = text(
            """
            WITH target AS (
                SELECT elem.ordinality - 1 AS idx
                FROM repository_agent_md_snapshot ras,
                     LATERAL jsonb_array_elements(ras.events -> 'codebases') WITH ORDINALITY AS elem(codebase, ordinality)
                WHERE ras.repository_owner_name = :owner_name
                  AND ras.repository_name = :repo_name
                  AND elem.codebase ->> 'codebase_name' = :codebase_name
                LIMIT 1
            ),
            updated AS (
                UPDATE repository_agent_md_snapshot AS ras
                SET events = jsonb_set(
                        jsonb_set(
                            jsonb_set(
                                ras.events,
                                ARRAY['codebases', target.idx::text, 'events'],
                                COALESCE(
                                    ras.events #> ARRAY['codebases', target.idx::text, 'events'],
                                    '[]'::jsonb
                                ) || CAST(:event_payload AS jsonb),
                                true
                            ),
                            ARRAY['codebases', target.idx::text, 'progress'],
                            to_jsonb(CAST(:codebase_progress AS numeric)),
                            true
                        ),
                        ARRAY['overall_progress'],
                        to_jsonb(CAST(:overall_progress AS numeric)),
                        true
                    ),
                    modified_at = NOW()
                FROM target
                WHERE ras.repository_owner_name = :owner_name
                  AND ras.repository_name = :repo_name
                RETURNING 1
            )
            SELECT COALESCE((SELECT 1 FROM updated), 0) AS updated;
            """
        )

        params = {
            "owner_name": owner_name,
            "repo_name": repo_name,
            "codebase_name": delta.codebase_delta.codebase_name,
            "event_payload": event_payload,
            "codebase_progress": str(delta.codebase_delta.progress),
            "overall_progress": str(delta.overall_progress),
        }

        async with get_startup_session() as session:
            result = await session.execute(query, params)
            updated = result.scalar_one()

            if not updated:
                logger.error(
                    "Failed to append event for %s/%s codebase=%s",
                    owner_name,
                    repo_name,
                    delta.codebase_delta.codebase_name,
                )
                raise ValueError(
                    f"Codebase {delta.codebase_delta.codebase_name} is not initialized in events document"
                )

    async def append_event_atomic(
        self,
        *,
        owner_name: str,
        repo_name: str,
        codebase_name: str,
        agent_name: str,
        phase: str,
        message: str | None,
        completion_namespaces: set[str],
        repository_workflow_run_id: str,
    ) -> int:
        """Atomically allocate event ID, append event, and update progress.

        All state is managed in the DB via a single atomic UPDATE with CTEs.
        Progress is calculated as (completed_namespaces / total_namespaces) * 100.

        Args:
            codebase_name: Name of the codebase this event belongs to
            agent_name: Name of the agent that emitted this event
            phase: Event phase (tool.call, tool.result, result)
            message: Human-readable event message
            completion_namespaces: Set of agent names that count toward progress
            repository_workflow_run_id: Workflow run ID for row identification

        Returns:
            The allocated event ID
        """
        total_namespaces = len(completion_namespaces)
        completion_namespaces_list = list(completion_namespaces)

        query = text(
            """
            WITH current_state AS (
                SELECT
                    ras.event_counters,
                    ras.codebase_progress,
                    ras.events,
                    COALESCE((ras.event_counters -> :codebase_name ->> 'next_id')::int, 1) AS current_id,
                    COALESCE(ras.codebase_progress -> :codebase_name -> 'completed_namespaces', '[]'::jsonb) AS completed
                FROM repository_agent_md_snapshot ras
                WHERE ras.repository_owner_name = :owner_name
                  AND ras.repository_name = :repo_name
                  AND ras.repository_workflow_run_id = :workflow_run_id
            ),
            codebase_idx AS (
                SELECT elem.ordinality - 1 AS idx
                FROM current_state cs,
                     LATERAL jsonb_array_elements(cs.events -> 'codebases') WITH ORDINALITY AS elem(codebase, ordinality)
                WHERE elem.codebase ->> 'codebase_name' = :codebase_name
                LIMIT 1
            ),
            new_completed_calc AS (
                SELECT
                    cs.current_id AS allocated_id,
                    cs.current_id + 1 AS next_id,
                    CASE
                        WHEN :phase = 'result'
                             AND :agent_name = ANY(CAST(:completion_namespaces_arr AS text[]))
                             AND NOT EXISTS (
                                 SELECT 1 FROM jsonb_array_elements_text(cs.completed) AS elem
                                 WHERE elem = :agent_name
                             )
                        THEN cs.completed || to_jsonb(CAST(:agent_name AS text))
                        ELSE cs.completed
                    END AS new_completed
                FROM current_state cs
            ),
            progress_calc AS (
                SELECT
                    ncc.allocated_id,
                    ncc.next_id,
                    ncc.new_completed,
                    ROUND((jsonb_array_length(ncc.new_completed)::numeric / :total_namespaces) * 100, 2) AS new_codebase_progress
                FROM new_completed_calc ncc
            ),
            overall_progress_calc AS (
                SELECT
                    pc.allocated_id,
                    pc.next_id,
                    pc.new_completed,
                    pc.new_codebase_progress,
                    ROUND(AVG(
                        CASE
                            WHEN cb_key = :codebase_name THEN pc.new_codebase_progress
                            ELSE COALESCE((cb_val -> 'progress')::numeric, 0)
                        END
                    ), 2) AS new_overall_progress
                FROM progress_calc pc, current_state cs,
                     LATERAL jsonb_each(cs.codebase_progress) AS cb(cb_key, cb_val)
                GROUP BY pc.allocated_id, pc.next_id, pc.new_completed, pc.new_codebase_progress
            ),
            new_event_obj AS (
                SELECT jsonb_build_object(
                    'id', opc.allocated_id,
                    'event', :agent_name,
                    'phase', :phase,
                    'message', CAST(:message AS text)
                ) AS event_obj,
                opc.allocated_id,
                opc.next_id,
                opc.new_completed,
                opc.new_codebase_progress,
                opc.new_overall_progress
                FROM overall_progress_calc opc
            ),
            updated AS (
                UPDATE repository_agent_md_snapshot AS ras
                SET
                    event_counters = jsonb_set(
                        ras.event_counters,
                        ARRAY[:codebase_name, 'next_id'],
                        to_jsonb(neo.next_id),
                        true
                    ),
                    codebase_progress = jsonb_set(
                        jsonb_set(
                            ras.codebase_progress,
                            ARRAY[:codebase_name, 'completed_namespaces'],
                            neo.new_completed,
                            true
                        ),
                        ARRAY[:codebase_name, 'progress'],
                        to_jsonb(neo.new_codebase_progress),
                        true
                    ),
                    events = jsonb_set(
                        jsonb_set(
                            jsonb_set(
                                ras.events,
                                ARRAY['codebases', ci.idx::text, 'events'],
                                COALESCE(
                                    ras.events #> ARRAY['codebases', ci.idx::text, 'events'],
                                    '[]'::jsonb
                                ) || neo.event_obj,
                                true
                            ),
                            ARRAY['codebases', ci.idx::text, 'progress'],
                            to_jsonb(neo.new_codebase_progress),
                            true
                        ),
                        ARRAY['overall_progress'],
                        to_jsonb(neo.new_overall_progress),
                        true
                    ),
                    overall_progress = neo.new_overall_progress,
                    latest_event_at = NOW(),
                    modified_at = NOW()
                FROM new_event_obj neo, codebase_idx ci
                WHERE ras.repository_owner_name = :owner_name
                  AND ras.repository_name = :repo_name
                  AND ras.repository_workflow_run_id = :workflow_run_id
                RETURNING neo.allocated_id
            )
            SELECT COALESCE((SELECT allocated_id FROM updated), -1) AS allocated_id;
            """
        )

        params = {
            "owner_name": owner_name,
            "repo_name": repo_name,
            "workflow_run_id": repository_workflow_run_id,
            "codebase_name": codebase_name,
            "agent_name": agent_name,
            "phase": phase,
            "message": message,
            "completion_namespaces_arr": completion_namespaces_list,
            "total_namespaces": total_namespaces,
        }

        async with get_startup_session() as session:
            result = await session.execute(query, params)
            allocated_id = result.scalar_one()

            if allocated_id == -1:
                logger.error(
                    "Failed to append event atomically for %s/%s codebase=%s run_id=%s",
                    owner_name,
                    repo_name,
                    codebase_name,
                    repository_workflow_run_id,
                )
                raise ValueError(
                    f"Snapshot row not found for {owner_name}/{repo_name} "
                    f"run_id={repository_workflow_run_id}"
                )

            return allocated_id

    async def complete_run(
        self,
        *,
        owner_name: str,
        repo_name: str,
        final_payload: dict[str, object],
        statistics_payload: dict[str, object] | None = None,
    ) -> None:
        """Mark the snapshot as completed and persist the final agent output."""
        # Log what's being persisted
        if statistics_payload:
            logger.info(
                "Persisting statistics for {}/{}: {} keys, has_cost={}",
                owner_name,
                repo_name,
                len(statistics_payload),
                "total_estimated_cost_usd" in statistics_payload,
            )
        else:
            logger.warning(
                "No statistics payload to persist for {}/{}",
                owner_name,
                repo_name,
            )

        async with get_startup_session() as session:
            stmt = (
                update(RepositoryAgentMdSnapshot)
                .where(
                    RepositoryAgentMdSnapshot.repository_owner_name == owner_name,
                    RepositoryAgentMdSnapshot.repository_name == repo_name,
                )
                .values(
                    status=RepoAgentSnapshotStatus.COMPLETED,
                    agent_md_output=final_payload,
                    statistics=statistics_payload,
                    modified_at=func.now(),
                )
            )
            await session.execute(stmt)

    async def fail_run(
        self,
        *,
        owner_name: str,
        repo_name: str,
        error_payload: dict[str, object] | None = None,
    ) -> None:
        """Mark the snapshot as errored and optionally persist diagnostic payload."""
        payload = error_payload or {}
        async with get_startup_session() as session:
            stmt = (
                update(RepositoryAgentMdSnapshot)
                .where(
                    RepositoryAgentMdSnapshot.repository_owner_name == owner_name,
                    RepositoryAgentMdSnapshot.repository_name == repo_name,
                )
                .values(
                    status=RepoAgentSnapshotStatus.ERROR,
                    agent_md_output=payload,
                    modified_at=func.now(),
                )
            )
            await session.execute(stmt)

    async def fetch_events(
        self,
        *,
        owner_name: str,
        repo_name: str,
    ) -> dict[str, object] | None:
        """Fetch the current events document for diagnostics or fallback flows."""
        async with get_startup_session() as session:
            stmt = select(RepositoryAgentMdSnapshot.events).where(
                RepositoryAgentMdSnapshot.repository_owner_name == owner_name,
                RepositoryAgentMdSnapshot.repository_name == repo_name,
            )
            result = await session.execute(stmt)
            row = result.scalar_one_or_none()
            return row


__all__ = ["RepositoryAgentSnapshotWriter"]
