"""Tests for commons engine models used by framework detection."""

from unoplat_code_confluence_commons.base_models import (
    Concept,
    ConstructQueryConfig,
    FeatureSpec,
    LocatorStrategy,
    TargetLevel,
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


def test_feature_spec_construct_query_typed_supports_new_regexes() -> None:
    spec = FeatureSpec(
        feature_key="route_handler_export",
        library="nextjs",
        absolute_paths=["next/server.NextResponse"],
        target_level=TargetLevel.FUNCTION,
        concept=Concept.FUNCTION_DEFINITION,
        locator_strategy=LocatorStrategy.DIRECT,
        construct_query={
            "function_name_regex": "^(GET|POST)$",
            "export_name_regex": "^(GET|POST)$",
        },
    )

    typed = spec.construct_query_typed
    assert typed is not None
    assert typed.function_name_regex == "^(GET|POST)$"
    assert typed.export_name_regex == "^(GET|POST)$"
