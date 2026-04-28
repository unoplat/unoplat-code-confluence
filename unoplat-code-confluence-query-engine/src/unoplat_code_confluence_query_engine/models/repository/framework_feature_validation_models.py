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
    feature_capability_key: str
    feature_operation_key: str
    start_line: int = Field(ge=1)
    end_line: int = Field(ge=1)

    model_config = ConfigDict(frozen=True)

    @property
    def feature_key(self) -> str:
        """Display-only dotted convenience key."""
        return f"{self.feature_capability_key}.{self.feature_operation_key}"

    @model_validator(mode="after")
    def validate_line_span(self) -> FrameworkFeatureUsageIdentity:
        if self.end_line < self.start_line:
            raise ValueError("end_line must be greater than or equal to start_line")
        return self

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

    def with_location_corrections(
        self,
        *,
        file_path: str | None = None,
        start_line: int | None = None,
        end_line: int | None = None,
    ) -> FrameworkFeatureUsageIdentity:
        """Return a copy with corrected location fields."""
        return self.model_copy(
            update={
                "file_path": file_path or self.file_path,
                "start_line": start_line if start_line is not None else self.start_line,
                "end_line": end_line if end_line is not None else self.end_line,
            }
        )


def _has_location_update(
    corrected_file_path: str | None,
    corrected_start_line: int | None,
    corrected_end_line: int | None,
) -> bool:
    return (
        corrected_file_path is not None
        or corrected_start_line is not None
        or corrected_end_line is not None
    )


def _has_any_update_fields(
    *,
    corrected_file_path: str | None,
    corrected_start_line: int | None,
    corrected_end_line: int | None,
    corrected_match_text: str | None,
) -> bool:
    return (
        _has_location_update(
            corrected_file_path,
            corrected_start_line,
            corrected_end_line,
        )
        or corrected_match_text is not None
    )


def _build_updated_identity(
    *,
    identity: FrameworkFeatureUsageIdentity,
    corrected_file_path: str | None,
    corrected_start_line: int | None,
    corrected_end_line: int | None,
) -> FrameworkFeatureUsageIdentity:
    return identity.with_location_corrections(
        file_path=corrected_file_path,
        start_line=corrected_start_line,
        end_line=corrected_end_line,
    )


def _validate_update_contract(
    *,
    decision: FrameworkFeatureValidationDecision,
    identity: FrameworkFeatureUsageIdentity,
    corrected_file_path: str | None,
    corrected_start_line: int | None,
    corrected_end_line: int | None,
    corrected_match_text: str | None,
) -> None:
    has_any_update_fields = _has_any_update_fields(
        corrected_file_path=corrected_file_path,
        corrected_start_line=corrected_start_line,
        corrected_end_line=corrected_end_line,
        corrected_match_text=corrected_match_text,
    )

    if decision != FrameworkFeatureValidationDecision.CORRECT:
        if has_any_update_fields:
            raise ValueError(
                "corrected_* fields are only allowed when decision='correct'"
            )
        return

    if not has_any_update_fields:
        raise ValueError(
            "decision='correct' requires corrected file_path/start_line/end_line "
            "and/or corrected_match_text"
        )

    updated_identity = _build_updated_identity(
        identity=identity,
        corrected_file_path=corrected_file_path,
        corrected_start_line=corrected_start_line,
        corrected_end_line=corrected_end_line,
    )

    if corrected_match_text is None and updated_identity == identity:
        raise ValueError(
            "Corrected location must differ from identity fields when corrected_match_text is not provided"
        )


class FrameworkFeatureValidationEvidenceUpsertRequest(BaseModel):
    """Repository input for evidence/confidence upsert operation."""

    identity: FrameworkFeatureUsageIdentity
    decision: FrameworkFeatureValidationDecision
    final_confidence: float = Field(ge=0.0, le=1.0)
    evidence_json: dict[str, object] = Field(default_factory=dict)
    corrected_file_path: str | None = None
    corrected_start_line: int | None = Field(default=None, ge=1)
    corrected_end_line: int | None = Field(default=None, ge=1)
    corrected_match_text: str | None = None

    @model_validator(mode="after")
    def validate_correct_decision_fields(
        self,
    ) -> FrameworkFeatureValidationEvidenceUpsertRequest:
        _validate_update_contract(
            decision=self.decision,
            identity=self.identity,
            corrected_file_path=self.corrected_file_path,
            corrected_start_line=self.corrected_start_line,
            corrected_end_line=self.corrected_end_line,
            corrected_match_text=self.corrected_match_text,
        )
        return self

    def build_updated_identity(self) -> FrameworkFeatureUsageIdentity:
        """Return the row identity after applying any location corrections."""
        return _build_updated_identity(
            identity=self.identity,
            corrected_file_path=self.corrected_file_path,
            corrected_start_line=self.corrected_start_line,
            corrected_end_line=self.corrected_end_line,
        )


class FrameworkFeatureValidationEvidenceUpsertResult(BaseModel):
    """Result summary for evidence/confidence upsert operations."""

    source_row_updated: bool
    current_identity: FrameworkFeatureUsageIdentity


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
    corrected_file_path: str | None = None
    corrected_start_line: int | None = Field(default=None, ge=1)
    corrected_end_line: int | None = Field(default=None, ge=1)
    corrected_match_text: str | None = None
    summary: str

    @model_validator(mode="after")
    def validate_decision_contract(self) -> CallExpressionValidationAgentOutput:
        _validate_update_contract(
            decision=self.decision,
            identity=self.identity,
            corrected_file_path=self.corrected_file_path,
            corrected_start_line=self.corrected_start_line,
            corrected_end_line=self.corrected_end_line,
            corrected_match_text=self.corrected_match_text,
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
