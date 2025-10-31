"""Helpers for writing repository agent snapshot events to Postgres."""

from __future__ import annotations

import json
from typing import Sequence

from loguru import logger
from sqlalchemy import func, select, text, update
from sqlalchemy.dialects.postgresql import insert
from unoplat_code_confluence_commons.repo_models import (
    RepoAgentSnapshotStatus,
    RepositoryAgentMdSnapshot,
)

from unoplat_code_confluence_query_engine.db.postgres.db import get_session
from unoplat_code_confluence_query_engine.models.agent_events import (
    RepositoryAgentEventDelta,
)


class RepositoryAgentSnapshotWriter:
    """Persist agent lifecycle events and progress snapshots."""

    def __init__(self, owner_name: str, repo_name: str) -> None:
        self.owner_name = owner_name
        self.repo_name = repo_name

    async def begin_run(
        self,
        *,
        repository_qualified_name: str,
        repository_workflow_run_id: str | None,
        codebase_names: Sequence[str],
    ) -> None:
        """Initialize the snapshot row with zeroed progress and empty event lists."""
        codebases = [
            {
                "codebase_name": codebase_name,
                "progress": 0.0,
                "events": [],
            }
            for codebase_name in codebase_names
        ]
        events_payload = {
            "repository_name": repository_qualified_name,
            "repository_workflow_run_id": repository_workflow_run_id,
            "overall_progress": 0.0,
            "codebases": codebases,
        }

        async with get_session() as session:
            stmt = insert(RepositoryAgentMdSnapshot).values(
                repository_owner_name=self.owner_name,
                repository_name=self.repo_name,
                status=RepoAgentSnapshotStatus.RUNNING,
                events=events_payload,
                agent_md_output={},
            )

            stmt = stmt.on_conflict_do_update(
                index_elements=[
                    RepositoryAgentMdSnapshot.repository_owner_name,
                    RepositoryAgentMdSnapshot.repository_name,
                ],
                set_={
                    "status": RepoAgentSnapshotStatus.RUNNING,
                    "events": stmt.excluded.events,
                    "agent_md_output": stmt.excluded.agent_md_output,
                    "modified_at": func.now(),
                },
            )

            await session.execute(stmt)

    async def get_active_run_id(self) -> str | None:
        """Return the currently running workflow ID if a run is in progress."""

        async with get_session() as session:
            stmt = (
                select(
                    RepositoryAgentMdSnapshot.status,
                    RepositoryAgentMdSnapshot.events,
                )
                .where(
                    RepositoryAgentMdSnapshot.repository_owner_name == self.owner_name,
                    RepositoryAgentMdSnapshot.repository_name == self.repo_name,
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

            run_id = events_payload.get("repository_workflow_run_id")
            if isinstance(run_id, str) and run_id:
                return run_id

            return None

    async def append_event(self, delta: RepositoryAgentEventDelta) -> None:
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
            "owner_name": self.owner_name,
            "repo_name": self.repo_name,
            "codebase_name": delta.codebase_delta.codebase_name,
            "event_payload": event_payload,
            "codebase_progress": str(delta.codebase_delta.progress),
            "overall_progress": str(delta.overall_progress),
        }

        async with get_session() as session:
            result = await session.execute(query, params)
            updated = result.scalar_one()

            if not updated:
                logger.error(
                    "Failed to append event for %s/%s codebase=%s",
                    self.owner_name,
                    self.repo_name,
                    delta.codebase_delta.codebase_name,
                )
                raise ValueError(
                    f"Codebase {delta.codebase_delta.codebase_name} is not initialized in events document"
                )

    async def complete_run(self, *, final_payload: dict[str, object]) -> None:
        """Mark the snapshot as completed and persist the final agent output."""
        async with get_session() as session:
            stmt = (
                update(RepositoryAgentMdSnapshot)
                .where(
                    RepositoryAgentMdSnapshot.repository_owner_name == self.owner_name,
                    RepositoryAgentMdSnapshot.repository_name == self.repo_name,
                )
                .values(
                    status=RepoAgentSnapshotStatus.COMPLETED,
                    agent_md_output=final_payload,
                    modified_at=func.now(),
                )
            )
            await session.execute(stmt)

    async def fail_run(self, *, error_payload: dict[str, object] | None = None) -> None:
        """Mark the snapshot as errored and optionally persist diagnostic payload."""
        payload = error_payload or {}
        async with get_session() as session:
            stmt = (
                update(RepositoryAgentMdSnapshot)
                .where(
                    RepositoryAgentMdSnapshot.repository_owner_name == self.owner_name,
                    RepositoryAgentMdSnapshot.repository_name == self.repo_name,
                )
                .values(
                    status=RepoAgentSnapshotStatus.ERROR,
                    agent_md_output=payload,
                    modified_at=func.now(),
                )
            )
            await session.execute(stmt)

    async def fetch_events(self) -> dict[str, object] | None:
        """Fetch the current events document for diagnostics or fallback flows."""
        async with get_session() as session:
            stmt = select(RepositoryAgentMdSnapshot.events).where(
                RepositoryAgentMdSnapshot.repository_owner_name == self.owner_name,
                RepositoryAgentMdSnapshot.repository_name == self.repo_name,
            )
            result = await session.execute(stmt)
            row = result.scalar_one_or_none()
            return row


__all__ = ["RepositoryAgentSnapshotWriter"]
