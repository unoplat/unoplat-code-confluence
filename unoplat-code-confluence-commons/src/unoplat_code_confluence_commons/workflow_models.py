"""Workflow status and error models shared across ingestion and query engine."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    """Workflow execution status values matching DB CHECK constraint."""

    SUBMITTED = "SUBMITTED"
    RUNNING = "RUNNING"
    FAILED = "FAILED"
    TIMED_OUT = "TIMED_OUT"
    COMPLETED = "COMPLETED"
    RETRYING = "RETRYING"


class ErrorReport(BaseModel):
    """Detailed error report capturing context of workflow failure."""

    error_message: str = Field(..., description="Error message")
    stack_trace: Optional[str] = Field(
        default=None, description="Stack trace of the error, if available"
    )
    metadata: Optional[dict[str, object]] = Field(
        default=None, description="Additional error metadata"
    )
