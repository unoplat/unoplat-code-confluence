"""Run-serialized immutable artifact publication shared by API and Temporal.

Required: capture -> freeze manifest -> publish commit/ref -> persist SHA.
Best effort: reconcile PR from the saved SHA, recording a static safe error.
Row transactions are short and never span provider calls. A persisted SHA is
independent of PR outcome; every pre-SHA retry tries exact remote recovery first.
Cancellation is never recorded as a failure: it unwinds through these handlers,
and session_advisory_lock releases both locks.
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Callable, Sequence
from contextlib import asynccontextmanager
from dataclasses import dataclass
from functools import partial
from pathlib import Path
from typing import Literal, TypeVar, override

from fastapi import HTTPException
from ghapi.core import GhApi
from loguru import logger
from pydantic import ValidationError
from sqlalchemy import Select, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncConnection
from unoplat_code_confluence_commons.credential_enums import ProviderKey
from unoplat_code_confluence_commons.pr_metadata_model import PrMetadata
from unoplat_code_confluence_commons.repo_models import (
    Repository,
    RepositoryAgentCodebaseProgress,
    RepositoryAgentMdSnapshot,
    RepositoryWorkflowOperation,
    RepositoryWorkflowRun,
)
from unoplat_code_confluence_commons.repository_checkout_coordination import (
    CheckoutAdmissionError,
    publisher_lock,
    repository_capture_guard,
)
from unoplat_code_confluence_commons.workflow_models import JobStatus

from unoplat_code_confluence_query_engine.db.postgres.db import (
    get_async_engine,
    get_startup_session,
)
from unoplat_code_confluence_query_engine.models.output.repository_artifacts import (
    ArtifactIdentityResult,
    ArtifactManifest,
    ArtifactPublicationError,
    PublicationStage,
    parse_stored_artifact_identity,
)
from unoplat_code_confluence_query_engine.services.github.agent_md_pr_publisher import (
    PublisherIdentityConflict,
    publication_branch_name,
    publish_artifact_commit,
    reconcile_artifact_pr,
    recover_artifact_commit,
    validate_commit_sha,
)
from unoplat_code_confluence_query_engine.services.github.github_api_helpers import (
    extract_http_error_status,
    is_rate_limited_error,
)
from unoplat_code_confluence_query_engine.services.github.repository_github_client import (
    RepositoryCredentialsInvalidError,
    RepositoryCredentialsMissingError,
    create_repository_github_client,
    git_web_base_url,
    load_repository_credentials,
)
from unoplat_code_confluence_query_engine.services.repository.artifact_manifest import (
    ArtifactValidationError,
    CapturedArtifact,
    MissingRequiredArtifactError,
    capture_managed_artifacts,
    manifest_from_capture,
    revalidate_manifest,
    validate_required_artifacts,
)
from unoplat_code_confluence_query_engine.services.repository.artifact_paths import (
    validate_codebase_name,
)
from unoplat_code_confluence_query_engine.services.repository.local_git_artifacts import (
    LocalGitError,
    fetch_local_commit,
    has_local_commit,
    pin_local_commit,
    resolve_repository_checkout_root,
)
from unoplat_code_confluence_query_engine.services.repository.repository_metadata_service import (
    fetch_repository_metadata,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_backend_paths import (
    resolve_common_repository_root,
)

_T = TypeVar("_T")
type _CallerMode = Literal["manual", "automatic"]

# Below the activity's 10 minute start-to-close timeout, so that a slow automatic
# PR attempt records its safe error before Temporal abandons the attempt.
_AUTOMATIC_PR_RECONCILE_SECONDS = 540.0


class AgentMdPrError(Exception):
    """Sanitized publication error that callers map to their transport."""

    code = "publication_failed"
    retryable = True

    def metadata(self, stage: PublicationStage) -> ArtifactPublicationError:
        return ArtifactPublicationError(
            code=self.code,
            stage=stage,
            message=str(self),
            retryable=self.retryable,
        )


class AgentMdPrNotFoundError(AgentMdPrError):
    """Repository, run, or snapshot is missing."""

    code = "run_not_found"
    retryable = False


class AgentMdPrConfigurationError(AgentMdPrError):
    """Provider credentials or host configuration are unavailable."""

    code = "credentials_unavailable"
    retryable = False


class AgentMdPrAuthError(AgentMdPrError):
    """GitHub rejected the request with an auth/permission error."""

    code = "provider_permission_denied"
    retryable = False

    def __init__(self, message: str, status_code: int) -> None:
        super().__init__(message)
        self.status_code = status_code


class AgentMdPrInternalError(AgentMdPrError):
    """Local metadata or infrastructure operation failed."""

    code = "publication_internal_failure"


class AgentMdPrGithubError(AgentMdPrError):
    """Sanitized provider failure, with explicit retryability."""

    code = "provider_failure"

    def __init__(self, message: str, *, retryable: bool = True) -> None:
        super().__init__(message)
        self.retryable = retryable

    @override
    def metadata(self, stage: PublicationStage) -> ArtifactPublicationError:
        if stage == "pr_create":
            return ArtifactPublicationError(
                code="pr_creation_failed",
                stage=stage,
                message="Artifact commit is available; pull request creation failed",
                retryable=self.retryable,
            )
        return super().metadata(stage)


class AgentMdPrConflictError(AgentMdPrError):
    """An ineligible run or conflicting remote identity cannot be retried safely."""

    code = "artifact_identity_conflict"
    retryable = False


class AgentMdPrStaleArtifactError(AgentMdPrConflictError):
    """Frozen artifact provenance was lost. Regeneration is required."""

    code = "stale_artifact"


class AgentMdPrMissingArtifactError(AgentMdPrStaleArtifactError):
    """A stage that ran did not leave its required generated file."""

    code = "required_artifact_missing"


class AgentMdPrLocalSyncError(AgentMdPrError):
    """The saved commit is not yet in the local clone, so it cannot be viewed."""

    code = "local_sync_failed"


@dataclass
class _PublicationAttempt:
    """The furthest stage reached, for the safe error recorded on failure."""

    stage: PublicationStage = "lock"


@dataclass(frozen=True)
class _RunArtifacts:
    provider_key: ProviderKey
    codebase_names: tuple[str, ...]
    manifest: ArtifactManifest | None
    commit_sha: str | None
    pr_metadata: PrMetadata | None


@dataclass(frozen=True)
class _SavedIdentity:
    """Durable outcome of required publication. No SHA means an empty inventory."""

    state: _RunArtifacts
    manifest: ArtifactManifest
    commit_sha: str | None


def _snapshot_query(
    owner: str, repository: str, run_id: str
) -> Select[tuple[RepositoryAgentMdSnapshot]]:
    return select(RepositoryAgentMdSnapshot).where(
        RepositoryAgentMdSnapshot.repository_owner_name == owner,
        RepositoryAgentMdSnapshot.repository_name == repository,
        RepositoryAgentMdSnapshot.repository_workflow_run_id == run_id,
    )


async def _read_run_artifacts(
    owner: str, repository: str, run_id: str, mode: _CallerMode
) -> _RunArtifacts:
    async with get_startup_session() as session:
        repo = await session.get(Repository, (repository, owner))
        run = await session.get(RepositoryWorkflowRun, (repository, owner, run_id))
        snapshot = (
            await session.execute(_snapshot_query(owner, repository, run_id))
        ).scalar_one_or_none()
        if repo is None or run is None or snapshot is None:
            raise AgentMdPrNotFoundError(
                "Repository workflow run or artifact metadata was not found"
            )
        if run.operation not in (
            RepositoryWorkflowOperation.AGENTS_GENERATION,
            RepositoryWorkflowOperation.AGENT_MD_UPDATE,
        ):
            raise AgentMdPrConflictError(
                "Only generation/update runs can publish artifacts"
            )
        eligible = (
            run.status == JobStatus.COMPLETED.value
            if mode == "manual"
            else run.status in {JobStatus.RUNNING.value, JobStatus.RETRYING.value}
        )
        if not eligible:
            raise AgentMdPrConflictError(
                "Manual publication requires a completed run; automatic publication requires its admitted active run"
            )
        names = (
            (
                await session.execute(
                    select(RepositoryAgentCodebaseProgress.codebase_name)
                    .where(
                        RepositoryAgentCodebaseProgress.repository_owner_name == owner,
                        RepositoryAgentCodebaseProgress.repository_name == repository,
                        RepositoryAgentCodebaseProgress.repository_workflow_run_id
                        == run_id,
                    )
                    .order_by(RepositoryAgentCodebaseProgress.codebase_name)
                )
            )
            .scalars()
            .all()
        )
        try:
            codebase_names = tuple(names)
            identity = parse_stored_artifact_identity(
                manifest=snapshot.artifact_manifest,
                commit_sha=snapshot.artifact_commit_sha,
                codebase_names=codebase_names,
            )
            manifest = identity.manifest
            sha = identity.commit_sha
            metadata = (
                PrMetadata.model_validate(snapshot.pr_metadata)
                if snapshot.pr_metadata is not None
                else None
            )
            if (
                metadata is not None
                and metadata.status != "no_artifacts"
                and metadata.branch_name != publication_branch_name(run_id)
            ):
                raise ValueError("Persisted PR does not belong to the full run branch")
        except (ValueError, ValidationError) as error:
            raise AgentMdPrStaleArtifactError(
                "Stored artifact identity is invalid; regeneration is required"
            ) from error
        if mode == "manual" and manifest is None:
            raise AgentMdPrStaleArtifactError(
                "This run has no frozen artifact manifest; regenerate before publishing"
            )
        return _RunArtifacts(
            repo.repository_provider, codebase_names, manifest, sha, metadata
        )


async def _persist_manifest(
    owner: str, repository: str, run_id: str, manifest: ArtifactManifest
) -> None:
    async with get_startup_session() as session:
        snapshot = (
            await session.execute(
                _snapshot_query(owner, repository, run_id).with_for_update()
            )
        ).scalar_one_or_none()
        if snapshot is None:
            raise AgentMdPrNotFoundError(
                "Artifact metadata disappeared during publication"
            )
        if snapshot.artifact_manifest is None:
            if snapshot.artifact_commit_sha is not None:
                raise AgentMdPrConflictError(
                    "Saved artifact SHA cannot acquire a replacement manifest"
                )
            snapshot.artifact_manifest = manifest.model_dump(mode="json")
        elif ArtifactManifest.model_validate(snapshot.artifact_manifest) != manifest:
            raise AgentMdPrConflictError(
                "Prepared manifest is immutable; regeneration is required"
            )


async def _persist_sha(
    owner: str, repository: str, run_id: str, manifest: ArtifactManifest, sha: str
) -> None:
    validate_commit_sha(sha)
    if not manifest.root:
        raise AgentMdPrConflictError(
            "An empty artifact manifest cannot have a commit SHA"
        )
    async with get_startup_session() as session:
        snapshot = (
            await session.execute(
                _snapshot_query(owner, repository, run_id).with_for_update()
            )
        ).scalar_one_or_none()
        if snapshot is None:
            raise AgentMdPrNotFoundError(
                "Artifact metadata disappeared during publication"
            )
        if (
            snapshot.artifact_manifest is None
            or ArtifactManifest.model_validate(snapshot.artifact_manifest) != manifest
        ):
            raise AgentMdPrConflictError(
                "Prepared artifact manifest changed during publication"
            )
        if snapshot.artifact_commit_sha is None:
            snapshot.artifact_commit_sha = sha
        elif snapshot.artifact_commit_sha != sha:
            raise AgentMdPrConflictError("Saved artifact commit identity is immutable")
        snapshot.artifact_publication_error = None


async def _persist_pr_metadata(
    owner: str,
    repository: str,
    run_id: str,
    metadata: PrMetadata,
    expected_sha: str | None,
) -> tuple[PrMetadata, bool]:
    async with get_startup_session() as session:
        snapshot = (
            await session.execute(
                _snapshot_query(owner, repository, run_id).with_for_update()
            )
        ).scalar_one_or_none()
        if snapshot is None:
            raise AgentMdPrNotFoundError(
                "Artifact metadata disappeared during publication"
            )
        if snapshot.artifact_commit_sha != expected_sha:
            raise AgentMdPrConflictError(
                "PR metadata cannot replace the saved artifact identity"
            )
        if expected_sha is None and snapshot.artifact_manifest != []:
            raise AgentMdPrConflictError(
                "PR metadata requires a saved SHA or verified empty manifest"
            )
        existed = snapshot.pr_metadata is not None
        if existed:
            previous = PrMetadata.model_validate(snapshot.pr_metadata)
            if (
                previous.branch_name != metadata.branch_name
                or previous.pr_number is not None
                and previous.pr_number != metadata.pr_number
                or previous.pr_url is not None
                and previous.pr_url != metadata.pr_url
            ):
                raise AgentMdPrConflictError("Persisted PR identity cannot be replaced")
            metadata = metadata.model_copy(update={"created_at": previous.created_at})
        snapshot.pr_metadata = metadata.model_dump(mode="json")
        snapshot.artifact_publication_error = None
        return metadata, existed


async def _persist_error(
    owner: str, repository: str, run_id: str, error: ArtifactPublicationError
) -> None:
    # This write is independent of PR metadata and never clears the manifest/SHA.
    # If persistence itself is unavailable, retain the original sanitized failure.
    try:
        async with get_startup_session() as session:
            snapshot = (
                await session.execute(
                    _snapshot_query(owner, repository, run_id).with_for_update()
                )
            ).scalar_one_or_none()
            if snapshot is not None:
                snapshot.artifact_publication_error = error.model_dump(mode="json")
    except Exception:
        logger.warning("Could not persist sanitized artifact publication error")


async def _blocking_call(operation: Callable[[], _T]) -> _T:
    """Keep locks held until a cancelled thread finishes its remote/file operation."""
    task = asyncio.create_task(asyncio.to_thread(operation))
    try:
        return await asyncio.shield(task)
    except asyncio.CancelledError:
        while not task.done():
            try:
                await asyncio.shield(task)
            except asyncio.CancelledError:
                continue
            except Exception:
                break
        # Retrieve the result/exception without masking cancellation. This prevents
        # a background urllib call from mutating a ref after the lock is released.
        if not task.cancelled():
            task.exception()
        raise


async def _github_call(operation: Callable[[], _T]) -> _T:
    try:
        return await _blocking_call(operation)
    except PublisherIdentityConflict as error:
        raise AgentMdPrConflictError(
            "Run branch or PR conflicts with the frozen artifact identity; it was not replaced"
        ) from error
    except Exception as error:
        status = extract_http_error_status(error)
        if status == 403 and is_rate_limited_error(error):
            raise AgentMdPrGithubError(
                "GitHub artifact publication was rate limited"
            ) from error
        if status in {401, 403}:
            raise AgentMdPrAuthError(
                "GitHub denied artifact publication access", status_code=status
            ) from error
        retryable = status is None or status in {408, 429} or status >= 500
        raise AgentMdPrGithubError(
            "GitHub artifact publication failed", retryable=retryable
        ) from error


async def _github_client(owner: str, repository: str, provider: ProviderKey) -> GhApi:
    try:
        return await create_repository_github_client(owner, repository, provider)
    except RepositoryCredentialsInvalidError as error:
        raise AgentMdPrConfigurationError(
            "Repository credentials or GitHub host configuration are invalid"
        ) from error
    except RepositoryCredentialsMissingError as error:
        raise AgentMdPrConfigurationError(
            "Configure repository credentials before publishing artifacts"
        ) from error


async def _sync_local_commit(
    owner: str, repository: str, run_id: str, provider: ProviderKey, sha: str
) -> None:
    """Make the saved commit readable from the local clone and pin it there.

    The artifact viewer reads only the local object store, so a saved SHA that is
    not stored locally cannot be viewed. A commit already present is only pinned,
    which keeps retries cheap and needs no provider call.
    """
    try:
        root = await resolve_repository_checkout_root(owner, repository)
        if not await _blocking_call(partial(has_local_commit, root, sha)):
            token, api_host = await load_repository_credentials(provider)
            remote_url = f"{git_web_base_url(api_host)}/{owner}/{repository}.git"
            await _blocking_call(
                partial(
                    fetch_local_commit, root, sha, remote_url=remote_url, token=token
                )
            )
        await _blocking_call(partial(pin_local_commit, root, sha, run_id))
    except (
        RepositoryCredentialsMissingError,
        RepositoryCredentialsInvalidError,
    ) as error:
        raise AgentMdPrConfigurationError(
            "Configure repository credentials before publishing artifacts"
        ) from error
    except LocalGitError as error:
        raise AgentMdPrLocalSyncError(
            "The artifact commit could not be stored in the local repository"
        ) from error


async def _checkout_root(owner: str, repository: str, names: tuple[str, ...]) -> Path:
    try:
        metadata = await fetch_repository_metadata(owner, repository)
        codebases = metadata.codebase_metadata
        for codebase in codebases:
            validate_codebase_name(codebase.codebase_name)
        root = Path(resolve_common_repository_root(codebases))
        paths = {
            codebase.codebase_name: Path(codebase.codebase_path)
            for codebase in codebases
        }
        for name in names:
            expected = root if name in {"", "."} else root / name
            if paths.get(name) != expected:
                raise ValueError(
                    "Run codebase no longer has its proven repository path"
                )
        return root
    except HTTPException as error:
        if error.status_code != 404:
            raise AgentMdPrInternalError(
                "Repository checkout metadata lookup failed"
            ) from error
        raise AgentMdPrStaleArtifactError(
            "Run checkout metadata is missing; regeneration is required"
        ) from error
    except ValueError as error:
        raise AgentMdPrStaleArtifactError(
            "Run checkout paths cannot be proven; regeneration is required"
        ) from error


async def _reject_newer_mutator(owner: str, repository: str, run_id: str) -> None:
    """Supplement original admission with frozen-retry provenance under the guard."""
    async with get_startup_session() as session:
        run = await session.get(RepositoryWorkflowRun, (repository, owner, run_id))
        if run is None:
            raise AgentMdPrNotFoundError("Repository workflow run was not found")
        newer = await session.execute(
            select(RepositoryWorkflowRun.repository_workflow_run_id)
            .where(
                RepositoryWorkflowRun.repository_owner_name == owner,
                RepositoryWorkflowRun.repository_name == repository,
                RepositoryWorkflowRun.repository_workflow_run_id != run_id,
                RepositoryWorkflowRun.operation.in_(tuple(RepositoryWorkflowOperation)),
                RepositoryWorkflowRun.status != JobStatus.SUBMITTED.value,
                RepositoryWorkflowRun.started_at >= run.started_at,
            )
            .limit(1)
        )
        if newer.scalar_one_or_none() is not None:
            raise AgentMdPrStaleArtifactError(
                "A newer checkout mutator invalidates this retry; regenerate"
            )


def _sanitize_publication_error(error: Exception) -> Exception:
    if isinstance(error, (AgentMdPrError, SQLAlchemyError)):
        return error
    if isinstance(error, MissingRequiredArtifactError):
        return AgentMdPrMissingArtifactError(
            "A required generated artifact is missing; regeneration is required"
        )
    if isinstance(error, (CheckoutAdmissionError, ArtifactValidationError)):
        return AgentMdPrStaleArtifactError(
            "Frozen artifact files or checkout provenance cannot be verified; regeneration is required"
        )
    return AgentMdPrInternalError("Artifact publication infrastructure failed")


def _publication_error_metadata(
    error: Exception, stage: PublicationStage
) -> ArtifactPublicationError:
    if isinstance(error, AgentMdPrError):
        return error.metadata(stage)
    return ArtifactPublicationError(
        code="publication_database_failure",
        stage=stage,
        message="Artifact publication metadata could not be persisted",
        retryable=True,
    )


@asynccontextmanager
async def _publication_attempt(
    owner: str, repository: str, run_id: str, attempt: _PublicationAttempt
) -> AsyncIterator[AsyncConnection]:
    """Hold the per-run lock and record any failure as a static safe error.

    Only Exception is handled, so cancellation propagates unrecorded and the lock
    is still released. Failures inside the lock are recorded before its release,
    so an older failed attempt cannot overwrite a newer successful attempt's state.
    """
    error_recorded = False
    try:
        # The dedicated lock connection has no long-lived row transaction. Always
        # acquire the per-run lock BEFORE the repository admission/capture lock.
        async with publisher_lock(
            get_async_engine(), owner, repository, run_id
        ) as connection:
            try:
                yield connection
            except Exception as error:
                sanitized = _sanitize_publication_error(error)
                await _persist_error(
                    owner,
                    repository,
                    run_id,
                    _publication_error_metadata(sanitized, attempt.stage),
                )
                error_recorded = True
                if sanitized is error:
                    raise
                raise sanitized from error
    except Exception as error:
        if error_recorded:
            raise
        sanitized = _sanitize_publication_error(error)
        await _persist_error(
            owner,
            repository,
            run_id,
            _publication_error_metadata(sanitized, attempt.stage),
        )
        if sanitized is error:
            raise
        raise sanitized from error


async def _ensure_saved_identity(
    connection: AsyncConnection,
    owner: str,
    repository: str,
    run_id: str,
    mode: _CallerMode,
    attempt: _PublicationAttempt,
    required_paths: Sequence[str] = (),
) -> _SavedIdentity:
    """Return the saved identity, establishing it first when none exists.

    A saved SHA wins and is returned without reading files or calling the provider;
    it was verified before it was saved. Only automatic original generation reaches
    the capture branch, because _read_run_artifacts rejects a manual run with no
    frozen manifest. Without a saved SHA, every inventory must hold the required
    paths, including one frozen by an earlier attempt. Credentials are intentionally
    fetched AFTER freezing bytes.
    """
    attempt.stage = "eligibility"
    state = await _read_run_artifacts(owner, repository, run_id, mode)
    manifest = state.manifest
    captured: tuple[CapturedArtifact, ...] | None = None
    if manifest is None:
        attempt.stage = "capture"
        async with repository_capture_guard(
            connection, owner, repository, run_id, original=True
        ):
            root = await _checkout_root(owner, repository, state.codebase_names)
            captured = await _blocking_call(
                partial(capture_managed_artifacts, root, state.codebase_names)
            )
            manifest = manifest_from_capture(captured)
            validate_required_artifacts(manifest, required_paths)
            attempt.stage = "manifest"
            await _persist_manifest(owner, repository, run_id, manifest)
    elif state.commit_sha is None:
        attempt.stage = "manifest"
        validate_required_artifacts(manifest, required_paths)
    if state.commit_sha is not None or not manifest.root:
        if state.commit_sha is not None:
            # A retry after an earlier local sync failure lands here.
            attempt.stage = "local_sync"
            await _sync_local_commit(
                owner, repository, run_id, state.provider_key, state.commit_sha
            )
        return _SavedIdentity(state, manifest, state.commit_sha)
    branch = publication_branch_name(run_id)
    attempt.stage = "credentials"
    api = await _github_client(owner, repository, state.provider_key)
    attempt.stage = "recovery"
    publication = await _github_call(
        partial(
            recover_artifact_commit,
            api,
            owner_name=owner,
            repo_name=repository,
            branch_name=branch,
            manifest=manifest,
        )
    )
    if publication is None:
        if captured is None:
            # Every automatic/manual pre-SHA retry uses this path only after
            # exact-manifest remote recovery failed. It revalidates frozen bytes
            # and never creates a replacement inventory.
            attempt.stage = "capture"
            async with repository_capture_guard(
                connection,
                owner,
                repository,
                run_id,
                original=mode == "automatic",
            ):
                await _reject_newer_mutator(owner, repository, run_id)
                root = await _checkout_root(owner, repository, state.codebase_names)
                captured = await _blocking_call(
                    partial(revalidate_manifest, root, manifest)
                )
        attempt.stage = "commit"
        publication = await _github_call(
            partial(
                publish_artifact_commit,
                api,
                owner_name=owner,
                repo_name=repository,
                branch_name=branch,
                captured=captured,
                manifest=manifest,
                repository_workflow_run_id=run_id,
            )
        )
    # Durable boundary: commit/ref success (or a verified unchanged base) is
    # committed to PostgreSQL BEFORE any PR work is attempted.
    attempt.stage = "identity"
    await _persist_sha(owner, repository, run_id, manifest, publication.commit_sha)
    # The SHA is saved first, so a failed fetch is retried without republishing.
    attempt.stage = "local_sync"
    await _sync_local_commit(
        owner, repository, run_id, state.provider_key, publication.commit_sha
    )
    return _SavedIdentity(state, manifest, publication.commit_sha)


async def _persist_no_artifacts(
    owner: str, repository: str, run_id: str, attempt: _PublicationAttempt
) -> tuple[PrMetadata, bool]:
    attempt.stage = "pr_metadata"
    return await _persist_pr_metadata(
        owner,
        repository,
        run_id,
        PrMetadata(
            status="no_artifacts",
            message="No managed artifact files were captured for this run",
        ),
        None,
    )


async def _reconcile_saved_identity(
    owner: str,
    repository: str,
    run_id: str,
    state: _RunArtifacts,
    manifest: ArtifactManifest,
    commit_sha: str,
    attempt: _PublicationAttempt,
    timeout_seconds: float | None = None,
) -> tuple[PrMetadata, bool]:
    """Reconcile a PR from the saved commit, without reading or capturing files.

    An unchanged inventory saved at the default-branch commit is not ahead of that
    branch, so reconcile_artifact_pr reports no_changes and opens no PR.
    """
    attempt.stage = "credentials"
    api = await _github_client(owner, repository, state.provider_key)
    attempt.stage = "pr_create"
    # On expiry _blocking_call still waits for its thread, keeping the lock held.
    async with asyncio.timeout(timeout_seconds):
        metadata = await _github_call(
            partial(
                reconcile_artifact_pr,
                api,
                owner_name=owner,
                repo_name=repository,
                branch_name=publication_branch_name(run_id),
                commit_sha=commit_sha,
                manifest=manifest,
                repository_workflow_run_id=run_id,
                expected_pr_number=state.pr_metadata.pr_number
                if state.pr_metadata is not None
                else None,
            )
        )
    attempt.stage = "pr_metadata"
    return await _persist_pr_metadata(owner, repository, run_id, metadata, commit_sha)


async def publish_agent_md_pr(
    *,
    owner_name: str,
    repo_name: str,
    repository_workflow_run_id: str,
) -> tuple[PrMetadata, bool]:
    """Manual publication: completed generation/update runs and frozen identity only.

    Runs both phases under one lock and raises typed errors from either, because
    the API caller reports PR failures rather than treating them as optional.
    """
    attempt = _PublicationAttempt()
    async with _publication_attempt(
        owner_name, repo_name, repository_workflow_run_id, attempt
    ) as connection:
        identity = await _ensure_saved_identity(
            connection,
            owner_name,
            repo_name,
            repository_workflow_run_id,
            "manual",
            attempt,
        )
        if identity.commit_sha is None:
            return await _persist_no_artifacts(
                owner_name, repo_name, repository_workflow_run_id, attempt
            )
        return await _reconcile_saved_identity(
            owner_name,
            repo_name,
            repository_workflow_run_id,
            identity.state,
            identity.manifest,
            identity.commit_sha,
            attempt,
        )


async def save_artifact_identity_after_generation(
    *,
    owner_name: str,
    repo_name: str,
    repository_workflow_run_id: str,
    required_artifact_paths: Sequence[str],
) -> ArtifactIdentityResult:
    """Trusted INTERNAL required phase, run after successful stages of the parent.

    Never bind this to a client parameter. Temporal supplies the exact owning run
    ID from its activity context, while the parent still owns admission.

    Raises:
        AgentMdPrError: The identity was not saved. Generation must not succeed.
    """
    attempt = _PublicationAttempt()
    async with _publication_attempt(
        owner_name, repo_name, repository_workflow_run_id, attempt
    ) as connection:
        identity = await _ensure_saved_identity(
            connection,
            owner_name,
            repo_name,
            repository_workflow_run_id,
            "automatic",
            attempt,
            required_artifact_paths,
        )
        if identity.commit_sha is None:
            await _persist_no_artifacts(
                owner_name, repo_name, repository_workflow_run_id, attempt
            )
            return ArtifactIdentityResult(status="no_artifacts")
        return ArtifactIdentityResult(status="saved", commit_sha=identity.commit_sha)


async def reconcile_agent_md_pr_after_generation(
    *,
    owner_name: str,
    repo_name: str,
    repository_workflow_run_id: str,
) -> tuple[PrMetadata, bool]:
    """Trusted INTERNAL best-effort phase. It requires an already saved identity.

    A failure records a static safe error on the snapshot, retains the saved SHA and
    manifest, and raises so the activity can apply its retry policy. The workflow
    treats exhausted retries as optional.
    """
    attempt = _PublicationAttempt()
    async with _publication_attempt(
        owner_name, repo_name, repository_workflow_run_id, attempt
    ):
        attempt.stage = "eligibility"
        state = await _read_run_artifacts(
            owner_name, repo_name, repository_workflow_run_id, "automatic"
        )
        if state.commit_sha is None or state.manifest is None:
            raise AgentMdPrConflictError(
                "Pull request reconciliation requires a saved artifact identity"
            )
        return await _reconcile_saved_identity(
            owner_name,
            repo_name,
            repository_workflow_run_id,
            state,
            state.manifest,
            state.commit_sha,
            attempt,
            _AUTOMATIC_PR_RECONCILE_SECONDS,
        )
