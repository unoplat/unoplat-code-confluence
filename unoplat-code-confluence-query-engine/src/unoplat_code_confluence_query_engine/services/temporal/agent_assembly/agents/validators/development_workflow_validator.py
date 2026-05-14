from __future__ import annotations

from pathlib import Path

from markdown_it import MarkdownIt
from markdown_it.token import Token
from pydantic_ai import ModelRetry, RunContext

from unoplat_code_confluence_query_engine.models.output.engineering_workflow_output import (
    ENGINEERING_WORKFLOW_NO_CHANGE,
    EngineeringWorkflow,
    EngineeringWorkflowAgentOutput,
    EngineeringWorkflowStage,
)
from unoplat_code_confluence_query_engine.models.runtime.agent_dependencies import (
    AgentDependencies,
)
from unoplat_code_confluence_query_engine.services.agents_md.managed_block import (
    MANAGED_BLOCK_BEGIN,
    MANAGED_BLOCK_END,
)
from unoplat_code_confluence_query_engine.services.agents_md.validation.managed_block_validation import (
    validate_managed_block_markdown,
)
from unoplat_code_confluence_query_engine.services.repository.engineering_workflow_service import (
    is_valid_config_file,
    is_valid_working_directory,
)

ENGINEERING_WORKFLOW_HEADING = "Engineering Workflow"
ENGINEERING_WORKFLOW_SECTION = f"## {ENGINEERING_WORKFLOW_HEADING}"
CANONICAL_STAGE_HEADINGS: dict[EngineeringWorkflowStage, str] = {
    EngineeringWorkflowStage.INSTALL: "Install",
    EngineeringWorkflowStage.BUILD: "Build",
    EngineeringWorkflowStage.DEV: "Dev",
    EngineeringWorkflowStage.TEST: "Test",
    EngineeringWorkflowStage.LINT: "Lint",
    EngineeringWorkflowStage.TYPE_CHECK: "Type Check",
}


def validate_engineering_development_workflow_output(
    ctx_or_output: RunContext[AgentDependencies] | EngineeringWorkflowAgentOutput,
    output: EngineeringWorkflowAgentOutput | None = None,
) -> EngineeringWorkflowAgentOutput:
    """Validate structured command output and the agent-owned AGENTS.md section.

    The validator supports both pydantic-ai ctx-aware invocation and direct unit-test
    invocation with just the output model.
    """
    if output is None:
        workflow = ctx_or_output
        ctx: RunContext[AgentDependencies] | None = None
    else:
        ctx = ctx_or_output if isinstance(ctx_or_output, RunContext) else None
        workflow = output

    if isinstance(workflow, str):
        if workflow != ENGINEERING_WORKFLOW_NO_CHANGE:
            raise ModelRetry(
                f"String output must be exactly {ENGINEERING_WORKFLOW_NO_CHANGE}. "
                "Return a full engineering_workflow JSON model if changes are needed."
            )
        if ctx is not None:
            markdown_text = _read_agents_md_for_validation(ctx)
            validate_engineering_workflow_section_markdown(markdown_text)
        return workflow

    if not isinstance(workflow, EngineeringWorkflow):
        raise TypeError("Expected EngineeringWorkflow or no-change string output")

    _validate_engineering_workflow_model(workflow)

    if ctx is not None:
        markdown_text = _read_agents_md_for_validation(ctx)
        validate_engineering_workflow_section_markdown(markdown_text, workflow)

    return workflow


def _read_agents_md_for_validation(ctx: RunContext[AgentDependencies]) -> str:
    codebase_path = ctx.deps.codebase_metadata.codebase_path
    agents_md_path = Path(codebase_path) / "AGENTS.md"
    try:
        return agents_md_path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ModelRetry(
            "AGENTS.md was not found. The managed block bootstrap must run before "
            "development_workflow_guide, and the agent must update ## Engineering Workflow."
        ) from exc


def _validate_engineering_workflow_model(output: EngineeringWorkflow) -> None:
    if not output.commands:
        raise ModelRetry(
            "engineering_workflow.commands is empty. Re-scan command sources "
            "(Taskfile/Makefile/package scripts/tool configs) and return commands."
        )

    for command in output.commands:
        if not command.command.strip():
            raise ModelRetry(
                "Found command with empty command string. Return non-empty runnable commands."
            )

        if not is_valid_config_file(command.config_file):
            raise ModelRetry(
                "config_file must be 'unknown' or a repository-root-relative POSIX file path "
                "without '.', backslashes, absolute prefixes, or traversal."
            )

        if command.working_directory is not None and not is_valid_working_directory(
            command.working_directory
        ):
            raise ModelRetry(
                "working_directory must be omitted/null for codebase root, '.' for repository root, "
                "or a repo-relative POSIX path without backslashes, absolute prefixes, or traversal."
            )


def validate_engineering_workflow_section_markdown(
    markdown_text: str,
    workflow: EngineeringWorkflow | None = None,
) -> None:
    """Validate the markdown-it-parsed Engineering Workflow AGENTS section.

    Required shape:
    - a valid managed block with canonical H2 order
    - exactly one `## Engineering Workflow` H2 inside the managed block
    - canonical H3 stage headings for install/build/dev/test/lint/type-check
    - non-empty content under each stage heading
    - every structured command appears in the section, when an output model is supplied
    """
    if not validate_managed_block_markdown(markdown_text):
        raise ModelRetry(
            "AGENTS.md managed block is invalid. Keep the bootstrap markers, "
            "CRITICAL_INSTRUCTION block, and canonical H2 section order intact."
        )

    section_text = _extract_owned_section(markdown_text, ENGINEERING_WORKFLOW_SECTION)
    tokens = MarkdownIt("commonmark", {"html": True}).parse(section_text)
    h3_headings = _collect_headings(tokens, level="h3")
    expected_stage_headings = list(CANONICAL_STAGE_HEADINGS.values())

    if h3_headings != expected_stage_headings:
        raise ModelRetry(
            "## Engineering Workflow must contain exactly these H3 headings in order: "
            + ", ".join(f"### {heading}" for heading in expected_stage_headings)
            + ". Use 'Not detected' under stages with no discovered command."
        )

    for heading in expected_stage_headings:
        stage_body = _extract_subsection(section_text, f"### {heading}")
        if not stage_body.strip():
            raise ModelRetry(
                f"### {heading} in ## Engineering Workflow is empty. Add commands, "
                "notes, or an explicit 'Not detected' statement."
            )

    if workflow is not None:
        missing_commands = [
            command.command
            for command in workflow.commands
            if command.command.strip() and command.command not in section_text
        ]
        if missing_commands:
            raise ModelRetry(
                "AGENTS.md ## Engineering Workflow is missing commands returned in "
                "engineering_workflow.commands: " + ", ".join(missing_commands)
            )


def _extract_owned_section(markdown_text: str, heading: str) -> str:
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

    heading_positions = [
        index
        for index in range(begin_line + 1, end_line)
        if lines[index].strip() == heading
    ]
    if len(heading_positions) != 1:
        raise ModelRetry(
            f"Expected exactly one {heading} section inside the managed block."
        )

    heading_line = heading_positions[0]
    next_h2_line = next(
        (
            index
            for index in range(heading_line + 1, end_line)
            if lines[index].startswith("## ")
        ),
        end_line,
    )
    section_lines = lines[heading_line:next_h2_line]
    section_text = "\n".join(section_lines).strip()
    if section_text == heading:
        raise ModelRetry(f"{heading} is empty. Write the engineering workflow section.")
    return section_text


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


def _extract_subsection(markdown_text: str, heading: str) -> str:
    lines = markdown_text.splitlines()
    start = next(
        (index for index, line in enumerate(lines) if line.strip() == heading),
        None,
    )
    if start is None:
        return ""
    end = next(
        (
            index
            for index in range(start + 1, len(lines))
            if lines[index].startswith("### ") or lines[index].startswith("## ")
        ),
        len(lines),
    )
    return "\n".join(lines[start + 1 : end]).strip()
