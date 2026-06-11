from __future__ import annotations

from typing import Any, Literal
from urllib.parse import urlsplit

import httpx2
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from unoplat_code_confluence_cli.app_runtime import AppRuntimeError
from unoplat_code_confluence_cli.config import CliSettings


class RepositoryGitUrlParts(BaseModel):
    """Repository identity parsed from a git remote URL."""

    model_config = ConfigDict(frozen=True)

    repository_owner_name: str
    repository_name: str
    repository_git_url: str
    host: str


class AgentMdGenerateUpdateResult(BaseModel):
    """Response returned by Query Engine after starting an AGENTS.md run."""

    model_config = ConfigDict(frozen=True)

    repository_workflow_run_id: str
    trace_id: str


class AgentMdSnapshotResult(BaseModel):
    """Subset of latest AGENTS.md snapshot response needed by the CLI."""

    model_config = ConfigDict(frozen=True)

    repository_workflow_run_id: str
    agent_md_output: dict[str, Any] = Field(default_factory=dict)


class AgentMdPrResult(BaseModel):
    """Response returned after publishing AGENTS.md artifacts to a PR."""

    model_config = ConfigDict(frozen=True)

    status: Literal["modified", "no_changes"]
    pr_url: str | None = None
    pr_number: int | None = None
    branch_name: str | None = None
    changed_files: list[str] = Field(default_factory=list)
    message: str


class AgentMdLatestPrResult(AgentMdPrResult):
    """PR response annotated with the latest completed AGENTS.md run ID."""

    repository_workflow_run_id: str


def parse_repository_git_url(repository_git_url: str) -> RepositoryGitUrlParts:
    """Parse HTTPS or SSH GitHub remote URL into repository identity.

    This mirrors Flow Bridge's accepted CLI input shape:
    - https://github.com/owner/repo.git
    - git@github.com:owner/repo.git
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
        host = parsed.hostname or ""
        path = parsed.path

    normalized_host = host.lower().strip()
    path_parts = [part for part in path.strip("/").split("/") if part]
    if len(path_parts) != 2 or not normalized_host:
        raise AppRuntimeError(
            "Repository git URL must include owner and repository name."
        )

    owner = path_parts[0].strip()
    repo_segment = path_parts[1].strip()
    if not repo_segment.endswith(".git"):
        raise AppRuntimeError("Repository git URL must end with .git.")

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
    )


def start_agent_md_generate_update(
    settings: CliSettings,
    *,
    repository_git_url: str,
) -> AgentMdGenerateUpdateResult:
    """Start an AGENTS.md generate/update workflow through Query Engine."""
    parsed = parse_repository_git_url(repository_git_url)
    response = _query_engine_get(
        settings,
        "/v1/codebase-agent-rules",
        params={
            "owner_name": parsed.repository_owner_name,
            "repo_name": parsed.repository_name,
        },
        action="start AGENTS.md generate/update",
    )

    try:
        return AgentMdGenerateUpdateResult.model_validate_json(response.text)
    except ValidationError as exc:
        raise AppRuntimeError(
            "Query Engine returned an unexpected AGENTS.md generate/update response payload."
        ) from exc


def create_agent_md_pr_for_latest(
    settings: CliSettings,
    *,
    repository_git_url: str,
) -> AgentMdLatestPrResult:
    """Create a PR for the latest completed AGENTS.md operation for a repository."""
    parsed = parse_repository_git_url(repository_git_url)
    latest_snapshot = _get_latest_agent_md_snapshot(settings, parsed)

    response = _query_engine_post(
        settings,
        "/v1/repository-agent-md-pr",
        json={
            "owner_name": parsed.repository_owner_name,
            "repo_name": parsed.repository_name,
            "repository_workflow_run_id": latest_snapshot.repository_workflow_run_id,
        },
        action="create AGENTS.md PR",
    )

    try:
        pr_result = AgentMdPrResult.model_validate_json(response.text)
    except ValidationError as exc:
        raise AppRuntimeError(
            "Query Engine returned an unexpected AGENTS.md PR response payload."
        ) from exc

    return AgentMdLatestPrResult(
        repository_workflow_run_id=latest_snapshot.repository_workflow_run_id,
        **pr_result.model_dump(),
    )


def _get_latest_agent_md_snapshot(
    settings: CliSettings,
    parsed: RepositoryGitUrlParts,
) -> AgentMdSnapshotResult:
    response = _query_engine_get(
        settings,
        "/v1/repository-agent-snapshot",
        params={
            "owner_name": parsed.repository_owner_name,
            "repo_name": parsed.repository_name,
        },
        action="retrieve latest completed AGENTS.md run",
    )

    try:
        return AgentMdSnapshotResult.model_validate_json(response.text)
    except ValidationError as exc:
        raise AppRuntimeError(
            "Query Engine returned an unexpected latest AGENTS.md snapshot response payload."
        ) from exc


def _query_engine_get(
    settings: CliSettings,
    path: str,
    *,
    params: dict[str, str],
    action: str,
) -> httpx2.Response:
    try:
        response = httpx2.get(
            f"{settings.query_engine_base_url}{path}",
            params=params,
            timeout=settings.request_timeout_seconds,
        )
    except httpx2.HTTPError as exc:
        raise AppRuntimeError(f"Unable to reach Query Engine to {action}: {exc}") from exc

    _raise_for_query_engine_status(response, action=action)
    return response


def _query_engine_post(
    settings: CliSettings,
    path: str,
    *,
    json: dict[str, str],
    action: str,
) -> httpx2.Response:
    try:
        response = httpx2.post(
            f"{settings.query_engine_base_url}{path}",
            json=json,
            timeout=settings.request_timeout_seconds,
        )
    except httpx2.HTTPError as exc:
        raise AppRuntimeError(f"Unable to reach Query Engine to {action}: {exc}") from exc

    _raise_for_query_engine_status(response, action=action)
    return response


def _raise_for_query_engine_status(response: httpx2.Response, *, action: str) -> None:
    if 200 <= response.status_code < 300:
        return

    detail = _extract_error_detail(response)
    if response.status_code == 404 and detail:
        raise AppRuntimeError(detail)
    if response.status_code in {400, 409, 422, 503} and detail:
        raise AppRuntimeError(detail)

    try:
        response.raise_for_status()
    except httpx2.HTTPError as exc:
        message = detail or f"Unable to {action}: {exc}"
        raise AppRuntimeError(message) from exc


def _extract_error_detail(response: httpx2.Response) -> str | None:
    try:
        payload: Any = response.json()
    except ValueError:
        return None

    if not isinstance(payload, dict):
        return None

    detail = payload.get("detail")
    if isinstance(detail, str):
        return detail
    if isinstance(detail, list):
        return "; ".join(str(item) for item in detail)
    if isinstance(detail, dict):
        return str(detail)
    return None
