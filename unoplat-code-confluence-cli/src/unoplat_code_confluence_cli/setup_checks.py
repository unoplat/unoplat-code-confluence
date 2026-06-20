from __future__ import annotations

from typing import Any

import httpx2
from pydantic import BaseModel, ConfigDict, ValidationError

from unoplat_code_confluence_cli.app_runtime import (
    AppRuntimeError,
    flow_bridge_probe_base_urls,
)
from unoplat_code_confluence_cli.config import CliSettings


class RepositoryProviderCheck(BaseModel):
    """Repository-provider credential verification result."""

    model_config = ConfigDict(frozen=True)

    provider_key: str
    configured: bool


class ModelProviderCheck(BaseModel):
    """Model-provider configuration verification result."""

    model_config = ConfigDict(frozen=True)

    configured: bool
    provider_key: str | None = None
    model_name: str | None = None
    has_api_key: bool = False


class SetupStatusResult(BaseModel):
    """Combined setup verification result."""

    model_config = ConfigDict(frozen=True)

    repository_provider: RepositoryProviderCheck
    model_provider: ModelProviderCheck


class ModelConfigResponse(BaseModel):
    """Subset of Query Engine's model config response used by the CLI."""

    provider_key: str
    model_name: str
    has_api_key: bool = False


def get_setup_status(
    settings: CliSettings,
    *,
    repository_provider_key: str | None = None,
) -> SetupStatusResult:
    """Check repository-provider and model-provider setup state."""
    provider_key = repository_provider_key or settings.default_provider
    return SetupStatusResult(
        repository_provider=check_repository_provider_token(
            settings,
            provider_key=provider_key,
            raise_on_missing=False,
        ),
        model_provider=check_model_provider_config(
            settings,
            raise_on_missing=False,
        ),
    )


def check_repository_provider_token(
    settings: CliSettings,
    *,
    provider_key: str | None = None,
    raise_on_missing: bool = True,
) -> RepositoryProviderCheck:
    """Verify repository-provider credentials by calling Flow Bridge user-details."""
    resolved_provider_key = provider_key or settings.default_provider
    response: httpx2.Response | None = None
    last_error: httpx2.HTTPError | None = None

    for base_url in flow_bridge_probe_base_urls(settings):
        try:
            response = httpx2.get(
                f"{base_url}/user-details",
                params={"provider_key": resolved_provider_key},
                timeout=settings.request_timeout_seconds,
            )
            break
        except httpx2.HTTPError as exc:
            last_error = exc
            continue

    if response is None:
        raise AppRuntimeError(
            f"Unable to reach Flow Bridge to verify repository-provider token: {last_error}"
        )

    if 200 <= response.status_code < 300:
        return RepositoryProviderCheck(
            provider_key=resolved_provider_key,
            configured=True,
        )

    detail = _extract_error_detail(response)
    if response.status_code == 404:
        if raise_on_missing:
            raise AppRuntimeError(
                detail
                or (
                    "Repository-provider token is not configured. Run "
                    "`ucc setup token-repo-provider` and complete the browser flow."
                )
            )
        return RepositoryProviderCheck(
            provider_key=resolved_provider_key,
            configured=False,
        )

    try:
        response.raise_for_status()
    except httpx2.HTTPError as exc:
        raise AppRuntimeError(
            detail or f"Unable to verify repository-provider token: {exc}"
        ) from exc
    raise AppRuntimeError(
        detail
        or (
            "Unable to verify repository-provider token: "
            f"HTTP status {response.status_code}"
        )
    )


def check_model_provider_config(
    settings: CliSettings,
    *,
    raise_on_missing: bool = True,
) -> ModelProviderCheck:
    """Verify Query Engine has an active model config with credentials."""
    try:
        response = httpx2.get(
            f"{settings.query_engine_base_url}/v1/model-config",
            timeout=settings.request_timeout_seconds,
        )
    except httpx2.HTTPError as exc:
        raise AppRuntimeError(
            f"Unable to reach Query Engine to verify model-provider configuration: {exc}"
        ) from exc

    if response.status_code == 404:
        if raise_on_missing:
            raise AppRuntimeError(
                "Model-provider configuration is not set. Run "
                "`ucc setup model-provider` and complete the browser flow."
            )
        return ModelProviderCheck(configured=False)

    if not 200 <= response.status_code < 300:
        detail = _extract_error_detail(response)
        try:
            response.raise_for_status()
        except httpx2.HTTPError as exc:
            raise AppRuntimeError(
                detail or f"Unable to verify model-provider configuration: {exc}"
            ) from exc
        raise AppRuntimeError(
            detail
            or (
                "Unable to verify model-provider configuration: "
                f"HTTP status {response.status_code}"
            )
        )

    try:
        config = ModelConfigResponse.model_validate_json(response.text)
    except ValidationError as exc:
        raise AppRuntimeError(
            "Query Engine returned an unexpected model-provider configuration payload."
        ) from exc

    if not config.has_api_key:
        if raise_on_missing:
            raise AppRuntimeError(
                "Model-provider configuration exists, but no model credential is set. "
                "Run `ucc setup model-provider` and complete the browser flow."
            )
        return ModelProviderCheck(
            configured=False,
            provider_key=config.provider_key,
            model_name=config.model_name,
            has_api_key=False,
        )

    return ModelProviderCheck(
        configured=True,
        provider_key=config.provider_key,
        model_name=config.model_name,
        has_api_key=True,
    )


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
