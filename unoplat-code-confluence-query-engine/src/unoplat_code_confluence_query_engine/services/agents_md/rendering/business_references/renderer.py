"""Renderer for the canonical business_domain_references.md artifact."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from unoplat_code_confluence_query_engine.models.output.agent_md_output import (
    BusinessLogicDomain,
)
from unoplat_code_confluence_query_engine.services.agents_md.rendering.jinja_environment import (
    build_markdown_jinja_environment,
)


@dataclass(frozen=True)
class BusinessReferenceSpanRow:
    """Template-ready line-level reference row."""

    identifier: str
    start_line: int
    end_line: int
    path_with_lines: str


@dataclass(frozen=True)
class BusinessReferenceFileRow:
    """Template-ready data model file row."""

    path: str
    responsibility: str
    references: tuple[BusinessReferenceSpanRow, ...]


_TEMPLATE_DIR = Path(__file__).parent / "templates"
_TEMPLATE_NAME = "business_domain_references.md.j2"
_DEFAULT_RESPONSIBILITY = "Data model definitions used to infer the business domain."


def render_business_domain_references(domain: BusinessLogicDomain) -> str:
    """Render BusinessLogicDomain into canonical business_domain_references.md markdown."""
    env = build_markdown_jinja_environment(_TEMPLATE_DIR)
    template = env.get_template(_TEMPLATE_NAME)
    rows: list[BusinessReferenceFileRow] = []
    for model in sorted(domain.data_models, key=lambda item: item.path):
        path = model.path.strip()
        if not path:
            continue
        references = tuple(
            BusinessReferenceSpanRow(
                identifier=reference.identifier.strip(),
                start_line=reference.start_line,
                end_line=reference.end_line,
                path_with_lines=(
                    f"{path}#L{reference.start_line}-L{reference.end_line}"
                ),
            )
            for reference in sorted(
                model.references,
                key=lambda item: (item.start_line, item.end_line, item.identifier),
            )
            if reference.identifier.strip()
        )
        rows.append(
            BusinessReferenceFileRow(
                path=path,
                responsibility=(model.responsibility or _DEFAULT_RESPONSIBILITY).strip(),
                references=references,
            )
        )
    rendered = template.render(
        description=domain.description.strip(),
        data_models=rows,
    )
    return rendered.rstrip() + "\n"


def write_business_domain_references(
    codebase_path: str | Path,
    domain: BusinessLogicDomain,
) -> None:
    """Overwrite business_domain_references.md with canonical content."""
    target_path = Path(codebase_path) / "business_domain_references.md"
    rendered = render_business_domain_references(domain)
    target_path.write_text(rendered, encoding="utf-8")
