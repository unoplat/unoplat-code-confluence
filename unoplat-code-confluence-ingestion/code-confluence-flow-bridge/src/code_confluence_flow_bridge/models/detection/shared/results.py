"""Shared detection result models."""

from pydantic import BaseModel, Field
from unoplat_code_confluence_commons.programming_language_metadata import (
    PackageManagerProvenance,
    WorkspaceOrchestratorType,
)


class DetectedCodebase(BaseModel):
    """Detection result carrying package-manager provenance and workspace context."""

    manager_name: str = Field(
        description="Effective package manager name (e.g. 'bun', 'pnpm', 'npm', 'yarn')"
    )
    provenance: PackageManagerProvenance = Field(
        description="Whether the package manager was detected locally or inherited from a parent workspace"
    )
    workspace_root: str | None = Field(
        default=None,
        description=(
            "Repo-relative POSIX path to the nearest aggregator directory "
            "that owns workspace commands. None for standalone or locally-owned leaf codebases."
        ),
    )
    workspace_orchestrator: WorkspaceOrchestratorType | None = Field(
        default=None,
        description="Nearest authoritative workspace orchestrator for workflow discovery.",
    )
    workspace_orchestrator_config_path: str | None = Field(
        default=None,
        description="Repo-relative config path for the nearest authoritative workspace orchestrator.",
    )
