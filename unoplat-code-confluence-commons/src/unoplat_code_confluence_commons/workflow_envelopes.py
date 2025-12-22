"""Envelope models for workflow DB activity parameters."""

from unoplat_code_confluence_commons.configuration_models import CodebaseConfig
from unoplat_code_confluence_commons.credential_enums import ProviderKey
from unoplat_code_confluence_commons.repo_models import RepositoryWorkflowOperation
from unoplat_code_confluence_commons.workflow_models import ErrorReport

from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ParentWorkflowDbActivityEnvelope(BaseModel):
    """Envelope for parent workflow status DB updates."""

    repository_name: str = Field(..., description="The name of the repository")
    repository_owner_name: str = Field(
        ..., description="The name of the repository owner"
    )
    workflow_id: Optional[str] = Field(
        default=None, description="Temporal workflow ID"
    )
    workflow_run_id: str = Field(..., description="Unique workflow run ID")
    status: str = Field(..., description="JobStatus value")
    operation: RepositoryWorkflowOperation = Field(
        default=RepositoryWorkflowOperation.INGESTION,
        description="Operation type for this workflow run",
    )
    error_report: Optional[ErrorReport] = Field(
        default=None, description="Error details if workflow failed"
    )
    trace_id: Optional[str] = Field(
        default=None, description="Trace ID for distributed tracing"
    )
    repository_metadata: Optional[List[CodebaseConfig]] = Field(
        default=None, description="List of codebase configurations for the repository"
    )
    provider_key: ProviderKey = Field(
        default=ProviderKey.GITHUB_OPEN,
        description="Provider key for credential and repository provider lookup",
    )
    model_config = ConfigDict(extra="allow")

    @property
    def extras(self) -> dict[str, Any]:
        """Return any extra fields passed to the model (required for Temporal)."""
        return dict(self.model_extra or {})


class CodebaseWorkflowDbActivityEnvelope(BaseModel):
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
    model_config = ConfigDict(extra="allow")

    @property
    def extras(self) -> dict[str, Any]:
        """Return any extra fields passed to the model (required for Temporal)."""
        return dict(self.model_extra or {})
