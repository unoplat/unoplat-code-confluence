"""Query-engine-specific Temporal workflow activity envelopes.

These envelopes are used only within the query-engine service
for Temporal activity parameters that don't need to be shared
across other services.
"""

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class AgentSnapshotCompleteEnvelope(BaseModel):
    """Envelope for persisting agent snapshot completion to database.

    Used by RepositoryAgentSnapshotActivity to call complete_run()
    and persist final agent_md_output and statistics.
    """

    owner_name: str = Field(..., description="Repository owner name")
    repo_name: str = Field(..., description="Repository name")
    repository_workflow_run_id: str = Field(
        ..., description="Workflow run ID for correct row targeting"
    )
    final_payload: dict[str, Any] = Field(
        ..., description="Final agent MD output payload to persist"
    )
    statistics_payload: Optional[dict[str, Any]] = Field(
        default=None, description="Usage statistics (optional, added by task-013)"
    )
    model_config = ConfigDict(extra="allow")

    @property
    def extras(self) -> dict[str, Any]:
        """Return any extra fields passed to the model (required for Temporal)."""
        return dict(self.model_extra or {})
