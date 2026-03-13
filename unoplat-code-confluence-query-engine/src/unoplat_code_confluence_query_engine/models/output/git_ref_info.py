"""Git reference metadata resolved at generation time."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class GitRefInfo(BaseModel):
    """Resolved default branch and head commit SHA for freshness metadata."""

    default_branch: str
    head_commit_sha: str

    model_config = ConfigDict(frozen=True, extra="forbid")
