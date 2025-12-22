"""Pydantic models that describe repository agent event progress payloads."""

from __future__ import annotations

from decimal import Decimal
from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, Field

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


class AgentEventPayload(BaseModel):
    """Snapshot of the latest agent event per codebase."""

    model_config = ConfigDict(extra="forbid")

    id: str
    event: str
    phase: str
    message: Optional[str] = None


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
    "AgentEventPayload",
    "CodebaseEventDelta",
    "RepositoryAgentEventDelta",
    "Percentage",
]
