from __future__ import annotations

from typing import Protocol

from unoplat_code_confluence_cli.domain.release import AppRelease, ReleaseManifest


class GitHubReleaseGateway(Protocol):
    def resolve_latest_app_release(self) -> AppRelease: ...
    def download_release_manifest(self, release: AppRelease) -> ReleaseManifest: ...
    def download_release_asset_text(self, *, tag: str, asset_name: str) -> str: ...
