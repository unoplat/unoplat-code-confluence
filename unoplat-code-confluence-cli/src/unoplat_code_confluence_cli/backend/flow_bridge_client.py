from __future__ import annotations

from pydantic import BaseModel, Field, ValidationError

from unoplat_code_confluence_cli.config import CliSettings
from unoplat_code_confluence_cli.domain.repository import normalize_repository_git_url
from unoplat_code_confluence_cli.domain.results import (
    RepositoryAddResult,
    RepositoryProviderCheck,
    RepositoryRefreshResult,
)
from unoplat_code_confluence_cli.errors import NetworkError, SetupRequiredError
from unoplat_code_confluence_cli.ports.http_client import HttpClient


class RepositoryAddPayload(BaseModel):
    """Payload sent to Flow Bridge's lightweight add repository endpoint."""

    repository_git_url: str = Field(description="Repository git remote URL")
    provider_key: str | None = None


class RepositoryRefreshPayload(BaseModel):
    """Payload sent to Flow Bridge's refresh endpoint."""

    repository_name: str
    repository_owner_name: str
    provider_key: str
    repository_git_url: str | None = None


class FlowBridgeClient:
    """Concrete client for the Flow Bridge backend API used by the CLI."""

    def __init__(self, settings: CliSettings, http: HttpClient) -> None:
        self._settings = settings
        self._http = http

    def is_reachable(self) -> bool:
        """Return whether Flow Bridge is serving its API.

        Newer Flow Bridge builds expose `/health`. Older pinned releases do not,
        so fall back to the lightweight Flow Bridge-specific
        `/repository-providers` endpoint to avoid restarting an already-running
        stack during status checks.
        """
        return self._probe_service(
            primary_path="/health",
            fallback_path="/repository-providers",
            action="check Flow Bridge reachability",
        )

    def is_ready(self) -> bool:
        """Return whether Flow Bridge is ready enough for CLI API calls."""
        return self._probe_service(
            primary_path="/health",
            fallback_path="/repository-providers",
            action="check Flow Bridge readiness",
        )

    def _probe_service(
        self,
        *,
        primary_path: str,
        fallback_path: str,
        action: str,
    ) -> bool:
        try:
            response = self._http.get(
                base_url=self._settings.flow_bridge_base_url,
                path=primary_path,
                timeout=self._settings.request_timeout_seconds,
                action=action,
                allow_statuses=set(range(100, 600)),
            )
        except NetworkError:
            return False

        if response.status_code == 200:
            return True
        if response.status_code != 404:
            return False

        try:
            fallback_response = self._http.get(
                base_url=self._settings.flow_bridge_base_url,
                path=fallback_path,
                timeout=self._settings.request_timeout_seconds,
                action=action,
                allow_statuses=set(range(100, 600)),
            )
        except NetworkError:
            return False
        return fallback_response.status_code == 200

    def add_repository(
        self,
        *,
        repository_git_url: str,
        provider_key: str | None,
    ) -> RepositoryAddResult:
        """Add a repository through Flow Bridge's lightweight repository endpoint."""
        payload = RepositoryAddPayload(
            repository_git_url=normalize_repository_git_url(repository_git_url),
            provider_key=provider_key,
        )
        response = self._http.post(
            base_url=self._settings.flow_bridge_base_url,
            path="/repositories",
            json=payload.model_dump(exclude_none=True),
            timeout=self._settings.request_timeout_seconds,
            action="add repository",
            detail_statuses={400, 404, 409, 422, 503},
        )
        try:
            return RepositoryAddResult.model_validate_json(response.text)
        except ValidationError as exc:
            raise NetworkError(
                "Flow Bridge returned an unexpected add repository response payload."
            ) from exc

    def refresh_repository(
        self,
        *,
        repository_name: str,
        repository_owner_name: str,
        provider_key: str,
        repository_git_url: str | None,
    ) -> RepositoryRefreshResult:
        """Start repository refresh and downstream AGENTS.md generation."""
        payload = RepositoryRefreshPayload(
            repository_name=repository_name,
            repository_owner_name=repository_owner_name,
            provider_key=provider_key,
            repository_git_url=repository_git_url,
        )
        response = self._http.post(
            base_url=self._settings.flow_bridge_base_url,
            path="/refresh-repository",
            json=payload.model_dump(exclude_none=True),
            timeout=self._settings.request_timeout_seconds,
            action="start repository refresh and AGENTS.md generation",
            detail_statuses={400, 404, 409, 422, 503},
        )
        try:
            return RepositoryRefreshResult.model_validate_json(response.text)
        except ValidationError as exc:
            raise NetworkError(
                "Flow Bridge returned an unexpected refresh repository response payload."
            ) from exc

    def check_repository_provider_token(
        self,
        *,
        provider_key: str,
        raise_on_missing: bool = True,
    ) -> RepositoryProviderCheck:
        """Verify repository-provider credentials for the requested provider key."""
        response = self._http.get(
            base_url=self._settings.flow_bridge_base_url,
            path="/user-details",
            params={"provider_key": provider_key},
            timeout=self._settings.request_timeout_seconds,
            action="verify repository-provider token",
            allow_statuses={404},
        )
        if 200 <= response.status_code < 300:
            return RepositoryProviderCheck(provider_key=provider_key, configured=True)

        detail = self._http.extract_error_detail(response)
        if response.status_code == 404:
            if raise_on_missing:
                raise SetupRequiredError(
                    detail
                    or (
                        "Repository-provider token is not configured. Run "
                        "`ucc setup token-repo-provider` and complete the browser flow."
                    )
                )
            return RepositoryProviderCheck(provider_key=provider_key, configured=False)

        raise NetworkError(
            detail
            or (
                "Unable to verify repository-provider token: "
                f"HTTP status {response.status_code}"
            )
        )
