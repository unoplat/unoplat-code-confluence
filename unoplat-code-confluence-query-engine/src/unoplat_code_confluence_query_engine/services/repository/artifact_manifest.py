"""Bounded, symlink-safe byte capture and frozen-manifest revalidation.

Call capture_managed_artifacts/revalidate_manifest only inside the shared
repository_capture_guard. The returned bytes are the sole publication payload;
no file is read again after leaving that guard.
"""

from __future__ import annotations

import os
from collections.abc import Sequence
from dataclasses import dataclass
import hashlib
from pathlib import Path
import stat

from unoplat_code_confluence_query_engine.models.output.repository_artifacts import (
    ArtifactManifest,
    ArtifactManifestEntry,
)
from unoplat_code_confluence_query_engine.services.repository.artifact_paths import (
    ARTIFACT_BYTE_LIMITS,
    CODEBASE_MANAGED_MARKDOWN_ARTIFACTS,
    REPOSITORY_MANAGED_ARTIFACTS,
    ArtifactKind,
    artifact_kind,
    codebase_artifact_path,
    validate_artifact_path,
)


@dataclass(frozen=True)
class CapturedArtifact:
    """Transient exact bytes paired with their content-free descriptor."""

    descriptor: ArtifactManifestEntry
    content: bytes


class ArtifactValidationError(ValueError):
    """A file/path cannot be safely captured, or differs from a frozen descriptor."""


class MissingRequiredArtifactError(ArtifactValidationError):
    """A stage that ran did not leave its generated file in the checkout."""


def validate_artifact_bytes(entry: ArtifactManifestEntry, content: bytes) -> None:
    """Require bounded UTF-8 bytes with the manifest's exact size and digest."""
    if (
        len(content) > ARTIFACT_BYTE_LIMITS[entry.kind]
        or len(content) != entry.byte_length
        or hashlib.sha256(content).hexdigest() != entry.sha256
    ):
        raise ArtifactValidationError("Artifact bytes do not match the frozen manifest")
    try:
        content.decode("utf-8")
    except UnicodeError as error:
        raise ArtifactValidationError("Artifact is not valid UTF-8") from error


def read_working_artifact(root: Path, path: str, kind: ArtifactKind) -> bytes | None:
    """Read a bounded regular file using directory FDs and O_NOFOLLOW.

    Missing files are omitted only during initial inventory. Every intermediate
    directory must be real, contained, and not a nested Git repository/submodule.
    File stats are checked before/after reading to reject concurrent replacement.
    """
    validate_artifact_path(path)
    try:
        if not root.is_absolute() or root.resolve(strict=True) != root:
            raise ArtifactValidationError(
                "Repository root must be a real absolute directory"
            )
        directory_fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    except OSError as error:
        raise ArtifactValidationError(
            "Repository root is not safely available"
        ) from error
    try:
        parts = path.split("/")
        for part in parts[:-1]:
            next_fd = os.open(
                part,
                os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                dir_fd=directory_fd,
            )
            os.close(directory_fd)
            directory_fd = next_fd
            try:
                os.stat(".git", dir_fd=directory_fd, follow_symlinks=False)
            except FileNotFoundError:
                pass
            else:
                raise ArtifactValidationError(
                    "Artifacts cannot traverse nested Git repositories"
                )
        file_fd = os.open(
            parts[-1],
            os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
            dir_fd=directory_fd,
        )
        with os.fdopen(file_fd, "rb") as handle:
            before = os.fstat(handle.fileno())
            limit = ARTIFACT_BYTE_LIMITS[kind]
            if not stat.S_ISREG(before.st_mode) or before.st_size > limit:
                raise ArtifactValidationError("Artifact must be a bounded regular file")
            content = handle.read(limit + 1)
            after = os.fstat(handle.fileno())
            try:
                current = os.stat(parts[-1], dir_fd=directory_fd, follow_symlinks=False)
            except FileNotFoundError as error:
                raise ArtifactValidationError(
                    "Artifact disappeared during byte capture"
                ) from error
            if (
                len(content) > limit
                or len(content) != before.st_size
                or _file_version(before) != _file_version(after)
                or _file_version(after) != _file_version(current)
            ):
                raise ArtifactValidationError("Artifact changed during byte capture")
            content.decode("utf-8")
            return content
    except FileNotFoundError:
        return None
    except (OSError, UnicodeError) as error:
        raise ArtifactValidationError(
            "Artifact is not a contained regular UTF-8 file"
        ) from error
    finally:
        os.close(directory_fd)


def _file_version(info: os.stat_result) -> tuple[int, int, int, int, int, int]:
    return (
        info.st_dev,
        info.st_ino,
        info.st_mode,
        info.st_size,
        info.st_mtime_ns,
        info.st_ctime_ns,
    )


def capture_managed_artifacts(
    root: Path, codebase_names: Sequence[str]
) -> tuple[CapturedArtifact, ...]:
    """Capture ALL existing allowlisted files, including locally unchanged ones."""
    ownership: dict[str, str | None] = {}
    for codebase in codebase_names:
        for filename in CODEBASE_MANAGED_MARKDOWN_ARTIFACTS:
            path = codebase_artifact_path(codebase, filename)
            if path in ownership:
                raise ArtifactValidationError(
                    "Run codebases have ambiguous artifact ownership"
                )
            ownership[path] = codebase
    ownership.update({path: None for path in REPOSITORY_MANAGED_ARTIFACTS})
    captured: list[CapturedArtifact] = []
    for path, codebase in sorted(ownership.items()):
        kind = artifact_kind(path)
        content = read_working_artifact(root, path, kind)
        if content is None:
            continue
        entry = ArtifactManifestEntry(
            path=path,
            kind=kind,
            scope="repository" if codebase is None else "codebase",
            codebase_name=codebase,
            byte_length=len(content),
            sha256=hashlib.sha256(content).hexdigest(),
        )
        captured.append(CapturedArtifact(entry, content))
    return tuple(captured)


def validate_required_artifacts(
    manifest: ArtifactManifest, required_paths: Sequence[str]
) -> None:
    """Reject an inventory missing any file its completed stages must have written.

    This reads only the manifest, so it applies equally to a new capture and to an
    inventory frozen by an earlier attempt, which is rejected and never recaptured.
    """
    available = {entry.path for entry in manifest.root}
    if not available.issuperset(required_paths):
        raise MissingRequiredArtifactError("A required generated artifact is missing")


def manifest_from_capture(captured: Sequence[CapturedArtifact]) -> ArtifactManifest:
    """Build the sorted content-free inventory for first-write-wins persistence."""
    return ArtifactManifest([artifact.descriptor for artifact in captured])


def revalidate_manifest(
    root: Path, manifest: ArtifactManifest
) -> tuple[CapturedArtifact, ...]:
    """Copy only the frozen inventory, rejecting missing/changed files.

    This never creates a replacement manifest or includes newly appearing files.
    """
    captured: list[CapturedArtifact] = []
    for entry in manifest.root:
        content = read_working_artifact(root, entry.path, entry.kind)
        if content is None:
            raise ArtifactValidationError(
                "A frozen artifact is no longer available; regenerate"
            )
        validate_artifact_bytes(entry, content)
        captured.append(CapturedArtifact(entry, content))
    return tuple(captured)
