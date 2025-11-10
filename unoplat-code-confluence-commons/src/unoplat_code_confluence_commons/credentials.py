"""Credentials SQLModel for storing encrypted credentials with support for multiple credential types."""

from unoplat_code_confluence_commons.base_models.sql_base import SQLBase
from unoplat_code_confluence_commons.credential_enums import (
    CredentialNamespace,
    ProviderKey,
    SecretKind,
)

from datetime import datetime
from typing import Any, Optional
import uuid

from sqlalchemy import Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import DateTime


class Credentials(SQLBase):
    """Model for storing encrypted credentials with support for multiple credential types."""

    __tablename__ = "credentials"
    __table_args__ = (
        # Add unique constraint on credential_key for multi-key credential support
        Index(
            "uq_credentials_namespace_provider_secret",
            "namespace",
            "provider_key",
            "secret_kind",
            unique=True,
        ),
        # Keep existing unique constraint on token_hash for backward compatibility
    )
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    namespace: Mapped[CredentialNamespace] = mapped_column(nullable=False)
    provider_key: Mapped[ProviderKey] = mapped_column(nullable=False)
    secret_kind: Mapped[SecretKind] = mapped_column(nullable=False)
    token_hash: Mapped[str] = mapped_column(comment="Encrypted credential value")
    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        JSONB, default=None, comment="Provider specific metadata"
    )
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), default=None
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), default=None
    )
