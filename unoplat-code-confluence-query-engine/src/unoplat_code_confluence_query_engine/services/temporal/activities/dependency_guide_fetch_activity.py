"""Dependency guide fetch activity for Temporal workflows."""

from __future__ import annotations

from loguru import logger
from temporalio import activity

from unoplat_code_confluence_query_engine.db.postgres.code_confluence_dependency_repository import (
    fetch_codebase_dependencies,
)
from unoplat_code_confluence_query_engine.models.runtime.dependency_guide_target import (
    DependencyGuideTarget,
)
from unoplat_code_confluence_query_engine.services.repository.dependency_guide_normalization_service import (
    normalize_dependency_guide_targets,
)


class DependencyGuideFetchActivity:
    """Activity for fetching dependency names from PostgreSQL."""

    @activity.defn
    async def fetch_codebase_dependencies(
        self,
        codebase_path: str,
        programming_language: str,
        package_manager: str,
    ) -> list[DependencyGuideTarget]:
        """Fetch normalized dependency-guide targets for a codebase path."""
        logger.info(
            "[dependency_guide_fetch] Fetching dependencies for codebase_path={}",
            codebase_path,
        )
        dependency_names = await fetch_codebase_dependencies(codebase_path)
        dependency_targets = normalize_dependency_guide_targets(
            dependency_names=dependency_names,
            programming_language=programming_language,
            package_manager=package_manager,
        )
        logger.info(
            "[dependency_guide_fetch] Normalized {} raw dependencies into {} targets for codebase_path={}",
            len(dependency_names),
            len(dependency_targets),
            codebase_path,
        )
        return dependency_targets
