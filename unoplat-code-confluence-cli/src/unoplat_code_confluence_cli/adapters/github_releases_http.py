from __future__ import annotations

from pydantic import TypeAdapter, ValidationError

from unoplat_code_confluence_cli.config import CliSettings
from unoplat_code_confluence_cli.domain.release import (
    RELEASE_MANIFEST_ASSET,
    AppRelease,
    GitHubRef,
    GitHubRelease,
    ReleaseManifest,
    app_release_from_tag,
)
from unoplat_code_confluence_cli.errors import NetworkError, ReleaseError
from unoplat_code_confluence_cli.ports.http_client import HttpClient


class HttpGitHubReleaseGateway:
    def __init__(self, settings: CliSettings, http: HttpClient) -> None:
        self._settings = settings
        self._http = http

    def resolve_latest_app_release(self) -> AppRelease:
        app_releases = self._list_app_release_refs()
        for app_release in sorted(app_releases, key=lambda release: release.semver, reverse=True):
            if self._github_release_exists_for_tag(app_release.tag):
                return app_release

        raise ReleaseError(
            "No consumable app release was found. Expected tags matching "
            "unoplat-code-confluence-vMAJOR.MINOR.PATCH with a matching GitHub release."
        )

    def download_release_manifest(self, release: AppRelease) -> ReleaseManifest:
        content = self.download_release_asset_text(
            tag=release.tag,
            asset_name=RELEASE_MANIFEST_ASSET,
        )
        try:
            return ReleaseManifest.model_validate_json(content)
        except ValidationError as exc:
            raise ReleaseError(
                "Release manifest payload does not match schema_version 1."
            ) from exc

    def download_release_asset_text(self, *, tag: str, asset_name: str) -> str:
        try:
            response = self._http.get(
                base_url=f"https://github.com/{self._settings.github_repository}",
                path=f"/releases/download/{tag}/{asset_name}",
                follow_redirects=True,
                timeout=self._settings.request_timeout_seconds,
                action=f"download release asset {asset_name} from {tag}",
            )
        except NetworkError as exc:
            raise ReleaseError(
                f"Unable to download release asset {asset_name} from {tag}: {exc}"
            ) from exc
        return response.text

    def _list_app_release_refs(self) -> list[AppRelease]:
        """List app release tags using GitHub's prefix-matching refs API.

        The releases-by-tag endpoint only accepts an exact tag, not a wildcard.
        To avoid paging every repository release, query matching git refs for the
        Unoplat Code Confluence app tag prefix, parse semantic versions
        client-side, then verify the selected tag has a GitHub release.
        """
        response = self._http.get(
            base_url=f"{self._settings.github_api_base}/repos/{self._settings.github_repository}",
            path="/git/matching-refs/tags/unoplat-code-confluence-v",
            headers={"Accept": "application/vnd.github+json"},
            timeout=self._settings.request_timeout_seconds,
            action="list matching Unoplat Code Confluence app release tags",
        )
        try:
            refs = TypeAdapter(list[GitHubRef]).validate_json(response.text)
        except ValidationError as exc:
            raise ReleaseError(
                "GitHub matching refs API returned an unexpected payload."
            ) from exc

        app_releases: list[AppRelease] = []
        for ref in refs:
            tag = ref.ref.removeprefix("refs/tags/")
            app_release = app_release_from_tag(tag)
            if app_release is not None:
                app_releases.append(app_release)
        return app_releases

    def _github_release_exists_for_tag(self, tag: str) -> bool:
        response = self._http.get(
            base_url=f"{self._settings.github_api_base}/repos/{self._settings.github_repository}",
            path=f"/releases/tags/{tag}",
            headers={"Accept": "application/vnd.github+json"},
            timeout=self._settings.request_timeout_seconds,
            action=f"get GitHub release by tag {tag}",
            allow_statuses={404},
        )
        if response.status_code == 404:
            return False
        try:
            release = GitHubRelease.model_validate_json(response.text)
        except ValidationError as exc:
            raise ReleaseError(
                "GitHub release-by-tag API returned an unexpected payload."
            ) from exc
        return release.tag_name == tag
