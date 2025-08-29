"""Credentials SQLModel for storing encrypted credentials with support for multiple credential types."""

from unoplat_code_confluence_commons.base_models.sql_base import SQLBase

from datetime import datetime
from typing import Optional

from sqlalchemy import Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import DateTime


class Credentials(SQLBase):
    """Model for storing encrypted credentials with support for multiple credential types."""
    
    __tablename__ = "credentials"
    __table_args__ = (
        # Add unique constraint on credential_key for multi-key credential support
        Index('ix_credentials_credential_key', 'credential_key', unique=True),
        # Keep existing unique constraint on token_hash for backward compatibility
    )
    
    credential_key: Mapped[str] = mapped_column(
        primary_key=True,
        comment="Stable identifier for this credential (e.g., 'github_pat', 'model_api_key')"
    )
    token_hash: Mapped[str] = mapped_column(
        comment="Encrypted credential value"
    )
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), default=None)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), default=None)
