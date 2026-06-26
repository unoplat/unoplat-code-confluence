from __future__ import annotations

from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict

from unoplat_code_confluence_cli.errors import RepositoryUrlError


class RepositoryGitUrl(BaseModel):
    """Repository identity parsed from a git remote URL."""

    model_config = ConfigDict(frozen=True)

    repository_owner_name: str
    repository_name: str
    repository_git_url: str
    host: str
    provider_key: str

    @classmethod
    def parse(cls, raw_url: str) -> "RepositoryGitUrl":
        raw_url = raw_url.strip()
        if not raw_url:
            raise RepositoryUrlError("Repository git URL is required.")

        if raw_url.startswith("git@"):
            try:
                host_and_path = raw_url.removeprefix("git@")
                host, path = host_and_path.split(":", 1)
            except ValueError as exc:
                raise RepositoryUrlError(
                    "Repository git URL must be a valid HTTPS or SSH GitHub remote URL."
                ) from exc
        else:
            parsed = urlsplit(raw_url)
            if parsed.scheme != "https" or not parsed.netloc:
                raise RepositoryUrlError(
                    "Repository git URL must be a valid HTTPS or SSH GitHub remote URL."
                )
            try:
                port = parsed.port
            except ValueError as exc:
                raise RepositoryUrlError(
                    "Repository git URL must be a valid HTTPS or SSH GitHub remote URL."
                ) from exc
            hostname = parsed.hostname or ""
            host = f"{hostname}:{port}" if port is not None else hostname
            path = parsed.path

        normalized_host = host.lower().strip()
        path_parts = [part for part in path.strip("/").split("/") if part]
        if len(path_parts) != 2 or not normalized_host:
            raise RepositoryUrlError(
                "Repository git URL must include owner and repository name."
            )

        owner = path_parts[0].strip()
        repo_segment = path_parts[1].strip()
        repo = repo_segment.removesuffix(".git").strip()
        if not owner or not repo:
            raise RepositoryUrlError(
                "Repository git URL must include owner and repository name."
            )

        return cls(
            repository_owner_name=owner,
            repository_name=repo,
            repository_git_url=f"https://{normalized_host}/{owner}/{repo}.git",
            host=normalized_host,
            provider_key=provider_key_for_host(normalized_host),
        )


def normalize_repository_git_url(raw_url: str) -> str:
    """Validate and normalize a repository URL to Flow Bridge's HTTPS clone URL."""
    return RepositoryGitUrl.parse(raw_url).repository_git_url


def provider_key_for_host(host: str) -> str:
    normalized_host = host.lower().strip()
    return "github_open" if normalized_host == "github.com" else "github_enterprise"
