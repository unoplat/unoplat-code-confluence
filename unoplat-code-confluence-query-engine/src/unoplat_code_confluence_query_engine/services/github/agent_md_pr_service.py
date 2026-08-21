"""Reusable service for publishing managed repository artifacts as a pull request.

Shared by the manual API endpoint (``POST /v1/repository-agent-md-pr``) and the
automatic publish activity at the end of ``RepositoryAgentWorkflow``. Raises
typed ``AgentMdPrError`` subclasses only — callers map them to their transport
errors (``HTTPException`` for FastAPI, ``ApplicationError`` for Temporal).
Database persistence errors propagate as-is.
"""

from __future__ import annotations

import asyncio
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import cast

from fastapi import HTTPException
from ghapi.core import GhApi
from git import INDEX, Repo
from git.diff import Diff
from git.exc import GitError
from loguru import logger
from sqlalchemy import select
from unoplat_code_confluence_commons.pr_metadata_model import PrMetadata
from unoplat_code_confluence_commons.repo_models import (
    Repository,
    RepositoryAgentMdSnapshot,
)

from unoplat_code_confluence_query_engine.db.postgres.db import get_startup_session
from unoplat_code_confluence_query_engine.services.config.credentials_service import (
    CredentialsService,
)
from unoplat_code_confluence_query_engine.services.github.agent_md_pr_publisher import (
    ArtifactChange,
    publish_agent_md_artifacts,
)
from unoplat_code_confluence_query_engine.services.github.github_api_helpers import (
    extract_http_error_status,
    resolve_github_host,
)
from unoplat_code_confluence_query_engine.services.repository.repository_metadata_service import (
    fetch_repository_metadata,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.constants import (
    APP_INTERFACES_ARTIFACT,
    ARCHITECTURE_MANAGED_ARTIFACTS,
    BUSINESS_DOMAIN_REFERENCES_ARTIFACT,
    DEPENDENCY_OVERVIEW_ARTIFACT,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_backend_paths import (
    resolve_common_repository_root,
)


class AgentMdPrError(Exception):
    """Base error for AGENTS.md PR publication."""


class AgentMdPrNotFoundError(AgentMdPrError):
    """Repository, snapshot, or repository metadata is missing."""


class AgentMdPrConfigurationError(AgentMdPrError):
    """Repository PAT or GitHub host configuration is missing or invalid."""


class AgentMdPrAuthError(AgentMdPrError):
    """GitHub rejected the request with an auth/permission error (401/403)."""

    def __init__(self, message: str, status_code: int) -> None:
        super().__init__(message)
        self.status_code: int = status_code


class AgentMdPrInternalError(AgentMdPrError):
    """Local artifact read or repository metadata lookup failed."""


class AgentMdPrGithubError(AgentMdPrError):
    """GitHub API failed with a non-auth error (network, 5xx, bad response)."""


CODEBASE_MANAGED_MARKDOWN_ARTIFACTS: tuple[str, ...] = (
    "AGENTS.md",
    DEPENDENCY_OVERVIEW_ARTIFACT,
    BUSINESS_DOMAIN_REFERENCES_ARTIFACT,
    APP_INTERFACES_ARTIFACT,
)

REPOSITORY_MANAGED_ARTIFACTS: tuple[str, ...] = ARCHITECTURE_MANAGED_ARTIFACTS


def _get_mapping_field(
    payload: Mapping[str, object],
    key: str,
) -> Mapping[str, object] | None:
    value = payload.get(key)
    if isinstance(value, Mapping):
        return cast(Mapping[str, object], value)
    return None


def _get_codebase_file_rel_path(codebase_name: str, file_relative: str) -> str:
    """Compute repository-relative path for any file in a codebase."""
    clean = codebase_name.strip().strip("/")
    if clean in {"", "."}:
        return file_relative
    return f"{clean}/{file_relative}"


def _matching_paths_from_diffs(
    diffs: Iterable[Diff],
    expected_paths: set[str],
) -> set[str]:
    """Return expected repository paths referenced by structured Git diffs."""
    matching_paths: set[str] = set()
    for diff in diffs:
        for path in (
            diff.a_path,
            diff.b_path,
            diff.rename_from,
            diff.rename_to,
        ):
            if path is not None and path in expected_paths:
                matching_paths.add(path)
    return matching_paths


def _collect_changed_managed_artifacts(
    root: Path,
    managed_artifacts: tuple[str, ...],
) -> list[Path]:
    """Return existing managed artifacts with staged, unstaged, or untracked changes.

    Tracked changes are inspected in two path-limited batches. Untracked checks are
    then limited to candidates not already found in either diff. If repository
    inspection fails, preserve the existing behavior of publishing every existing
    managed artifact.
    """
    existing_targets = [
        artifact for artifact in managed_artifacts if (root / artifact).is_file()
    ]
    existing_paths = [root / artifact for artifact in existing_targets]
    if not existing_targets:
        return []

    try:
        with Repo(str(root), search_parent_directories=True) as repo:
            working_tree_dir = repo.working_tree_dir
            if repo.bare or working_tree_dir is None:
                raise ValueError(f"Repository at '{root}' has no working tree")

            working_tree_root = Path(working_tree_dir).resolve()
            artifact_root = root.resolve().relative_to(working_tree_root)
            repository_paths = tuple(
                (artifact_root / artifact).as_posix() for artifact in existing_targets
            )
            expected_paths = set(repository_paths)
            changed_paths: set[str] = set()
            index = repo.index

            if repo.head.is_valid():
                staged_diffs = repo.head.commit.diff(INDEX, paths=repository_paths)
                changed_paths.update(
                    _matching_paths_from_diffs(staged_diffs, expected_paths)
                )
            else:
                # In an unborn repository every stage-zero index entry is an add.
                indexed_paths = {
                    str(path)
                    for path, stage in index.entries
                    if stage == 0 and str(path) in expected_paths
                }
                changed_paths.update(indexed_paths)

            unstaged_diffs = index.diff(None, paths=repository_paths)
            changed_paths.update(
                _matching_paths_from_diffs(unstaged_diffs, expected_paths)
            )

            for repository_path in expected_paths - changed_paths:
                if repo.is_dirty(
                    path=repository_path,
                    index=False,
                    working_tree=False,
                    untracked_files=True,
                    submodules=False,
                ):
                    changed_paths.add(repository_path)
    except (GitError, OSError, ValueError) as status_error:
        logger.warning(
            "Unable to inspect git changes for managed artifacts in '{}': {}. "
            "Falling back to existing managed artifacts.",
            root,
            status_error,
        )
        return existing_paths

    return [
        local_path
        for local_path, repository_path in zip(
            existing_paths,
            repository_paths,
            strict=True,
        )
        if repository_path in changed_paths
    ]


def _collect_changed_managed_markdown_files(
    root: Path,
    managed_artifacts: tuple[str, ...],
) -> list[Path]:
    """Return existing changed codebase Markdown artifacts under ``root``."""
    return _collect_changed_managed_artifacts(root, managed_artifacts)


async def _persist_pr_metadata(
    owner_name: str,
    repo_name: str,
    repository_workflow_run_id: str,
    pr_metadata: PrMetadata,
) -> tuple[PrMetadata, bool]:
    """Persist PR metadata with row-level lock. Returns (metadata, already_existed).

    Uses SELECT ... FOR UPDATE to guard against concurrent publish requests.
    If pr_metadata is already non-null (another request won the race), returns
    the existing metadata with already_existed=True.
    """
    # Session 2 (short write transaction): acquire row lock only for the final
    # persistence step so we do not hold DB locks while performing network-bound
    # GitHub API calls.
    async with get_startup_session() as session:
        stmt = (
            select(RepositoryAgentMdSnapshot)
            .where(
                RepositoryAgentMdSnapshot.repository_owner_name == owner_name,
                RepositoryAgentMdSnapshot.repository_name == repo_name,
                RepositoryAgentMdSnapshot.repository_workflow_run_id
                == repository_workflow_run_id,
            )
            .with_for_update()
        )
        result = await session.execute(stmt)
        snapshot = result.scalar_one_or_none()
        if snapshot is None:
            # Defensive fallback: under normal workflow invariants the snapshot row
            # exists for this run and is not deleted during publish. If it is gone
            # (e.g. concurrent maintenance/deletion), treat as already handled to
            # preserve one-shot no-op behavior.
            return pr_metadata, True

        if snapshot.pr_metadata is not None:
            # Another request already persisted — return existing data
            existing = PrMetadata.model_validate(snapshot.pr_metadata)
            return existing, True

        snapshot.pr_metadata = pr_metadata.model_dump(mode="json")
        return pr_metadata, False


async def publish_agent_md_pr(
    *,
    owner_name: str,
    repo_name: str,
    repository_workflow_run_id: str,
) -> tuple[PrMetadata, bool]:
    """Publish managed artifacts as a PR for a workflow run (one-shot per run).

    One-shot semantics: the first successful publish for a run persists
    ``pr_metadata``; subsequent calls return the existing metadata with
    ``already_existed=True``. If a retry follows a publish-success /
    persist-failure, the publisher's open-PR early-exit records status
    ``no_changes`` while still capturing the PR url/number.

    Returns:
        Tuple of (pr_metadata, already_existed).

    Raises:
        AgentMdPrNotFoundError: Repository, snapshot, or repository metadata missing.
        AgentMdPrConfigurationError: PAT missing/undecryptable or invalid GitHub host.
        AgentMdPrAuthError: GitHub auth/permission error (401/403).
        AgentMdPrInternalError: Local artifact read or metadata lookup failure.
        AgentMdPrGithubError: Other GitHub API failures (network, 5xx).
    """
    # ── Session 1: read snapshot + repository + PAT credentials ──────────
    # Keep this read transaction separate from the persistence step: GitHub
    # operations below are network-bound and can take time; we avoid holding
    # DB transaction/locks across those remote calls.
    async with get_startup_session() as session:
        repository = await session.get(Repository, (repo_name, owner_name))
        if repository is None:
            raise AgentMdPrNotFoundError(
                f"Repository not found: {owner_name}/{repo_name}"
            )

        snapshot_stmt = select(RepositoryAgentMdSnapshot).where(
            RepositoryAgentMdSnapshot.repository_owner_name == owner_name,
            RepositoryAgentMdSnapshot.repository_name == repo_name,
            RepositoryAgentMdSnapshot.repository_workflow_run_id
            == repository_workflow_run_id,
        )
        snapshot_result = await session.execute(snapshot_stmt)
        snapshot = snapshot_result.scalar_one_or_none()
        if snapshot is None:
            raise AgentMdPrNotFoundError(
                f"No snapshot found for {owner_name}/{repo_name} "
                f"run_id={repository_workflow_run_id}"
            )

        # ONE-SHOT GUARD: if pr_metadata already persisted → return immediately
        if snapshot.pr_metadata is not None:
            existing = PrMetadata.model_validate(snapshot.pr_metadata)
            return existing, True

        provider_key = repository.repository_provider
        try:
            repository_pat = await CredentialsService.get_repository_pat(
                session, provider_key
            )
        except ValueError as decrypt_error:
            raise AgentMdPrConfigurationError(str(decrypt_error)) from decrypt_error
        if not repository_pat:
            raise AgentMdPrConfigurationError(
                f"Repository PAT not configured for provider '{provider_key.value}'. "
                "Please configure repository credentials first."
            )

        credential_metadata = (
            await CredentialsService.get_repository_credential_metadata(
                session,
                provider_key,
            )
        )

    # ── Collect files to publish ─────────────────────────────────────────
    codebases_payload = _get_mapping_field(snapshot.agent_md_output, "codebases")
    if not codebases_payload:
        no_codebases_meta = PrMetadata(
            status="no_changes",
            message="No codebase outputs found in snapshot",
        )
        return await _persist_pr_metadata(
            owner_name, repo_name, repository_workflow_run_id, no_codebases_meta
        )

    try:
        ruleset_metadata = await fetch_repository_metadata(owner_name, repo_name)
    except HTTPException as metadata_error:
        # fetch_repository_metadata is endpoint-oriented and raises HTTPException
        # internally; translate so this service never leaks transport errors.
        detail = str(metadata_error.detail)
        if metadata_error.status_code == 404:
            raise AgentMdPrNotFoundError(detail) from metadata_error
        raise AgentMdPrInternalError(detail) from metadata_error

    codebase_metadata = ruleset_metadata.codebase_metadata
    codebase_path_map = {
        metadata.codebase_name: metadata.codebase_path for metadata in codebase_metadata
    }
    try:
        repository_root_path = Path(resolve_common_repository_root(codebase_metadata))
    except ValueError as path_error:
        raise AgentMdPrInternalError(
            f"Failed to resolve common repository root: {path_error}"
        ) from path_error

    files_to_publish: list[ArtifactChange] = []
    seen_rel_paths: set[str] = set()

    for codebase_name in codebases_payload.keys():
        codebase_root = codebase_path_map.get(codebase_name)
        if not codebase_root:
            logger.warning(
                "Skipping codebase '{}' for PR: path not found", codebase_name
            )
            continue

        codebase_root_path = Path(codebase_root)
        changed_managed_files = await asyncio.to_thread(
            _collect_changed_managed_markdown_files,
            codebase_root_path,
            CODEBASE_MANAGED_MARKDOWN_ARTIFACTS,
        )
        if not changed_managed_files:
            logger.info(
                "Skipping codebase '{}': no managed markdown files changed",
                codebase_name,
            )
            continue

        for local_path in changed_managed_files:
            file_relative = str(local_path.relative_to(codebase_root_path))

            try:
                local_content = local_path.read_text(encoding="utf-8")
            except (OSError, UnicodeError) as read_error:
                raise AgentMdPrInternalError(
                    f"Failed to read managed artifact as UTF-8 at "
                    f"{local_path}: {read_error}"
                ) from read_error

            rel_path = _get_codebase_file_rel_path(codebase_name, file_relative)

            # Deduplicate defensively across codebase payload entries.
            if rel_path in seen_rel_paths:
                continue
            seen_rel_paths.add(rel_path)

            files_to_publish.append((rel_path, local_content))

    changed_repository_artifacts = await asyncio.to_thread(
        _collect_changed_managed_artifacts,
        repository_root_path,
        REPOSITORY_MANAGED_ARTIFACTS,
    )
    for local_path in changed_repository_artifacts:
        rel_path = str(local_path.relative_to(repository_root_path))
        if rel_path in seen_rel_paths:
            continue
        seen_rel_paths.add(rel_path)

        try:
            local_content = local_path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as read_error:
            raise AgentMdPrInternalError(
                f"Failed to read managed artifact as UTF-8 at "
                f"{local_path}: {read_error}"
            ) from read_error
        files_to_publish.append((rel_path, local_content))

    if not files_to_publish:
        no_files_meta = PrMetadata(
            status="no_changes",
            message="No managed artifact files available to publish",
        )
        return await _persist_pr_metadata(
            owner_name, repo_name, repository_workflow_run_id, no_files_meta
        )

    # ── GitHub operations ────────────────────────────────────────────────
    try:
        github_host = resolve_github_host(provider_key, credential_metadata)
    except ValueError as host_error:
        raise AgentMdPrConfigurationError(str(host_error)) from host_error

    api = GhApi(
        owner=owner_name,
        repo=repo_name,
        token=repository_pat,
        gh_host=github_host,
    )

    branch_name = f"agents-md/{repository_workflow_run_id[:12]}"

    try:
        publish_result = await asyncio.to_thread(
            publish_agent_md_artifacts,
            api,
            owner_name=owner_name,
            repo_name=repo_name,
            branch_name=branch_name,
            files_to_publish=files_to_publish,
            repository_workflow_run_id=repository_workflow_run_id,
        )
    except ValueError as github_response_error:
        raise AgentMdPrGithubError(
            f"GitHub API error while creating PR: {github_response_error}"
        ) from github_response_error
    except Exception as github_error:
        gh_status_code = extract_http_error_status(github_error)
        if gh_status_code is not None and gh_status_code in {401, 403}:
            raise AgentMdPrAuthError(
                f"GitHub permission/auth error: {github_error}",
                status_code=gh_status_code,
            ) from github_error
        raise AgentMdPrGithubError(
            f"GitHub API error while creating PR: {github_error}"
        ) from github_error

    return await _persist_pr_metadata(
        owner_name, repo_name, repository_workflow_run_id, publish_result
    )
