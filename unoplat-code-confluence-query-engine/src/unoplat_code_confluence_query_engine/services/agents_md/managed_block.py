"""Bootstrap and maintain the managed block in codebase-local AGENTS.md."""

from __future__ import annotations

from datetime import UTC, datetime
import hashlib
from pathlib import Path

import aiofiles

from unoplat_code_confluence_query_engine.models.output.agents_md_updater_output import (
    AgentsMdUpdaterOutput,
    UpdaterFileChange,
)

MANAGED_BLOCK_BEGIN = "<!-- UNOPLAT_CODE_CONFLUENCE_CONTEXT:BEGIN -->"
MANAGED_BLOCK_END = "<!-- UNOPLAT_CODE_CONFLUENCE_CONTEXT:END -->"

SECTION_HEADINGS: list[str] = [
    "## Engineering Workflow",
    "## Dependency Guide",
    "## Business Logic Domain",
    "## App Interfaces",
]


def _build_freshness_line(
    default_branch: str,
    head_commit_sha: str,
) -> str:
    """Build the freshness metadata line for the CRITICAL_INSTRUCTION block."""
    today = datetime.now(tz=UTC).strftime("%Y-%m-%d")
    return (
        f"> Generated from branch `{default_branch}` at commit "
        f"`{head_commit_sha}` ({today}). Content may become stale as new commits land."
    )


def _build_managed_block(
    default_branch: str | None,
    head_commit_sha: str | None,
) -> str:
    """Build the complete managed block content."""
    lines: list[str] = [MANAGED_BLOCK_BEGIN, "<CRITICAL_INSTRUCTION>", ""]

    if default_branch and head_commit_sha:
        lines.append(_build_freshness_line(default_branch, head_commit_sha))
        lines.append("")

    lines.append("</CRITICAL_INSTRUCTION>")
    lines.append("")

    for heading in SECTION_HEADINGS:
        lines.append(heading)
        lines.append("")

    lines.append(MANAGED_BLOCK_END)
    return "\n".join(lines)


def _extract_managed_block_range(content: str) -> tuple[int, int] | None:
    """Find the start and end character offsets of the managed block.

    Returns (start, end) offsets or None if markers are not found.
    """
    begin_idx = content.find(MANAGED_BLOCK_BEGIN)
    if begin_idx == -1:
        return None
    end_marker_idx = content.find(MANAGED_BLOCK_END, begin_idx)
    if end_marker_idx == -1:
        return None
    end_idx = end_marker_idx + len(MANAGED_BLOCK_END)
    return (begin_idx, end_idx)


def _rebuild_block_internals(
    existing_block: str,
    default_branch: str | None,
    head_commit_sha: str | None,
) -> str:
    """Rebuild the managed block internals while preserving existing section content.

    Refreshes the CRITICAL_INSTRUCTION/freshness metadata and ensures all
    four section headings exist in correct order. Existing content under
    headings is preserved.
    """
    # Extract content between markers
    inner_start = existing_block.find(MANAGED_BLOCK_BEGIN) + len(MANAGED_BLOCK_BEGIN)
    inner_end = existing_block.find(MANAGED_BLOCK_END)
    inner = existing_block[inner_start:inner_end].strip()

    # Parse existing section content keyed by heading
    existing_sections: dict[str, str] = {}
    current_heading: str | None = None
    current_lines: list[str] = []

    # Strip out CRITICAL_INSTRUCTION block first
    ci_start = inner.find("<CRITICAL_INSTRUCTION>")
    ci_end = inner.find("</CRITICAL_INSTRUCTION>")
    if ci_start != -1 and ci_end != -1:
        body_after_ci = inner[ci_end + len("</CRITICAL_INSTRUCTION>") :].strip()
    else:
        body_after_ci = inner

    for line in body_after_ci.split("\n"):
        stripped = line.strip()
        if stripped in SECTION_HEADINGS:
            if current_heading is not None:
                existing_sections[current_heading] = "\n".join(current_lines).strip()
            current_heading = stripped
            current_lines = []
        elif current_heading is not None:
            current_lines.append(line)

    if current_heading is not None:
        existing_sections[current_heading] = "\n".join(current_lines).strip()

    # Rebuild
    lines: list[str] = [MANAGED_BLOCK_BEGIN, "<CRITICAL_INSTRUCTION>", ""]

    if default_branch and head_commit_sha:
        lines.append(_build_freshness_line(default_branch, head_commit_sha))
        lines.append("")

    lines.append("</CRITICAL_INSTRUCTION>")
    lines.append("")

    for heading in SECTION_HEADINGS:
        lines.append(heading)
        section_content = existing_sections.get(heading, "")
        if section_content:
            lines.append(section_content)
        lines.append("")

    lines.append(MANAGED_BLOCK_END)
    return "\n".join(lines)


async def bootstrap_managed_block(
    codebase_path: str,
    default_branch: str | None = None,
    head_commit_sha: str | None = None,
) -> AgentsMdUpdaterOutput:
    """Ensure AGENTS.md has managed block with markers, CRITICAL_INSTRUCTION, and freshness metadata.

    Cases:
    - AGENTS.md does not exist: create with full managed block skeleton.
    - AGENTS.md exists without markers: append managed block at end.
    - AGENTS.md exists with markers: update internals (freshness, ensure headings),
      preserve existing section content, leave content outside block untouched.

    Args:
        codebase_path: Absolute path to the codebase root directory.
        default_branch: Default branch name (e.g. "main"). None to omit freshness.
        head_commit_sha: HEAD commit SHA. None to omit freshness.

    Returns:
        AgentsMdUpdaterOutput with status reflecting whether content changed.
    """
    agents_md_path = Path(codebase_path) / "AGENTS.md"
    abs_path = str(agents_md_path)

    existing_content: str | None = None
    if agents_md_path.exists():
        async with aiofiles.open(agents_md_path, mode="r", encoding="utf-8") as f:
            existing_content = await f.read()

    if existing_content is None:
        # Case 1: AGENTS.md does not exist — create with full skeleton
        new_content = _build_managed_block(default_branch, head_commit_sha) + "\n"
        async with aiofiles.open(agents_md_path, mode="w", encoding="utf-8") as f:
            await f.write(new_content)
        return AgentsMdUpdaterOutput(
            status="updated",
            touched_file_paths=[abs_path],
            file_changes=[
                UpdaterFileChange(
                    path=abs_path,
                    changed=True,
                    change_type="created",
                    change_summary="Created AGENTS.md with managed block skeleton",
                    content_sha256=hashlib.sha256(
                        new_content.encode("utf-8")
                    ).hexdigest(),
                )
            ],
        )

    block_range = _extract_managed_block_range(existing_content)

    if block_range is None:
        # Case 2: AGENTS.md exists but no managed block — append at end
        managed_block = _build_managed_block(default_branch, head_commit_sha)
        separator = (
            "\n\n"
            if existing_content and not existing_content.endswith("\n")
            else "\n"
            if existing_content
            else ""
        )
        new_content = existing_content + separator + managed_block + "\n"
        async with aiofiles.open(agents_md_path, mode="w", encoding="utf-8") as f:
            await f.write(new_content)
        return AgentsMdUpdaterOutput(
            status="updated",
            touched_file_paths=[abs_path],
            file_changes=[
                UpdaterFileChange(
                    path=abs_path,
                    changed=True,
                    change_type="updated",
                    change_summary="Appended managed block to existing AGENTS.md",
                    content_sha256=hashlib.sha256(
                        new_content.encode("utf-8")
                    ).hexdigest(),
                )
            ],
        )

    # Case 3: AGENTS.md exists with markers — update internals
    begin_offset, end_offset = block_range
    existing_block = existing_content[begin_offset:end_offset]
    rebuilt_block = _rebuild_block_internals(
        existing_block, default_branch, head_commit_sha
    )

    if existing_block == rebuilt_block:
        return AgentsMdUpdaterOutput(
            status="no_changes",
            touched_file_paths=[abs_path],
            file_changes=[
                UpdaterFileChange(
                    path=abs_path,
                    changed=False,
                    change_type="unchanged",
                    change_summary="Managed block already matches expected structure",
                )
            ],
        )

    new_content = (
        existing_content[:begin_offset] + rebuilt_block + existing_content[end_offset:]
    )
    async with aiofiles.open(agents_md_path, mode="w", encoding="utf-8") as f:
        await f.write(new_content)
    return AgentsMdUpdaterOutput(
        status="updated",
        touched_file_paths=[abs_path],
        file_changes=[
            UpdaterFileChange(
                path=abs_path,
                changed=True,
                change_type="updated",
                change_summary="Updated managed block internals (freshness/headings)",
                content_sha256=hashlib.sha256(new_content.encode("utf-8")).hexdigest(),
            )
        ],
    )
