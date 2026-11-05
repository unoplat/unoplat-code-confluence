from __future__ import annotations

from pydantic import ValidationError

from unoplat_code_confluence_cli.config import CliSettings
from unoplat_code_confluence_cli.domain.results import ModelProviderCheck
from unoplat_code_confluence_cli.domain.setup import ModelConfigResponse
from unoplat_code_confluence_cli.errors import NetworkError, SetupRequiredError
from unoplat_code_confluence_cli.ports.http_client import HttpClient


class QueryEngineClient:
    """Concrete client for the Query Engine backend API used by the CLI."""

    def __init__(self, settings: CliSettings, http: HttpClient) -> None:
        self._settings = settings
        self._http = http

    def is_ready(self) -> bool:
        """Probe readiness, supporting pinned releases without a `/ready` route.

        `/v1/flags` is a read-only, database-backed endpoint available on older
        releases even before a model is configured. Only a missing readiness
        route permits fallback; never mask an explicit unhealthy response.
        """
        try:
            response = self._http.get(
                base_url=self._settings.query_engine_base_url,
                path="/ready",
                timeout=self._settings.request_timeout_seconds,
                action="check Query Engine readiness",
                allow_statuses=set(range(100, 600)),
            )
            if response.status_code == 200:
                return True
            if response.status_code != 404:
                return False
            fallback_response = self._http.get(
                base_url=self._settings.query_engine_base_url,
                path="/v1/flags",
                timeout=self._settings.request_timeout_seconds,
                action="check Query Engine readiness on older releases",
                allow_statuses=set(range(100, 600)),
            )
        except NetworkError:
            return False
        return fallback_response.status_code == 200

    def check_model_provider_config(
        self,
        *,
        raise_on_missing: bool = True,
    ) -> ModelProviderCheck:
        """Verify Query Engine has an active model config with credentials."""
        response = self._http.get(
            base_url=self._settings.query_engine_base_url,
            path="/v1/model-config",
            timeout=self._settings.request_timeout_seconds,
            action="verify model-provider configuration",
            allow_statuses={404},
        )

        if response.status_code == 404:
            if raise_on_missing:
                raise SetupRequiredError(
                    "Model-provider configuration is not set. Run "
                    "`ucc setup model-provider` and complete the browser flow."
                )
            return ModelProviderCheck(configured=False)

        if not 200 <= response.status_code < 300:
            detail = self._http.extract_error_detail(response)
            raise NetworkError(
                detail
                or (
                    "Unable to verify model-provider configuration: "
                    f"HTTP status {response.status_code}"
                )
            )

        try:
            config = ModelConfigResponse.model_validate_json(response.text)
        except ValidationError as exc:
            raise NetworkError(
                "Query Engine returned an unexpected model-provider configuration payload."
            ) from exc

        if not config.has_api_key:
            if raise_on_missing:
                raise SetupRequiredError(
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
