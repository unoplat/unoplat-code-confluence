"""Canonical engineering workflow output models."""

from enum import Enum
from typing import List, Optional

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
