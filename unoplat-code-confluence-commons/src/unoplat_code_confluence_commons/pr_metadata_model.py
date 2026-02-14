from datetime import datetime, timezone
from typing import Literal

from pydantic import AwareDatetime, BaseModel, Field


class PrMetadata(BaseModel):
    """Persisted metadata for a manual AGENTS.md PR publication.

    Stored as JSONB on RepositoryAgentMdSnapshot.pr_metadata.
    One row per (owner, repo, workflow_run_id) — one-shot semantics
    mean the first successful publish writes this; subsequent calls
    for the same run are no-ops.
    """

    pr_number: int | None = Field(default=None)
    pr_url: str | None = Field(default=None)
    branch_name: str | None = Field(default=None)
    status: Literal["modified", "no_changes"] = Field(...)
    changed_files: list[str] = Field(default_factory=list)
    message: str = Field(...)
    created_at: AwareDatetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )
    updated_at: AwareDatetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )
