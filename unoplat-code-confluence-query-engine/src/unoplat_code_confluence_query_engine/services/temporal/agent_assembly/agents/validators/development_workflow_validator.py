from __future__ import annotations

from pydantic_ai import ModelRetry

from unoplat_code_confluence_query_engine.models.output.engineering_workflow_output import (
    EngineeringWorkflow,
)
from unoplat_code_confluence_query_engine.services.repository.engineering_workflow_service import (
    CONFIDENCE_THRESHOLD,
    is_valid_working_directory,
)


def validate_engineering_development_workflow_output(
    output: EngineeringWorkflow,
) -> EngineeringWorkflow:
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
        if command.config_file.startswith("/") or command.config_file.startswith("../"):
            raise ModelRetry(
                f"config_file '{command.config_file}' must be repo-relative without leading '/' or '../'. "
                "Use 'unknown' if no config file applies."
            )
        if command.confidence < 0.0 or command.confidence > 1.0:
            raise ModelRetry(
                f"confidence {command.confidence} for command '{command.command}' must be between 0.0 and 1.0."
            )
        if command.working_directory is not None and not is_valid_working_directory(
            command.working_directory
        ):
            raise ModelRetry(
                "working_directory must be omitted/null for codebase root, '.' for repository root, "
                "or a repo-relative POSIX path without backslashes, absolute prefixes, or traversal."
            )

    if not any(
        command.confidence > CONFIDENCE_THRESHOLD for command in output.commands
    ):
        raise ModelRetry(
            "All engineering workflow commands are at or below the confidence threshold "
            f"({CONFIDENCE_THRESHOLD}). Re-validate against official documentation and return at least one command with confidence > threshold."
        )
    return output
