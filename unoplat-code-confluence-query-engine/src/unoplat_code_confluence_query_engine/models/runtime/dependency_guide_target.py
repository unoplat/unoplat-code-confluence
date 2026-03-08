from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class DependencyGuideTarget(BaseModel):
    """Canonical dependency documentation target used before agent fan-out."""

    name: str = Field(..., description="Canonical dependency or family name")
    source_packages: list[str] = Field(
        default_factory=list,
        description="Raw package names represented by this documentation target",
    )
    search_query: str | None = Field(
        default=None,
        description="Optional official-doc search query hint for the dependency agent",
    )

    model_config = ConfigDict(extra="forbid")


class UIDependencyFamilyMatchRule(BaseModel):
    """Single matcher rule for a configured UI component library family."""

    type: str = Field(..., description="Matcher type: exact, prefix, or regex")
    value: str = Field(..., description="Matcher value for the dependency name")

    model_config = ConfigDict(extra="forbid")


class UIDependencyFamilyRule(BaseModel):
    """Configured UI component library family that can collapse many packages."""

    id: str = Field(..., description="Stable unique identifier for the family rule")
    kind: str = Field(..., description="Family kind; currently ui_component_library")
    enabled: bool = Field(default=True, description="Whether the family rule is active")
    languages: list[str] = Field(
        default_factory=list,
        description="Optional programming language filter for this family rule",
    )
    package_managers: list[str] = Field(
        default_factory=list,
        description="Optional package-manager filter for this family rule",
    )
    display_name: str = Field(..., description="Canonical name to document")
    search_query: str | None = Field(
        default=None,
        description="Optional official-doc search query override",
    )
    match: UIDependencyFamilyMatchRule = Field(
        ..., description="Rule used to match raw dependency package names"
    )

    model_config = ConfigDict(extra="forbid")


class UIDependencyFamilyRegistry(BaseModel):
    """Registry of explicitly configured UI component library families."""

    version: int = Field(..., description="Registry schema version")
    families: list[UIDependencyFamilyRule] = Field(
        default_factory=list,
        description="Configured UI component library family rules",
    )

    model_config = ConfigDict(extra="forbid")
