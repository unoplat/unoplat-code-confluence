from __future__ import annotations

from urllib.parse import urlsplit

from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict
from unoplat_code_confluence_commons.credential_enums import ProviderKey


class RepositoryGitUrlParts(BaseModel):
    """Repository identity parsed from a supported GitHub git remote URL."""

    model_config = ConfigDict(frozen=True)

    repository_owner_name: str
    repository_name: str
    repository_git_url: str
    provider_key: ProviderKey
    host: str


def parse_repository_git_url(repository_git_url: str) -> RepositoryGitUrlParts:
    """Parse HTTPS or SSH GitHub remote URL into repository identity."""
    raw_url = repository_git_url.strip()
    if not raw_url:
        raise HTTPException(status_code=400, detail="Repository git URL is required")

    if raw_url.startswith("git@"):
        try:
            host_and_path = raw_url.removeprefix("git@")
            host, path = host_and_path.split(":", 1)
        except ValueError as exc:
            raise HTTPException(
                status_code=400,
                detail="Repository git URL must be a valid HTTPS or SSH GitHub remote URL",
            ) from exc
    else:
        parsed = urlsplit(raw_url)
        if parsed.scheme != "https" or not parsed.netloc:
            raise HTTPException(
                status_code=400,
                detail="Repository git URL must be a valid HTTPS or SSH GitHub remote URL",
            )
        try:
            port = parsed.port
        except ValueError as exc:
            raise HTTPException(
                status_code=400,
                detail="Repository git URL must be a valid HTTPS or SSH GitHub remote URL",
            ) from exc
        hostname = parsed.hostname or ""
        host = f"{hostname}:{port}" if port is not None else hostname
        path = parsed.path

    normalized_host = host.lower().strip()
    path_parts = [part for part in path.strip("/").split("/") if part]
    if len(path_parts) != 2 or not normalized_host:
        raise HTTPException(
            status_code=400,
            detail="Repository git URL must include owner and repository name",
        )

    owner = path_parts[0].strip()
    repo_segment = path_parts[1].strip()
    # Provider repository lists return the browser/HTML URL (for example
    # https://github.com/owner/repo) rather than the clone URL. Accept both
    # forms here and normalize to the HTTPS clone URL used by downstream clone
    # and refresh paths.
    repo = repo_segment.removesuffix(".git").strip()
    if not owner or not repo:
        raise HTTPException(
            status_code=400,
            detail="Repository git URL must include owner and repository name",
        )

    return RepositoryGitUrlParts(
        repository_owner_name=owner,
        repository_name=repo,
        repository_git_url=f"https://{normalized_host}/{owner}/{repo}.git",
        provider_key=_provider_key_for_host(normalized_host),
        host=normalized_host,
    )


def _provider_key_for_host(host: str) -> ProviderKey:
    if host == "github.com":
        return ProviderKey.GITHUB_OPEN
    return ProviderKey.GITHUB_ENTERPRISE
