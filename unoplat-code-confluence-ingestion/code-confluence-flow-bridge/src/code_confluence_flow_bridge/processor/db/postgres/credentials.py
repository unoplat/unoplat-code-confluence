from datetime import datetime
from typing import Optional

from sqlalchemy import Column
from sqlalchemy.sql.sqltypes import DateTime
from sqlmodel import Field, SQLModel


class Credentials(SQLModel, table=True):
    """Model for storing GitHub credentials."""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    token_hash: str = Field(unique=True)
    created_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    updated_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True))) 