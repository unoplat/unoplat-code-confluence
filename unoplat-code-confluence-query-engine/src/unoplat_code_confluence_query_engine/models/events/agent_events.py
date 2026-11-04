"""Pydantic models that describe repository agent event progress payloads."""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
import re
from types import MappingProxyType
from typing import Annotated, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

# Percentages are reported in the range [0, 100] with two decimal points.
Percentage = Annotated[
    Decimal,
    Field(
        ge=Decimal("0"),
        le=Decimal("100"),
        max_digits=5,
        decimal_places=2,
    ),
]


type AgentEventPhase = Literal["tool.call", "tool.result", "result"]

AGENT_EVENT_MESSAGES: Mapping[AgentEventPhase, str] = MappingProxyType(
    {
        "tool.call": "Tool call started",
        "tool.result": "Tool call finished",
        "result": "Agent step completed",
    }
)

_TOOL_NAME_PATTERN = re.compile(r"[A-Za-z0-9_.:-]{1,128}")
_TOOL_CALL_ID_PATTERN = re.compile(r"[A-Za-z0-9_.:|-]{1,200}")


class PersistedAgentEvent(BaseModel):
    """The only agent event fields allowed in the database.

    The stream handler and the database writer both build this model. Tool names
    and call IDs come from the model or provider, so an invalid value is dropped
    rather than raised, which keeps the event row and its progress update. An
    invalid agent name or phase is a programming error and raises.
    """

    model_config = ConfigDict(extra="forbid", frozen=True, hide_input_in_errors=True)

    agent_name: str = Field(pattern=r"^[a-z][a-z0-9_]{0,79}$")
    phase: AgentEventPhase
    tool_name: str | None = None
    tool_call_id: str | None = None

    @field_validator("tool_name", mode="before")
    @classmethod
    def _discard_invalid_tool_name(cls, value: object) -> str | None:
        if isinstance(value, str) and _TOOL_NAME_PATTERN.fullmatch(value):
            return value
        return None

    @field_validator("tool_call_id", mode="before")
    @classmethod
    def _discard_invalid_tool_call_id(cls, value: object) -> str | None:
        if isinstance(value, str) and _TOOL_CALL_ID_PATTERN.fullmatch(value):
            return value
        return None

    @property
    def message(self) -> str:
        """Static message for this event's phase."""
        return AGENT_EVENT_MESSAGES[self.phase]


class AgentEventPayload(BaseModel):
    """Snapshot of the latest agent event per codebase."""

    model_config = ConfigDict(extra="forbid")

    id: int
    event: str
    phase: str
    message: Optional[str] = None
    tool_name: Optional[str] = None
    tool_call_id: Optional[str] = None


class CodebaseEventDelta(BaseModel):
    """Delta for an individual codebase when a new event arrives."""

    model_config = ConfigDict(extra="forbid")

    codebase_name: str
    progress: Percentage
    new_event: AgentEventPayload


class RepositoryAgentEventDelta(BaseModel):
    """Delta payload for repository-level agent progress updates."""

    model_config = ConfigDict(extra="forbid")

    repository_name: str
    overall_progress: Percentage
    codebase_delta: CodebaseEventDelta


__all__ = [
    "AGENT_EVENT_MESSAGES",
    "AgentEventPayload",
    "AgentEventPhase",
    "CodebaseEventDelta",
    "RepositoryAgentEventDelta",
    "Percentage",
    "PersistedAgentEvent",
]
