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


class RepositoryIngestionPayload(BaseModel):
    """Payload sent to Flow Bridge's ingestion endpoint."""

    repository_git_url: str = Field(description="Repository git remote URL")
    repository_metadata: None = None


class RepositoryIngestionResult(BaseModel):
    """Response returned by Flow Bridge after starting ingestion."""

    model_config = ConfigDict(frozen=True)

    workflow_id: str
    run_id: str


def validate_repository_git_url(repository_git_url: str) -> str:
    """Validate and normalize a repository git remote URL for CLI input."""
    normalized = repository_git_url.strip()
    if not normalized:
        raise AppRuntimeError("Repository git URL is required.")

    if normalized.startswith("git@"):
        if ":" not in normalized or not normalized.endswith(".git"):
            raise AppRuntimeError(
                "Repository git URL must be an HTTPS or SSH git remote URL."
            )
        return normalized

    parsed = urlsplit(normalized)
    if parsed.scheme != "https" or not parsed.netloc or not parsed.path.endswith(".git"):
        raise AppRuntimeError(
            "Repository git URL must be an HTTPS or SSH git remote URL ending with .git."
        )
    return normalized


def start_repository_ingestion(
    settings: CliSettings,
    *,
    repository_git_url: str,
) -> RepositoryIngestionResult:
    """Start repository ingestion through the local Flow Bridge API."""
    payload = RepositoryIngestionPayload(
        repository_git_url=validate_repository_git_url(repository_git_url),
        repository_metadata=None,
    )

    response: httpx2.Response | None = None
    last_error: httpx2.HTTPError | None = None
    for base_url in flow_bridge_probe_base_urls(settings):
        try:
            response = httpx2.post(
                f"{base_url}/start-ingestion",
                json=payload.model_dump(),
                timeout=settings.request_timeout_seconds,
            )
            break
        except httpx2.HTTPError as exc:
            last_error = exc
            continue

    if response is None:
        raise AppRuntimeError(f"Unable to reach Flow Bridge: {last_error}")

    if response.status_code == 409:
        detail = _extract_error_detail(response)
        raise AppRuntimeError(detail or "Repository already exists.")
    if response.status_code == 400:
        detail = _extract_error_detail(response)
        raise AppRuntimeError(detail or "Invalid repository ingestion request.")

    try:
        response.raise_for_status()
    except httpx2.HTTPError as exc:
        detail = _extract_error_detail(response)
        message = detail or f"Unable to start repository ingestion: {exc}"
        raise AppRuntimeError(message) from exc

    try:
        return RepositoryIngestionResult.model_validate_json(response.text)
    except ValidationError as exc:
        raise AppRuntimeError(
            "Flow Bridge returned an unexpected ingestion response payload."
        ) from exc


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
