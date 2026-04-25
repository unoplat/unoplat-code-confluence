"""markdown-it-py validation helpers for managed AGENTS.md blocks."""

from __future__ import annotations

from collections.abc import MutableMapping, Sequence
from pathlib import Path
from typing import Any, cast

from markdown_it import MarkdownIt
from markdown_it.rules_core import StateCore
from markdown_it.token import Token

from unoplat_code_confluence_query_engine.services.agents_md.managed_block import (
    MANAGED_BLOCK_BEGIN,
    MANAGED_BLOCK_END,
    SECTION_HEADINGS,
)

MANAGED_BLOCK_VALID_ENV_KEY = "managed_block_valid"
MANAGED_BLOCK_ERRORS_ENV_KEY = "managed_block_errors"
CRITICAL_INSTRUCTION_OPEN = "<CRITICAL_INSTRUCTION>"
CRITICAL_INSTRUCTION_CLOSE = "</CRITICAL_INSTRUCTION>"


def build_markdown_validator() -> MarkdownIt:
    """Build a markdown-it-py validator for managed AGENTS.md blocks."""
    return MarkdownIt("commonmark", {"html": True}).use(
        managed_block_validation_plugin
    )


def validate_managed_block_markdown(markdown_text: str) -> bool:
    """Return True when *markdown_text* contains one canonical managed block."""
    return not collect_managed_block_errors(markdown_text)


def collect_managed_block_errors(markdown_text: str) -> list[str]:
    """Return validation errors for the managed block in *markdown_text*."""
    validator = build_markdown_validator()
    env: dict[str, Any] = {}
    validator.parse(markdown_text, env)
    errors = env.get(MANAGED_BLOCK_ERRORS_ENV_KEY, [])
    if not isinstance(errors, list):
        return ["Managed block validator returned an invalid error payload."]
    return [str(error) for error in errors]


def validate_managed_block_file(markdown_path: str | Path) -> bool:
    """Return True when *markdown_path* contains one canonical managed block."""
    resolved_path = Path(markdown_path)
    markdown_text = resolved_path.read_text(encoding="utf-8")
    return validate_managed_block_markdown(markdown_text)


def managed_block_validation_plugin(md: MarkdownIt) -> None:
    """Register the managed-block validation rule on the parser."""
    md.core.ruler.after(
        "inline",
        "managed_block_validation",
        managed_block_validation_rule,
    )


def managed_block_validation_rule(state: StateCore) -> None:
    """Validate the managed block and store the result in markdown-it env."""
    env = _coerce_env_mapping(state.env)
    errors = _validate_managed_block(state.src, state.tokens)
    env[MANAGED_BLOCK_ERRORS_ENV_KEY] = errors
    env[MANAGED_BLOCK_VALID_ENV_KEY] = len(errors) == 0


def _validate_managed_block(source: str, tokens: Sequence[Token]) -> list[str]:
    """Validate the managed block structure for the supplied markdown source."""
    lines = source.splitlines()
    errors: list[str] = []

    begin_positions = _find_exact_line_positions(lines, MANAGED_BLOCK_BEGIN)
    end_positions = _find_exact_line_positions(lines, MANAGED_BLOCK_END)
    ci_open_positions = _find_exact_line_positions(lines, CRITICAL_INSTRUCTION_OPEN)
    ci_close_positions = _find_exact_line_positions(lines, CRITICAL_INSTRUCTION_CLOSE)

    if len(begin_positions) != 1:
        errors.append(
            "Expected exactly one managed block begin marker line inside the markdown."
        )
    if len(end_positions) != 1:
        errors.append(
            "Expected exactly one managed block end marker line inside the markdown."
        )
    if len(ci_open_positions) != 1:
        errors.append(
            "Expected exactly one <CRITICAL_INSTRUCTION> line inside the managed block."
        )
    if len(ci_close_positions) != 1:
        errors.append(
            "Expected exactly one </CRITICAL_INSTRUCTION> line inside the managed block."
        )

    if errors:
        return errors

    begin_line = begin_positions[0]
    end_line = end_positions[0]
    ci_open_line = ci_open_positions[0]
    ci_close_line = ci_close_positions[0]

    if begin_line >= end_line:
        errors.append("Managed block begin marker must appear before the end marker.")

    if not begin_line < ci_open_line < ci_close_line < end_line:
        errors.append(
            "CRITICAL_INSTRUCTION tags must appear exactly once and stay between the managed block markers."
        )

    if errors:
        return errors

    observed_headings = _collect_h2_headings_within_range(tokens, begin_line, end_line)
    expected_headings = [
        _heading_text_from_section_heading(item) for item in SECTION_HEADINGS
    ]

    if observed_headings != expected_headings:
        errors.append(
            "Managed block H2 headings must exactly match the canonical section order."
        )

    return errors


def _find_exact_line_positions(lines: Sequence[str], target: str) -> list[int]:
    """Return zero-based line positions whose stripped content matches the target."""
    return [index for index, line in enumerate(lines) if line.strip() == target]


def _collect_h2_headings_within_range(
    tokens: Sequence[Token],
    begin_line: int,
    end_line: int,
) -> list[str]:
    """Collect H2 heading text observed between the managed block markers."""
    headings: list[str] = []
    token_count = len(tokens)

    for index, token in enumerate(tokens):
        if token.type != "heading_open" or token.tag != "h2" or token.map is None:
            continue

        token_line = token.map[0]
        if not begin_line < token_line < end_line:
            continue

        if index + 1 >= token_count:
            continue

        inline_token = tokens[index + 1]
        if inline_token.type != "inline":
            continue

        headings.append(inline_token.content.strip())

    return headings


def _heading_text_from_section_heading(section_heading: str) -> str:
    """Normalize a canonical section heading like '## Name' to 'Name'."""
    return section_heading.removeprefix("##").strip()


def _coerce_env_mapping(env: Any) -> MutableMapping[str, Any]:
    """Ensure env is always a mutable mapping for plugin communication."""
    if isinstance(env, MutableMapping):
        return cast(MutableMapping[str, Any], env)
    raise TypeError("markdown-it env must be a mutable mapping")
