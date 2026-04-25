"""Renderer for the canonical app_interfaces.md artifact."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping

from unoplat_code_confluence_query_engine.models.output.agent_md_output import (
    InboundConstruct,
    Interfaces,
    InternalConstruct,
    OutboundConstruct,
)
from unoplat_code_confluence_query_engine.services.agents_md.rendering.jinja_environment import (
    build_markdown_jinja_environment,
)


@dataclass(frozen=True)
class InterfaceConstructRow:
    """Template-ready interface construct row."""

    kind: str
    library: str
    references: tuple[str, ...]


@dataclass(frozen=True)
class InterfaceSection:
    """Template-ready app-interface section."""

    title: str
    empty_message: str
    constructs: tuple[InterfaceConstructRow, ...]


_TEMPLATE_DIR = Path(__file__).parent / "templates"
_TEMPLATE_NAME = "app_interfaces.md.j2"
_DEFAULT_LIBRARY = "unknown"
_APP_INTERFACES_ARTIFACT = "app_interfaces.md"

_InterfaceConstruct = InboundConstruct | OutboundConstruct | InternalConstruct


def render_app_interfaces(interfaces: Interfaces) -> str:
    """Render Interfaces into canonical app_interfaces.md markdown."""
    env = build_markdown_jinja_environment(_TEMPLATE_DIR)
    template = env.get_template(_TEMPLATE_NAME)
    rendered = template.render(
        sections=(
            InterfaceSection(
                title="Inbound Constructs",
                empty_message="No inbound constructs detected.",
                constructs=_build_construct_rows(interfaces.inbound_constructs),
            ),
            InterfaceSection(
                title="Outbound Constructs",
                empty_message="No outbound constructs detected.",
                constructs=_build_construct_rows(interfaces.outbound_constructs),
            ),
            InterfaceSection(
                title="Internal Constructs",
                empty_message="No internal constructs detected.",
                constructs=_build_construct_rows(interfaces.internal_constructs),
            ),
        ),
    )
    return rendered.rstrip() + "\n"


def write_app_interfaces_if_changed(
    codebase_path: str | Path,
    interfaces: Interfaces,
) -> bool:
    """Overwrite app_interfaces.md with canonical content when it differs."""
    target_path = Path(codebase_path) / _APP_INTERFACES_ARTIFACT
    rendered = render_app_interfaces(interfaces)
    existing = target_path.read_text(encoding="utf-8") if target_path.exists() else None
    if existing == rendered:
        return False
    target_path.write_text(rendered, encoding="utf-8")
    return True


def _build_construct_rows(
    constructs: Iterable[_InterfaceConstruct],
) -> tuple[InterfaceConstructRow, ...]:
    """Normalize and sort constructs for stable markdown rendering."""
    rows = [
        InterfaceConstructRow(
            kind=_normalize_inline_text(_kind_value(construct.kind)) or "unknown",
            library=_normalize_inline_text(construct.library or _DEFAULT_LIBRARY)
            or _DEFAULT_LIBRARY,
            references=_build_reference_lines(construct.match_pattern),
        )
        for construct in constructs
    ]
    return tuple(
        sorted(
            rows,
            key=lambda row: (
                row.kind.casefold(),
                row.library.casefold(),
                row.references[0].casefold() if row.references else "",
            ),
        )
    )


def _build_reference_lines(match_pattern: Mapping[str, list[str]]) -> tuple[str, ...]:
    """Build deterministic file/match reference lines for a construct."""
    references: list[str] = []
    for raw_path, matches in sorted(
        match_pattern.items(),
        key=lambda item: str(item[0]).casefold(),
    ):
        path = _normalize_inline_text(raw_path) or "unknown"
        normalized_matches = sorted(
            {
                normalized_match
                for match in matches
                if (normalized_match := _normalize_inline_text(match))
            },
            key=str.casefold,
        )
        if normalized_matches:
            references.extend(f"`{path}`: {match}" for match in normalized_matches)
        else:
            references.append(f"`{path}`")
    return tuple(references)


def _kind_value(kind: object) -> str:
    """Return enum values as strings while supporting plain string kinds."""
    value = getattr(kind, "value", kind)
    return str(value)


def _normalize_inline_text(value: object) -> str:
    """Collapse multiline values into stable single-line markdown text."""
    return " ".join(str(value).split())
