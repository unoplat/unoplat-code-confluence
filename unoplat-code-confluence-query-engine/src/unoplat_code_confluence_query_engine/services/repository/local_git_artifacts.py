"""Exact-commit artifact access through the repository's local Git object store.

Viewing reads bytes from the run's saved commit in the local clone, never from the
working tree (later runs change it) and never from the provider. Publication
fetches the saved commit once and pins it under a run-owned ref, so the object
store keeps it whatever later happens to branches, PRs or garbage collection.

Every Git call passes arguments directly (no shell), disables prompts and lazy
fetches, and never surfaces Git's output, which can contain remote details.
"""

from __future__ import annotations

import os
from base64 import b64encode
from pathlib import Path, PurePosixPath
import re
import subprocess

from loguru import logger
from sqlalchemy import select
from unoplat_code_confluence_commons.relational_models import (
    UnoplatCodeConfluenceCodebase,
)

from unoplat_code_confluence_query_engine.db.postgres.db import get_startup_session
from unoplat_code_confluence_query_engine.models.output.repository_artifacts import (
    ArtifactManifestEntry,
)
from unoplat_code_confluence_query_engine.services.repository.artifact_manifest import (
    ArtifactValidationError,
    validate_artifact_bytes,
)
from unoplat_code_confluence_query_engine.services.repository.artifact_paths import (
    ARTIFACT_BYTE_LIMITS,
    validate_artifact_path,
)

_LOCAL_READ_TIMEOUT_SECONDS = 15
_FETCH_TIMEOUT_SECONDS = 120
_OBJECT_ID = re.compile(r"[0-9a-f]{40}")
_RUN_ID = re.compile(r"[A-Za-z0-9_-]+")
_REGULAR_FILE_MODES = frozenset({b"100644", b"100755"})
_ARTIFACT_REF_PREFIX = "refs/unoplat/artifacts"


class LocalGitError(Exception):
    """A local Git operation failed. The message is static and safe to log."""


class LocalCheckoutUnavailableError(LocalGitError):
    """No single, existing local clone can be proven for the repository."""


class LocalArtifactCommitMissingError(LocalGitError):
    """The saved commit is not in the local object store."""


def _require_object_id(value: str) -> str:
    if _OBJECT_ID.fullmatch(value) is None:
        raise ValueError("Invalid full Git object SHA")
    return value


def _git(
    root: Path,
    *args: str,
    timeout: float = _LOCAL_READ_TIMEOUT_SECONDS,
    extra_env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[bytes]:
    env = {
        **os.environ,
        "GIT_TERMINAL_PROMPT": "0",
        "GIT_ASKPASS": "/bin/echo",
        "GIT_NO_LAZY_FETCH": "1",
        "GIT_LITERAL_PATHSPECS": "1",
        **(extra_env or {}),
    }
    try:
        # The clone is written by the ingestion service, which may run as another
        # user, so trust exactly this directory for this one command.
        return subprocess.run(
            ["git", "-c", f"safe.directory={root}", "-C", str(root), *args],
            capture_output=True,
            check=False,
            env=env,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as error:
        raise LocalGitError("Local Git operation timed out") from error
    except OSError as error:
        raise LocalGitError("Local Git is not available") from error


def _codebase_root(folder: str | None, codebase_path: str) -> PurePosixPath:
    path = PurePosixPath(codebase_path)
    if not path.is_absolute():
        raise LocalCheckoutUnavailableError("Codebase path is not absolute")
    parts = tuple(
        part for part in PurePosixPath(folder or ".").parts if part not in {".", "/"}
    )
    if ".." in parts or len(path.parts) <= len(parts):
        raise LocalCheckoutUnavailableError("Codebase path cannot be proven")
    root = PurePosixPath(*path.parts[: len(path.parts) - len(parts)])
    if root.joinpath(*parts) != path:
        raise LocalCheckoutUnavailableError("Codebase path does not end in its folder")
    return root


async def resolve_repository_checkout_root(owner_name: str, repo_name: str) -> Path:
    """Return the one local clone root shared by the repository's codebases.

    Raises:
        LocalCheckoutUnavailableError: No codebase rows exist, they disagree on the
            root, or the root is not an existing Git clone.
    """
    async with get_startup_session() as session:
        rows = (
            (
                await session.execute(
                    select(
                        UnoplatCodeConfluenceCodebase.codebase_folder,
                        UnoplatCodeConfluenceCodebase.codebase_path,
                    ).where(
                        UnoplatCodeConfluenceCodebase.repository_qualified_name
                        == f"{owner_name}_{repo_name}"
                    )
                )
            )
            .tuples()
            .all()
        )
    roots = {_codebase_root(folder, path) for folder, path in rows}
    if len(roots) != 1:
        raise LocalCheckoutUnavailableError(
            "Repository has no single local checkout root"
        )
    root = Path(str(roots.pop()))
    if not (root / ".git").exists():
        raise LocalCheckoutUnavailableError("Local checkout is not a Git clone")
    return root


def has_local_commit(root: Path, commit_sha: str) -> bool:
    """Report whether the local object store holds the exact commit."""
    _require_object_id(commit_sha)
    return _git(root, "cat-file", "-e", f"{commit_sha}^{{commit}}").returncode == 0


def read_local_artifact(
    root: Path, commit_sha: str, entry: ArtifactManifestEntry
) -> bytes | None:
    """Read a manifest file at the exact saved commit from the local object store.

    Returns:
        Bytes verified against the manifest, or None when the commit has no
        regular file at that path.

    Raises:
        LocalArtifactCommitMissingError: The commit is not in the local store.
        ArtifactValidationError: The blob does not match the manifest.
        LocalGitError: Git failed.
    """
    validate_artifact_path(entry.path)
    if not has_local_commit(root, commit_sha):
        raise LocalArtifactCommitMissingError("Saved commit is not stored locally")
    listing = _git(
        root, "ls-tree", "-l", "-z", "--full-tree", commit_sha, "--", entry.path
    )
    if listing.returncode != 0:
        raise LocalGitError("Local commit tree could not be listed")
    records = [record for record in listing.stdout.split(b"\0") if record]
    if not records:
        return None
    if len(records) != 1:
        raise ArtifactValidationError("Local commit tree lists ambiguous paths")
    meta, _, listed_path = records[0].partition(b"\t")
    fields = meta.split()
    if len(fields) != 4 or listed_path != entry.path.encode("utf-8"):
        return None
    mode, object_type, object_id, size = fields
    if object_type != b"blob" or mode not in _REGULAR_FILE_MODES:
        return None
    if not size.isdigit() or int(size) != entry.byte_length:
        raise ArtifactValidationError("Local artifact size does not match manifest")
    if int(size) > ARTIFACT_BYTE_LIMITS[entry.kind]:
        raise ArtifactValidationError("Local artifact exceeds its byte limit")
    blob = _git(root, "cat-file", "blob", _require_object_id(object_id.decode("ascii")))
    if blob.returncode != 0:
        raise LocalGitError("Local artifact blob could not be read")
    validate_artifact_bytes(entry, blob.stdout)
    return blob.stdout


def fetch_local_commit(
    root: Path, commit_sha: str, *, remote_url: str, token: str
) -> None:
    """Fetch one commit into the local object store, authenticated by header.

    The token travels only in a per-process environment config entry: it never
    appears in the command line, the remote URL, FETCH_HEAD or an error.

    Raises:
        LocalGitError: The fetch failed or did not deliver the commit.
    """
    _require_object_id(commit_sha)
    basic = b64encode(f"x-access-token:{token}".encode()).decode("ascii")
    result = _git(
        root,
        "-c",
        "gc.auto=0",
        "-c",
        "maintenance.auto=false",
        "fetch",
        "--quiet",
        "--no-tags",
        "--no-write-fetch-head",
        "--no-recurse-submodules",
        remote_url,
        commit_sha,
        timeout=_FETCH_TIMEOUT_SECONDS,
        extra_env={
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": "http.extraHeader",
            "GIT_CONFIG_VALUE_0": f"Authorization: Basic {basic}",
        },
    )
    if result.returncode != 0:
        # Git's stderr can echo remote details, so only the exit status is kept.
        logger.warning(
            "Artifact commit fetch failed with git exit status {}", result.returncode
        )
        raise LocalGitError("Artifact commit could not be fetched")
    if not has_local_commit(root, commit_sha):
        raise LocalGitError("Fetch did not deliver the artifact commit")


def pin_local_commit(root: Path, commit_sha: str, run_id: str) -> None:
    """Point the run's own ref at its commit so garbage collection keeps it.

    Raises:
        LocalGitError: The ref could not be written.
    """
    _require_object_id(commit_sha)
    if _RUN_ID.fullmatch(run_id) is None or run_id.startswith("-"):
        raise ValueError("Invalid workflow run ID for an artifact ref")
    result = _git(root, "update-ref", f"{_ARTIFACT_REF_PREFIX}/{run_id}", commit_sha)
    if result.returncode != 0:
        raise LocalGitError("Artifact commit ref could not be written")
