"""Unit tests for non-FunctionDefinition TypeScript feature extraction."""

from typing import cast

from src.code_confluence_flow_bridge.engine.programming_language.typescript.typescript_source_context import (
    TypeScriptSourceContext,
)
from src.code_confluence_flow_bridge.engine.programming_language.typescript.typescript_tree_sitter_framework_detector import (
    TypeScriptTreeSitterFrameworkDetector,
)
from unoplat_code_confluence_commons.base_models import (
    AnnotationLikeInfo,
    CallExpressionInfo,
    Concept,
    FeatureSpec,
    InheritanceInfo,
    LocatorStrategy,
    TargetLevel,
)


def _build_call_spec(
    *, feature_key: str, absolute_paths: list[str], library: str = "zustand"
) -> FeatureSpec:
    return FeatureSpec(
        feature_key=feature_key,
        library=library,
        description="Test call-expression feature",
        absolute_paths=absolute_paths,
        target_level=TargetLevel.FUNCTION,
        concept=Concept.CALL_EXPRESSION,
        locator_strategy=LocatorStrategy.VARIABLE_BOUND,
        base_confidence=0.9,
    )


def test_detector_detects_named_import_call_expression() -> None:
    source_code = """
import { createStore } from "zustand/vanilla"

const store = createStore(() => ({}))
"""

    context = TypeScriptSourceContext.from_source(source_code)
    detector = TypeScriptTreeSitterFrameworkDetector()

    detections = detector.detect(
        context,
        [
            _build_call_spec(
                feature_key="store_definition",
                absolute_paths=["zustand/vanilla.createStore"],
            )
        ],
    )

    assert len(detections) == 1
    detection = detections[0]
    call_detection = cast(CallExpressionInfo, detection)
    assert detection.feature_key == "store_definition"
    assert detection.metadata["concept"] == "CallExpression"
    assert call_detection.callee == "createStore"


def test_detector_detects_default_import_member_call_expression() -> None:
    source_code = """
import zustand from "zustand"

const store = zustand.create(() => ({}))
"""

    context = TypeScriptSourceContext.from_source(source_code)
    detector = TypeScriptTreeSitterFrameworkDetector()

    detections = detector.detect(
        context,
        [
            _build_call_spec(
                feature_key="store_definition",
                absolute_paths=["zustand.create"],
            )
        ],
    )

    assert len(detections) == 1
    call_detection = cast(CallExpressionInfo, detections[0])
    assert call_detection.callee == "zustand.create"


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
    call_detection = cast(CallExpressionInfo, detections[0])
    assert call_detection.callee == "useSWR"


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
    inheritance_detection = cast(InheritanceInfo, detections[0])
    assert inheritance_detection.subclass == "SearchWidget"
    assert inheritance_detection.superclass == "LitElement"


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
    annotation_detections = [
        cast(AnnotationLikeInfo, detection) for detection in detections
    ]
    detected_names = sorted(
        detection.annotation_name for detection in annotation_detections
    )
    assert detected_names == ["property", "state"]
