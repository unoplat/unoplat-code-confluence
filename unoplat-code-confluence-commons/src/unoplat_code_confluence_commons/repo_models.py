from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKeyConstraint, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel


class Repository(SQLModel, table=True):
    """SQLModel for repository table in code_confluence schema."""
    __tablename__ = "repository"

    repository_name: str = Field(primary_key=True, description="The name of the repository")
    repository_owner_name: str = Field(primary_key=True, description="The name of the repository owner")
    is_local: bool = Field(default=False, description="Whether this is a local repository")
    local_path: Optional[str] = Field(default=None, description="Local filesystem path for local repositories")
    
    # Relationships - will be populated after class definitions
    workflow_runs: List["RepositoryWorkflowRun"] = Relationship(
        back_populates="repository",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "passive_deletes": True,
        },
    )
    configs: List["CodebaseConfig"] = Relationship(
        back_populates="repository",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "passive_deletes": True,
        },
    )


class CodebaseConfig(SQLModel, table=True):
    """SQLModel for codebase_config table in code_confluence schema."""
    __tablename__ = "codebase_config"
    __table_args__ = (
        ForeignKeyConstraint(
            ["repository_name", "repository_owner_name"],
            ["repository.repository_name", "repository.repository_owner_name"],
            ondelete="CASCADE"
        ),
    )
    
    repository_name: str = Field(
        primary_key=True, 
        description="The name of the repository"
    )
    repository_owner_name: str = Field(
        primary_key=True, 
        description="The name of the repository owner"
    )
    codebase_folder: str = Field(
        primary_key=True, 
        description="Path to codebase folder relative to repo root"
    )
    root_packages: Optional[List[str]] = Field(
        default=None,
        sa_column=Column(JSONB),
        description="List of root packages within the codebase folder"
    )
    programming_language_metadata: Dict[str, Any] = Field(
        sa_column=Column(JSONB, nullable=False),
        description="Language-specific metadata for this codebase like programming language, package manager etc"
    )
    
    # Relationships
    repository: Repository = Relationship(back_populates="configs")
    workflow_runs: List["CodebaseWorkflowRun"] = Relationship(
        back_populates="codebase_config",
        sa_relationship_kwargs={
            "viewonly": True,
            "overlaps": "repository_workflow_run,workflow_runs",
        },
    )