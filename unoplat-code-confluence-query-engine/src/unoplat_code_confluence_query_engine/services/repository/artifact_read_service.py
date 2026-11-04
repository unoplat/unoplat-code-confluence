"""Read-only artifact metadata and exact-commit single-file reads.

Availability is derived once here, so the snapshot and file endpoints cannot
disagree. Bytes come only from the provider at the run's saved SHA, never from a
checkout, a branch, or a legacy column.
"""

from __future__ import annotations

import asyncio
from collections.abc import Mapping
from dataclasses import dataclass
from http.client import HTTPException as HttpProtocolError

from ghapi.core import GhApi
from loguru import logger
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from unoplat_code_confluence_commons.credential_enums import ProviderKey
from unoplat_code_confluence_commons.pr_metadata_model import PrMetadata
from unoplat_code_confluence_commons.repo_models import (
    Repository,
    RepositoryAgentCodebaseProgress,
    RepositoryAgentMdSnapshot,
    RepositoryWorkflowRun,
)

from unoplat_code_confluence_query_engine.db.postgres.db import get_startup_session
from unoplat_code_confluence_query_engine.models.output.repository_artifacts import (
    ArtifactAvailability,
    ArtifactManifestEntry,
    ArtifactPublicationError,
    ArtifactReadErrorCode,
    ArtifactReadErrorDetail,
    RepositoryAgentSnapshotMetadata,
    StoredArtifactIdentity,
    parse_stored_artifact_identity,
)
from unoplat_code_confluence_query_engine.models.statistics.agent_usage_statistics import (
    WorkflowStatistics,
)
from unoplat_code_confluence_query_engine.services.github.agent_md_pr_publisher import (
    read_remote_artifact,
)
from unoplat_code_confluence_query_engine.services.github.github_api_helpers import (
    extract_http_error_status,
    is_rate_limited_error,
)
from unoplat_code_confluence_query_engine.services.github.repository_github_client import (
    RepositoryCredentialsInvalidError,
    RepositoryCredentialsMissingError,
    create_repository_github_client,
)
from unoplat_code_confluence_query_engine.services.repository.artifact_manifest import (
    ArtifactValidationError,
)
from unoplat_code_confluence_query_engine.services.repository.artifact_paths import (
    artifact_kind,
)
from unoplat_code_confluence_query_engine.services.repository.idempotency_service import (
    ACTIVE_AGENT_WORKFLOW_STATUSES,
    get_latest_completed_agent_snapshot,
)

_READ_ERRORS: dict[ArtifactReadErrorCode, tuple[str, bool]] = {
    "invalid_artifact_path": ("Artifact path is not a managed artifact path", False),
    "run_not_found": ("Repository workflow run was not found", False),
    "artifact_not_found": ("This run's manifest does not list that path", False),
    "artifact_identity_pending": (
        "Artifacts are viewable once this run saves its Git identity",
        True,
    ),
    "artifact_identity_unavailable": (
        "This run has no saved Git identity; regenerate to view artifacts",
        False,
    ),
    "artifact_identity_invalid": (
        "Stored artifact identity is invalid; regeneration is required",
        False,
    ),
    "artifact_integrity_failed": (
        "Artifact bytes at the saved commit do not match the manifest",
        False,
    ),
    "artifact_missing_at_commit": (
        "The saved commit has no regular file at that path",
        False,
    ),
    "credentials_unavailable": (
        "Configure repository credentials before reading artifacts",
        False,
    ),
    "credentials_invalid": (
        "Repository credentials or GitHub host configuration are invalid",
        False,
    ),
    "provider_credentials_rejected": (
        "GitHub rejected the stored repository credentials",
        False,
    ),
    "provider_permission_denied": (
        "The stored repository credentials cannot read this repository",
        False,
    ),
    "provider_not_found": (
        "GitHub could not find the saved commit, or the credentials cannot see it",
        False,
    ),
    "provider_request_rejected": ("GitHub rejected the artifact read", False),
    "provider_response_invalid": ("GitHub returned an invalid response", False),
    "provider_rate_limited": ("GitHub rate limited the artifact read", True),
    "provider_unavailable": ("GitHub is temporarily unavailable", True),
    "metadata_unavailable": ("Artifact metadata is temporarily unavailable", True),
    "artifact_read_failed": ("Artifact read failed unexpectedly", False),
}

_INVALID_IDENTITY_ERROR = ArtifactPublicationError(
    code="artifact_identity_invalid",
    stage="identity",
    message="Stored artifact identity is invalid; regeneration is required",
    retryable=False,
)
_UNREADABLE_PUBLICATION_ERROR = ArtifactPublicationError(
    code="publication_error_unreadable",
    stage="identity",
    message="Stored publication diagnostics could not be read",
    retryable=False,
)

_AVAILABILITY_READ_ERRORS: dict[ArtifactAvailability, ArtifactReadErrorCode] = {
    "no_artifacts": "artifact_not_found",
    "pending": "artifact_identity_pending",
    "failed": "artifact_identity_unavailable",
    "unavailable": "artifact_identity_unavailable",
}


class ArtifactReadError(Exception):
    """A static, safe artifact read failure with a stable machine code."""

    def __init__(self, code: ArtifactReadErrorCode) -> None:
        message, retryable = _READ_ERRORS[code]
        super().__init__(message)
        self.detail = ArtifactReadErrorDetail(
            code=code, message=message, retryable=retryable
        )


@dataclass(frozen=True)
class VerifiedArtifact:
    """Bytes proven to match their manifest entry at the run's saved commit."""

    entry: ArtifactManifestEntry
    content: bytes


@dataclass(frozen=True)
class _RunArtifactState:
    availability: ArtifactAvailability
    identity: StoredArtifactIdentity | None
    publication_error: ArtifactPublicationError | None


@dataclass(frozen=True)
class _ArtifactReadTarget:
    provider_key: ProviderKey
    commit_sha: str
    entry: ArtifactManifestEntry


def derive_artifact_availability(
    *,
    run_status: str,
    identity: StoredArtifactIdentity | None,
    no_artifacts_recorded: bool,
    has_publication_error: bool,
) -> ArtifactAvailability:
    """Derive a run's availability from validated stored state.

    Args:
        run_status: The run's workflow status.
        identity: Validated identity, or None when the stored identity is invalid.
        no_artifacts_recorded: Whether the publisher recorded its no-artifact result.
        has_publication_error: Whether a publication error is stored.

    Returns:
        The availability. A saved SHA stays available whatever later happened to the
        PR or the run. A NULL manifest never counts as an empty inventory.
    """
    if identity is None:
        return "failed"
    if identity.commit_sha is not None:
        return "available"
    if (
        identity.manifest is not None
        and not identity.manifest.root
        and no_artifacts_recorded
    ):
        return "no_artifacts"
    if run_status in ACTIVE_AGENT_WORKFLOW_STATUSES:
        return "pending"
    return "failed" if has_publication_error else "unavailable"


def classify_provider_failure(error: Exception) -> ArtifactReadErrorCode:
    """Map a provider read failure to a static code, without using its text."""
    if isinstance(error, ArtifactValidationError):
        return "artifact_integrity_failed"
    status = extract_http_error_status(error)
    if status is None:
        if isinstance(error, ValueError):
            return "provider_response_invalid"
        if isinstance(error, (OSError, HttpProtocolError)):
            return "provider_unavailable"
        return "artifact_read_failed"
    if status == 401:
        return "provider_credentials_rejected"
    if status == 403:
        return (
            "provider_rate_limited"
            if is_rate_limited_error(error)
            else "provider_permission_denied"
        )
    if status == 404:
        return "provider_not_found"
    if status == 429:
        return "provider_rate_limited"
    if status == 408 or status >= 500:
        return "provider_unavailable"
    return "provider_request_rejected"


def _parse_publication_error(raw: object) -> ArtifactPublicationError | None:
    if raw is None:
        return None
    try:
        return ArtifactPublicationError.model_validate(raw)
    except ValidationError:
        return _UNREADABLE_PUBLICATION_ERROR


def _records_no_artifacts(raw_pr_metadata: object) -> bool:
    if raw_pr_metadata is None:
        return False
    try:
        return PrMetadata.model_validate(raw_pr_metadata).status == "no_artifacts"
    except ValidationError:
        return False


def _activity_progress(raw: Mapping[str, object]) -> dict[str, float]:
    """Keep numeric progress only, so no stored text can reach the response."""
    return {
        name: float(value)
        for name, value in raw.items()
        if isinstance(value, (int, float)) and not isinstance(value, bool)
    }


def _workflow_statistics(raw: object) -> WorkflowStatistics | None:
    if raw is None:
        return None
    try:
        return WorkflowStatistics.model_validate(raw)
    except ValidationError:
        logger.warning("Stored workflow statistics could not be read")
        return None


async def _run_artifact_state(
    session: AsyncSession,
    snapshot: RepositoryAgentMdSnapshot,
    run_status: str,
) -> _RunArtifactState:
    names = (
        (
            await session.execute(
                select(RepositoryAgentCodebaseProgress.codebase_name).where(
                    RepositoryAgentCodebaseProgress.repository_owner_name
                    == snapshot.repository_owner_name,
                    RepositoryAgentCodebaseProgress.repository_name
                    == snapshot.repository_name,
                    RepositoryAgentCodebaseProgress.repository_workflow_run_id
                    == snapshot.repository_workflow_run_id,
                )
            )
        )
        .scalars()
        .all()
    )
    try:
        identity = parse_stored_artifact_identity(
            manifest=snapshot.artifact_manifest,
            commit_sha=snapshot.artifact_commit_sha,
            codebase_names=names,
        )
    except ValueError:
        logger.warning(
            "Stored artifact identity is invalid for run_id={}",
            snapshot.repository_workflow_run_id,
        )
        identity = None
    publication_error = (
        _parse_publication_error(snapshot.artifact_publication_error)
        if identity is not None
        else _INVALID_IDENTITY_ERROR
    )
    return _RunArtifactState(
        availability=derive_artifact_availability(
            run_status=run_status,
            identity=identity,
            no_artifacts_recorded=_records_no_artifacts(snapshot.pr_metadata),
            has_publication_error=publication_error is not None,
        ),
        identity=identity,
        publication_error=publication_error,
    )


async def _exact_snapshot(
    session: AsyncSession, owner_name: str, repo_name: str, run_id: str
) -> RepositoryAgentMdSnapshot | None:
    result = await session.execute(
        select(RepositoryAgentMdSnapshot).where(
            RepositoryAgentMdSnapshot.repository_owner_name == owner_name,
            RepositoryAgentMdSnapshot.repository_name == repo_name,
            RepositoryAgentMdSnapshot.repository_workflow_run_id == run_id,
        )
    )
    return result.scalar_one_or_none()


async def read_repository_snapshot_metadata(
    *,
    owner_name: str,
    repo_name: str,
    repository_workflow_run_id: str | None,
) -> RepositoryAgentSnapshotMetadata | None:
    """Read metadata for an exact run, or for the latest completed agent run.

    Args:
        owner_name: Repository owner name.
        repo_name: Repository name.
        repository_workflow_run_id: Exact run, or None for the latest completed run.

    Returns:
        The run's metadata, or None when no matching snapshot exists. Run selection
        never considers whether a run has files.
    """
    async with get_startup_session() as session:
        snapshot = (
            await _exact_snapshot(
                session, owner_name, repo_name, repository_workflow_run_id
            )
            if repository_workflow_run_id is not None
            else await get_latest_completed_agent_snapshot(
                session=session,
                repository_name=repo_name,
                repository_owner_name=owner_name,
            )
        )
        if snapshot is None:
            return None
        run = await session.get(
            RepositoryWorkflowRun,
            (repo_name, owner_name, snapshot.repository_workflow_run_id),
        )
        if run is None:
            return None
        state = await _run_artifact_state(session, snapshot, run.status)
        identity = state.identity
        return RepositoryAgentSnapshotMetadata(
            repository_workflow_run_id=snapshot.repository_workflow_run_id,
            availability=state.availability,
            artifact_commit_sha=identity.commit_sha if identity else None,
            artifact_manifest=identity.manifest if identity else None,
            artifact_publication_error=state.publication_error,
            repository_activity_progress=_activity_progress(
                snapshot.repository_activity_progress
            ),
            overall_progress=(
                float(snapshot.overall_progress)
                if snapshot.overall_progress is not None
                else None
            ),
            statistics=_workflow_statistics(snapshot.statistics),
        )


async def _load_read_target(
    owner_name: str, repo_name: str, run_id: str, path: str
) -> _ArtifactReadTarget:
    """Resolve the saved SHA and exact manifest entry for a requested path.

    Errors are raised after the session closes, because get_startup_session logs
    every exception that crosses it as a database session error.
    """
    async with get_startup_session() as session:
        repository = await session.get(Repository, (repo_name, owner_name))
        run = await session.get(
            RepositoryWorkflowRun, (repo_name, owner_name, run_id)
        )
        snapshot = await _exact_snapshot(session, owner_name, repo_name, run_id)
        if repository is None or run is None or snapshot is None:
            state = None
            provider_key = None
        else:
            state = await _run_artifact_state(session, snapshot, run.status)
            provider_key = repository.repository_provider
    if state is None or provider_key is None:
        raise ArtifactReadError("run_not_found")
    if state.identity is None:
        raise ArtifactReadError("artifact_identity_invalid")
    if state.availability != "available":
        raise ArtifactReadError(_AVAILABILITY_READ_ERRORS[state.availability])
    commit_sha = state.identity.commit_sha
    manifest = state.identity.manifest
    if commit_sha is None or manifest is None:
        raise ArtifactReadError("artifact_identity_invalid")
    for entry in manifest.root:
        if entry.path == path:
            return _ArtifactReadTarget(provider_key, commit_sha, entry)
    raise ArtifactReadError("artifact_not_found")


async def _provider_client(
    owner_name: str, repo_name: str, provider_key: ProviderKey
) -> GhApi:
    try:
        return await create_repository_github_client(
            owner_name, repo_name, provider_key
        )
    except RepositoryCredentialsMissingError:
        raise ArtifactReadError("credentials_unavailable") from None
    except RepositoryCredentialsInvalidError:
        raise ArtifactReadError("credentials_invalid") from None


async def read_repository_artifact(
    *,
    owner_name: str,
    repo_name: str,
    repository_workflow_run_id: str,
    path: str,
) -> VerifiedArtifact:
    """Read one manifest-listed file at the commit saved for an exact run.

    This app has no per-user authentication. Access is limited to repositories and
    runs it tracks, using the provider credentials it stores for that repository.

    Args:
        owner_name: Repository owner name.
        repo_name: Repository name.
        repository_workflow_run_id: Exact run that owns the file.
        path: Repository-relative path, matched exactly against the manifest.

    Returns:
        Bytes verified against the manifest for size, UTF-8 and SHA-256.

    Raises:
        ArtifactReadError: The read failed. Its detail holds only static text, and
            the provider exception is deliberately not chained to it.
    """
    try:
        artifact_kind(path)
    except ValueError:
        raise ArtifactReadError("invalid_artifact_path") from None
    try:
        target = await _load_read_target(
            owner_name, repo_name, repository_workflow_run_id, path
        )
        api = await _provider_client(owner_name, repo_name, target.provider_key)
    except (SQLAlchemyError, OSError):
        raise ArtifactReadError("metadata_unavailable") from None
    try:
        content = await asyncio.to_thread(
            read_remote_artifact,
            api,
            owner_name=owner_name,
            repo_name=repo_name,
            commit_sha=target.commit_sha,
            entry=target.entry,
        )
    except Exception as error:
        code = classify_provider_failure(error)
        # Type and status only. Provider messages and bodies are never logged.
        logger.warning(
            "Artifact read failed code={} run_id={} path={} status={} error_type={}",
            code,
            repository_workflow_run_id,
            path,
            extract_http_error_status(error),
            type(error).__name__,
        )
        raise ArtifactReadError(code) from None
    if content is None:
        raise ArtifactReadError("artifact_missing_at_commit")
    return VerifiedArtifact(target.entry, content)
