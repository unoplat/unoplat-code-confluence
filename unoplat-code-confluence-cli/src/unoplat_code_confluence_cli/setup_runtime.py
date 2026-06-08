from __future__ import annotations

import webbrowser
from typing import Literal

from pydantic import BaseModel, ConfigDict, AnyUrl

from unoplat_code_confluence_cli.config import CliSettings


class SetupOpenResult(BaseModel):
    """Result emitted by setup commands after opening a frontend setup URL."""

    model_config = ConfigDict(frozen=True)

    setup_target: Literal["token-repo-provider", "model-provider"]
    url: AnyUrl
    opened: bool


def setup_url(settings: CliSettings, path: str) -> str:
    """Build a setup URL from the configured frontend base URL and route path."""
    normalized_path = path if path.startswith("/") else f"/{path}"
    return f"{settings.frontend_base_url}{normalized_path}"


def open_setup_url(
    settings: CliSettings,
    *,
    setup_target: Literal["token-repo-provider", "model-provider"],
    path: str,
) -> SetupOpenResult:
    """Open a setup route in the user's default browser."""
    url = setup_url(settings, path)
    opened = webbrowser.open(url)
    return SetupOpenResult(setup_target=setup_target, url=AnyUrl(url), opened=opened)
