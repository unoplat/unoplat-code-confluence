"""Temporal activity for resolving repository git ref metadata."""

from __future__ import annotations

from ghapi.core import GhApi
from loguru import logger
from sqlalchemy import select
from temporalio import activity
from unoplat_code_confluence_commons.repo_models import Repository

from unoplat_code_confluence_query_engine.db.postgres.db import get_startup_session
from unoplat_code_confluence_query_engine.models.output.git_ref_info import GitRefInfo
from unoplat_code_confluence_query_engine.services.config.credentials_service import (
    CredentialsService,
)
from unoplat_code_confluence_query_engine.services.github.git_ref_resolver import (
    resolve_repository_git_ref,
)
from unoplat_code_confluence_query_engine.services.github.github_api_helpers import (
    resolve_github_host,
)


class GitRefResolutionActivity:
    """Activity that resolves default branch and head commit SHA via GitHub API."""

    @activity.defn(name="resolve-repository-git-ref")
    async def resolve_git_ref(
        self,
        owner_name: str,
        repo_name: str,
    ) -> GitRefInfo | None:
        """Resolve default branch and head commit SHA for freshness metadata.

        Returns None if PAT is not configured — the workflow skips freshness
        metadata gracefully in that case.

        Args:
            owner_name: Repository owner.
            repo_name: Repository name.

        Returns:
            GitRefInfo with default_branch and head_commit_sha, or None.
        """
        async with get_startup_session() as session:
            repository = (
                await session.execute(
                    select(Repository).where(
                        Repository.repository_name == repo_name,
                        Repository.repository_owner_name == owner_name,
                    )
                )
            ).scalar_one_or_none()

            if repository is None:
                logger.warning(
                    "[git_ref_resolution] Repository not found: {}/{}",
                    owner_name,
                    repo_name,
                )
                return None

            provider_key = repository.repository_provider

            try:
                repository_pat = await CredentialsService.get_repository_pat(
                    session, provider_key
                )
            except ValueError:
                logger.warning(
                    "[git_ref_resolution] PAT decrypt failed for {}/{}; skipping freshness metadata",
                    owner_name,
                    repo_name,
                )
                return None

            if not repository_pat:
                logger.info(
                    "[git_ref_resolution] PAT not configured for {}/{}; skipping freshness metadata",
                    owner_name,
                    repo_name,
                )
                return None

            credential_metadata = (
                await CredentialsService.get_repository_credential_metadata(
                    session,
                    provider_key,
                )
            )

        try:
            github_host = resolve_github_host(provider_key, credential_metadata)
        except ValueError as host_error:
            logger.warning(
                "[git_ref_resolution] GitHub host resolution failed: {}",
                host_error,
            )
            return None

        api = GhApi(
            owner=owner_name,
            repo=repo_name,
            token=repository_pat,
            gh_host=github_host,
        )

        git_ref_info = resolve_repository_git_ref(api, owner_name, repo_name)
        logger.info(
            "[git_ref_resolution] Resolved git ref for {}/{}: branch={}, sha={}",
            owner_name,
            repo_name,
            git_ref_info.default_branch,
            git_ref_info.head_commit_sha,
        )
        return git_ref_info
