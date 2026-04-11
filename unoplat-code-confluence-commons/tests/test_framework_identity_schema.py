"""Tests for structured framework feature identity in commons ORM models."""

from unoplat_code_confluence_commons.base_models import FeatureAbsolutePath, FrameworkFeature
from unoplat_code_confluence_commons.relational_models import (
    UnoplatCodeConfluenceFileFrameworkFeature,
)


def test_framework_feature_primary_key_uses_structured_identity() -> None:
    assert list(FrameworkFeature.__table__.primary_key.columns.keys()) == [
        "language",
        "library",
        "capability_key",
        "operation_key",
    ]


def test_feature_absolute_path_foreign_key_uses_structured_identity() -> None:
    assert list(FeatureAbsolutePath.__table__.primary_key.columns.keys()) == [
        "language",
        "library",
        "capability_key",
        "operation_key",
        "absolute_path",
    ]

    foreign_key_constraint = next(
        constraint
        for constraint in FeatureAbsolutePath.__table__.foreign_key_constraints
        if {element.parent.name for element in constraint.elements}
        == {"language", "library", "capability_key", "operation_key"}
    )

    assert [element.parent.name for element in foreign_key_constraint.elements] == [
        "language",
        "library",
        "capability_key",
        "operation_key",
    ]
    assert [element.target_fullname for element in foreign_key_constraint.elements] == [
        "framework_feature.language",
        "framework_feature.library",
        "framework_feature.capability_key",
        "framework_feature.operation_key",
    ]


def test_file_framework_feature_foreign_key_uses_structured_identity() -> None:
    assert list(
        UnoplatCodeConfluenceFileFrameworkFeature.__table__.primary_key.columns.keys()
    ) == [
        "file_path",
        "feature_language",
        "feature_library",
        "feature_capability_key",
        "feature_operation_key",
        "start_line",
        "end_line",
    ]

    foreign_key_constraint = next(
        constraint
        for constraint in (
            UnoplatCodeConfluenceFileFrameworkFeature.__table__.foreign_key_constraints
        )
        if {element.parent.name for element in constraint.elements}
        == {
            "feature_language",
            "feature_library",
            "feature_capability_key",
            "feature_operation_key",
        }
    )

    assert [element.parent.name for element in foreign_key_constraint.elements] == [
        "feature_language",
        "feature_library",
        "feature_capability_key",
        "feature_operation_key",
    ]
    assert [element.target_fullname for element in foreign_key_constraint.elements] == [
        "framework_feature.language",
        "framework_feature.library",
        "framework_feature.capability_key",
        "framework_feature.operation_key",
    ]


def test_feature_key_properties_are_computed_only_convenience() -> None:
    framework_feature = FrameworkFeature(
        language="python",
        library="fastapi",
        capability_key="rest_api",
        operation_key="get",
        feature_definition={
            "target_level": "function",
            "concept": "AnnotationLike",
            "locator_strategy": "VariableBound",
            "startpoint": False,
        },
    )
    absolute_path = FeatureAbsolutePath(
        language="python",
        library="fastapi",
        capability_key="rest_api",
        operation_key="get",
        absolute_path="fastapi.FastAPI",
    )
    usage = UnoplatCodeConfluenceFileFrameworkFeature(
        file_path="app/routes.py",
        feature_language="python",
        feature_library="fastapi",
        feature_capability_key="rest_api",
        feature_operation_key="get",
        start_line=10,
        end_line=10,
    )

    assert framework_feature.feature_key == "rest_api.get"
    assert absolute_path.feature_key == "rest_api.get"
    assert usage.feature_key == "rest_api.get"
