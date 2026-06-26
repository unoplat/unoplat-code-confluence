from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, ConfigDict

from unoplat_code_confluence_cli.errors import ReleaseError

APP_TAG_RE = re.compile(r"^unoplat-code-confluence-v(\d+)\.(\d+)\.(\d+)$")
RELEASE_MANIFEST_ASSET = "unoplat-code-confluence-release.json"


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


class GitHubRelease(BaseModel):
    model_config = ConfigDict(frozen=True)

    tag_name: str | None = None


class GitHubRef(BaseModel):
    model_config = ConfigDict(frozen=True)

    ref: str


def semver_tuple(version: str) -> tuple[int, int, int]:
    parts = version.split(".")
    if len(parts) != 3:
        raise ReleaseError(f"Invalid semantic version: {version}")
    try:
        return (int(parts[0]), int(parts[1]), int(parts[2]))
    except ValueError as exc:
        raise ReleaseError(f"Invalid semantic version: {version}") from exc


def app_release_from_tag(tag: str) -> AppRelease | None:
    match = APP_TAG_RE.fullmatch(tag)
    if match is None:
        return None
    major, minor, patch = (int(part) for part in match.groups())
    return AppRelease(
        version=f"{major}.{minor}.{patch}",
        tag=tag,
        semver=(major, minor, patch),
    )


def select_latest_app_release(releases: list[GitHubRelease]) -> AppRelease:
    app_releases: list[AppRelease] = []
    for release in releases:
        tag = release.tag_name
        if tag is None:
            continue
        app_release = app_release_from_tag(tag)
        if app_release is not None:
            app_releases.append(app_release)

    if not app_releases:
        raise ReleaseError(
            "No consumable app release was found. Expected tags matching "
            "unoplat-code-confluence-vMAJOR.MINOR.PATCH; component releases are ignored."
        )
    return max(app_releases, key=lambda release: release.semver)


def validate_manifest(manifest: ReleaseManifest, release: AppRelease) -> None:
    if manifest.app.version != release.version or manifest.app.tag != release.tag:
        raise ReleaseError(
            "Release manifest app.version/app.tag do not match the selected GitHub release."
        )
