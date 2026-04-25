from __future__ import annotations

from pathlib import Path

from pydantic_ai import ModelRetry, RunContext

from unoplat_code_confluence_query_engine.models.runtime.agent_dependencies import (
    AgentDependencies,
)
from unoplat_code_confluence_query_engine.services.agents_md.managed_block import (
    BUSINESS_DOMAIN_DESCRIPTION_HEADING,
    BUSINESS_DOMAIN_REFERENCES_HEADING,
    BUSINESS_DOMAIN_SECTION,
    MANAGED_BLOCK_BEGIN,
    MANAGED_BLOCK_END,
)
from unoplat_code_confluence_query_engine.services.agents_md.validation.managed_block_validation import (
    validate_managed_block_markdown,
)


def validate_business_logic_domain_output(
    ctx_or_output: RunContext[AgentDependencies] | str,
    output: str | None = None,
) -> str:
    """Validate plain-text output and the agent-owned AGENTS.md section boundary.

    Supports direct unit-test invocation with just the output string and ctx-aware
    pydantic-ai invocation where the final on-disk AGENTS.md can be inspected.
    """
    if output is None:
        text = ctx_or_output
        ctx: RunContext[AgentDependencies] | None = None
    else:
        ctx = ctx_or_output if isinstance(ctx_or_output, RunContext) else None
        text = output

    if not isinstance(text, str):
        raise TypeError("Expected business-domain output to be a string")

    _validate_plain_text_business_domain_output(text)

    if ctx is not None:
        agents_md_path = Path(ctx.deps.codebase_metadata.codebase_path) / "AGENTS.md"
        try:
            markdown_text = agents_md_path.read_text(encoding="utf-8")
        except FileNotFoundError as exc:
            raise ModelRetry(
                "AGENTS.md was not found. The managed block bootstrap must run before "
                "business_domain_guide, and the agent must update ## Business Domain / ### Description."
            ) from exc

        validate_business_logic_domain_section_boundary(markdown_text)

    return text


def _validate_plain_text_business_domain_output(output: str) -> None:
    if not output or not output.strip():
        raise ModelRetry(
            "Output is empty. Return a plain text description (2-4 sentences) "
            "summarizing the business domain based on the data models analyzed."
        )

    stripped_output = output.strip()
    if stripped_output.startswith("{") or stripped_output.startswith("["):
        raise ModelRetry(
            "Return ONLY plain text (2-4 sentences), NOT JSON or structured data. "
            "Summarize the business domain in natural language."
        )


def validate_business_logic_domain_section_boundary(markdown_text: str) -> None:
    """Validate that the business-domain AGENTS section is inside managed boundaries."""
    if not validate_managed_block_markdown(markdown_text):
        raise ModelRetry(
            "AGENTS.md managed block is invalid. Keep the bootstrap markers, "
            "CRITICAL_INSTRUCTION block, and canonical H2 section order intact."
        )

    lines = markdown_text.splitlines()
    begin_positions = [
        index for index, line in enumerate(lines) if line.strip() == MANAGED_BLOCK_BEGIN
    ]
    end_positions = [
        index for index, line in enumerate(lines) if line.strip() == MANAGED_BLOCK_END
    ]
    if len(begin_positions) != 1 or len(end_positions) != 1:
        raise ModelRetry("AGENTS.md must contain exactly one managed block marker pair.")

    begin_line = begin_positions[0]
    end_line = end_positions[0]
    if begin_line >= end_line:
        raise ModelRetry("AGENTS.md managed block begin marker must precede end marker.")

    all_heading_positions = [
        index for index, line in enumerate(lines) if line.strip() == BUSINESS_DOMAIN_SECTION
    ]
    inside_heading_positions = [
        index for index in all_heading_positions if begin_line < index < end_line
    ]

    if len(all_heading_positions) != 1 or len(inside_heading_positions) != 1:
        raise ModelRetry(
            "Expected exactly one ## Business Domain section, and it must be inside "
            "the managed block. Do not create duplicate business-domain headings."
        )

    heading_line = inside_heading_positions[0]
    next_h2_line = next(
        (
            index
            for index in range(heading_line + 1, end_line)
            if lines[index].startswith("## ")
        ),
        end_line,
    )
    section_lines = lines[heading_line + 1 : next_h2_line]

    description_positions = [
        index
        for index, line in enumerate(section_lines)
        if line.strip() == BUSINESS_DOMAIN_DESCRIPTION_HEADING
    ]
    if len(description_positions) != 1:
        raise ModelRetry(
            "## Business Domain must contain exactly one ### Description heading. "
            "Update only the owned subsection content without deleting or duplicating headings."
        )

    references_positions = [
        index
        for index, line in enumerate(section_lines)
        if line.strip() == BUSINESS_DOMAIN_REFERENCES_HEADING
    ]
    if len(references_positions) != 1:
        raise ModelRetry(
            "## Business Domain must contain exactly one ### References heading. "
            "Do not delete, rename, or duplicate the managed references subsection."
        )

    description_start = description_positions[0] + 1
    description_end = next(
        (
            index
            for index in range(description_start, len(section_lines))
            if section_lines[index].strip().startswith("### ")
        ),
        len(section_lines),
    )
    description_body = "\n".join(section_lines[description_start:description_end]).strip()
    if not description_body:
        raise ModelRetry(
            "## Business Domain / ### Description is empty. Write a concise business-domain "
            "summary inside the owned managed-block subsection."
        )
