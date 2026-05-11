"""Unit tests for non-FunctionDefinition TypeScript feature extraction."""

from typing import cast

from src.code_confluence_flow_bridge.engine.programming_language.typescript.typescript_framework_query_builder import (
    TypeScriptFrameworkQueryBuilder,
)
from src.code_confluence_flow_bridge.engine.programming_language.typescript.typescript_source_context import (
    TypeScriptSourceContext,
)
from src.code_confluence_flow_bridge.engine.programming_language.typescript.typescript_tree_sitter_framework_detector import (
    TypeScriptTreeSitterFrameworkDetector,
)
import tree_sitter
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
        capability_key=feature_key,
        operation_key=feature_key,
        library=library,
        description="Test call-expression feature",
        absolute_paths=absolute_paths,
        target_level=TargetLevel.FUNCTION,
        concept=Concept.CALL_EXPRESSION,
        locator_strategy=LocatorStrategy.VARIABLE_BOUND,
        base_confidence=0.9,
    )


def _build_function_definition_spec() -> FeatureSpec:
    return FeatureSpec(
        capability_key="route",
        operation_key="handler",
        library="next",
        description="Test exported function definition feature",
        absolute_paths=["next.server.GET"],
        target_level=TargetLevel.FUNCTION,
        concept=Concept.FUNCTION_DEFINITION,
        locator_strategy=LocatorStrategy.VARIABLE_BOUND,
        construct_query={"function_name_regex": "^GET$", "export_name_regex": "^GET$"},
    )


def test_detector_detects_named_import_call_expression() -> None:
    source_code = """
import { createStore } from "zustand/vanilla"

const store = createStore(() => ({}))
"""

    context = TypeScriptSourceContext.from_bytes(source_code.encode("utf-8", errors="ignore"))
    detector = TypeScriptTreeSitterFrameworkDetector()
    spec = _build_call_spec(
        feature_key="store_definition",
        absolute_paths=["zustand/vanilla.createStore"],
    )

    detections = detector.detect(context, [spec])

    assert len(detections) == 1
    detection = detections[0]
    call_detection = cast(CallExpressionInfo, detection)
    assert detection.metadata["concept"] == "CallExpression"
    assert call_detection.callee == "createStore"
    assert detection.metadata["match_confidence"] == spec.base_confidence
    assert detection.metadata["call_match_kind"] == "symbol_exact"
    assert detection.metadata["matched_absolute_path"] == "zustand/vanilla.createStore"
    assert detection.metadata["matched_alias"] == "createStore"
    assert detection.metadata["call_match_policy_version"] == "v1_import_bound"


def test_function_definition_query_emits_single_raw_match_for_exported_function() -> (
    None
):
    source_code = """
import type { NextRequest } from "next/server"

export async function GET(_request: NextRequest): Promise<Response> {
  return Response.json({ ok: true })
}
"""

    context = TypeScriptSourceContext.from_bytes(source_code.encode("utf-8", errors="ignore"))
    query_builder = TypeScriptFrameworkQueryBuilder()
    spec = _build_function_definition_spec()

    query = query_builder.build_query(spec)
    cursor = tree_sitter.QueryCursor(query)
    matches = cursor.matches(context.root_node)

    assert len(matches) == 1
    _pattern_index, captures = matches[0]
    function_name_nodes = captures["function_name"]
    export_statement_nodes = captures["export_statement"]

    assert len(function_name_nodes) == 1
    assert len(export_statement_nodes) == 1
    function_name = context.source_bytes[
        function_name_nodes[0].start_byte : function_name_nodes[0].end_byte
    ].decode("utf-8")
    export_statement = context.source_bytes[
        export_statement_nodes[0].start_byte : export_statement_nodes[0].end_byte
    ].decode("utf-8")
    assert function_name == "GET"
    assert export_statement.lstrip().startswith("export async function GET")


def test_detector_rejects_unbound_member_collision_for_named_import() -> None:
    source_code = """
import { createStore } from "zustand/vanilla"

const api = {
  createStore: () => ({})
}

const store = api.createStore(() => ({}))
"""

    context = TypeScriptSourceContext.from_bytes(source_code.encode("utf-8", errors="ignore"))
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

    assert detections == []


def test_detector_detects_default_import_member_call_expression() -> None:
    source_code = """
import zustand from "zustand"

const store = zustand.create(() => ({}))
"""

    context = TypeScriptSourceContext.from_bytes(source_code.encode("utf-8", errors="ignore"))
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

    context = TypeScriptSourceContext.from_bytes(source_code.encode("utf-8", errors="ignore"))
    detector = TypeScriptTreeSitterFrameworkDetector()
    spec = FeatureSpec(
        capability_key="data",
        operation_key="fetch",
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
    assert call_detection.metadata["match_confidence"] == spec.base_confidence
    assert call_detection.metadata["call_match_kind"] == "default_import_exact"
    assert call_detection.metadata["matched_absolute_path"] == "swr.default"
    assert call_detection.metadata["matched_alias"] == "useSWR"
    assert call_detection.metadata["call_match_policy_version"] == "v1_import_bound"


def test_detector_detects_inheritance_for_lit_element() -> None:
    source_code = """
import { LitElement } from "lit"

class SearchWidget extends LitElement {}
"""

    context = TypeScriptSourceContext.from_bytes(source_code.encode("utf-8", errors="ignore"))
    detector = TypeScriptTreeSitterFrameworkDetector()
    spec = FeatureSpec(
        capability_key="web",
        operation_key="component",
        library="lit",
        description="LitElement inheritance",
        absolute_paths=["lit.LitElement"],
        target_level=TargetLevel.CLASS,
        concept=Concept.INHERITANCE,
        locator_strategy=LocatorStrategy.VARIABLE_BOUND,
    )

    detections = detector.detect(context, [spec])

    assert len(detections) == 1
    inheritance_detection = cast(InheritanceInfo, detections[0])
    assert inheritance_detection.subclass == "SearchWidget"
    assert inheritance_detection.superclass == "LitElement"


def test_detector_rejects_unbound_member_inheritance_for_lit_element() -> None:
    source_code = """
import { LitElement } from "lit"

class SearchWidget extends foo.LitElement {}
"""

    context = TypeScriptSourceContext.from_bytes(source_code.encode("utf-8", errors="ignore"))
    detector = TypeScriptTreeSitterFrameworkDetector()
    spec = FeatureSpec(
        capability_key="web",
        operation_key="component",
        library="lit",
        description="LitElement inheritance",
        absolute_paths=["lit.LitElement"],
        target_level=TargetLevel.CLASS,
        concept=Concept.INHERITANCE,
        locator_strategy=LocatorStrategy.VARIABLE_BOUND,
    )

    detections = detector.detect(context, [spec])

    assert detections == []


def test_detector_detects_inheritance_for_lit_element_import_alias() -> None:
    source_code = """
import { LitElement as BaseElement } from "lit"

class SearchWidget extends BaseElement {}
"""

    context = TypeScriptSourceContext.from_bytes(source_code.encode("utf-8", errors="ignore"))
    detector = TypeScriptTreeSitterFrameworkDetector()
    spec = FeatureSpec(
        capability_key="web",
        operation_key="component",
        library="lit",
        description="LitElement inheritance",
        absolute_paths=["lit.LitElement"],
        target_level=TargetLevel.CLASS,
        concept=Concept.INHERITANCE,
        locator_strategy=LocatorStrategy.VARIABLE_BOUND,
    )

    detections = detector.detect(context, [spec])

    assert len(detections) == 1
    inheritance_detection = cast(InheritanceInfo, detections[0])
    assert inheritance_detection.subclass == "SearchWidget"
    assert inheritance_detection.superclass == "BaseElement"


def test_detector_detects_lit_reactive_property_decorators() -> None:
    source_code = """
import { property, state } from "lit/decorators.js"

class SearchWidget {
  @property() query = ""
  @state() active = true
}
"""

    context = TypeScriptSourceContext.from_bytes(source_code.encode("utf-8", errors="ignore"))
    detector = TypeScriptTreeSitterFrameworkDetector()
    spec = FeatureSpec(
        capability_key="reactive",
        operation_key="property",
        library="lit",
        description="Lit decorators",
        absolute_paths=["lit/decorators.js.property", "lit/decorators.js.state"],
        target_level=TargetLevel.FUNCTION,
        concept=Concept.ANNOTATION_LIKE,
        locator_strategy=LocatorStrategy.VARIABLE_BOUND,
        construct_query={"annotation_name_regex": "^(property|state)$"},
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
