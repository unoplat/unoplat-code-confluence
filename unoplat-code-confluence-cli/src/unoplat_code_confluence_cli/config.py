from __future__ import annotations

from pathlib import Path

from platformdirs import user_data_dir
from pydantic import AnyHttpUrl, Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class CliSettings(BaseSettings):
    """Runtime settings for the Unoplat Code Confluence CLI."""

    model_config = SettingsConfigDict(
        env_prefix="UNOPLAT_CODE_CONFLUENCE_",
        env_file=".env",
        extra="ignore",
    )

    flow_bridge_url: AnyHttpUrl = Field(default=AnyHttpUrl("http://127.0.0.1:8000"))
    query_engine_url: AnyHttpUrl = Field(default=AnyHttpUrl("http://127.0.0.1:8001"))
    frontend_url: AnyHttpUrl = Field(default=AnyHttpUrl("http://127.0.0.1:3000"))
    github_repository: str = "unoplat/unoplat-code-confluence"
    github_api_base_url: AnyHttpUrl = Field(default=AnyHttpUrl("https://api.github.com"))
    compose_project_name: str = "unoplat-code-confluence"
    default_provider: str = "github_open"
    request_timeout_seconds: float = 120.0
    startup_timeout_seconds: float = 180.0
    auto_start: bool = True
    data_dir: Path | None = None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def resolved_data_dir(self) -> Path:
        if self.data_dir is not None:
            return self.data_dir.expanduser()
        return Path(user_data_dir("unoplat-code-confluence", "unoplat"))

    @computed_field  # type: ignore[prop-decorator]
    @property
    def compose_file_path(self) -> Path:
        return self.resolved_data_dir / "prod-docker-compose.yml"

    @property
    def flow_bridge_base_url(self) -> str:
        return str(self.flow_bridge_url).rstrip("/")

    @property
    def query_engine_base_url(self) -> str:
        return str(self.query_engine_url).rstrip("/")

    @property
    def frontend_base_url(self) -> str:
        return str(self.frontend_url).rstrip("/")

    @computed_field  # type: ignore[prop-decorator]
    @property
    def release_state_path(self) -> Path:
        return self.resolved_data_dir / "release-state.json"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def setup_metadata_path(self) -> Path:
        return self.resolved_data_dir / "setup-metadata.json"

    @property
    def github_api_base(self) -> str:
        return str(self.github_api_base_url).rstrip("/")
