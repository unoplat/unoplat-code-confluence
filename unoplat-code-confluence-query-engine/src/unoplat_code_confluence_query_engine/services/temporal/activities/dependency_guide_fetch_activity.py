"""Dependency guide fetch activity for Temporal workflows."""

from __future__ import annotations

from loguru import logger
from temporalio import activity

from unoplat_code_confluence_query_engine.db.postgres.code_confluence_dependency_repository import (
    fetch_codebase_dependencies,
)


class DependencyGuideFetchActivity:
    """Activity for fetching dependency names from PostgreSQL."""

    @activity.defn
    async def fetch_codebase_dependencies(self, codebase_path: str) -> list[str]:
        """Fetch dependency names for a codebase path via PostgreSQL."""
        logger.info(
            "[dependency_guide_fetch] Fetching dependencies for codebase_path={}",
            codebase_path,
        )
        return await fetch_codebase_dependencies(codebase_path)
