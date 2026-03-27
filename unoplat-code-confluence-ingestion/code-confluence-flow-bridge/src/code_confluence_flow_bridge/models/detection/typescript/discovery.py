"""TypeScript-specific workspace discovery and scan models."""

from pydantic import BaseModel, ConfigDict, Field
from unoplat_code_confluence_commons.programming_language_metadata import (
    WorkspaceOrchestratorType,
)

from src.code_confluence_flow_bridge.models.detection.shared.inventory import FileNode


class WorkspaceOrchestratorMetadata(BaseModel):
    """Authoritative workspace-runner metadata attached to a workspace root."""

    model_config = ConfigDict(frozen=True)

    orchestrator: WorkspaceOrchestratorType = Field(
        description="Nearest authoritative monorepo orchestrator."
    )
    config_path: str = Field(
        description="Repo-relative path to the authoritative orchestrator config file."
    )


class WorkspaceDiscoveryContext(BaseModel):
    """Authoritative workspace membership and ownership resolved from root config."""

    model_config = ConfigDict(frozen=True)

    root_dir: str = Field(description="Repo-relative directory owning the workspace.")
    manager_name: str = Field(description="Package manager owning the workspace root.")
    member_dirs: tuple[str, ...] = Field(
        default_factory=tuple,
        description="Repo-relative workspace member directories.",
    )
    excluded_dirs: tuple[str, ...] = Field(
        default_factory=tuple,
        description="Repo-relative directories excluded by workspace negations.",
    )
    orchestrator: WorkspaceOrchestratorMetadata | None = Field(
        default=None,
        description="Nearest authoritative workspace orchestrator metadata.",
    )


class TypeScriptRepositoryScan(BaseModel):
    """Single ripgrep-backed repository scan reused across detector phases."""

    model_config = ConfigDict(frozen=True)

    inventory: tuple[FileNode, ...] = Field(
        default_factory=tuple,
        description="Repository file inventory captured from ripgrep.",
    )
    inventory_paths: frozenset[str] = Field(
        default_factory=frozenset,
        description="Fast lookup set of repo-relative inventory paths.",
    )
    dirs_to_files: dict[str, tuple[str, ...]] = Field(
        default_factory=dict,
        description="Repo-relative directory to matching file paths.",
    )
    known_dirs: tuple[str, ...] = Field(
        default_factory=tuple,
        description="Known repo-relative directories discovered during the scan.",
    )
    manifest_dirs: tuple[str, ...] = Field(
        default_factory=tuple,
        description="Repo-relative directories that contain a package.json manifest.",
    )
