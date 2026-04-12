from __future__ import annotations

from src.code_confluence_flow_bridge.parser.code_confluence_codebase_parser import (
    _resolve_match_confidence,
    _resolve_validation_status,
)
from unoplat_code_confluence_commons.base_models import (
    CallExpressionInfo,
    InheritanceInfo,
    ValidationStatus,
)


def test_resolve_validation_status_marks_low_confidence_call_expression_pending() -> (
    None
):
    detection = CallExpressionInfo(
        capability_key="http_client",
        operation_key="request",
        library="httpx",
        match_text="client.get('/health')",
        start_line=8,
        end_line=8,
        callee="client.get",
        args_text="('/health')",
        metadata={"match_confidence": 0.55},
    )

    match_confidence = _resolve_match_confidence(detection)
    status = _resolve_validation_status(detection, match_confidence=match_confidence)

    assert match_confidence == 0.55
    assert status == ValidationStatus.PENDING.value


def test_resolve_validation_status_marks_non_call_expression_completed() -> None:
    detection = InheritanceInfo(
        capability_key="data_model",
        operation_key="data_model",
        library="pydantic",
        match_text="class User(BaseModel)",
        start_line=3,
        end_line=10,
        subclass="User",
        superclass="BaseModel",
        metadata={"match_confidence": 0.2},
    )

    match_confidence = _resolve_match_confidence(detection)
    status = _resolve_validation_status(detection, match_confidence=match_confidence)

    assert match_confidence == 0.2
    assert status == ValidationStatus.COMPLETED.value


def test_resolve_validation_status_marks_high_confidence_call_expression_completed() -> (
    None
):
    detection = CallExpressionInfo(
        capability_key="llm_inference",
        operation_key="llm_completion",
        library="litellm",
        match_text="completion(model='gpt-4o-mini')",
        start_line=11,
        end_line=11,
        callee="completion",
        args_text="(model='gpt-4o-mini')",
        metadata={"match_confidence": 0.93},
    )

    match_confidence = _resolve_match_confidence(detection)
    status = _resolve_validation_status(detection, match_confidence=match_confidence)

    assert match_confidence == 0.93
    assert status == ValidationStatus.COMPLETED.value
