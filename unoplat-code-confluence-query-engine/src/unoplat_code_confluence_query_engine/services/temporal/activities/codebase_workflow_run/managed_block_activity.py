"""Temporal activity for bootstrapping the managed block in AGENTS.md."""

from __future__ import annotations

from temporalio import activity

from unoplat_code_confluence_query_engine.services.agents_md.managed_block import (
    bootstrap_managed_block,
)


class ManagedBlockActivity:
    """Activity for managed block lifecycle operations on AGENTS.md."""

    @activity.defn(name="bootstrap-managed-block")
    async def bootstrap(
        self,
        codebase_path: str,
        default_branch: str | None = None,
        head_commit_sha: str | None = None,
    ) -> bool:
        """Bootstrap managed block with markers, CRITICAL_INSTRUCTION, and freshness metadata.

        Args:
            codebase_path: Absolute path to codebase root.
            default_branch: Default branch name for freshness line (optional).
            head_commit_sha: HEAD commit SHA for freshness line (optional).

        Returns:
            True when AGENTS.md was created or updated, otherwise False.
        """
        return await bootstrap_managed_block(
            codebase_path, default_branch, head_commit_sha
        )
