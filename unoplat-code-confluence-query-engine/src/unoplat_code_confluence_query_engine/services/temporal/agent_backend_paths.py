"""Shared path helpers for agent backends.

These helpers derive validated absolute paths from ``CodebaseMetadata`` and
are shared by both readonly local and Docker-backed backend construction.
They live in a tiny dependency-free module so runtime and resolver modules can
reuse them without circular imports.
"""

from __future__ import annotations

from pathlib import PurePosixPath

from unoplat_code_confluence_query_engine.models.repository.repository_ruleset_metadata import (
    CodebaseMetadata,
)


def resolve_work_dir(metadata: CodebaseMetadata) -> str:
    """Return the validated absolute working directory from codebase metadata."""
    codebase_path = metadata.codebase_path.strip()
    path = PurePosixPath(codebase_path)
    if not codebase_path or not path.is_absolute():
        raise ValueError(
            f"Agent backend requires an absolute codebase_path, got: {metadata.codebase_path!r}"
        )
    return str(path)


def resolve_repository_root(metadata: CodebaseMetadata) -> str:
    """Derive the repository root from absolute codebase metadata.

    ``codebase_path`` is the absolute filesystem path to the codebase root.
    ``codebase_name`` is the path relative to the repository root. We use that
    relationship to walk back to the repository root.
    """
    codebase_path = PurePosixPath(resolve_work_dir(metadata))
    codebase_parts = _normalize_codebase_name_parts(metadata.codebase_name)

    if not codebase_parts:
        return str(codebase_path)

    if len(codebase_path.parts) <= len(codebase_parts):
        raise ValueError(
            "Cannot derive repository root because codebase_path is shallower "
            f"than codebase_name: {metadata.codebase_path!r} vs {metadata.codebase_name!r}"
        )

    repository_root = PurePosixPath(*codebase_path.parts[: -len(codebase_parts)])
    expected_codebase_path = repository_root.joinpath(*codebase_parts)
    if expected_codebase_path != codebase_path:
        raise ValueError(
            "Codebase metadata is inconsistent: codebase_path does not end with "
            f"codebase_name ({metadata.codebase_path!r} vs {metadata.codebase_name!r})"
        )

    return str(repository_root)


def _normalize_codebase_name_parts(codebase_name: str) -> tuple[str, ...]:
    raw = codebase_name.strip()
    if raw in {"", "."}:
        return ()

    path = PurePosixPath(raw)
    parts = path.parts
    if any(part == ".." for part in parts):
        raise ValueError(f"codebase_name must not traverse upward: {codebase_name!r}")

    return tuple(part for part in parts if part not in {"", ".", "/"})
