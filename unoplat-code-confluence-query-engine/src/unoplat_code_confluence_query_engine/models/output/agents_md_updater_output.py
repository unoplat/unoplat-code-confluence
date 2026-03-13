"""Structured output contracts for AGENTS updater agent."""

from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class SectionId(str, Enum):
    """Identifiers for AGENTS.md section-scoped updater runs."""

    ENGINEERING_WORKFLOW = "engineering_workflow"
    DEPENDENCY_GUIDE = "dependency_guide"
    BUSINESS_DOMAIN = "business_domain"
    APP_INTERFACES = "app_interfaces"


class UpdaterFileChange(BaseModel):
    """Summary metadata for one updater-managed file."""

    path: str = Field(..., description="Absolute file path within codebase root")
    changed: bool = Field(..., description="Whether file content changed this run")
    change_type: Literal["created", "updated", "unchanged"] = Field(
        ..., description="Change classification for this file"
    )
    change_summary: str = Field(
        ..., description="Concise summary of the applied or detected change"
    )
    content_sha256: str | None = Field(
        default=None,
        description="Optional SHA-256 hash of final file content (no raw content persisted)",
    )

    model_config = ConfigDict(extra="forbid")


class AgentsMdUpdaterOutput(BaseModel):
    """Top-level output produced by AGENTS updater agent."""

    status: Literal["updated", "no_changes"] = Field(
        ..., description="Overall updater status"
    )
    touched_file_paths: list[str] = Field(
        default_factory=list,
        description="Absolute file paths touched by updater tools",
    )
    file_changes: list[UpdaterFileChange] = Field(
        default_factory=list,
        description="Summary metadata for each managed file",
    )

    model_config = ConfigDict(extra="forbid")


class SectionUpdaterRunRecord(BaseModel):
    """Record of a single section-scoped updater run, stored in workflow results."""

    section_id: SectionId = Field(..., description="Section identifier (e.g., 'engineering_workflow')")
    agent_name: str = Field(..., description="Agent name used for event tracking")
    output: AgentsMdUpdaterOutput = Field(..., description="Updater output for this section")

    model_config = ConfigDict(extra="forbid")


class ManagedBlockRunRecord(BaseModel):
    """Record of a managed-block lifecycle step (e.g., bootstrap), stored in workflow results."""

    lifecycle_step: Literal["bootstrap"] = Field(
        ..., description="Lifecycle step identifier"
    )
    agent_name: str = Field(..., description="Agent/activity name for event tracking")
    output: AgentsMdUpdaterOutput = Field(
        ..., description="File-change output from this lifecycle step"
    )

    model_config = ConfigDict(extra="forbid")
