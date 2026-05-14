"""markdown-it-style validation for dependencies_overview.md."""

from __future__ import annotations

from collections.abc import Iterator
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


def parse_dependency_overview_entries(markdown_text: str) -> dict[str, str]:
    """Parse dependency entries from canonical dependencies overview markdown.

    Returns a mapping of dependency name to purpose. The package-management bullet
    is intentionally ignored because it is guide metadata, not a dependency.
    """
    dependency_entries: dict[str, str] = {}
    tokens = MarkdownIt("commonmark", {"html": True}).parse(markdown_text)

    for inline in _iter_list_item_inline_tokens(tokens):
        parsed_entry = _parse_dependency_inline_token(inline)
        if parsed_entry is None:
            continue
        dependency_name, purpose = parsed_entry
        if dependency_name.casefold() == "package management":
            continue
        dependency_entries[dependency_name] = purpose

    return dependency_entries


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
    """Extract list item text using markdown-it-py tokenization."""
    tokens = MarkdownIt("commonmark", {"html": True}).parse(markdown_text)
    items: list[str] = []
    for inline in _iter_list_item_inline_tokens(tokens):
        items.append(_inline_token_to_markdown_text(inline))
    return items


def _iter_list_item_inline_tokens(tokens: list[Token]) -> Iterator[Token]:
    """Yield the first inline token for each bullet list item."""
    in_list_item = False
    list_item_level = 0

    for token in tokens:
        if token.type == "list_item_open":
            in_list_item = True
            list_item_level = token.level
            continue
        if token.type == "list_item_close" and in_list_item:
            in_list_item = False
            continue
        if not in_list_item or token.type != "inline":
            continue
        if token.level <= list_item_level + 2:
            yield token
            in_list_item = False


def _inline_token_to_markdown_text(inline: Token) -> str:
    """Render the inline token back to the canonical text shape used by validation."""
    parsed_entry = _parse_strong_prefixed_inline_token(inline)
    if parsed_entry is None:
        return " ".join(inline.content.split())
    dependency_name, suffix = parsed_entry
    return f"**{dependency_name}**{suffix}"


def _parse_dependency_inline_token(inline: Token) -> tuple[str, str] | None:
    parsed_entry = _parse_strong_prefixed_inline_token(inline)
    if parsed_entry is None:
        return None
    dependency_name, suffix = parsed_entry
    if not suffix.startswith(":"):
        return None
    purpose_text = suffix.removeprefix(":").strip()
    if purpose_text.startswith("Purpose:"):
        purpose_text = purpose_text.removeprefix("Purpose:").strip()
    return dependency_name, purpose_text


def _parse_strong_prefixed_inline_token(inline: Token) -> tuple[str, str] | None:
    children = inline.children or []
    strong_open_index = next(
        (index for index, child in enumerate(children) if child.type == "strong_open"),
        None,
    )
    if strong_open_index is None:
        return None
    if strong_open_index + 2 >= len(children):
        return None
    name_token = children[strong_open_index + 1]
    strong_close = children[strong_open_index + 2]
    if name_token.type != "text" or strong_close.type != "strong_close":
        return None

    dependency_name = name_token.content.strip()
    suffix_parts: list[str] = []
    for child in children[strong_open_index + 3 :]:
        if child.type in {"text", "code_inline"}:
            suffix_parts.append(child.content)
        elif child.type in {"softbreak", "hardbreak"}:
            suffix_parts.append(" ")
    suffix = " ".join("".join(suffix_parts).split())
    return dependency_name, suffix
