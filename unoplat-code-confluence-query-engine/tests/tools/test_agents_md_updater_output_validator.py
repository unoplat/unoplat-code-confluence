"""Unit tests for AGENTS.md updater output validation semantics."""

from __future__ import annotations

from pydantic_ai import ModelRetry
import pytest

from unoplat_code_confluence_query_engine.models.output.agents_md_updater_output import (
    AgentsMdUpdaterOutput,
    UpdaterFileChange,
)
<<<<<<< HEAD
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.agents.validators.agents_md_updater_validator import (
=======
from unoplat_code_confluence_query_engine.services.temporal.temporal_agents import (
>>>>>>> origin/main
    validate_agents_md_updater_output,
)


def test_no_changes_with_changed_file_is_rejected() -> None:
    """status=no_changes cannot include changed=true entries."""
    output = AgentsMdUpdaterOutput(
        status="no_changes",
        touched_file_paths=["/repo/AGENTS.md"],
        file_changes=[
            UpdaterFileChange(
                path="/repo/AGENTS.md",
                changed=True,
                change_type="updated",
                change_summary="unexpected mutation",
            )
        ],
    )

    with pytest.raises(
        ModelRetry,
        match=r"status no_changes requires file_changes\[\]\.changed to be false",
    ):
        validate_agents_md_updater_output(output)


def test_updated_with_no_changed_files_is_rejected() -> None:
    """status=updated requires at least one changed file."""
    output = AgentsMdUpdaterOutput(
        status="updated",
        touched_file_paths=["/repo/AGENTS.md"],
        file_changes=[
            UpdaterFileChange(
                path="/repo/AGENTS.md",
                changed=False,
                change_type="unchanged",
                change_summary="already up to date",
            )
        ],
    )

    with pytest.raises(
        ModelRetry,
        match=r"status updated requires at least one file_changes\[\]\.changed to be true",
    ):
        validate_agents_md_updater_output(output)


def test_valid_no_changes_payload_passes() -> None:
    """Consistent no_changes payload should pass validation."""
    output = AgentsMdUpdaterOutput(
        status="no_changes",
        touched_file_paths=["/repo/AGENTS.md"],
        file_changes=[
            UpdaterFileChange(
                path="/repo/AGENTS.md",
                changed=False,
                change_type="unchanged",
                change_summary="section already equivalent",
            )
        ],
    )

    validated = validate_agents_md_updater_output(output)
    assert validated is output


def test_valid_updated_payload_passes() -> None:
    """Consistent updated payload should pass validation."""
    output = AgentsMdUpdaterOutput(
        status="updated",
        touched_file_paths=["/repo/AGENTS.md", "/repo/business_logic_references.md"],
        file_changes=[
            UpdaterFileChange(
                path="/repo/AGENTS.md",
                changed=True,
                change_type="updated",
                change_summary="refreshed section content",
            ),
            UpdaterFileChange(
                path="/repo/business_logic_references.md",
                changed=False,
                change_type="unchanged",
                change_summary="already current",
            ),
        ],
    )

    validated = validate_agents_md_updater_output(output)
    assert validated is output
