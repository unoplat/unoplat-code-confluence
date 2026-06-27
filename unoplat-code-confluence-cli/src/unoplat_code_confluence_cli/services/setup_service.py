from __future__ import annotations

from collections.abc import Callable
from typing import Literal

from pydantic import AnyUrl

from unoplat_code_confluence_cli.backend.flow_bridge_client import FlowBridgeClient
from unoplat_code_confluence_cli.backend.query_engine_client import QueryEngineClient
from unoplat_code_confluence_cli.config import CliSettings
from unoplat_code_confluence_cli.domain.results import (
    ModelProviderCheck,
    RepositoryProviderCheck,
    SetupOpenResult,
    SetupStatusResult,
)
from unoplat_code_confluence_cli.ports.browser import BrowserOpener
from unoplat_code_confluence_cli.services.app_service import AppService

ProgressCallback = Callable[[str], None]


class SetupService:
    def __init__(
        self,
        *,
        settings: CliSettings,
        app: AppService,
        flow_bridge: FlowBridgeClient,
        query_engine: QueryEngineClient,
        browser: BrowserOpener,
    ) -> None:
        self._settings = settings
        self._app = app
        self._flow_bridge = flow_bridge
        self._query_engine = query_engine
        self._browser = browser

    def get_status(
        self,
        *,
        repository_provider_key: str | None = None,
        progress: ProgressCallback | None = None,
    ) -> SetupStatusResult:
        if self._settings.auto_start:
            self._app.ensure_running(progress=progress)
        provider_key = repository_provider_key or self._settings.default_provider
        return SetupStatusResult(
            repository_provider=self.check_repository_provider_token(
                provider_key=provider_key,
                raise_on_missing=False,
            ),
            model_provider=self.check_model_provider_config(raise_on_missing=False),
        )

    def check_repository_provider_token(
        self,
        *,
        provider_key: str | None = None,
        raise_on_missing: bool = True,
    ) -> RepositoryProviderCheck:
        resolved_provider_key = provider_key or self._settings.default_provider
        return self._flow_bridge.check_repository_provider_token(
            provider_key=resolved_provider_key,
            raise_on_missing=raise_on_missing,
        )

    def check_model_provider_config(
        self,
        *,
        raise_on_missing: bool = True,
    ) -> ModelProviderCheck:
        return self._query_engine.check_model_provider_config(
            raise_on_missing=raise_on_missing,
        )

    def open_setup_url(
        self,
        *,
        setup_target: Literal["token-repo-provider", "model-provider"],
        path: str,
        progress: ProgressCallback | None = None,
    ) -> SetupOpenResult:
        self._app.ensure_running(progress=progress)
        url = self.setup_url(path)
        opened = self._browser.open(url)
        return SetupOpenResult(
            setup_target=setup_target,
            url=AnyUrl(url),
            opened=opened,
        )

    def setup_url(self, path: str) -> str:
        normalized_path = path if path.startswith("/") else f"/{path}"
        return f"{self._settings.frontend_base_url}{normalized_path}"
