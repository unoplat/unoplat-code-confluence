"""Minimal validation helpers for engineering workflow output."""

from __future__ import annotations

from pathlib import PurePosixPath


def _normalize_repo_relative_posix_path(
    raw_value: str,
    *,
    allow_dot: bool,
) -> str | None:
    """Normalize a repo-relative POSIX path or return ``None`` when invalid."""
    candidate = raw_value.strip()
    if not candidate:
        return None

    if "\\" in candidate or candidate.startswith("/"):
        return None

    normalized = PurePosixPath(candidate).as_posix()
    if ".." in PurePosixPath(normalized).parts:
        return None

    if normalized == ".":
        return "." if allow_dot else None

    return normalized


def is_valid_working_directory(raw_value: str) -> bool:
    """Return whether a working directory matches the output contract."""
    return _normalize_repo_relative_posix_path(raw_value, allow_dot=True) is not None


def is_valid_config_file(raw_value: str) -> bool:
    """Return whether a config_file matches the output contract."""
    candidate = raw_value.strip()
    if candidate == "unknown":
        return True
    return _normalize_repo_relative_posix_path(candidate, allow_dot=False) is not None
