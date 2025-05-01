from typing import Any, List, Optional

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class RepositoryData(SQLModel, table=True):
    """SQLModel for repository_data table in code_confluence schema."""
    repository_name: str = Field(primary_key=True, description="The name of the repository")
    repository_owner_name: str = Field(primary_key=True, description="The name of the repository owner")
    repository_workflow_status: Optional[dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSONB),
        description="The status of the repository workflows and its child workflows"
    )
    repository_metadata: List[dict[str, Any]] = Field(
        sa_column=Column(JSONB), description="List of codebase configurations for the repository"
    )
    