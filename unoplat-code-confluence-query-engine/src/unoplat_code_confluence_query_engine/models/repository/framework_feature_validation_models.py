from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator
from unoplat_code_confluence_commons.base_models import Concept, ValidationStatus


class FrameworkFeatureIdentity(BaseModel):
    """Catalog identity for one framework feature, independent of a usage span."""

    feature_language: str
    feature_library: str
    feature_capability_key: str
    feature_operation_key: str

    model_config = ConfigDict(frozen=True)

    @property
    def feature_key(self) -> str:
        """Display-only dotted convenience key."""
        return f"{self.feature_capability_key}.{self.feature_operation_key}"


class FrameworkFeatureUsageIdentity(FrameworkFeatureIdentity):
    """Primary-key identity for code_confluence_file_framework_feature rows."""

    file_path: str
    start_line: int = Field(ge=1)
    end_line: int = Field(ge=1)

    @model_validator(mode="after")
    def validate_line_span(self) -> FrameworkFeatureUsageIdentity:
        if self.end_line < self.start_line:
            raise ValueError("end_line must be greater than or equal to start_line")
        return self


class CallExpressionFeatureDefinition(BaseModel):
    """Catalog metadata supplied to one operation-scoped discoverer run."""

    concept: Concept
    description: str
    base_confidence: float = Field(ge=0.0, le=1.0)
    notes: str | None = None
    construct_query: dict[str, object] | None = None


class CallExpressionDiscoveryExistingSpan(BaseModel):
    """An existing usage row supplied only as a discoverer hint."""

    model_config = ConfigDict(from_attributes=True)

    file_path: str
    start_line: int = Field(ge=1)
    end_line: int = Field(ge=1)
    match_text: str | None = None
    match_confidence: float = Field(ge=0.0, le=1.0)
    validation_status: ValidationStatus


class CallExpressionDiscoveryOperation(BaseModel):
    """One catalog operation and optional codebase usage hints."""

    feature_operation_key: str
    definition: CallExpressionFeatureDefinition
    absolute_paths: list[str] = Field(default_factory=list)
    existing_spans: list[CallExpressionDiscoveryExistingSpan] = Field(
        default_factory=list
    )


class CallExpressionDiscoveryTarget(BaseModel):
    """Operations under one evidenced framework capability."""

    feature_language: str
    feature_library: str
    feature_capability_key: str
    operations: list[CallExpressionDiscoveryOperation] = Field(min_length=1)


class DiscoveredFrameworkFeatureUsageSpan(BaseModel):
    """Verified source span discovered for an existing framework feature."""

    file_path: str = Field(min_length=1)
    start_line: int = Field(ge=1)
    end_line: int = Field(ge=1)
    match_text: str = Field(min_length=1)
    final_confidence: float = Field(ge=0.0, le=1.0)

    @model_validator(mode="after")
    def validate_line_span(self) -> DiscoveredFrameworkFeatureUsageSpan:
        if self.end_line < self.start_line:
            raise ValueError("end_line must be greater than or equal to start_line")
        return self


class DiscoveredFrameworkFeatureUsagesUpsertRequest(BaseModel):
    """Batch of verified spans for one authorized catalog framework feature."""

    target_feature_identity: FrameworkFeatureIdentity
    usages: list[DiscoveredFrameworkFeatureUsageSpan] = Field(min_length=1)


class DiscoveredFrameworkFeatureUsagesUpsertResult(BaseModel):
    """Created and updated rows produced by a discovered-usage upsert."""

    created_count: int = Field(default=0, ge=0)
    updated_count: int = Field(default=0, ge=0)
