from src.code_confluence_flow_bridge.models.github.github_repo import CodebaseRepoConfig, WorkflowStatus

from typing import List, Optional

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class RepositoryData(SQLModel, table=True):
    """SQLModel for repository_data table in code_confluence schema."""
    repository_name: str = Field(primary_key=True, description="The name of the repository")
    repository_owner_name: str = Field(primary_key=True, description="The name of the repository owner")
    repository_workflow_status: Optional[WorkflowStatus] = Field(
        default=None,
        sa_column=Column(JSONB),
        description="The status of the repository workflows"
    )
    repository_metadata: List[CodebaseRepoConfig] = Field(
        sa_column=Column(JSONB), description="List of codebase configurations for the repository"
    )
    