"""Envelope models for workflow DB activity parameters."""

from typing import Optional

from pydantic import BaseModel, Field

from unoplat_code_confluence_commons.repo_models import RepositoryWorkflowOperation
from unoplat_code_confluence_commons.workflow_models import ErrorReport


class RepositoryWorkflowDbEnvelope(BaseModel):
    """Envelope for repository workflow status DB updates."""

    repository_name: str = Field(..., description="The name of the repository")
    repository_owner_name: str = Field(
        ..., description="The name of the repository owner"
    )
    workflow_id: str = Field(..., description="Temporal workflow ID")
    workflow_run_id: str = Field(..., description="Unique workflow run ID")
    status: str = Field(..., description="JobStatus value")
    operation: RepositoryWorkflowOperation = Field(
        default=RepositoryWorkflowOperation.AGENTS_GENERATION,
        description="Operation type for this workflow run",
    )
    error_report: Optional[ErrorReport] = Field(
        default=None, description="Error details if workflow failed"
    )
    trace_id: str = Field(default="", description="Trace ID for distributed tracing")


class CodebaseWorkflowDbEnvelope(BaseModel):
    """Envelope for codebase workflow status DB updates."""

    repository_name: str = Field(..., description="The name of the repository")
    repository_owner_name: str = Field(
        ..., description="The name of the repository owner"
    )
    codebase_folder: str = Field(
        ..., description="Path to codebase folder (same as codebase_name for POC)"
    )
    repository_workflow_run_id: str = Field(
        ..., description="Parent repository workflow run ID"
    )
    codebase_workflow_id: str = Field(..., description="Temporal workflow ID")
    codebase_workflow_run_id: str = Field(..., description="Unique codebase run ID")
    status: str = Field(..., description="JobStatus value")
    error_report: Optional[ErrorReport] = Field(
        default=None, description="Error details if workflow failed"
    )
    trace_id: str = Field(default="", description="Trace ID for distributed tracing")
