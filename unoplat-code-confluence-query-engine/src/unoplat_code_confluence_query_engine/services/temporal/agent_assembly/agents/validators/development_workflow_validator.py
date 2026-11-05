from __future__ import annotations

from datetime import timedelta
import hashlib
from pathlib import Path
import re

from markdown_it import MarkdownIt
from markdown_it.token import Token
from pydantic_ai import ModelRetry, RunContext
from temporalio import workflow as temporal_workflow
from temporalio.common import RetryPolicy

from unoplat_code_confluence_query_engine.models.output.engineering_workflow_output import (
    ENGINEERING_WORKFLOW_FULL_OUTPUT,
    ENGINEERING_WORKFLOW_NO_CHANGE,
    EngineeringWorkflow,
    EngineeringWorkflowAgentOutput,
    EngineeringWorkflowAgentResponse,
    EngineeringWorkflowSectionInspection,
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
from unoplat_code_confluence_query_engine.services.repository.artifact_manifest import (
    ArtifactValidationError,
    read_working_artifact,
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
INSPECT_ENGINEERING_WORKFLOW_SECTION_ACTIVITY = "inspect-engineering-workflow-section"
INSPECTION_TIMEOUT = timedelta(seconds=30)
INSPECTION_RETRY_POLICY = RetryPolicy(maximum_attempts=3)
# Matches how markdown-it counts lines, so heading token maps index these lines.
MARKDOWN_LINE_PATTERN = re.compile(r"[^\r\n]*(?:\r\n?|\n)|[^\r\n]+")


async def validate_engineering_development_workflow_output(
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

    if not isinstance(workflow, EngineeringWorkflowAgentResponse):
        raise TypeError("Expected EngineeringWorkflowAgentResponse output")

    if workflow.status == ENGINEERING_WORKFLOW_NO_CHANGE:
        if workflow.commands is not None:
            raise ModelRetry(
                f"For status={ENGINEERING_WORKFLOW_NO_CHANGE}, omit the commands field. "
                "Do not return commands for no-change output."
            )
        if ctx is not None:
            await _validate_no_change_section_is_untouched(ctx)
        return workflow

    if workflow.status != ENGINEERING_WORKFLOW_FULL_OUTPUT:
        raise TypeError("Unsupported EngineeringWorkflowAgentResponse status")

    if not workflow.commands:
        raise ModelRetry(
            f"For status={ENGINEERING_WORKFLOW_FULL_OUTPUT}, commands is required and must be non-empty."
        )

    engineering_workflow = EngineeringWorkflow(commands=workflow.commands)
    _validate_engineering_workflow_model(engineering_workflow)

    if ctx is not None:
        inspection = await _inspect_section_for_validator(ctx, engineering_workflow)
        if inspection.validation_error is not None:
            raise ModelRetry(inspection.validation_error)

    return workflow


def inspect_engineering_workflow_section(
    codebase_path: str,
    engineering_workflow: EngineeringWorkflow | None = None,
) -> EngineeringWorkflowSectionInspection:
    """Validate the owned section with a bounded read and digest its exact bytes.

    Args:
        codebase_path: Absolute path to the codebase root directory.
        engineering_workflow: Commands that must appear in the section, when known.

    Returns:
        The section digest, or retry guidance when AGENTS.md is missing or unsafe or
        its section is invalid, in which case the section must be regenerated.
    """
    try:
        markdown_text = _read_agents_md(codebase_path)
    except ArtifactValidationError:
        return EngineeringWorkflowSectionInspection(
            validation_error=(
                "AGENTS.md could not be read safely. It must be a regular UTF-8 file "
                "within the managed artifact size limit at the supplied path."
            )
        )
    if markdown_text is None:
        return EngineeringWorkflowSectionInspection(
            validation_error=(
                "AGENTS.md was not found. The managed block bootstrap must run before "
                "development_workflow_guide, and the agent must update ## Engineering Workflow."
            )
        )
    try:
        validate_engineering_workflow_section_markdown(
            markdown_text, engineering_workflow
        )
        section_text = _extract_exact_owned_section(
            markdown_text, ENGINEERING_WORKFLOW_SECTION
        )
    except ModelRetry as error:
        return EngineeringWorkflowSectionInspection(validation_error=error.message)
    return EngineeringWorkflowSectionInspection(
        section_sha256=hashlib.sha256(section_text.encode("utf-8")).hexdigest()
    )


async def _inspect_section_for_validator(
    ctx: RunContext[AgentDependencies],
    engineering_workflow: EngineeringWorkflow | None,
) -> EngineeringWorkflowSectionInspection:
    """Inspect through a recorded activity so workflow replay never reads the file.

    Pydantic AI runs output validators in workflow code, and they run again on
    replay. Outside a workflow, the same inspection runs directly.
    """
    codebase_path = ctx.deps.codebase_metadata.codebase_path
    if temporal_workflow.in_workflow():
        return await temporal_workflow.execute_activity(
            INSPECT_ENGINEERING_WORKFLOW_SECTION_ACTIVITY,
            args=[codebase_path, engineering_workflow],
            result_type=EngineeringWorkflowSectionInspection,
            start_to_close_timeout=INSPECTION_TIMEOUT,
            retry_policy=INSPECTION_RETRY_POLICY,
        )
    return inspect_engineering_workflow_section(codebase_path, engineering_workflow)


async def _validate_no_change_section_is_untouched(
    ctx: RunContext[AgentDependencies],
) -> None:
    """Allow no_change only for a valid section with bytes unchanged in this attempt."""
    baseline_digest = ctx.deps.engineering_section_sha256
    if baseline_digest is None:
        raise ModelRetry(
            f"status={ENGINEERING_WORKFLOW_NO_CHANGE} is not valid for this run because "
            "the existing ## Engineering Workflow section is missing or invalid. "
            "Regenerate that section from verified repository evidence and return "
            f"status={ENGINEERING_WORKFLOW_FULL_OUTPUT} with the commands you wrote."
        )

    inspection = await _inspect_section_for_validator(ctx, None)
    if inspection.section_sha256 != baseline_digest:
        raise ModelRetry(
            f"status={ENGINEERING_WORKFLOW_NO_CHANGE} is not valid because "
            "## Engineering Workflow changed during this run or is no longer valid. "
            "Keep the section valid and return "
            f"status={ENGINEERING_WORKFLOW_FULL_OUTPUT} with the commands you wrote."
        )


def _read_agents_md(codebase_path: str) -> str | None:
    """Read the exact codebase AGENTS.md through the bounded artifact reader."""
    content = read_working_artifact(Path(codebase_path), "AGENTS.md", "markdown")
    return None if content is None else content.decode("utf-8")


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
    section_text = _extract_exact_owned_section(markdown_text, heading).strip()
    if section_text == heading:
        raise ModelRetry(f"{heading} is empty. Write the engineering workflow section.")
    return section_text


def _extract_exact_owned_section(markdown_text: str, heading: str) -> str:
    """Return every character from the heading line up to the next real H2 heading."""
    lines = MARKDOWN_LINE_PATTERN.findall(markdown_text)
    begin_positions = [
        index for index, line in enumerate(lines) if line.strip() == MANAGED_BLOCK_BEGIN
    ]
    end_positions = [
        index for index, line in enumerate(lines) if line.strip() == MANAGED_BLOCK_END
    ]
    if len(begin_positions) != 1 or len(end_positions) != 1:
        raise ModelRetry(
            "AGENTS.md must contain exactly one managed block marker pair."
        )

    begin_line = begin_positions[0]
    end_line = end_positions[0]
    if begin_line >= end_line:
        raise ModelRetry(
            "AGENTS.md managed block begin marker must precede end marker."
        )

    tokens = MarkdownIt("commonmark", {"html": True}).parse(markdown_text)
    h2_lines = [
        token.map[0]
        for token in tokens
        if token.type == "heading_open"
        and token.tag == "h2"
        and token.map is not None
        and begin_line < token.map[0] < end_line
    ]
    heading_positions = [index for index in h2_lines if lines[index].strip() == heading]
    if len(heading_positions) != 1:
        raise ModelRetry(
            f"Expected exactly one {heading} section inside the managed block."
        )

    heading_line = heading_positions[0]
    next_h2_line = next(
        (index for index in h2_lines if index > heading_line),
        end_line,
    )
    return "".join(lines[heading_line:next_h2_line])


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
