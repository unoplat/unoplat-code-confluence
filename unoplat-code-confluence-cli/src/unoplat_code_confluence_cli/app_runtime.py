from __future__ import annotations

import os
import re
import time
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

import httpx2
from pydantic import BaseModel, ConfigDict, TypeAdapter, ValidationError
from python_on_whales import DockerClient
from python_on_whales.client_config import ClientNotFoundError
from python_on_whales.exceptions import DockerException

from unoplat_code_confluence_cli.config import CliSettings

APP_TAG_RE = re.compile(r"^unoplat-code-confluence-v(\d+)\.(\d+)\.(\d+)$")
RELEASE_MANIFEST_ASSET = "unoplat-code-confluence-release.json"


class AppRuntimeError(RuntimeError):
    """Raised when the local Code Confluence app runtime cannot be prepared."""


class AppRelease(BaseModel):
    model_config = ConfigDict(frozen=True)

    version: str
    tag: str
    semver: tuple[int, int, int]


class ReleaseManifestApp(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: Literal["unoplat-code-confluence"]
    version: str
    tag: str


class ReleaseManifestCompose(BaseModel):
    model_config = ConfigDict(frozen=True)

    asset: Literal["prod-docker-compose.yml"]


class ReleaseManifestComponent(BaseModel):
    model_config = ConfigDict(frozen=True)

    image: str
    tag: str


class ReleaseManifestComponents(BaseModel):
    model_config = ConfigDict(frozen=True)

    flow_bridge: ReleaseManifestComponent
    query_engine: ReleaseManifestComponent
    frontend: ReleaseManifestComponent


class ReleaseManifest(BaseModel):
    model_config = ConfigDict(frozen=True)

    schema_version: Literal[1]
    app: ReleaseManifestApp
    compose: ReleaseManifestCompose
    components: ReleaseManifestComponents


class ReleaseState(BaseModel):
    model_config = ConfigDict(frozen=True)

    schema_version: Literal[1]
    installed_version: str
    installed_tag: str
    fetched_at: str
    manifest: ReleaseManifest


class AppRunResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    compose_file: Path
    release_state_file: Path
    installed_version: str | None
    installed_tag: str | None
    available_version: str | None
    available_tag: str | None
    update_available: bool
    installed_release: bool
    pulled_images: bool
    started_stack: bool
    already_reachable: bool
    warnings: tuple[str, ...]


class AppUpdateResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    compose_file: Path
    release_state_file: Path
    previous_version: str
    previous_tag: str
    installed_version: str
    installed_tag: str
    available_version: str
    available_tag: str
    updated: bool
    pulled_images: bool
    started_stack: bool
    warnings: tuple[str, ...]


class GitHubRelease(BaseModel):
    model_config = ConfigDict(frozen=True)

    tag_name: str | None = None


def is_flow_bridge_reachable(settings: CliSettings) -> bool:
    """Return whether Flow Bridge is accepting HTTP requests."""
    try:
        response = httpx2.get(
            f"{settings.flow_bridge_base_url}/docs",
            timeout=settings.request_timeout_seconds,
        )
        return response.status_code < 500
    except httpx2.HTTPError:
        return False


def run_app(
    settings: CliSettings,
    *,
    progress: Callable[[str], None] | None = None,
) -> AppRunResult:
    """Install-on-first-run and start the pinned app release.

    Later runs never mutate the pinned assets just because a newer app release is
    available. A newer release is reported in the result only.
    """
    emit_progress(progress, "Checking local app runtime and release state...")
    already_reachable = is_flow_bridge_reachable(settings)
    state = read_release_state(settings)
    warnings: list[str] = []
    emit_progress(progress, "Resolving latest Unoplat Code Confluence app release...")
    latest_release = resolve_latest_app_release_or_warn(settings, warnings)
    installed_release = False
    pulled_images = False
    started_stack = False

    if state is None:
        if latest_release is None:
            raise AppRuntimeError(
                "No local app release is installed and the latest app release could not be resolved. "
                "Check network access to GitHub releases and retry."
            )
        emit_progress(progress, f"Installing app release {latest_release.tag}...")
        state = install_release(settings, latest_release)
        installed_release = True
    elif not settings.compose_file_path.exists():
        release = AppRelease(
            version=state.installed_version,
            tag=state.installed_tag,
            semver=semver_tuple(state.installed_version),
        )
        emit_progress(progress, f"Repairing cached app assets for {release.tag}...")
        state = install_release(settings, release)
        installed_release = True

    available_version = latest_release.version if latest_release is not None else None
    available_tag = latest_release.tag if latest_release is not None else None
    has_update = latest_release is not None and semver_tuple(
        latest_release.version
    ) > semver_tuple(state.installed_version)

    if not already_reachable:
        docker = build_docker_client(settings)
        ensure_docker_compose_available(docker)
        emit_progress(progress, "Pulling Docker images for the pinned app release...")
        pull_compose_images(docker)
        pulled_images = True
        emit_progress(progress, "Starting Docker Compose stack...")
        start_compose_stack(docker)
        started_stack = True
        emit_progress(progress, "Waiting for Flow Bridge to become reachable...")
        wait_for_flow_bridge(settings)
    else:
        emit_progress(
            progress, "Flow Bridge is already reachable; not restarting the stack."
        )

    return AppRunResult(
        compose_file=settings.compose_file_path,
        release_state_file=settings.release_state_path,
        installed_version=state.installed_version,
        installed_tag=state.installed_tag,
        available_version=available_version,
        available_tag=available_tag,
        update_available=has_update,
        installed_release=installed_release,
        pulled_images=pulled_images,
        started_stack=started_stack,
        already_reachable=already_reachable,
        warnings=tuple(warnings),
    )


def update_app(
    settings: CliSettings,
    *,
    progress: Callable[[str], None] | None = None,
) -> AppUpdateResult:
    """Upgrade the pinned local release to the latest app release with explicit consent."""
    emit_progress(progress, "Reading local release state...")
    state = read_release_state(settings)
    if state is None:
        raise AppRuntimeError(
            "Nothing is installed yet, so there is no pinned version to update. "
            "Run `unoplat run` first to fetch and start the latest release."
        )

    warnings: list[str] = []
    emit_progress(progress, "Resolving latest Unoplat Code Confluence app release...")
    latest_release = resolve_latest_app_release_or_warn(settings, warnings)
    if latest_release is None:
        raise AppRuntimeError(
            "Unable to resolve the latest app release from GitHub, so the installed "
            f"version {state.installed_version} was not changed."
        )

    updated = semver_tuple(latest_release.version) > semver_tuple(
        state.installed_version
    )
    previous_version = state.installed_version
    previous_tag = state.installed_tag

    if updated:
        emit_progress(progress, f"Installing app release {latest_release.tag}...")
        state = install_release(settings, latest_release)
    else:
        emit_progress(progress, "Installed app release is already up to date.")

    docker = build_docker_client(settings)
    ensure_docker_compose_available(docker)
    emit_progress(progress, "Pulling Docker images for the pinned app release...")
    pull_compose_images(docker)
    emit_progress(progress, "Applying Docker image updates with Docker Compose...")
    start_compose_stack(docker)

    return AppUpdateResult(
        compose_file=settings.compose_file_path,
        release_state_file=settings.release_state_path,
        previous_version=previous_version,
        previous_tag=previous_tag,
        installed_version=state.installed_version,
        installed_tag=state.installed_tag,
        available_version=latest_release.version,
        available_tag=latest_release.tag,
        updated=updated,
        pulled_images=True,
        started_stack=True,
        warnings=tuple(warnings),
    )


# Compatibility alias for future runtime-dependent commands.
def ensure_app_running(settings: CliSettings) -> AppRunResult:
    return run_app(settings)


def emit_progress(progress: Callable[[str], None] | None, message: str) -> None:
    if progress is not None:
        progress(message)


def resolve_latest_app_release_or_warn(
    settings: CliSettings, warnings: list[str]
) -> AppRelease | None:
    try:
        return resolve_latest_app_release(settings)
    except AppRuntimeError as exc:
        warnings.append(str(exc))
        return None


def resolve_latest_app_release(settings: CliSettings) -> AppRelease:
    releases = list_github_releases(settings)
    app_releases: list[AppRelease] = []
    for release in releases:
        tag = release.tag_name
        if tag is None:
            continue
        match = APP_TAG_RE.fullmatch(tag)
        if match is None:
            continue
        major, minor, patch = (int(part) for part in match.groups())
        app_releases.append(
            AppRelease(
                version=f"{major}.{minor}.{patch}",
                tag=tag,
                semver=(major, minor, patch),
            )
        )

    if not app_releases:
        raise AppRuntimeError(
            "No consumable app release was found. Expected tags matching "
            "unoplat-code-confluence-vMAJOR.MINOR.PATCH; component releases are ignored."
        )
    return max(app_releases, key=lambda release: release.semver)


def list_github_releases(settings: CliSettings) -> list[GitHubRelease]:
    releases: list[GitHubRelease] = []
    page = 1
    while True:
        url = (
            f"{settings.github_api_base}/repos/{settings.github_repository}/releases"
            f"?per_page=100&page={page}"
        )
        try:
            response = httpx2.get(
                url,
                headers={"Accept": "application/vnd.github+json"},
                timeout=settings.request_timeout_seconds,
            )
            response.raise_for_status()
        except httpx2.HTTPError as exc:
            raise AppRuntimeError(f"Unable to list GitHub releases: {exc}") from exc

        try:
            page_items = TypeAdapter(list[GitHubRelease]).validate_json(response.text)
        except ValidationError as exc:
            raise AppRuntimeError(
                "GitHub releases API returned an unexpected payload."
            ) from exc
        releases.extend(page_items)
        if len(page_items) < 100:
            break
        page += 1
    return releases


def install_release(settings: CliSettings, release: AppRelease) -> ReleaseState:
    manifest = download_release_manifest(settings, release)
    validate_manifest(manifest, release)
    compose_asset = manifest.compose.asset
    compose_content = download_release_asset(settings, release.tag, compose_asset).text
    state = ReleaseState(
        schema_version=1,
        installed_version=manifest.app.version,
        installed_tag=manifest.app.tag,
        fetched_at=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        manifest=manifest,
    )

    settings.resolved_data_dir.mkdir(parents=True, exist_ok=True)
    atomic_write_text(settings.compose_file_path, compose_content)
    write_release_state(settings, state)
    return state


def download_release_manifest(
    settings: CliSettings, release: AppRelease
) -> ReleaseManifest:
    response = download_release_asset(settings, release.tag, RELEASE_MANIFEST_ASSET)
    try:
        return ReleaseManifest.model_validate_json(response.text)
    except ValidationError as exc:
        raise AppRuntimeError(
            "Release manifest payload does not match schema_version 1."
        ) from exc


def download_release_asset(
    settings: CliSettings, tag: str, asset_name: str
) -> httpx2.Response:
    url = (
        f"https://github.com/{settings.github_repository}/releases/download/"
        f"{tag}/{asset_name}"
    )
    try:
        response = httpx2.get(
            url, follow_redirects=True, timeout=settings.request_timeout_seconds
        )
        response.raise_for_status()
    except httpx2.HTTPError as exc:
        raise AppRuntimeError(
            f"Unable to download release asset {asset_name} from {tag}: {exc}"
        ) from exc
    return response


def validate_manifest(manifest: ReleaseManifest, release: AppRelease) -> None:
    if manifest.app.version != release.version or manifest.app.tag != release.tag:
        raise AppRuntimeError(
            "Release manifest app.version/app.tag do not match the selected GitHub release."
        )


def read_release_state(settings: CliSettings) -> ReleaseState | None:
    path = settings.release_state_path
    if not path.exists():
        return None
    try:
        return ReleaseState.model_validate_json(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise AppRuntimeError(
            f"Unable to read local release state at {path}: {exc}"
        ) from exc
    except ValidationError as exc:
        raise AppRuntimeError(
            f"Local release state at {path} does not match schema_version 1."
        ) from exc


def write_release_state(settings: CliSettings, state: ReleaseState) -> None:
    atomic_write_text(
        settings.release_state_path,
        state.model_dump_json(indent=2) + "\n",
    )


def atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_name(f".{path.name}.tmp")
    temp_path.write_text(content, encoding="utf-8")
    os.replace(temp_path, path)


def semver_tuple(version: str) -> tuple[int, int, int]:
    parts = version.split(".")
    if len(parts) != 3:
        raise AppRuntimeError(f"Invalid semantic version: {version}")
    try:
        return (int(parts[0]), int(parts[1]), int(parts[2]))
    except ValueError as exc:
        raise AppRuntimeError(f"Invalid semantic version: {version}") from exc


def build_docker_client(settings: CliSettings) -> DockerClient:
    return DockerClient(
        compose_files=[settings.compose_file_path],
        compose_project_name=settings.compose_project_name,
    )


def ensure_docker_compose_available(docker: DockerClient) -> None:
    try:
        if not docker.compose.is_installed():
            raise AppRuntimeError(
                "Docker Compose is required to auto-start Unoplat Code Confluence. "
                "Install/enable the Docker Compose plugin and ensure `docker compose version` works."
            )
    except ClientNotFoundError as exc:
        raise AppRuntimeError(
            "Docker is required to auto-start Unoplat Code Confluence, but the "
            "docker executable was not found. Install Docker Desktop or Docker Engine "
            "with the Compose plugin, then retry."
        ) from exc
    except DockerException as exc:
        raise AppRuntimeError(
            "Docker Compose is required to auto-start Unoplat Code Confluence. "
            "Install/enable the Docker Compose plugin and ensure `docker compose version` works."
        ) from exc


def pull_compose_images(docker: DockerClient) -> None:
    try:
        docker.compose.pull()
    except (ClientNotFoundError, DockerException) as exc:
        raise_docker_runtime_error("Docker Compose pull failed", exc)


def start_compose_stack(docker: DockerClient) -> None:
    try:
        docker.compose.up(detach=True)
    except (ClientNotFoundError, DockerException) as exc:
        raise_docker_runtime_error("Docker Compose up failed", exc)


def raise_docker_runtime_error(
    message: str, exc: ClientNotFoundError | DockerException
) -> None:
    if isinstance(exc, ClientNotFoundError):
        raise AppRuntimeError(
            "Docker is required to auto-start Unoplat Code Confluence, but the "
            "docker executable was not found. Install Docker Desktop or Docker Engine "
            "with the Compose plugin, then retry."
        ) from exc

    details = exc.stderr or exc.stdout or str(exc)
    raise AppRuntimeError(f"{message}: {details}") from exc


def wait_for_flow_bridge(settings: CliSettings) -> None:
    deadline = time.monotonic() + settings.startup_timeout_seconds
    while time.monotonic() < deadline:
        if is_flow_bridge_reachable(settings):
            return
        time.sleep(2)

    raise AppRuntimeError(
        "Docker Compose stack was started, but Flow Bridge did not become reachable at "
        f"{settings.flow_bridge_base_url} within {settings.startup_timeout_seconds:.0f}s. "
        "Check Docker container logs and retry."
    )
