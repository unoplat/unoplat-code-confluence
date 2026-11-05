"""Canonical managed-artifact paths, allowlists, and byte limits.

Shared by publication and exact-commit readers. Paths are validated, never
silently normalized. Only the legacy root-codebase identifiers '' and '.'
refer to the repository root.
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import PurePosixPath
from typing import Literal
import unicodedata

from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.constants import (
    APP_INTERFACES_ARTIFACT,
    ARCHITECTURE_RENDER_ARTIFACT,
    ARCHITECTURE_SOURCE_ARTIFACT,
    BUSINESS_DOMAIN_REFERENCES_ARTIFACT,
    DEPENDENCY_OVERVIEW_ARTIFACT,
)

type ArtifactKind = Literal["markdown", "d2", "svg"]

CODEBASE_MANAGED_MARKDOWN_ARTIFACTS = (
    "AGENTS.md",
    DEPENDENCY_OVERVIEW_ARTIFACT,
    BUSINESS_DOMAIN_REFERENCES_ARTIFACT,
    APP_INTERFACES_ARTIFACT,
)
REPOSITORY_MANAGED_ARTIFACTS = (
    ARCHITECTURE_SOURCE_ARTIFACT,
    ARCHITECTURE_RENDER_ARTIFACT,
)
ARTIFACT_BYTE_LIMITS: dict[ArtifactKind, int] = {
    "markdown": 1024 * 1024,
    "d2": 256 * 1024,
    "svg": 5 * 1024 * 1024,
}


def validate_artifact_path(path: str) -> str:
    """Return a strict repository-relative POSIX path, or raise ValueError."""
    if (
        not path
        or path.startswith("/")
        or path.split("/", 1)[0].endswith(":")
        or "\\" in path
        or any(unicodedata.category(char).startswith("C") for char in path)
        or any(
            part in {"", ".", ".."} or part.casefold() == ".git"
            for part in path.split("/")
        )
        or PurePosixPath(path).as_posix() != path
    ):
        raise ValueError(
            "Artifact path must be a strict repository-relative POSIX path"
        )
    return path


def validate_codebase_name(codebase_name: str) -> str:
    """Validate a run membership identifier without changing its stored identity."""
    if codebase_name not in {"", "."}:
        validate_artifact_path(codebase_name)
    return codebase_name


def codebase_artifact_path(codebase_name: str, filename: str) -> str:
    """Map a run codebase and allowlisted Markdown filename to its Git path."""
    validate_codebase_name(codebase_name)
    if filename not in CODEBASE_MANAGED_MARKDOWN_ARTIFACTS:
        raise ValueError("File is not a managed codebase artifact")
    path = filename if codebase_name in {"", "."} else f"{codebase_name}/{filename}"
    return validate_artifact_path(path)


def required_generated_artifact_paths(
    *,
    codebases: Iterable[tuple[str, bool]],
    dependency_guide_enabled: bool,
    business_domain_enabled: bool,
    architecture_generated: bool,
) -> list[str]:
    """Return the files a successful run's stages must have left in the checkout.

    AGENTS.md is always bootstrapped. Other files belong to stages that can be
    disabled or skipped, so they are required only when their stage ran.

    Args:
        codebases: Codebase name and whether its app interfaces were generated.
        dependency_guide_enabled: Whether the dependency guide stage ran.
        business_domain_enabled: Whether the business domain stage ran.
        architecture_generated: Whether the Architecture agent ran.

    Returns:
        Sorted repository-relative paths that must exist before manifest freeze.
    """
    paths: list[str] = []
    for codebase_name, app_interfaces_generated in codebases:
        filenames = ["AGENTS.md"]
        if dependency_guide_enabled:
            filenames.append(DEPENDENCY_OVERVIEW_ARTIFACT)
        if business_domain_enabled:
            filenames.append(BUSINESS_DOMAIN_REFERENCES_ARTIFACT)
        if app_interfaces_generated:
            filenames.append(APP_INTERFACES_ARTIFACT)
        paths.extend(
            codebase_artifact_path(codebase_name, filename) for filename in filenames
        )
    if architecture_generated:
        paths.extend(REPOSITORY_MANAGED_ARTIFACTS)
    return sorted(paths)


def artifact_kind(path: str) -> ArtifactKind:
    """Resolve the kind of an allowlisted path, rejecting arbitrary repository files."""
    validate_artifact_path(path)
    if path == ARCHITECTURE_SOURCE_ARTIFACT:
        return "d2"
    if path == ARCHITECTURE_RENDER_ARTIFACT:
        return "svg"
    if PurePosixPath(path).name in CODEBASE_MANAGED_MARKDOWN_ARTIFACTS:
        return "markdown"
    raise ValueError("File is not a managed artifact")
