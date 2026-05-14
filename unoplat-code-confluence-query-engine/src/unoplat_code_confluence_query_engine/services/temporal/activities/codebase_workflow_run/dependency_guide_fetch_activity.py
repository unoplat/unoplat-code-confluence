"""Dependency guide fetch activity for Temporal workflows."""

from __future__ import annotations

from pathlib import Path

from loguru import logger
from temporalio import activity

from unoplat_code_confluence_query_engine.db.postgres.code_confluence_dependency_repository import (
    fetch_codebase_dependencies,
)
from unoplat_code_confluence_query_engine.models.runtime.dependency_guide_target import (
    DependencyGuideDelta,
    DependencyGuideTarget,
)
from unoplat_code_confluence_query_engine.services.agents_md.validation.dependency_overview import (
    parse_dependency_overview_entries,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.constants import (
    DEPENDENCY_OVERVIEW_ARTIFACT,
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

    @activity.defn
    async def fetch_dependency_guide_delta(
        self,
        codebase_path: str,
        programming_language: str,
        package_manager: str,
    ) -> DependencyGuideDelta:
        """Fetch current targets and diff them against existing dependencies_overview.md."""
        dependency_targets = await self.fetch_codebase_dependencies(
            codebase_path=codebase_path,
            programming_language=programming_language,
            package_manager=package_manager,
        )
        current_names = {target.name for target in dependency_targets}

        overview_path = Path(codebase_path) / DEPENDENCY_OVERVIEW_ARTIFACT
        if not overview_path.exists():
            logger.info(
                "[dependency_guide_fetch] No existing {} for codebase_path={}; generating all {} targets",
                DEPENDENCY_OVERVIEW_ARTIFACT,
                codebase_path,
                len(dependency_targets),
            )
            return DependencyGuideDelta(targets_to_generate=dependency_targets)

        previous_entries = parse_dependency_overview_entries(
            overview_path.read_text(encoding="utf-8")
        )
        targets_to_generate = [
            target for target in dependency_targets if target.name not in previous_entries
        ]
        reusable_entries = [
            {"name": target.name, "purpose": previous_entries[target.name]}
            for target in dependency_targets
            if target.name in previous_entries
        ]
        removed_names = [name for name in previous_entries if name not in current_names]

        logger.info(
            "[dependency_guide_fetch] Dependency guide delta for codebase_path={}: reusable={} generate={} removed={}",
            codebase_path,
            len(reusable_entries),
            len(targets_to_generate),
            len(removed_names),
        )
        return DependencyGuideDelta(
            reusable_entries=reusable_entries,
            targets_to_generate=targets_to_generate,
            removed_names=removed_names,
        )
