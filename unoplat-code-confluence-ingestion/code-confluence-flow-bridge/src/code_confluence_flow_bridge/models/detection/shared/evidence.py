"""Shared package-manager detection evidence model."""

from pydantic import BaseModel, ConfigDict, Field


class ManagerDetectionResult(BaseModel):
    """Structured package-manager detection evidence."""

    model_config = ConfigDict(frozen=True)

    manager_name: str = Field(description="Detected package manager name.")
    evidence_type: str = Field(description="Type of evidence that matched the manager.")
    evidence_value: str = Field(description="Matched filename, glob, or field name.")
