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


class RepositoryWorkflowRun(SQLModel, table=True):
    """SQLModel for repository_workflow_run table in code_confluence schema."""
    __tablename__ = "repository_workflow_run"
    __table_args__ = (
        CheckConstraint(
            "status IN ('SUBMITTED','RUNNING','FAILED','TIMED_OUT','COMPLETED','RETRYING')",
            name="status_check"
        ),
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
    repository_workflow_run_id: str = Field(
        primary_key=True, 
        description="The run ID of the repository workflow"
    )
    repository_workflow_id: str = Field(
        description="The ID of the repository workflow"
    )
    status: str = Field(
        sa_column=Column(String, nullable=False), 
        description="Status of the workflow run. One of: SUBMITTED, RUNNING, FAILED, TIMED_OUT, COMPLETED, RETRYING."
    )
    error_report: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSONB),
        description="Error report if the workflow run failed"
    )
    issue_tracking: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSONB),
        description="GitHub issue tracking info for this repository workflow run"
    )
    
    started_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False), 
        description="Timestamp when the workflow run started"
    )
    completed_at: Optional[datetime] = Field(
        default=None, 
        sa_column=Column(DateTime(timezone=True), nullable=True), 
        description="Timestamp when the workflow run completed"
    )
    
    # Relationships
    repository: Repository = Relationship(back_populates="workflow_runs")
    codebase_workflow_runs: List["CodebaseWorkflowRun"] = Relationship(
        back_populates="repository_workflow_run",
        sa_relationship_kwargs={
            "viewonly": True,
            "overlaps": "codebase_config,workflow_runs",
            "passive_deletes": True,
        },
    )


class CodebaseWorkflowRun(SQLModel, table=True):
    """SQLModel for codebase_workflow_run table in code_confluence schema."""
    __tablename__ = "codebase_workflow_run"
    __table_args__ = (
        CheckConstraint(
            "status IN ('SUBMITTED','RUNNING','FAILED','TIMED_OUT','COMPLETED','RETRYING')",
            name="codebase_status_check"
        ),
        ForeignKeyConstraint(
            ["repository_name", "repository_owner_name", "codebase_folder"],
            ["codebase_config.repository_name",
             "codebase_config.repository_owner_name",
             "codebase_config.codebase_folder"],
            ondelete="CASCADE"
        ),
        ForeignKeyConstraint(
            ["repository_name", "repository_owner_name", "repository_workflow_run_id"],
            ["repository_workflow_run.repository_name",
             "repository_workflow_run.repository_owner_name",
             "repository_workflow_run.repository_workflow_run_id"],
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
        description="FK to codebase_config - path to codebase folder"
    )
    codebase_workflow_run_id: str = Field(
        primary_key=True, 
        description="Unique identifier for this specific run of the codebase workflow"
    )
    codebase_workflow_id: str = Field(
        description="The ID of the codebase workflow"
    )
    repository_workflow_run_id: str = Field(
        description="Link back to parent repository workflow run"
    )
    status: str = Field(
        sa_column=Column(String, nullable=False), 
        description="Status of the workflow run. One of: SUBMITTED, RUNNING, FAILED, TIMED_OUT, COMPLETED, RETRYING."
    )
    error_report: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSONB),
        description="Error report if the workflow run failed"
    )
    issue_tracking: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSONB),
        description="GitHub issue tracking info for this codebase workflow run"
    )
    
    started_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False), 
        description="Timestamp when the workflow run started"
    )
    completed_at: Optional[datetime] = Field(
        default=None, 
        sa_column=Column(DateTime(timezone=True), nullable=True), 
        description="Timestamp when the workflow run completed"
    )
    
    # Relationships
    codebase_config: CodebaseConfig = Relationship(back_populates="workflow_runs")
    repository_workflow_run: RepositoryWorkflowRun = Relationship(back_populates="codebase_workflow_runs")