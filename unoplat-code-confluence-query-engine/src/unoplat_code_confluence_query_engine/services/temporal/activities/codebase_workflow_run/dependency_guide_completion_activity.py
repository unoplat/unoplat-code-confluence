"""Dependency guide completion activity for Temporal workflows."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from loguru import logger
from temporalio import activity

from unoplat_code_confluence_query_engine.models.output.agent_md_output import (
    DependencyGuide,
    DependencyGuideEntry,
)
from unoplat_code_confluence_query_engine.services.agents_md.validation.dependency_overview import (
    collect_dependency_overview_errors,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.constants import (
    DEPENDENCY_OVERVIEW_ARTIFACT,
)
from unoplat_code_confluence_query_engine.services.temporal.event_stream_handler import (
    get_completion_namespaces,
)
from unoplat_code_confluence_query_engine.services.temporal.service_registry import (
    get_snapshot_writer,
)


class DependencyGuideCompletionActivity:
    """Activities for dependency-guide artifact writes and completion events."""

    @activity.defn
    async def write_dependency_overview(
        self,
        codebase_path: str,
        dependency_entries: list[dict[str, Any]],
        package_manager: str | None,
    ) -> bool:
        """Render and write dependencies_overview.md when content changes."""
        guide = DependencyGuide(
            dependencies=[
                DependencyGuideEntry.model_validate(item) for item in dependency_entries
            ]
        )
        rendered = _render_dependency_overview_markdown(
            guide=guide,
            package_manager=package_manager,
        )
        validation_errors = collect_dependency_overview_errors(rendered)
        if validation_errors:
            raise ValueError(
                "Rendered dependencies_overview.md failed validation: "
                + "; ".join(validation_errors)
            )

        target_path = Path(codebase_path) / DEPENDENCY_OVERVIEW_ARTIFACT
        existing_content = (
            target_path.read_text(encoding="utf-8") if target_path.exists() else None
        )
        if existing_content == rendered:
            logger.info(
                "[dependency_guide] {} is already up to date for {}",
                DEPENDENCY_OVERVIEW_ARTIFACT,
                codebase_path,
            )
            return False

        target_path.write_text(rendered, encoding="utf-8")
        logger.info(
            "[dependency_guide] Wrote {} for {} with {} dependencies",
            DEPENDENCY_OVERVIEW_ARTIFACT,
            codebase_path,
            len(_dependency_entries_for_render(guide)),
        )
        return True

    @activity.defn
    async def emit_dependency_guide_completion(
        self,
        repository_qualified_name: str,
        repository_workflow_run_id: str,
        codebase_name: str,
        programming_language: str,
    ) -> None:
        """Append a single completion event for dependency_guide."""
        if "/" not in repository_qualified_name:
            logger.warning(
                "[dependency_guide_completion] Invalid repository_qualified_name: {}",
                repository_qualified_name,
            )
            return

        owner_name, repo_name = repository_qualified_name.split("/", 1)
        writer = get_snapshot_writer()

        await writer.append_event_atomic(
            owner_name=owner_name,
            repo_name=repo_name,
            codebase_name=codebase_name,
            agent_name="dependency_guide",
            phase="result",
            message="Dependency guide completed",
            completion_namespaces=set(get_completion_namespaces(programming_language)),
            repository_workflow_run_id=repository_workflow_run_id,
        )

        logger.info(
            "[dependency_guide_completion] Emitted completion event for {}/{} codebase={}",
            owner_name,
            repo_name,
            codebase_name,
        )



def _render_dependency_overview_markdown(
    *,
    guide: DependencyGuide,
    package_manager: str | None,
) -> str:
    """Render the canonical dependencies overview markdown."""
    lines: list[str] = ["# Dependencies Overview", ""]
    normalized_package_manager = _normalize_inline_text(package_manager or "unknown")
    lines.append(
        "- **Package management**: "
        f"Use `{normalized_package_manager}` as the package manager for this codebase."
    )

    for entry in _dependency_entries_for_render(guide):
        lines.append(
            f"- **{_normalize_inline_text(entry.name)}**: "
            f"Purpose: {_normalize_inline_text(entry.purpose)}"
        )

    return "\n".join(lines) + "\n"


def _dependency_entries_for_render(guide: DependencyGuide) -> list[DependencyGuideEntry]:
    """Return dependency entries in their combined generation/reuse order."""
    return guide.dependencies


def _normalize_inline_text(value: str) -> str:
    """Collapse multiline agent output into stable single-line markdown text."""
    return " ".join(str(value).split())
