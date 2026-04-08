from __future__ import annotations

from pydantic_ai import ModelRetry

from unoplat_code_confluence_query_engine.models.output.agents_md_updater_output import (
    AgentsMdUpdaterOutput,
)


def validate_agents_md_updater_output(
    output: AgentsMdUpdaterOutput,
) -> AgentsMdUpdaterOutput:
    """Validate updater output contract."""

    if not output.touched_file_paths:
        raise ModelRetry("touched_file_paths cannot be empty")
    if not output.file_changes:
        raise ModelRetry("file_changes cannot be empty")

    if output.status == "no_changes":
        for file_change in output.file_changes:
            if file_change.changed:
                raise ModelRetry(
                    "status no_changes requires file_changes[].changed to be false"
                )
            if file_change.change_type != "unchanged":
                raise ModelRetry(
                    "status no_changes requires file_changes[].change_type to be 'unchanged'"
                )

    if output.status == "updated":
        has_changed_file = any(
            file_change.changed for file_change in output.file_changes
        )
        if not has_changed_file:
            raise ModelRetry(
                "status updated requires at least one file_changes[].changed to be true"
            )

        has_mutation_change_type = any(
            file_change.change_type in {"created", "updated"}
            for file_change in output.file_changes
        )
        if not has_mutation_change_type:
            raise ModelRetry(
                "status updated requires at least one file_changes[].change_type in {'created','updated'}"
            )

    return output
