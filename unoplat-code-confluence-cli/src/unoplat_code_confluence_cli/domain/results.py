from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import AnyUrl, BaseModel, ConfigDict


class AppRunResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    compose_file: Path
    release_state_file: Path
    installed_tag: str | None
    available_tag: str | None
    update_available: bool
    installed_release: bool
    warnings: tuple[str, ...]


class AppUpdateResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    compose_file: Path
    release_state_file: Path
    previous_tag: str
    installed_tag: str
    available_tag: str
    warnings: tuple[str, ...]


class AppDownResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    compose_file: Path
    release_state_file: Path
    removed_volumes: bool
    stopped_stack: bool


class RepositoryAddResult(BaseModel):
    """Response returned by Flow Bridge after adding a repository."""

    model_config = ConfigDict(frozen=True)

    repository_name: str
    repository_owner_name: str
    repository_git_url: str
    provider_key: str
    already_added: bool
    message: str


class RepositoryRefreshResult(BaseModel):
    """Response returned by Flow Bridge after starting refresh-then-agent-md."""

    model_config = ConfigDict(frozen=True)

    repository_name: str
    repository_owner_name: str
    workflow_id: str
    run_id: str
    message: str = (
        "AGENTS.md generation/update has started. A pull request will be raised "
        "automatically when the workflow completes."
    )


class RepositoryProviderCheck(BaseModel):
    """Repository-provider credential verification result."""

    model_config = ConfigDict(frozen=True)

    provider_key: str
    configured: bool


class ModelProviderCheck(BaseModel):
    """Model-provider configuration verification result."""

    model_config = ConfigDict(frozen=True)

    configured: bool
    provider_key: str | None = None
    model_name: str | None = None
    has_api_key: bool = False


class SetupStatusResult(BaseModel):
    """Combined setup verification result."""

    model_config = ConfigDict(frozen=True)

    repository_provider: RepositoryProviderCheck
    model_provider: ModelProviderCheck


class SetupOpenResult(BaseModel):
    """Result emitted by setup commands after opening a frontend setup URL."""

    model_config = ConfigDict(frozen=True)

    setup_target: Literal["token-repo-provider", "model-provider"]
    url: AnyUrl
    opened: bool
