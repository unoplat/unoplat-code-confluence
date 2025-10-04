from unoplat_code_confluence_commons.base_models.sql_base import SQLBase

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum as SQLEnum,
    ForeignKeyConstraint,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship


class RepoAgentSnapshotStatus(Enum):
    """Lifecycle status for repository agent markdown snapshot persistence."""

    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"


class Repository(SQLBase):
    """SQLModel for repository table in code_confluence schema."""
    __tablename__ = "repository"

    repository_name: Mapped[str] = mapped_column(primary_key=True, comment="The name of the repository")
    repository_owner_name: Mapped[str] = mapped_column(primary_key=True, comment="The name of the repository owner")
    is_local: Mapped[bool] = mapped_column(default=False, comment="Whether this is a local repository")
    local_path: Mapped[Optional[str]] = mapped_column(default=None, comment="Local filesystem path for local repositories")
    
    # Relationships - will be populated after class definitions
    workflow_runs: Mapped[List["RepositoryWorkflowRun"]] = relationship(
        back_populates="repository",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    configs: Mapped[List["CodebaseConfig"]] = relationship(
        back_populates="repository",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    agent_md_snapshot: Mapped[Optional["RepositoryAgentMdSnapshot"]] = relationship(
        back_populates="repository",
        cascade="all, delete-orphan",
        passive_deletes=True,
        uselist=False,
    )


class CodebaseConfig(SQLBase):
    """SQLModel for codebase_config table in code_confluence schema."""
    __tablename__ = "codebase_config"
    __table_args__ = (
        ForeignKeyConstraint(
            ["repository_name", "repository_owner_name"],
            ["repository.repository_name", "repository.repository_owner_name"],
            ondelete="CASCADE"
        ),
    )
    
    repository_name: Mapped[str] = mapped_column(
        primary_key=True, 
        comment="The name of the repository"
    )
    repository_owner_name: Mapped[str] = mapped_column(
        primary_key=True, 
        comment="The name of the repository owner"
    )
    codebase_folder: Mapped[str] = mapped_column(
        primary_key=True, 
        comment="Path to codebase folder relative to repo root"
    )
    root_packages: Mapped[Optional[List[str]]] = mapped_column(
        JSONB,
        default=None,
        comment="List of root packages within the codebase folder"
    )
    programming_language_metadata: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        comment="Language-specific metadata for this codebase like programming language, package manager etc"
    )
    
    # Relationships
    repository: Mapped[Repository] = relationship(back_populates="configs")
    workflow_runs: Mapped[List["CodebaseWorkflowRun"]] = relationship(
        back_populates="codebase_config",
        viewonly=True,
        overlaps="repository_workflow_run,workflow_runs",
    )


class RepositoryWorkflowRun(SQLBase):
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
    
    repository_name: Mapped[str] = mapped_column(
        primary_key=True, 
        comment="The name of the repository"
    )
    repository_owner_name: Mapped[str] = mapped_column(
        primary_key=True, 
        comment="The name of the repository owner"
    )
    repository_workflow_run_id: Mapped[str] = mapped_column(
        primary_key=True, 
        comment="The run ID of the repository workflow"
    )
    repository_workflow_id: Mapped[str] = mapped_column(
        comment="The ID of the repository workflow"
    )
    status: Mapped[str] = mapped_column(
        String, 
        nullable=False,
        comment="Status of the workflow run. One of: SUBMITTED, RUNNING, FAILED, TIMED_OUT, COMPLETED, RETRYING."
    )
    error_report: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        default=None,
        comment="Error report if the workflow run failed"
    )
    issue_tracking: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        default=None,
        comment="GitHub issue tracking info for this repository workflow run"
    )
    
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False,
        comment="Timestamp when the workflow run started"
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        nullable=True,
        default=None,
        comment="Timestamp when the workflow run completed"
    )
    
    # Relationships
    repository: Mapped[Repository] = relationship(back_populates="workflow_runs")
    codebase_workflow_runs: Mapped[List["CodebaseWorkflowRun"]] = relationship(
        back_populates="repository_workflow_run",
        viewonly=True,
        overlaps="codebase_config,workflow_runs",
    )


class CodebaseWorkflowRun(SQLBase):
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
    
    repository_name: Mapped[str] = mapped_column(
        primary_key=True, 
        comment="The name of the repository"
    )
    repository_owner_name: Mapped[str] = mapped_column(
        primary_key=True, 
        comment="The name of the repository owner"
    )
    codebase_folder: Mapped[str] = mapped_column(
        primary_key=True, 
        comment="FK to codebase_config - path to codebase folder"
    )
    codebase_workflow_run_id: Mapped[str] = mapped_column(
        primary_key=True, 
        comment="Unique identifier for this specific run of the codebase workflow"
    )
    codebase_workflow_id: Mapped[str] = mapped_column(
        comment="The ID of the codebase workflow"
    )
    repository_workflow_run_id: Mapped[str] = mapped_column(
        comment="Link back to parent repository workflow run"
    )
    status: Mapped[str] = mapped_column(
        String, 
        nullable=False,
        comment="Status of the workflow run. One of: SUBMITTED, RUNNING, FAILED, TIMED_OUT, COMPLETED, RETRYING."
    )
    error_report: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        default=None,
        comment="Error report if the workflow run failed"
    )
    issue_tracking: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        default=None,
        comment="GitHub issue tracking info for this codebase workflow run"
    )
    
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False,
        comment="Timestamp when the workflow run started"
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        nullable=True,
        default=None,
        comment="Timestamp when the workflow run completed"
    )
    
    # Relationships
    codebase_config: Mapped[CodebaseConfig] = relationship(back_populates="workflow_runs")
    repository_workflow_run: Mapped[RepositoryWorkflowRun] = relationship(back_populates="codebase_workflow_runs")


class RepositoryAgentMdSnapshot(SQLBase):
    """SQLModel for repository_agent_md_snapshot table in code_confluence schema."""
    __tablename__ = "repository_agent_md_snapshot"
    __table_args__ = (
        ForeignKeyConstraint(
            ["repository_name", "repository_owner_name"],
            ["repository.repository_name", "repository.repository_owner_name"],
            ondelete="CASCADE",
        ),
    )

    repository_name: Mapped[str] = mapped_column(
        primary_key=True,
        comment="The name of the repository"
    )
    repository_owner_name: Mapped[str] = mapped_column(
        primary_key=True,
        comment="The name of the repository owner"
    )
    events: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        comment="Events and progress captured during agent execution",
    )

    agent_md_output: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        comment="Complete final payload from agent execution containing per-codebase agent data",
    )
    status: Mapped[RepoAgentSnapshotStatus] = mapped_column(
        SQLEnum(
            RepoAgentSnapshotStatus,
            name="repo_agent_snapshot_status",
            native_enum=False,
        ),
        default=RepoAgentSnapshotStatus.RUNNING,
        nullable=False,
        comment="Lifecycle status for the snapshot: RUNNING, COMPLETED, or ERROR",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        nullable=False,
        comment="Timestamp when the row was first inserted"
    )
    modified_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Timestamp when the latest overwrite occurred"
    )

    # Relationships
    repository: Mapped["Repository"] = relationship(back_populates="agent_md_snapshot")
