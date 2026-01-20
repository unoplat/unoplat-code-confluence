"""Pydantic and SQLModel definitions for GitHub App onboarding."""

from __future__ import annotations

# Standard Library
from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional

# Third Party
from pydantic import AnyHttpUrl, BaseModel, Field
from sqlalchemy import Index, Text
from sqlalchemy.orm import Mapped, mapped_column

# Local
from unoplat_code_confluence_commons.base_models.sql_base import SQLBase


class GithubAppManifestRecord(SQLBase):
    """Database record tracking active manifest states awaiting conversion."""

    __tablename__ = "github_app_manifest_request"
    __table_args__ = (
        Index(
            "ix_github_app_manifest_request_expires_at",
            "expires_at",
        ),
    )

    state: Mapped[str] = mapped_column(primary_key=True)
    manifest_json: Mapped[str] = mapped_column(Text, nullable=False)
    owner_login: Mapped[Optional[str]] = mapped_column(nullable=True)
    owner_type: Mapped[str] = mapped_column(nullable=False, default="user")
    registration_url: Mapped[Optional[str]] = mapped_column(nullable=True)
    requested_by: Mapped[Optional[str]] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)


class ManifestGenerationRequest(BaseModel):
    """Incoming payload for initiating the manifest flow."""

    owner: Optional[str] = Field(
        default=None,
        description=(
            "GitHub username or organization slug that will own the GitHub App. "
            "Falls back to service defaults when omitted."
        ),
    )
    owner_type: Literal["user", "organization"] = Field(
        default="user",
        description="Determines whether to use /settings/apps/new or /organizations/{owner}/settings/apps/new.",
    )
    service_base_url: AnyHttpUrl = Field(
        description="Base URL where this service is reachable (e.g. https://bridge.example.com).",
    )
    webhook_proxy_url: Optional[AnyHttpUrl] = Field(
        default=None,
        description="Optional webhook proxy (e.g. smee.io) used in place of the service webhook for local testing.",
    )
    app_name: Optional[str] = Field(
        default=None,
        description="Optional override for the GitHub App name; defaults to the service configuration.",
    )
    description: Optional[str] = Field(
        default=None,
        description="Optional override for the GitHub App description.",
    )
    homepage_url: Optional[AnyHttpUrl] = Field(
        default=None,
        description="Optional override for the GitHub App homepage URL.",
    )
    post_install_redirect_url: Optional[AnyHttpUrl] = Field(
        default=None,
        description="Optional URL GitHub should redirect to after the installation completes.",
    )
    requested_by: Optional[str] = Field(
        default=None,
        description="Opaque identifier representing the operator that initiated the manifest flow.",
    )


class ManifestGenerationResponse(BaseModel):
    """Response payload returned to the operator initiating the manifest flow."""

    state: str = Field(
        description="Opaque state token that must be echoed back by GitHub."
    )
    manifest: Dict[str, Any] = Field(
        description="Final manifest JSON submitted to GitHub."
    )
    registration_url: AnyHttpUrl = Field(
        description="GitHub URL the operator should open to register the manifest."
    )
    owner: Optional[str] = Field(
        default=None, description="Effective owner slug resolved for the manifest."
    )
    owner_type: Literal["user", "organization"] = Field(
        description="Owner type that will receive the GitHub App."
    )
    expires_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp (UTC) when the manifest state will expire if unused.",
    )


class ManifestConversionResponse(BaseModel):
    """Response payload returned after exchanging the manifest code with GitHub."""

    app_slug: str = Field(description="Short slug assigned to the created GitHub App.")
    app_id: int = Field(description="Numeric identifier of the created GitHub App.")
    client_id: str = Field(
        description="OAuth client identifier associated with the app."
    )
    html_url: AnyHttpUrl = Field(description="GitHub UI URL for managing the app.")
    installation_url: AnyHttpUrl = Field(
        description="URL the operator should visit to install the GitHub App."
    )
    instructions: List[str] = Field(
        description="Ordered list of recommended follow-up steps for the operator."
    )
