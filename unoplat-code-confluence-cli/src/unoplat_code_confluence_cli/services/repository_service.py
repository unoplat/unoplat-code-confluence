from __future__ import annotations

from collections.abc import Callable

from unoplat_code_confluence_cli.backend.flow_bridge_client import FlowBridgeClient
from unoplat_code_confluence_cli.domain.repository import RepositoryGitUrl
from unoplat_code_confluence_cli.domain.results import RepositoryAddResult, RepositoryRefreshResult
from unoplat_code_confluence_cli.services.app_service import AppService
from unoplat_code_confluence_cli.services.setup_service import SetupService

ProgressCallback = Callable[[str], None]


class RepositoryService:
    def __init__(
        self,
        *,
        app: AppService,
        setup: SetupService,
        flow_bridge: FlowBridgeClient,
        auto_start: bool,
    ) -> None:
        self._app = app
        self._setup = setup
        self._flow_bridge = flow_bridge
        self._auto_start = auto_start

    def add_repository(
        self,
        *,
        repository_git_url: str,
        progress: ProgressCallback | None = None,
    ) -> RepositoryAddResult:
        parsed = RepositoryGitUrl.parse(repository_git_url)
        if self._auto_start:
            self._app.ensure_running(progress=progress)
        self._setup.check_repository_provider_token(provider_key=parsed.provider_key)
        return self._flow_bridge.add_repository(
            repository_git_url=parsed.repository_git_url,
            provider_key=parsed.provider_key,
        )

    def start_agent_md_generate_update(
        self,
        *,
        repository_git_url: str,
        progress: ProgressCallback | None = None,
    ) -> RepositoryRefreshResult:
        parsed = RepositoryGitUrl.parse(repository_git_url)
        if self._auto_start:
            self._app.ensure_running(progress=progress)
        self._setup.check_repository_provider_token(provider_key=parsed.provider_key)
        self._setup.check_model_provider_config()
        add_result = self._flow_bridge.add_repository(
            repository_git_url=parsed.repository_git_url,
            provider_key=parsed.provider_key,
        )
        return self._flow_bridge.refresh_repository(
            repository_name=add_result.repository_name,
            repository_owner_name=add_result.repository_owner_name,
            provider_key=add_result.provider_key,
            repository_git_url=add_result.repository_git_url,
        )
