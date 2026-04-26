"""HTTP client for the Code Confluence query-engine snapshot endpoint."""

from __future__ import annotations

from typing import Any

import httpx
from pydantic import ValidationError

from unoplat_code_confluence_openmetadata.config import CodeConfluenceSourceConfig
from unoplat_code_confluence_openmetadata.models import RepositoryAgentSnapshotResponse

SNAPSHOT_ENDPOINT_PATH = "/v1/repository-agent-snapshot"


class CodeConfluenceClientError(RuntimeError):
    """Base error raised when the query-engine snapshot cannot be fetched."""


class CodeConfluenceSnapshotNotFoundError(CodeConfluenceClientError):
    """Raised when the query-engine returns 404 for the requested snapshot."""


class CodeConfluenceSnapshotValidationError(CodeConfluenceClientError):
    """Raised when the query-engine response does not match the expected shape."""


class CodeConfluenceClient:
    """Small synchronous client for query-engine repository snapshots."""

    def __init__(self, config: CodeConfluenceSourceConfig) -> None:
        self._config = config
        self._client = httpx.Client(
            base_url=config.normalized_query_engine_base_url,
            timeout=httpx.Timeout(config.timeout_seconds),
        )

    def fetch_repository_agent_snapshot(self) -> RepositoryAgentSnapshotResponse:
        """Fetch and validate the completed repository agent snapshot."""

        params = {
            "owner_name": self._config.owner_name,
            "repo_name": self._config.repo_name,
        }

        try:
            response = self._client.get(
                SNAPSHOT_ENDPOINT_PATH,
                params=params,
            )
        except httpx.TimeoutException as exc:
            raise CodeConfluenceClientError(
                "Timed out while fetching repository agent snapshot from query-engine"
            ) from exc
        except httpx.HTTPError as exc:
            raise CodeConfluenceClientError(
                "Failed to fetch repository agent snapshot from query-engine"
            ) from exc

        if response.status_code == httpx.codes.NOT_FOUND:
            raise CodeConfluenceSnapshotNotFoundError(_response_error_message(response))

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise CodeConfluenceClientError(_response_error_message(response)) from exc

        return _parse_snapshot_response(response)

    def close(self) -> None:
        """Close the underlying HTTP connection pool."""

        self._client.close()

    def __enter__(self) -> CodeConfluenceClient:
        return self

    def __exit__(self, *_exc_info: object) -> None:
        self.close()


def _parse_snapshot_response(response: httpx.Response) -> RepositoryAgentSnapshotResponse:
    try:
        payload: Any = response.json()
    except ValueError as exc:
        raise CodeConfluenceSnapshotValidationError(
            "Query-engine snapshot response is not valid JSON"
        ) from exc

    try:
        return RepositoryAgentSnapshotResponse.model_validate(payload)
    except ValidationError as exc:
        raise CodeConfluenceSnapshotValidationError(
            f"Query-engine snapshot response does not match expected shape: {exc}"
        ) from exc


def _response_error_message(response: httpx.Response) -> str:
    try:
        payload: Any = response.json()
    except ValueError:
        payload = None

    detail = payload.get("detail") if isinstance(payload, dict) else None
    if isinstance(detail, str) and detail:
        return detail

    return (
        "Query-engine snapshot request failed with "
        f"HTTP {response.status_code}: {response.text}"
    )
