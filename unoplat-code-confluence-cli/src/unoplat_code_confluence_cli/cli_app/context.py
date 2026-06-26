from __future__ import annotations

from dataclasses import dataclass

from unoplat_code_confluence_cli.adapters.browser import WebbrowserOpener
from unoplat_code_confluence_cli.adapters.docker_compose import WhalesDockerComposeManager
from unoplat_code_confluence_cli.adapters.github_releases_http import HttpGitHubReleaseGateway
from unoplat_code_confluence_cli.adapters.httpx2_client import Httpx2HttpClient
from unoplat_code_confluence_cli.adapters.release_store_file import FileReleaseStore
from unoplat_code_confluence_cli.backend.flow_bridge_client import FlowBridgeClient
from unoplat_code_confluence_cli.backend.query_engine_client import QueryEngineClient
from unoplat_code_confluence_cli.config import CliSettings
from unoplat_code_confluence_cli.services.app_service import AppService
from unoplat_code_confluence_cli.services.repository_service import RepositoryService
from unoplat_code_confluence_cli.services.setup_service import SetupService


@dataclass(frozen=True)
class CliServices:
    settings: CliSettings
    app: AppService
    repository: RepositoryService
    setup: SetupService


def build_services(settings: CliSettings | None = None) -> CliServices:
    resolved_settings = settings or CliSettings()
    http = Httpx2HttpClient()
    flow_bridge = FlowBridgeClient(resolved_settings, http)
    query_engine = QueryEngineClient(resolved_settings, http)
    releases = HttpGitHubReleaseGateway(resolved_settings, http)
    docker = WhalesDockerComposeManager(resolved_settings)
    store = FileReleaseStore(resolved_settings)
    browser = WebbrowserOpener()
    app = AppService(
        settings=resolved_settings,
        flow_bridge=flow_bridge,
        query_engine=query_engine,
        releases=releases,
        docker=docker,
        store=store,
    )
    setup = SetupService(
        settings=resolved_settings,
        app=app,
        flow_bridge=flow_bridge,
        query_engine=query_engine,
        browser=browser,
    )
    repository = RepositoryService(
        app=app,
        setup=setup,
        flow_bridge=flow_bridge,
        auto_start=resolved_settings.auto_start,
    )
    return CliServices(
        settings=resolved_settings,
        app=app,
        repository=repository,
        setup=setup,
    )

