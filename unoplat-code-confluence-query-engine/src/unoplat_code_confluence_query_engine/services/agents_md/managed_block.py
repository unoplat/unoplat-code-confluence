"""Bootstrap and maintain the managed block in codebase-local AGENTS.md."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import aiofiles

MANAGED_BLOCK_BEGIN = "<!-- UNOPLAT_CODE_CONFLUENCE_CONTEXT:BEGIN -->"
MANAGED_BLOCK_END = "<!-- UNOPLAT_CODE_CONFLUENCE_CONTEXT:END -->"

BUSINESS_DOMAIN_SECTION = "## Business Domain"
BUSINESS_DOMAIN_DESCRIPTION_HEADING = "### Description"
BUSINESS_DOMAIN_REFERENCES_HEADING = "### References"
BUSINESS_DOMAIN_REFERENCES_TEXT = (
    "See [`business_domain_references.md`](./business_domain_references.md) "
    "for the supporting source references used to derive this domain summary."
)

SECTION_HEADINGS: list[str] = [
    "## Engineering Workflow",
    "## Dependency Guide",
    BUSINESS_DOMAIN_SECTION,
    "## App Interfaces",
]

_SECTION_POINTER_TEMPLATES: dict[str, str] = {
    "## Dependency Guide": (
        "See [`dependencies_overview.md`](./dependencies_overview.md) "
        "for the full dependency catalog and usage notes."
    ),
    "## App Interfaces": (
        "See [`app_interfaces.md`](./app_interfaces.md) "
        "for the canonical interface and endpoint reference."
    ),
}


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


def _extract_business_domain_description(existing_content: str) -> str:
    """Extract agent-authored text from the canonical Business Domain description."""
    lines = existing_content.splitlines()
    description_lines: list[str] = []
    in_description = False

    for line in lines:
        stripped = line.strip()
        if not in_description:
            if stripped == BUSINESS_DOMAIN_DESCRIPTION_HEADING:
                in_description = True
            continue

        if stripped.startswith("### "):
            break
        description_lines.append(line)

    return "\n".join(description_lines).strip()


def _compose_business_domain_content(existing_content: str = "") -> str:
    """Compose the canonical Business Domain section content."""
    description = _extract_business_domain_description(existing_content)
    lines = [BUSINESS_DOMAIN_DESCRIPTION_HEADING, ""]

    if description:
        lines.append(description)
        lines.append("")

    lines.extend(
        [
            BUSINESS_DOMAIN_REFERENCES_HEADING,
            "",
            BUSINESS_DOMAIN_REFERENCES_TEXT,
        ]
    )
    return "\n".join(lines).strip()


def _compose_section_content(heading: str, existing_content: str = "") -> str:
    """Compose canonical content for a managed-block section."""
    if heading == BUSINESS_DOMAIN_SECTION:
        return _compose_business_domain_content(existing_content)

    pointer_content = _SECTION_POINTER_TEMPLATES.get(heading)
    if pointer_content is not None:
        return pointer_content

    return existing_content.strip()


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
        section_content = _compose_section_content(heading)
        if section_content:
            lines.append(section_content)
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
    four section headings exist in correct order.
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
        section_content = _compose_section_content(
            heading,
            existing_sections.get(heading, ""),
        )
        if section_content:
            lines.append(section_content)
        lines.append("")

    lines.append(MANAGED_BLOCK_END)
    return "\n".join(lines)


async def bootstrap_managed_block(
    codebase_path: str,
    default_branch: str | None = None,
    head_commit_sha: str | None = None,
) -> bool:
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
        True when AGENTS.md content changed, otherwise False.
    """
    agents_md_path = Path(codebase_path) / "AGENTS.md"

    existing_content: str | None = None
    if agents_md_path.exists():
        async with aiofiles.open(agents_md_path, mode="r", encoding="utf-8") as f:
            existing_content = await f.read()

    if existing_content is None:
        # Case 1: AGENTS.md does not exist — create with full skeleton
        new_content = _build_managed_block(default_branch, head_commit_sha) + "\n"
        async with aiofiles.open(agents_md_path, mode="w", encoding="utf-8") as f:
            await f.write(new_content)
        return True

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
        return True

    # Case 3: AGENTS.md exists with markers — update internals
    begin_offset, end_offset = block_range
    existing_block = existing_content[begin_offset:end_offset]
    rebuilt_block = _rebuild_block_internals(
        existing_block, default_branch, head_commit_sha
    )

    if existing_block == rebuilt_block:
        return False

    new_content = (
        existing_content[:begin_offset] + rebuilt_block + existing_content[end_offset:]
    )
    async with aiofiles.open(agents_md_path, mode="w", encoding="utf-8") as f:
        await f.write(new_content)
    return True
