"""markdown-it-style validation for dependencies_overview.md."""

from __future__ import annotations

from pathlib import Path

from markdown_it import MarkdownIt
from markdown_it.token import Token

DEPENDENCIES_OVERVIEW_TITLE = "Dependencies Overview"


def validate_dependency_overview_markdown(markdown_text: str) -> bool:
    """Return True when dependency overview markdown has the canonical shape.

    Required shape:
    - exactly one H1 named ``Dependencies Overview``
    - at least one bullet item
    - every bullet starts with strong text, e.g. ``- **fastapi**: ...``
    - non-package-management bullets include a ``Purpose:`` label
    """
    return not collect_dependency_overview_errors(markdown_text)


def validate_dependency_overview_file(markdown_path: str | Path) -> bool:
    """Validate a dependencies overview markdown file from disk."""
    resolved_path = Path(markdown_path)
    return validate_dependency_overview_markdown(
        resolved_path.read_text(encoding="utf-8")
    )


def collect_dependency_overview_errors(markdown_text: str) -> list[str]:
    """Collect structural validation errors for dependency overview markdown."""
    tokens = MarkdownIt("commonmark", {"html": True}).parse(markdown_text)
    errors: list[str] = []

    h1_headings = _collect_headings(tokens, level="h1")
    if h1_headings != [DEPENDENCIES_OVERVIEW_TITLE]:
        errors.append("Expected exactly one '# Dependencies Overview' heading.")

    bullet_items = _extract_bullet_list_items(markdown_text)
    if not bullet_items:
        errors.append("Expected at least one dependency bullet item.")
        return errors

    for item in bullet_items:
        if not item.startswith("**") or "**:" not in item:
            errors.append(
                "Each dependency bullet must start with bold dependency text, "
                "for example '- **fastapi**: Purpose: ...'."
            )
            continue

        dependency_name = item.split("**:", 1)[0].removeprefix("**").strip()
        if not dependency_name:
            errors.append("Dependency bullet has an empty dependency name.")
            continue

        if dependency_name.casefold() == "package management":
            if len(item.split("**:", 1)[1].strip()) == 0:
                errors.append("Package management bullet must contain explanatory text.")
            continue

        if "Purpose:" not in item:
            errors.append(
                f"Dependency bullet for '{dependency_name}' must contain a 'Purpose:' label."
            )

    return errors


def _collect_headings(tokens: list[Token], *, level: str) -> list[str]:
    headings: list[str] = []
    token_count = len(tokens)
    for index, token in enumerate(tokens):
        if token.type != "heading_open" or token.tag != level:
            continue
        if index + 1 >= token_count:
            continue
        inline = tokens[index + 1]
        if inline.type == "inline":
            headings.append(inline.content.strip())
    return headings


def _extract_bullet_list_items(markdown_text: str) -> list[str]:
    items: list[str] = []
    current: list[str] = []

    for line in markdown_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            if current:
                items.append(" ".join(current).strip())
            current = [stripped[2:].strip()]
        elif current and (line.startswith("  ") or line.startswith("\t")):
            current.append(stripped)
        elif current and not stripped:
            continue
        else:
            if current:
                items.append(" ".join(current).strip())
                current = []

    if current:
        items.append(" ".join(current).strip())

    return items
