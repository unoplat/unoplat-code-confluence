"""Reusable service for publishing managed markdown artifacts as a pull request.

Shared by the manual API endpoint (``POST /v1/repository-agent-md-pr``) and the
automatic publish activity at the end of ``RepositoryAgentWorkflow``. Raises
typed ``AgentMdPrError`` subclasses only — callers map them to their transport
errors (``HTTPException`` for FastAPI, ``ApplicationError`` for Temporal).
Database persistence errors propagate as-is.
"""

from __future__ import annotations

import asyncio
from collections.abc import Mapping
from pathlib import Path
import subprocess
from typing import cast

from fastapi import HTTPException
from ghapi.core import GhApi
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
    ARCHITECTURE_ARTIFACT,
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

REPOSITORY_MANAGED_MARKDOWN_ARTIFACTS: tuple[str, ...] = (ARCHITECTURE_ARTIFACT,)


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


def _collect_changed_managed_markdown_files(
    root: Path,
    managed_artifacts: tuple[str, ...],
) -> list[Path]:
    """Return existing managed artifacts changed under ``root`` in the git tree.

    The workflow now has direct artifact owners instead of section-updater run
    records. Publishing therefore discovers files from the supplied scoped target
    set and lets git working-tree status decide which ones are candidates.
    """
    existing_targets = [
        artifact for artifact in managed_artifacts if (root / artifact).is_file()
    ]
    if not existing_targets:
        return []

    try:
        status_result = subprocess.run(
            [
                "git",
                "-C",
                str(root),
                "status",
                "--porcelain",
                "--",
                *existing_targets,
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError) as status_error:
        logger.warning(
            "Unable to inspect git status for managed markdown in '{}': {}. "
            "Falling back to existing managed artifacts.",
            root,
            status_error,
        )
        return [root / artifact for artifact in existing_targets]

    if status_result.returncode != 0:
        logger.warning(
            "git status failed for managed markdown in '{}': {}. "
            "Falling back to existing managed artifacts.",
            root,
            status_result.stderr.strip(),
        )
        return [root / artifact for artifact in existing_targets]

    changed_artifacts = _parse_changed_artifacts_from_porcelain(
        status_result.stdout,
        set(existing_targets),
    )
    return [
        root / artifact
        for artifact in existing_targets
        if artifact in changed_artifacts
    ]


def _parse_changed_artifacts_from_porcelain(
    porcelain_output: str,
    expected_artifacts: set[str],
) -> set[str]:
    """Parse `git status --porcelain` output for known managed artifacts.

    Git porcelain output reports paths relative to the repository root, even when
    the status command is executed with ``git -C`` from a nested discovery root.
    Managed artifacts are direct children of that root, so normalize each porcelain
    path to its filename before comparing against the expected artifact names and
    return those bare artifact names.
    """
    changed: set[str] = set()
    for raw_line in porcelain_output.splitlines():
        if len(raw_line) < 4:
            continue
        path_part = raw_line[3:].strip()
        if " -> " in path_part:
            path_part = path_part.rsplit(" -> ", 1)[1].strip()
        path_part = path_part.strip('"')
        artifact_name = Path(path_part).name
        if artifact_name in expected_artifacts:
            changed.add(artifact_name)
    return changed


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
    """Publish managed markdown artifacts as a PR for a workflow run (one-shot per run).

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

    files_to_publish: list[tuple[str, str]] = []
    seen_rel_paths: set[str] = set()

    for codebase_name in codebases_payload.keys():
        codebase_root = codebase_path_map.get(codebase_name)
        if not codebase_root:
            logger.warning(
                "Skipping codebase '{}' for PR: path not found", codebase_name
            )
            continue

        codebase_root_path = Path(codebase_root)
        changed_managed_files = _collect_changed_managed_markdown_files(
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
            except OSError as read_error:
                raise AgentMdPrInternalError(
                    f"Failed to read managed artifact at {local_path}: {read_error}"
                ) from read_error

            rel_path = _get_codebase_file_rel_path(codebase_name, file_relative)

            # Deduplicate defensively across codebase payload entries.
            if rel_path in seen_rel_paths:
                continue
            seen_rel_paths.add(rel_path)

            files_to_publish.append((rel_path, local_content))

    changed_repository_files = _collect_changed_managed_markdown_files(
        repository_root_path,
        REPOSITORY_MANAGED_MARKDOWN_ARTIFACTS,
    )
    for local_path in changed_repository_files:
        try:
            local_content = local_path.read_text(encoding="utf-8")
        except OSError as read_error:
            raise AgentMdPrInternalError(
                f"Failed to read managed artifact at {local_path}: {read_error}"
            ) from read_error

        rel_path = ARCHITECTURE_ARTIFACT
        if rel_path in seen_rel_paths:
            continue
        seen_rel_paths.add(rel_path)
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
