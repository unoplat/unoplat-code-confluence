from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, model_validator
from unoplat_code_confluence_commons.base_models import ValidationStatus


class FrameworkFeatureValidationDecision(str, Enum):
    """Allowed validator decisions for low-confidence framework usage rows."""

    CONFIRM = "confirm"
    REJECT = "reject"
    CORRECT = "correct"
    NEEDS_REVIEW = "needs_review"


class FrameworkFeatureUsageIdentity(BaseModel):
    """Primary-key identity for code_confluence_file_framework_feature rows."""

    file_path: str
    feature_language: str
    feature_library: str
<<<<<<< HEAD
    feature_capability_key: str
    feature_operation_key: str
=======
    feature_key: str
>>>>>>> origin/main
    start_line: int = Field(ge=1)
    end_line: int = Field(ge=1)

    model_config = ConfigDict(frozen=True)

<<<<<<< HEAD
    @property
    def feature_key(self) -> str:
        """Display-only dotted convenience key."""
        return f"{self.feature_capability_key}.{self.feature_operation_key}"

=======
>>>>>>> origin/main
    @model_validator(mode="after")
    def validate_line_span(self) -> FrameworkFeatureUsageIdentity:
        if self.end_line < self.start_line:
            raise ValueError("end_line must be greater than or equal to start_line")
        return self

<<<<<<< HEAD
    def with_feature_identity(
        self,
        feature_capability_key: str,
        feature_operation_key: str,
    ) -> FrameworkFeatureUsageIdentity:
        """Return a copy with a different structured feature identity."""
        return self.model_copy(
            update={
                "feature_capability_key": feature_capability_key,
                "feature_operation_key": feature_operation_key,
            }
        )
=======
    def with_feature_key(self, feature_key: str) -> FrameworkFeatureUsageIdentity:
        """Return a copy with a different feature key."""
        return self.model_copy(update={"feature_key": feature_key})
>>>>>>> origin/main


class FrameworkFeatureValidationEvidenceUpsertRequest(BaseModel):
    """Repository input for evidence/confidence upsert operation."""

    identity: FrameworkFeatureUsageIdentity
    decision: FrameworkFeatureValidationDecision
    final_confidence: float = Field(ge=0.0, le=1.0)
    evidence_json: dict[str, object] = Field(default_factory=dict)
<<<<<<< HEAD
    updated_feature_capability_key: str | None = None
    updated_feature_operation_key: str | None = None
=======
    updated_feature_key: str | None = None
>>>>>>> origin/main

    @model_validator(mode="after")
    def validate_correct_decision_fields(
        self,
    ) -> FrameworkFeatureValidationEvidenceUpsertRequest:
        if self.decision == FrameworkFeatureValidationDecision.CORRECT:
<<<<<<< HEAD
            if not self.updated_feature_capability_key:
                raise ValueError(
                    "updated_feature_capability_key is required when decision='correct'"
                )
            if not self.updated_feature_operation_key:
                raise ValueError(
                    "updated_feature_operation_key is required when decision='correct'"
                )
            if (
                self.updated_feature_capability_key
                == self.identity.feature_capability_key
                and self.updated_feature_operation_key
                == self.identity.feature_operation_key
            ):
                raise ValueError(
                    "Updated structured feature identity must differ from identity fields"
=======
            if not self.updated_feature_key:
                raise ValueError(
                    "updated_feature_key is required when decision='correct'"
                )
            if self.updated_feature_key == self.identity.feature_key:
                raise ValueError(
                    "updated_feature_key must differ from identity.feature_key"
>>>>>>> origin/main
                )
        return self


class FrameworkFeatureValidationEvidenceUpsertResult(BaseModel):
    """Result summary for evidence/confidence upsert operations."""

    source_row_updated: bool
    corrected_row_upserted: bool
    corrected_identity: FrameworkFeatureUsageIdentity | None = None


class FrameworkFeatureValidationStatusTransitionRequest(BaseModel):
    """Repository input for status-only transition operation."""

    identity: FrameworkFeatureUsageIdentity
    target_status: ValidationStatus
    expected_current_status: ValidationStatus | None = None


class FrameworkFeatureValidationStatusTransitionResult(BaseModel):
    """Result summary for status transition operations."""

    status: str
    previous_status: ValidationStatus
    current_status: ValidationStatus


class FrameworkFeatureValidationCandidate(BaseModel):
    """Low-confidence CallExpression usage candidate for validator execution."""

    identity: FrameworkFeatureUsageIdentity
    concept: str
    match_confidence: float = Field(ge=0.0, le=1.0)
    validation_status: ValidationStatus
    match_text: str | None = None
    evidence_json: dict[str, object] | None = None
    base_confidence: float = Field(ge=0.0, le=1.0)
    notes: str | None = None
    construct_query: dict[str, object] | None = None
    absolute_paths: list[str] = Field(default_factory=list)


class CallExpressionValidationAgentOutput(BaseModel):
    """Structured validator-agent summary for one candidate decision run."""

    identity: FrameworkFeatureUsageIdentity
    decision: FrameworkFeatureValidationDecision
    final_confidence: float = Field(ge=0.0, le=1.0)
    target_status: ValidationStatus
<<<<<<< HEAD
    updated_feature_capability_key: str | None = None
    updated_feature_operation_key: str | None = None
=======
    updated_feature_key: str | None = None
>>>>>>> origin/main
    summary: str

    @model_validator(mode="after")
    def validate_decision_contract(self) -> CallExpressionValidationAgentOutput:
        if self.decision == FrameworkFeatureValidationDecision.CORRECT:
<<<<<<< HEAD
            if not self.updated_feature_capability_key:
                raise ValueError(
                    "updated_feature_capability_key is required when decision='correct'"
                )
            if not self.updated_feature_operation_key:
                raise ValueError(
                    "updated_feature_operation_key is required when decision='correct'"
                )
            if (
                self.updated_feature_capability_key
                == self.identity.feature_capability_key
                and self.updated_feature_operation_key
                == self.identity.feature_operation_key
            ):
                raise ValueError(
                    "Updated structured feature identity must differ from identity fields"
=======
            if not self.updated_feature_key:
                raise ValueError(
                    "updated_feature_key is required when decision='correct'"
                )
            if self.updated_feature_key == self.identity.feature_key:
                raise ValueError(
                    "updated_feature_key must differ from identity.feature_key"
>>>>>>> origin/main
                )

        if self.decision == FrameworkFeatureValidationDecision.NEEDS_REVIEW:
            if self.target_status != ValidationStatus.NEEDS_REVIEW:
                raise ValueError(
                    "target_status must be 'needs_review' when decision='needs_review'"
                )
        elif self.target_status != ValidationStatus.COMPLETED:
            raise ValueError(
                "target_status must be 'completed' for confirm/reject/correct decisions"
            )

        return self
