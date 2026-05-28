"""Canonical engineering workflow output models."""

from enum import Enum
from typing import List, Literal, Optional, TypeAlias

from pydantic import BaseModel, ConfigDict, Field


class EngineeringWorkflowStage(str, Enum):
    """Execution stage for engineering commands."""

    INSTALL = "install"
    BUILD = "build"
    DEV = "dev"
    TEST = "test"
    LINT = "lint"
    TYPE_CHECK = "type_check"


class EngineeringWorkflowCommand(BaseModel):
    """Canonical workflow command entry."""

    command: str = Field(..., description="Runnable command")
    stage: EngineeringWorkflowStage = Field(..., description="Execution stage")
    config_file: str = Field(
        ..., description="Repository-root-relative path to the most relevant config file, or 'unknown'"
    )
    working_directory: Optional[str] = Field(
        default=None,
        description=(
            "Repository-root-relative directory from which command should execute. "
            "None/omitted = codebase root, '.' = repository root, "
            "nested path = specific workspace root."
        ),
    )

    model_config = ConfigDict(extra="forbid")


class EngineeringWorkflow(BaseModel):
    """Canonical engineering workflow contract."""

    commands: List[EngineeringWorkflowCommand] = Field(
        default_factory=list,
        description="Canonical list of engineering commands",
    )

    model_config = ConfigDict(extra="forbid")


ENGINEERING_WORKFLOW_FULL_OUTPUT = "full_output"
"""Agent response status indicating commands are present and should be persisted."""

ENGINEERING_WORKFLOW_NO_CHANGE = "no_change"
"""Agent response status indicating previous structured workflow should be carried forward."""

EngineeringWorkflowAgentStatus: TypeAlias = Literal["full_output", "no_change"]
"""Allowed development workflow agent response statuses."""


class EngineeringWorkflowAgentResponse(BaseModel):
    """Single-model response contract for development_workflow_guide."""

    status: EngineeringWorkflowAgentStatus = Field(
        ...,
        description=(
            "full_output when commands are included for persistence; "
            "no_change only when prior structured workflow may be carried forward"
        ),
    )
    commands: Optional[List[EngineeringWorkflowCommand]] = Field(
        default=None,
        description=(
            "Required and non-empty for status=full_output. Must be omitted/null "
            "for status=no_change."
        ),
    )

    model_config = ConfigDict(extra="forbid")


EngineeringWorkflowAgentOutput: TypeAlias = EngineeringWorkflowAgentResponse
"""Development workflow agent output: single explicit response model."""
