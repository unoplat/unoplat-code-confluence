from __future__ import annotations

from pydantic_ai import ModelRetry

from unoplat_code_confluence_query_engine.models.output.engineering_workflow_output import (
    EngineeringWorkflow,
)
from unoplat_code_confluence_query_engine.services.repository.engineering_workflow_service import (
    is_valid_config_file,
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

    return output
