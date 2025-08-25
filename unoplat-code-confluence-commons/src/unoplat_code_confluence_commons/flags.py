"""SQLModel for storing feature flags shared across ingestion and query engine projects."""

from typing import Optional

from sqlmodel import Field, SQLModel


class Flag(SQLModel, table=True):
    """Model for storing feature flags."""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    status: bool = Field(default=False)