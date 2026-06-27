from __future__ import annotations

import time
from collections.abc import Callable
from datetime import UTC, datetime

from unoplat_code_confluence_cli.backend.flow_bridge_client import FlowBridgeClient
from unoplat_code_confluence_cli.backend.query_engine_client import QueryEngineClient
from unoplat_code_confluence_cli.config import CliSettings
from unoplat_code_confluence_cli.domain.release import AppRelease, ReleaseState, semver_tuple, validate_manifest
from unoplat_code_confluence_cli.domain.results import AppDownResult, AppRunResult, AppUpdateResult
from unoplat_code_confluence_cli.errors import CliError, ReleaseError, ServiceReadinessError
from unoplat_code_confluence_cli.ports.docker_compose import DockerComposeManager
from unoplat_code_confluence_cli.ports.github_releases import GitHubReleaseGateway
from unoplat_code_confluence_cli.ports.release_store import ReleaseStore

ProgressCallback = Callable[[str], None]


class AppService:
    def __init__(
        self,
        *,
        settings: CliSettings,
        flow_bridge: FlowBridgeClient,
        query_engine: QueryEngineClient,
        releases: GitHubReleaseGateway,
        docker: DockerComposeManager,
        store: ReleaseStore,
    ) -> None:
        self._settings = settings
        self._flow_bridge = flow_bridge
        self._query_engine = query_engine
        self._releases = releases
        self._docker = docker
        self._store = store

    def run(self, *, progress: ProgressCallback | None = None) -> AppRunResult:
        """Install-on-first-run and start the pinned app release."""
        emit_progress(progress, "Checking local app runtime and release state...")
        already_reachable = self._flow_bridge.is_reachable()
        state = self._store.read_release_state()
        warnings: list[str] = []
        emit_progress(progress, "Resolving latest Unoplat Code Confluence app release...")
        latest_release = self._resolve_latest_app_release_or_warn(warnings)
        installed_release = False

        if state is None:
            if latest_release is None:
                raise ReleaseError(
                    "No local app release is installed and the latest app release could not be resolved. "
                    "Check network access to GitHub releases and retry."
                )
            emit_progress(progress, f"Installing app release {latest_release.tag}...")
            state = self.install_release(latest_release)
            installed_release = True
        elif not self._store.compose_file_exists():
            release = AppRelease(
                version=state.installed_version,
                tag=state.installed_tag,
                semver=semver_tuple(state.installed_version),
            )
            emit_progress(progress, f"Repairing cached app assets for {release.tag}...")
            state = self.install_release(release)
            installed_release = True

        available_tag = latest_release.tag if latest_release is not None else None
        has_update = latest_release is not None and semver_tuple(
            latest_release.version
        ) > semver_tuple(state.installed_version)

        if not already_reachable:
            self._docker.ensure_available()
            emit_progress(progress, "Pulling Docker images for the pinned app release...")
            self._docker.pull_images()
            emit_progress(progress, "Starting Docker Compose stack...")
            self._docker.start_stack()
        else:
            emit_progress(
                progress, "Flow Bridge is already reachable; not restarting the stack."
            )

        return AppRunResult(
            compose_file=self._store.compose_file_path,
            release_state_file=self._store.release_state_path,
            installed_tag=state.installed_tag,
            available_tag=available_tag,
            update_available=has_update,
            installed_release=installed_release,
            warnings=tuple(warnings),
        )

    def update(self, *, progress: ProgressCallback | None = None) -> AppUpdateResult:
        """Upgrade the pinned local release to the latest app release."""
        emit_progress(progress, "Reading local release state...")
        state = self._store.read_release_state()
        if state is None:
            raise ReleaseError(
                "Nothing is installed yet, so there is no pinned version to update. "
                "Run `unoplat service run` first to fetch and start the latest release."
            )

        warnings: list[str] = []
        emit_progress(progress, "Resolving latest Unoplat Code Confluence app release...")
        latest_release = self._resolve_latest_app_release_or_warn(warnings)
        if latest_release is None:
            raise ReleaseError(
                "Unable to resolve the latest app release from GitHub, so the installed "
                f"version {state.installed_version} was not changed."
            )

        updated = semver_tuple(latest_release.version) > semver_tuple(state.installed_version)
        previous_tag = state.installed_tag

        if updated:
            emit_progress(progress, f"Installing app release {latest_release.tag}...")
            state = self.install_release(latest_release)
        else:
            emit_progress(progress, "Installed app release is already up to date.")

        self._docker.ensure_available()
        emit_progress(progress, "Pulling Docker images for the pinned app release...")
        self._docker.pull_images()
        emit_progress(progress, "Applying Docker image updates with Docker Compose...")
        self._docker.start_stack()

        return AppUpdateResult(
            compose_file=self._store.compose_file_path,
            release_state_file=self._store.release_state_path,
            previous_tag=previous_tag,
            installed_tag=state.installed_tag,
            available_tag=latest_release.tag,
            warnings=tuple(warnings),
        )

    def stop(self, *, progress: ProgressCallback | None = None) -> AppDownResult:
        return self._down(progress=progress, volumes=False)

    def destroy(self, *, progress: ProgressCallback | None = None) -> AppDownResult:
        return self._down(progress=progress, volumes=True)

    def ensure_running(self, *, progress: ProgressCallback | None = None) -> AppRunResult:
        result = self.run(progress=progress)
        self.wait_for_services_ready(progress=progress)
        return result

    def install_release(self, release: AppRelease) -> ReleaseState:
        manifest = self._releases.download_release_manifest(release)
        validate_manifest(manifest, release)
        compose_content = self._releases.download_release_asset_text(
            tag=release.tag,
            asset_name=manifest.compose.asset,
        )
        state = ReleaseState(
            schema_version=1,
            installed_version=manifest.app.version,
            installed_tag=manifest.app.tag,
            fetched_at=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            manifest=manifest,
        )
        self._store.write_compose_file(compose_content)
        self._store.write_release_state(state)
        return state

    def wait_for_services_ready(self, *, progress: ProgressCallback | None = None) -> None:
        self.wait_for_service_ready(
            service_name="Flow Bridge",
            is_ready=self._flow_bridge.is_ready,
            base_url=self._settings.flow_bridge_base_url,
            progress=progress,
        )
        self.wait_for_service_ready(
            service_name="Query Engine",
            is_ready=self._query_engine.is_ready,
            base_url=self._settings.query_engine_base_url,
            progress=progress,
        )

    def wait_for_service_ready(
        self,
        *,
        service_name: str,
        is_ready: Callable[[], bool],
        base_url: str,
        progress: ProgressCallback | None = None,
    ) -> None:
        emit_progress(progress, f"Waiting for {service_name} to become ready...")
        deadline = time.monotonic() + self._settings.startup_timeout_seconds
        while time.monotonic() < deadline:
            if is_ready():
                return
            time.sleep(2)

        raise ServiceReadinessError(
            f"{service_name} did not become ready at {base_url} within "
            f"{self._settings.startup_timeout_seconds:.0f}s. Check Docker container logs and retry."
        )

    def _down(self, *, progress: ProgressCallback | None, volumes: bool) -> AppDownResult:
        if not self._store.compose_file_exists():
            raise ReleaseError(
                "No cached Docker Compose file was found. Run `unoplat service run` first to "
                "fetch the pinned app release before stopping or destroying it."
            )

        self._docker.ensure_available()
        if volumes:
            emit_progress(progress, "Stopping Docker Compose stack and deleting volumes...")
        else:
            emit_progress(progress, "Stopping Docker Compose stack...")
        self._docker.stop_stack(volumes=volumes)

        return AppDownResult(
            compose_file=self._store.compose_file_path,
            release_state_file=self._store.release_state_path,
            removed_volumes=volumes,
            stopped_stack=True,
        )

    def _resolve_latest_app_release_or_warn(self, warnings: list[str]) -> AppRelease | None:
        try:
            return self._releases.resolve_latest_app_release()
        except CliError as exc:
            warnings.append(str(exc))
            return None


def emit_progress(progress: ProgressCallback | None, message: str) -> None:
    if progress is not None:
        progress(message)
