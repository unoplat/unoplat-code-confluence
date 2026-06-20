from __future__ import annotations

from typing import Any
from urllib.parse import urlsplit

import httpx2
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from unoplat_code_confluence_cli.app_runtime import (
    AppRuntimeError,
    flow_bridge_probe_base_urls,
)
from unoplat_code_confluence_cli.config import CliSettings


class RepositoryAddPayload(BaseModel):
    """Payload sent to Flow Bridge's lightweight add repository endpoint."""

    repository_git_url: str = Field(description="Repository git remote URL")
    provider_key: str | None = None


class RepositoryAddResult(BaseModel):
    """Response returned by Flow Bridge after adding a repository."""

    model_config = ConfigDict(frozen=True)

    repository_name: str
    repository_owner_name: str
    repository_git_url: str
    provider_key: str
    already_added: bool
    message: str


class RepositoryRefreshPayload(BaseModel):
    """Payload sent to Flow Bridge's refresh endpoint."""

    repository_name: str
    repository_owner_name: str
    provider_key: str
    repository_git_url: str | None = None


class RepositoryRefreshResult(BaseModel):
    """Response returned by Flow Bridge after starting refresh-then-agent-md."""

    model_config = ConfigDict(frozen=True)

    repository_name: str
    repository_owner_name: str
    workflow_id: str
    run_id: str


def validate_repository_git_url(repository_git_url: str) -> str:
    """Validate and normalize a repository URL for CLI input.

    Accept both clone URLs and provider browser URLs. GitHub.com and
    GitHub Enterprise hosts are preserved from the input URL; Flow Bridge derives
    the provider key from the host unless the caller supplies an explicit
    provider key.
    """
    normalized = repository_git_url.strip()
    if not normalized:
        raise AppRuntimeError("Repository git URL is required.")

    if normalized.startswith("git@"):
        try:
            host_and_path = normalized.removeprefix("git@")
            host, path = host_and_path.split(":", 1)
        except ValueError as exc:
            raise AppRuntimeError(
                "Repository git URL must be an HTTPS or SSH Git remote URL."
            ) from exc
        path_parts = [part for part in path.strip("/").split("/") if part]
        if not host.strip() or len(path_parts) != 2:
            raise AppRuntimeError(
                "Repository git URL must include owner and repository name."
            )
        owner = path_parts[0].strip()
        repo = path_parts[1].strip().removesuffix(".git").strip()
        if not owner or not repo:
            raise AppRuntimeError(
                "Repository git URL must include owner and repository name."
            )
        return f"git@{host.lower().strip()}:{owner}/{repo}.git"

    parsed = urlsplit(normalized)
    if parsed.scheme != "https" or not parsed.netloc:
        raise AppRuntimeError(
            "Repository git URL must be an HTTPS or SSH Git remote URL."
        )
    try:
        port = parsed.port
    except ValueError as exc:
        raise AppRuntimeError(
            "Repository git URL must be an HTTPS or SSH Git remote URL."
        ) from exc
    hostname = parsed.hostname or ""
    host = f"{hostname}:{port}" if port is not None else hostname
    path_parts = [part for part in parsed.path.strip("/").split("/") if part]
    if not host.strip() or len(path_parts) != 2:
        raise AppRuntimeError(
            "Repository git URL must include owner and repository name."
        )
    owner = path_parts[0].strip()
    repo = path_parts[1].strip().removesuffix(".git").strip()
    if not owner or not repo:
        raise AppRuntimeError(
            "Repository git URL must include owner and repository name."
        )
    return f"https://{host.lower().strip()}/{owner}/{repo}.git"


def add_repository(
    settings: CliSettings,
    *,
    repository_git_url: str,
    provider_key: str | None = None,
) -> RepositoryAddResult:
    """Add a repository through the local Flow Bridge API without ingestion."""
    payload = RepositoryAddPayload(
        repository_git_url=validate_repository_git_url(repository_git_url),
        provider_key=provider_key,
    )

    response = _flow_bridge_post(
        settings,
        path="/repositories",
        payload=payload.model_dump(exclude_none=True),
        action="add repository",
    )

    try:
        return RepositoryAddResult.model_validate_json(response.text)
    except ValidationError as exc:
        raise AppRuntimeError(
            "Flow Bridge returned an unexpected add repository response payload."
        ) from exc


def refresh_repository(
    settings: CliSettings,
    *,
    repository_name: str,
    repository_owner_name: str,
    provider_key: str,
    repository_git_url: str | None = None,
) -> RepositoryRefreshResult:
    """Start Flow Bridge refresh, which triggers AGENTS.md generation after refresh."""
    payload = RepositoryRefreshPayload(
        repository_name=repository_name,
        repository_owner_name=repository_owner_name,
        provider_key=provider_key,
        repository_git_url=repository_git_url,
    )

    response = _flow_bridge_post(
        settings,
        path="/refresh-repository",
        payload=payload.model_dump(exclude_none=True),
        action="start repository refresh and AGENTS.md generation",
    )

    try:
        return RepositoryRefreshResult.model_validate_json(response.text)
    except ValidationError as exc:
        raise AppRuntimeError(
            "Flow Bridge returned an unexpected refresh repository response payload."
        ) from exc


def _flow_bridge_post(
    settings: CliSettings,
    *,
    path: str,
    payload: dict[str, Any],
    action: str,
) -> httpx2.Response:
    response: httpx2.Response | None = None
    last_error: httpx2.HTTPError | None = None
    for base_url in flow_bridge_probe_base_urls(settings):
        try:
            response = httpx2.post(
                f"{base_url}{path}",
                json=payload,
                timeout=settings.request_timeout_seconds,
            )
            break
        except httpx2.HTTPError as exc:
            last_error = exc
            continue

    if response is None:
        raise AppRuntimeError(f"Unable to reach Flow Bridge: {last_error}")

    if response.status_code in {400, 404, 409, 422, 503}:
        detail = _extract_error_detail(response)
        raise AppRuntimeError(detail or f"Unable to {action}.")

    try:
        response.raise_for_status()
    except httpx2.HTTPError as exc:
        detail = _extract_error_detail(response)
        message = detail or f"Unable to {action}: {exc}"
        raise AppRuntimeError(message) from exc

    return response


def _extract_error_detail(response: httpx2.Response) -> str | None:
    try:
        payload: Any = response.json()
    except ValueError:
        return None
    if isinstance(payload, dict):
        detail = payload.get("detail")
        if isinstance(detail, str):
            return detail
    return None
