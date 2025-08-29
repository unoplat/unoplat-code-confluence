"""SQLModel for storing feature flags shared across ingestion and query engine projects."""

from unoplat_code_confluence_commons.base_models.sql_base import SQLBase

from sqlalchemy.orm import Mapped, mapped_column


class Flag(SQLBase):
    """Model for storing feature flags."""
    
    __tablename__ = "flag"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, index=True)
    status: Mapped[bool] = mapped_column(default=False)