"""Unit tests for non-FunctionDefinition TypeScript feature extraction."""

from src.code_confluence_flow_bridge.engine.programming_language.typescript.typescript_source_context import (
    TypeScriptSourceContext,
)
from src.code_confluence_flow_bridge.engine.programming_language.typescript.typescript_tree_sitter_framework_detector import (
    TypeScriptTreeSitterFrameworkDetector,
)
from unoplat_code_confluence_commons.base_models import (
    Concept,
    FeatureSpec,
    LocatorStrategy,
    TargetLevel,
)


def _build_call_spec(*, feature_key: str, absolute_paths: list[str]) -> FeatureSpec:
    return FeatureSpec(
        feature_key=feature_key,
        library="react",
        description="Test call-expression feature",
        absolute_paths=absolute_paths,
        target_level=TargetLevel.FUNCTION,
        concept=Concept.CALL_EXPRESSION,
        locator_strategy=LocatorStrategy.VARIABLE_BOUND,
        base_confidence=0.9,
    )


def test_detector_detects_named_import_call_expression() -> None:
    source_code = """
import { useState } from "react"

const value = useState(0)
"""

    context = TypeScriptSourceContext.from_source(source_code)
    detector = TypeScriptTreeSitterFrameworkDetector()

    detections = detector.detect(
        context,
        [_build_call_spec(feature_key="state_hook", absolute_paths=["react.useState"])],
    )

    assert len(detections) == 1
    detection = detections[0]
    assert detection.feature_key == "state_hook"
    assert detection.metadata["concept"] == "CallExpression"
    assert detection.callee == "useState"


def test_detector_detects_default_import_member_call_expression() -> None:
    source_code = """
import React from "react"

const memoized = React.useMemo(() => 1, [])
"""

    context = TypeScriptSourceContext.from_source(source_code)
    detector = TypeScriptTreeSitterFrameworkDetector()

    detections = detector.detect(
        context,
        [_build_call_spec(feature_key="memo_hook", absolute_paths=["react.useMemo"])],
    )

    assert len(detections) == 1
    assert detections[0].callee == "React.useMemo"


def test_detector_detects_default_export_call_expression() -> None:
    source_code = """
import useSWR from "swr"

const result = useSWR("/api/search", fetcher)
"""

    context = TypeScriptSourceContext.from_source(source_code)
    detector = TypeScriptTreeSitterFrameworkDetector()
    spec = FeatureSpec(
        feature_key="data_fetch",
        library="swr",
        description="SWR default export hook",
        absolute_paths=["swr.default"],
        target_level=TargetLevel.FUNCTION,
        concept=Concept.CALL_EXPRESSION,
        locator_strategy=LocatorStrategy.VARIABLE_BOUND,
        base_confidence=0.9,
    )

    detections = detector.detect(context, [spec])

    assert len(detections) == 1
    assert detections[0].callee == "useSWR"


def test_detector_detects_inheritance_for_lit_element() -> None:
    source_code = """
import { LitElement } from "lit"

class SearchWidget extends LitElement {}
"""

    context = TypeScriptSourceContext.from_source(source_code)
    detector = TypeScriptTreeSitterFrameworkDetector()
    spec = FeatureSpec(
        feature_key="web_component",
        library="litellm",
        description="LitElement inheritance",
        absolute_paths=["lit.LitElement"],
        target_level=TargetLevel.CLASS,
        concept=Concept.INHERITANCE,
        locator_strategy=LocatorStrategy.VARIABLE_BOUND,
        base_confidence=0.9,
    )

    detections = detector.detect(context, [spec])

    assert len(detections) == 1
    detection = detections[0]
    assert detection.subclass == "SearchWidget"
    assert detection.superclass == "LitElement"


def test_detector_detects_lit_reactive_property_decorators() -> None:
    source_code = """
import { property, state } from "lit/decorators.js"

class SearchWidget {
  @property() query = ""
  @state() active = true
}
"""

    context = TypeScriptSourceContext.from_source(source_code)
    detector = TypeScriptTreeSitterFrameworkDetector()
    spec = FeatureSpec(
        feature_key="reactive_property",
        library="litellm",
        description="Lit decorators",
        absolute_paths=["lit/decorators.js.property", "lit/decorators.js.state"],
        target_level=TargetLevel.FUNCTION,
        concept=Concept.ANNOTATION_LIKE,
        locator_strategy=LocatorStrategy.VARIABLE_BOUND,
        construct_query={"annotation_name_regex": "^(property|state)$"},
        base_confidence=0.9,
    )

    detections = detector.detect(context, [spec])

    assert len(detections) == 2
    detected_names = sorted(d.annotation_name for d in detections)
    assert detected_names == ["property", "state"]
