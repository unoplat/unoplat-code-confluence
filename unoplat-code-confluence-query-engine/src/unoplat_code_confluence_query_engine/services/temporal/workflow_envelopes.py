"""Query-engine-specific Temporal workflow activity envelopes.

These envelopes are used only within the query-engine service
for Temporal activity parameters that don't need to be shared
across other services.
"""

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class AgentSnapshotCodebasePatchEnvelope(BaseModel):
    """Envelope for atomically patching one codebase in agent_md_output."""

    owner_name: str = Field(..., description="Repository owner name")
    repo_name: str = Field(..., description="Repository name")
    repository_workflow_run_id: str = Field(
        ..., description="Workflow run ID for correct row targeting"
    )
    codebase_name: str = Field(..., description="Codebase key under agent_md_output.codebases")
    codebase_patch: dict[str, Any] = Field(
        ..., description="JSON object to merge into the codebase snapshot"
    )
    model_config = ConfigDict(extra="allow")

    @property
    def extras(self) -> dict[str, Any]:
        """Return any extra fields passed to the model (required for Temporal)."""
        return dict(self.model_extra or {})


class AgentSnapshotBeginRunEnvelope(BaseModel):
    """Envelope for initializing repository agent snapshot/progress rows."""

    owner_name: str = Field(..., description="Repository owner name")
    repo_name: str = Field(..., description="Repository name")
    repository_qualified_name: str = Field(..., description="owner/repo qualified name")
    repository_workflow_run_id: str = Field(
        ..., description="Temporal run ID for the repository workflow"
    )
    codebase_names: list[str] = Field(
        default_factory=list,
        description="Codebase names to initialize progress tracking for",
    )
    model_config = ConfigDict(extra="allow")

    @property
    def extras(self) -> dict[str, Any]:
        """Return any extra fields passed to the model (required for Temporal)."""
        return dict(self.model_extra or {})


class AgentSnapshotCompleteEnvelope(BaseModel):
    """Envelope for persisting agent snapshot completion to database.

    Used by RepositoryAgentSnapshotActivity to call complete_run()
    and persist final statistics without overwriting partial agent_md_output.
    """

    owner_name: str = Field(..., description="Repository owner name")
    repo_name: str = Field(..., description="Repository name")
    repository_workflow_run_id: str = Field(
        ..., description="Workflow run ID for correct row targeting"
    )
    final_payload: Optional[dict[str, Any]] = Field(
        default=None,
        description="Optional final agent MD output payload to persist for legacy callers",
    )
    statistics_payload: Optional[dict[str, Any]] = Field(
        default=None, description="Usage statistics (optional, added by task-013)"
    )
    model_config = ConfigDict(extra="allow")

    @property
    def extras(self) -> dict[str, Any]:
        """Return any extra fields passed to the model (required for Temporal)."""
        return dict(self.model_extra or {})
