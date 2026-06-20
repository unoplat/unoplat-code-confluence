from __future__ import annotations

from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict

from unoplat_code_confluence_cli.app_runtime import AppRuntimeError
from unoplat_code_confluence_cli.config import CliSettings
from unoplat_code_confluence_cli.ingestion_runtime import (
    RepositoryRefreshResult,
    add_repository,
    refresh_repository,
)


class RepositoryGitUrlParts(BaseModel):
    """Repository identity parsed from a git remote URL."""

    model_config = ConfigDict(frozen=True)

    repository_owner_name: str
    repository_name: str
    repository_git_url: str
    host: str
    provider_key: str


def parse_repository_git_url(repository_git_url: str) -> RepositoryGitUrlParts:
    """Parse HTTPS or SSH GitHub remote URL into repository identity.

    This mirrors Flow Bridge's accepted CLI input shape:
    - https://github.com/owner/repo
    - https://github.com/owner/repo.git
    - git@github.com:owner/repo
    - git@github.com:owner/repo.git

    Provider handling is host-based for the repository providers currently
    implemented by Flow Bridge: github.com maps to github_open, and any other
    GitHub-compatible host maps to github_enterprise.
    """
    raw_url = repository_git_url.strip()
    if not raw_url:
        raise AppRuntimeError("Repository git URL is required.")

    if raw_url.startswith("git@"):
        try:
            host_and_path = raw_url.removeprefix("git@")
            host, path = host_and_path.split(":", 1)
        except ValueError as exc:
            raise AppRuntimeError(
                "Repository git URL must be a valid HTTPS or SSH GitHub remote URL."
            ) from exc
    else:
        parsed = urlsplit(raw_url)
        if parsed.scheme != "https" or not parsed.netloc:
            raise AppRuntimeError(
                "Repository git URL must be a valid HTTPS or SSH GitHub remote URL."
            )
        try:
            port = parsed.port
        except ValueError as exc:
            raise AppRuntimeError(
                "Repository git URL must be a valid HTTPS or SSH GitHub remote URL."
            ) from exc
        hostname = parsed.hostname or ""
        host = f"{hostname}:{port}" if port is not None else hostname
        path = parsed.path

    normalized_host = host.lower().strip()
    path_parts = [part for part in path.strip("/").split("/") if part]
    if len(path_parts) != 2 or not normalized_host:
        raise AppRuntimeError(
            "Repository git URL must include owner and repository name."
        )

    owner = path_parts[0].strip()
    repo_segment = path_parts[1].strip()
    repo = repo_segment.removesuffix(".git").strip()
    if not owner or not repo:
        raise AppRuntimeError(
            "Repository git URL must include owner and repository name."
        )

    return RepositoryGitUrlParts(
        repository_owner_name=owner,
        repository_name=repo,
        repository_git_url=f"https://{normalized_host}/{owner}/{repo}.git",
        host=normalized_host,
        provider_key="github_open" if normalized_host == "github.com" else "github_enterprise",
    )


def start_agent_md_generate_update(
    settings: CliSettings,
    *,
    repository_git_url: str,
) -> RepositoryRefreshResult:
    """Refresh latest code through Flow Bridge, then trigger AGENTS.md generation.

    The lightweight add call is idempotent, so ``ucc agent-md`` works both for
    repositories that were already added and for a repository URL passed directly.
    """
    parsed = parse_repository_git_url(repository_git_url)
    add_result = add_repository(
        settings,
        repository_git_url=parsed.repository_git_url,
        provider_key=parsed.provider_key,
    )
    return refresh_repository(
        settings,
        repository_name=add_result.repository_name,
        repository_owner_name=add_result.repository_owner_name,
        provider_key=add_result.provider_key,
        repository_git_url=add_result.repository_git_url,
    )
