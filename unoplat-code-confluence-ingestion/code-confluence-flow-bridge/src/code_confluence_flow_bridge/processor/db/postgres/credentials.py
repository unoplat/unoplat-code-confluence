from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Index
from sqlalchemy.sql.sqltypes import DateTime
from sqlmodel import Field, SQLModel


class Credentials(SQLModel, table=True):
    """Model for storing encrypted credentials with support for multiple credential types."""
    
    __table_args__ = (
        # Add unique constraint on credential_key for multi-key credential support
        Index('ix_credentials_credential_key', 'credential_key', unique=True),
        # Keep existing unique constraint on token_hash for backward compatibility
    )
    
    id: Optional[int] = Field(default=None, primary_key=True)
    credential_key: str = Field(
        default="github_pat", 
        description="Stable identifier for this credential (e.g., 'github_pat', 'model_api_key')"
    )
    token_hash: str = Field(
        description="Encrypted credential value"
    )
    created_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    updated_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True))) 