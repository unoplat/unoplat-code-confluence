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


class EngineeringWorkflowConfig(BaseModel):
    """Canonical configuration inventory entry."""

    id: str = Field(
        default="",
        description="Deterministic config identifier (optional in agent output, populated in normalization)",
    )
    path: str = Field(..., description="Repo-relative path to the config file")
    purpose: str = Field(..., description="Purpose of this config file")
    required_for: List[str] = Field(
        default_factory=list,
        description="Workflows this config is required for",
    )

    model_config = ConfigDict(extra="forbid")


class EngineeringWorkflowCommand(BaseModel):
    """Canonical workflow command entry."""

    id: str = Field(
        default="",
        description="Deterministic command identifier (optional in agent output, populated in normalization)",
    )
    stage: EngineeringWorkflowStage = Field(..., description="Execution stage")
    command: str = Field(..., description="Runnable command")
    description: Optional[str] = Field(None, description="Short command description")
    config_refs: List[str] = Field(
        default_factory=list,
        description="Referenced config IDs from engineering_workflow.configs",
    )

    model_config = ConfigDict(extra="forbid")


class EngineeringWorkflow(BaseModel):
    """Canonical engineering workflow contract."""

    configs: List[EngineeringWorkflowConfig] = Field(
        default_factory=list,
        description="Canonical list of engineering configuration files",
    )
    commands: List[EngineeringWorkflowCommand] = Field(
        default_factory=list,
        description="Canonical list of engineering commands",
    )

    model_config = ConfigDict(extra="forbid")
