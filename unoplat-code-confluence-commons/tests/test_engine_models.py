"""Tests for commons engine models used by framework detection."""

from pydantic import ValidationError
from unoplat_code_confluence_commons.base_models import (
    CallExpressionMatchPolicy,
    Concept,
    ConstructQueryConfig,
    Detection,
    FeatureSpec,
    FeatureUsagePayload,
    LocatorStrategy,
    TargetLevel,
    ValidationStatus,
)


def test_concept_includes_function_definition() -> None:
    assert Concept.FUNCTION_DEFINITION.value == "FunctionDefinition"


def test_construct_query_config_accepts_function_export_regex_keys() -> None:
    config = ConstructQueryConfig.model_validate(
        {
            "function_name_regex": "^(GET|POST)$",
            "export_name_regex": "^(GET|POST)$",
        }
    )

    assert config.function_name_regex == "^(GET|POST)$"
    assert config.export_name_regex == "^(GET|POST)$"


def test_construct_query_config_defaults_to_match_callee_policy() -> None:
    config = ConstructQueryConfig.model_validate({})

    assert config.match_policy == CallExpressionMatchPolicy.MATCH_CALLEE


def test_construct_query_config_accepts_import_guarded_regex_policy() -> None:
    config = ConstructQueryConfig.model_validate(
        {"match_policy": "import_guarded_regex", "callee_regex": r"\\.execute$"}
    )

    assert config.match_policy == CallExpressionMatchPolicy.IMPORT_GUARDED_REGEX


def test_construct_query_config_rejects_invalid_match_policy() -> None:
    try:
        ConstructQueryConfig.model_validate({"match_policy": "receiver_inference"})
    except ValidationError as exc:
        assert "match_policy" in str(exc)
    else:
        raise AssertionError("Expected invalid match_policy to fail")


def test_import_guarded_regex_policy_requires_callee_regex() -> None:
    try:
        ConstructQueryConfig.model_validate(
            {"match_policy": "import_guarded_regex"}
        )
    except ValidationError as exc:
        assert "requires a non-empty callee_regex" in str(exc)
    else:
        raise AssertionError("Expected missing callee_regex to fail")


def test_import_guarded_regex_policy_rejects_blank_callee_regex() -> None:
    try:
        ConstructQueryConfig.model_validate(
            {"match_policy": "import_guarded_regex", "callee_regex": "   "}
        )
    except ValidationError as exc:
        assert "requires a non-empty callee_regex" in str(exc)
    else:
        raise AssertionError("Expected blank callee_regex to fail")


def test_feature_spec_rejects_match_policy_for_non_call_expression() -> None:
    try:
        FeatureSpec(
            capability_key="rest_api",
            operation_key="route_handler_export",
            library="nextjs",
            absolute_paths=["next/server.NextResponse"],
            target_level=TargetLevel.FUNCTION,
            concept=Concept.FUNCTION_DEFINITION,
            locator_strategy=LocatorStrategy.DIRECT,
            construct_query={"match_policy": "match_callee"},
        )
    except ValidationError as exc:
        assert "supported only for CallExpression" in str(exc)
    else:
        raise AssertionError("Expected non-CallExpression match_policy to fail")


def test_feature_spec_construct_query_typed_supports_new_regexes() -> None:
    spec = FeatureSpec(
        capability_key="rest_api",
        operation_key="route_handler_export",
        library="nextjs",
        absolute_paths=["next/server.NextResponse"],
        target_level=TargetLevel.FUNCTION,
        concept=Concept.FUNCTION_DEFINITION,
        locator_strategy=LocatorStrategy.DIRECT,
        description="Route handler export",
        construct_query={
            "function_name_regex": "^(GET|POST)$",
            "export_name_regex": "^(GET|POST)$",
        },
    )

    typed = spec.construct_query_typed
    assert typed is not None
    assert typed.function_name_regex == "^(GET|POST)$"
    assert typed.export_name_regex == "^(GET|POST)$"
    assert spec.feature_key == "rest_api.route_handler_export"


def test_feature_spec_requires_base_confidence_for_call_expression() -> None:
    try:
        FeatureSpec(
            capability_key="relational_database",
            operation_key="relationship",
            library="sqlalchemy",
            absolute_paths=["sqlalchemy.orm.relationship"],
            target_level=TargetLevel.FUNCTION,
            concept=Concept.CALL_EXPRESSION,
            locator_strategy=LocatorStrategy.VARIABLE_BOUND,
            description="Relationship call",
        )
    except ValidationError as exc:
        assert "must define base_confidence" in str(exc)
    else:
        raise AssertionError("Expected CallExpression without base_confidence to fail")


def test_feature_spec_rejects_base_confidence_for_non_call_expression() -> None:
    try:
        FeatureSpec(
            capability_key="rest_api",
            operation_key="http_endpoint",
            library="fastapi",
            absolute_paths=["fastapi.FastAPI"],
            target_level=TargetLevel.FUNCTION,
            concept=Concept.ANNOTATION_LIKE,
            locator_strategy=LocatorStrategy.VARIABLE_BOUND,
            description="FastAPI route",
            base_confidence=0.85,
        )
    except ValidationError as exc:
        assert "only for CallExpression" in str(exc)
    else:
        raise AssertionError("Expected non-CallExpression base_confidence to fail")


def test_feature_spec_accepts_base_confidence_for_call_expression() -> None:
    spec = FeatureSpec(
        capability_key="relational_database",
        operation_key="relationship",
        library="sqlalchemy",
        absolute_paths=["sqlalchemy.orm.relationship"],
        target_level=TargetLevel.FUNCTION,
        concept=Concept.CALL_EXPRESSION,
        locator_strategy=LocatorStrategy.VARIABLE_BOUND,
        description="Relationship call",
        base_confidence=0.61,
    )

    assert spec.base_confidence == 0.61
    assert spec.feature_key == "relational_database.relationship"


def test_feature_usage_payload_defaults() -> None:
    payload = FeatureUsagePayload.model_validate({})

    assert payload.match_confidence == 1.0
    assert payload.validation_status == ValidationStatus.COMPLETED
    assert payload.evidence_json is None


def test_feature_usage_payload_accepts_completed_status() -> None:
    payload = FeatureUsagePayload.model_validate(
        {
            "match_confidence": 0.64,
            "validation_status": "completed",
            "evidence_json": {"decision": "confirm"},
        }
    )

    assert payload.match_confidence == 0.64
    assert payload.validation_status == ValidationStatus.COMPLETED
    assert payload.evidence_json == {"decision": "confirm"}


def test_detection_feature_key_is_computed_from_structured_identity() -> None:
    detection = Detection(
        capability_key="rest_api",
        operation_key="get",
        library="fastapi",
        match_text="@app.get('/items')",
        start_line=10,
        end_line=10,
    )

    assert detection.feature_key == "rest_api.get"
