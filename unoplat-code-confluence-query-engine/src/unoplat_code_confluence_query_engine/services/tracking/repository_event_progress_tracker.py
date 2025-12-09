from decimal import ROUND_HALF_UP, Decimal
from typing import Any, Dict

from loguru import logger

from unoplat_code_confluence_query_engine.models.events.agent_events import (
    AgentEventPayload,
    CodebaseEventDelta,
    RepositoryAgentEventDelta,
)
from unoplat_code_confluence_query_engine.services.tracking.repository_agent_snapshot_service import (
    RepositoryAgentSnapshotWriter,
)


class RepositoryEventProgressTracker:
    """Track per-codebase progress and persist ElectricSQL event deltas."""

    def __init__(
        self,
        snapshot_writer: RepositoryAgentSnapshotWriter,
        *,
        repository_qualified_name: str,
        connection_id: str,
        owner_name: str,
        repo_name: str,
        codebase_names: list[str],
        completion_namespaces: set[str],
    ) -> None:
        self._writer = snapshot_writer
        self._repository_qualified_name = repository_qualified_name
        self._connection_id = connection_id
        self._owner_name = owner_name
        self._repo_name = repo_name
        self._completion_namespaces = completion_namespaces
        self._progress_increment = (
            Decimal("100") / Decimal(len(completion_namespaces))
            if completion_namespaces
            else Decimal("0")
        )
        self._codebase_state: Dict[str, Dict[str, Any]] = {
            name: {"progress": Decimal("0"), "completed_namespaces": set()}
            for name in codebase_names
        }

    def _quantize(self, value: Decimal) -> Decimal:
        return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def _compute_overall_progress(self) -> Decimal:
        if not self._codebase_state:
            return Decimal("0")
        total_progress = sum(
            state["progress"] for state in self._codebase_state.values()
        )
        return self._quantize(total_progress / Decimal(len(self._codebase_state)))

    async def persist_codebase_event(
        self, event_name: str, event_data: Dict[str, Any], event_identifier: int
    ) -> None:
        parts = event_name.split(":", 2)
        if len(parts) != 3:
            return

        codebase_name, event_namespace, phase = parts
        state = self._codebase_state.get(codebase_name)
        if state is None:
            return

        completed_namespaces: set[str] = state["completed_namespaces"]
        if (
            phase == "result"
            and event_namespace in self._completion_namespaces
            and event_namespace not in completed_namespaces
        ):
            completed_namespaces.add(event_namespace)
            if len(completed_namespaces) == len(self._completion_namespaces):
                state["progress"] = Decimal("100")
            else:
                state["progress"] = min(
                    Decimal("100"), state["progress"] + self._progress_increment
                )

        progress_value = self._quantize(state["progress"])
        overall_progress = self._compute_overall_progress()

        message = event_data.get("message")
        if message is not None and not isinstance(message, str):
            message = str(message)

        payload = RepositoryAgentEventDelta(
            repository_name=self._repository_qualified_name,
            overall_progress=overall_progress,
            codebase_delta=CodebaseEventDelta(
                codebase_name=codebase_name,
                progress=progress_value,
                new_event=AgentEventPayload(
                    id=str(event_identifier),
                    event=(
                        f"{self._repository_qualified_name}:{event_namespace}:{phase}"
                    ),
                    phase=phase,
                    message=message,
                ),
            ),
        )

        try:
            await self._writer.append_event(
                owner_name=self._owner_name,
                repo_name=self._repo_name,
                delta=payload,
            )
        except Exception as persist_error:  # noqa: BLE001
            logger.warning(
                "SSE[{}] Failed to append event {} for {}/{}: {}",
                self._connection_id,
                event_name,
                self._owner_name,
                self._repo_name,
                persist_error,
            )

    async def append_final_events(self, event_identifier: int) -> None:
        if not self._codebase_state:
            return

        final_event_name = (
            f"{self._repository_qualified_name}:"
            "aggregated_final_summary_agent:agent_md_output"
        )

        for state in self._codebase_state.values():
            state["progress"] = Decimal("100")

        for codebase_name in self._codebase_state:
            payload = RepositoryAgentEventDelta(
                repository_name=self._repository_qualified_name,
                overall_progress=Decimal("100"),
                codebase_delta=CodebaseEventDelta(
                    codebase_name=codebase_name,
                    progress=Decimal("100"),
                    new_event=AgentEventPayload(
                        id=str(event_identifier),
                        event=final_event_name,
                        phase="agent_md_output",
                        message=f"Aggregated summary for {codebase_name} ready",
                    ),
                ),
            )

            try:
                await self._writer.append_event(
                    owner_name=self._owner_name,
                    repo_name=self._repo_name,
                    delta=payload,
                )
            except Exception as persist_error:  # noqa: BLE001
                logger.warning(
                    "SSE[{}] Failed to append final event for {}/{} codebase {}: {}",
                    self._connection_id,
                    self._owner_name,
                    self._repo_name,
                    codebase_name,
                    persist_error,
                )
