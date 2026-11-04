"""Content-free, validated contracts for immutable repository artifacts."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Annotated, Literal, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    StringConstraints,
    field_validator,
    model_validator,
)

from unoplat_code_confluence_query_engine.models.statistics.agent_usage_statistics import (
    WorkflowStatistics,
)
from unoplat_code_confluence_query_engine.services.repository.artifact_paths import (
    ARTIFACT_BYTE_LIMITS,
    REPOSITORY_MANAGED_ARTIFACTS,
    ArtifactKind,
    artifact_kind,
    codebase_artifact_path,
    validate_artifact_path,
    validate_codebase_name,
)

type FullCommitSha = Annotated[
    str,
    StringConstraints(
        pattern=r"^[0-9a-f]{40}$", min_length=40, max_length=40, strict=True
    ),
]
type PublicationStage = Literal[
    "lock",
    "eligibility",
    "capture",
    "manifest",
    "credentials",
    "recovery",
    "commit",
    "identity",
    "pr_create",
    "pr_metadata",
]
type ArtifactAvailability = Literal[
    "available",
    "no_artifacts",
    "pending",
    "failed",
    "unavailable",
]
type ArtifactReadErrorCode = Literal[
    "invalid_artifact_path",
    "run_not_found",
    "artifact_not_found",
    "artifact_identity_pending",
    "artifact_identity_unavailable",
    "artifact_identity_invalid",
    "artifact_integrity_failed",
    "artifact_missing_at_commit",
    "credentials_unavailable",
    "credentials_invalid",
    "provider_credentials_rejected",
    "provider_permission_denied",
    "provider_not_found",
    "provider_request_rejected",
    "provider_response_invalid",
    "provider_rate_limited",
    "provider_unavailable",
    "metadata_unavailable",
    "artifact_read_failed",
]


class ArtifactManifestEntry(BaseModel):
    """One exact-byte artifact descriptor, with no content or absolute paths."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    path: str
    kind: ArtifactKind
    scope: Literal["codebase", "repository"]
    codebase_name: str | None
    byte_length: int = Field(ge=0)
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$", min_length=64, max_length=64)

    @field_validator("path")
    @classmethod
    def validate_path(cls, path: str) -> str:
        return validate_artifact_path(path)

    @model_validator(mode="after")
    def validate_ownership(self) -> Self:
        if self.kind != artifact_kind(self.path):
            raise ValueError("Artifact kind does not match its allowlisted path")
        if self.byte_length > ARTIFACT_BYTE_LIMITS[self.kind]:
            raise ValueError("Artifact exceeds its byte limit")
        if self.scope == "repository":
            if (
                self.codebase_name is not None
                or self.path not in REPOSITORY_MANAGED_ARTIFACTS
            ):
                raise ValueError("Invalid repository artifact ownership")
        elif self.codebase_name is None or self.path != codebase_artifact_path(
            self.codebase_name, self.path.rsplit("/", 1)[-1]
        ):
            raise ValueError("Invalid codebase artifact ownership")
        return self


class ArtifactManifest(RootModel[list[ArtifactManifestEntry]]):
    """JSONB array whose entries must have unique, deterministically sorted paths."""

    @model_validator(mode="after")
    def validate_inventory(self) -> Self:
        paths = [entry.path for entry in self.root]
        if paths != sorted(set(paths)):
            raise ValueError("Artifact manifest paths must be unique and sorted")
        return self


class ArtifactPublicationError(BaseModel):
    """Safe persisted error metadata. Callers supply static, sanitized messages."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    code: str = Field(pattern=r"^[a-z][a-z0-9_]*$", max_length=80)
    stage: PublicationStage
    message: str = Field(max_length=512)
    retryable: bool


class StoredArtifactIdentity(BaseModel):
    """Validated persisted identity. A NULL manifest is never treated as empty."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    manifest: ArtifactManifest | None
    commit_sha: FullCommitSha | None

    @model_validator(mode="after")
    def validate_sha_has_inventory(self) -> Self:
        if self.commit_sha is not None and (
            self.manifest is None or not self.manifest.root
        ):
            raise ValueError("Saved SHA has no manifest")
        return self


def parse_stored_artifact_identity(
    *,
    manifest: object,
    commit_sha: object,
    codebase_names: Iterable[str],
) -> StoredArtifactIdentity:
    """Validate a run's persisted SHA and manifest, including codebase ownership.

    Args:
        manifest: Stored manifest JSON value.
        commit_sha: Stored commit SHA value.
        codebase_names: Codebase names recorded for the run.

    Returns:
        The validated identity.

    Raises:
        ValueError: The stored identity is malformed or belongs to other codebases.
            Pydantic's ValidationError is a ValueError.
    """
    names = {validate_codebase_name(name) for name in codebase_names}
    identity = StoredArtifactIdentity.model_validate(
        {"manifest": manifest, "commit_sha": commit_sha}
    )
    if identity.manifest is not None and any(
        entry.scope == "codebase" and entry.codebase_name not in names
        for entry in identity.manifest.root
    ):
        raise ValueError("Manifest does not belong to the run's codebases")
    return identity


class RepositoryAgentSnapshotMetadata(BaseModel):
    """Run metadata returned by the snapshot API. It holds no generated content.

    ``artifact_manifest`` is null when no inventory was saved and ``[]`` only when
    an empty inventory was persisted, so the two cannot be confused.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    repository_workflow_run_id: str
    availability: ArtifactAvailability
    artifact_commit_sha: FullCommitSha | None
    artifact_manifest: ArtifactManifest | None
    artifact_publication_error: ArtifactPublicationError | None
    repository_activity_progress: dict[str, float]
    overall_progress: float | None
    statistics: WorkflowStatistics | None

    @model_validator(mode="after")
    def validate_availability(self) -> Self:
        if (self.availability == "available") != (self.artifact_commit_sha is not None):
            raise ValueError("Only available artifacts have a commit SHA")
        if self.availability == "no_artifacts" and (
            self.artifact_manifest is None or self.artifact_manifest.root
        ):
            raise ValueError("No-artifact runs require a persisted empty manifest")
        return self


class ArtifactReadErrorDetail(BaseModel):
    """Static, machine-readable artifact read failure."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    code: ArtifactReadErrorCode
    message: str
    retryable: bool


class ArtifactIdentityResult(BaseModel):
    """Durably saved outcome of required publication, returned before any PR work.

    ``saved`` means a provider-verified full SHA and frozen manifest are in
    PostgreSQL. ``no_artifacts`` means a valid empty inventory, which has no SHA.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    status: Literal["saved", "no_artifacts"]
    commit_sha: FullCommitSha | None = None

    @model_validator(mode="after")
    def validate_identity(self) -> Self:
        if (self.status == "saved") != (self.commit_sha is not None):
            raise ValueError("Only saved artifact identities have a commit SHA")
        return self


class ArtifactCommitPublication(BaseModel):
    """Verified remote identity returned before any PR-creation operation."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    commit_sha: FullCommitSha
    status: Literal["modified", "no_changes"]
    branch_name: str
    default_branch: str
