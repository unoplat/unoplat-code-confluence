"""Unit tests for non-FunctionDefinition TypeScript feature extraction."""

import inspect
import re
from typing import cast

from code_confluence_flow_bridge.engine.programming_language.typescript import (
    typescript_framework_query_builder as query_builder_module,
    typescript_tree_sitter_framework_detector as detector_module,
)
from code_confluence_flow_bridge.engine.programming_language.typescript.typescript_framework_query_builder import (
    TypeScriptFrameworkQueryBuilder,
)
from code_confluence_flow_bridge.engine.programming_language.typescript.typescript_source_context import (
    TypeScriptSourceContext,
)
from code_confluence_flow_bridge.engine.programming_language.typescript.typescript_tree_sitter_framework_detector import (
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


def test_typescript_framework_detection_sources_are_library_agnostic() -> None:
    sources = {
        "query_builder": inspect.getsource(query_builder_module),
        "detector": inspect.getsource(detector_module),
    }

    for source_name, source in sources.items():
        assert "axios" not in source.lower(), source_name
        assert re.search(r"spec\.library\s*(?:==|!=)", source) is None, source_name

    fabricated_paths = re.findall(
        r'matched_absolute_path\s*=\s*["\']([^"\']*)["\']',
        sources["detector"],
    )
    assert set(fabricated_paths) <= {""}


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


def _build_axios_spec() -> FeatureSpec:
    return FeatureSpec(
        capability_key="http_client",
        operation_key="request",
        library="axios",
        description="Axios requests",
        absolute_paths=[
            "axios.default",
            "axios.create",
            "axios.request",
            "axios.get",
            "axios.delete",
            "axios.head",
            "axios.options",
            "axios.post",
            "axios.put",
            "axios.patch",
            "axios.postForm",
            "axios.putForm",
            "axios.patchForm",
            "axios.AxiosInstance",
        ],
        target_level=TargetLevel.FUNCTION,
        concept=Concept.CALL_EXPRESSION,
        locator_strategy=LocatorStrategy.DIRECT,
        construct_query={
            "match_policy": "import_guarded_regex",
            "callee_regex": r"^(?:axios(?:\.default)?|(?:[A-Za-z_$][A-Za-z0-9_$]*\.)+(?:create|request|get|delete|head|options|post|put|patch|postForm|putForm|patchForm))$",
        },
        base_confidence=0.62,
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

    context = TypeScriptSourceContext.from_bytes(
        source_code.encode("utf-8", errors="ignore")
    )
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


def test_import_guarded_regex_emits_direct_same_file_and_factory_candidates() -> None:
    source_code = """
import axios from "axios"
import { apiClient } from "./api/clients"

const localClient = axios.create({ baseURL: "/api" })

axios("/direct")
axios.get("/users")
localClient.post("/users", {})
apiClient.put("/users/1", {})
"""

    context = TypeScriptSourceContext.from_bytes(source_code.encode("utf-8"))
    spec = _build_axios_spec()
    detections = TypeScriptTreeSitterFrameworkDetector().detect(context, [spec])
    calls = [cast(CallExpressionInfo, detection) for detection in detections]

    assert {call.callee for call in calls} == {
        "axios",
        "axios.create",
        "axios.get",
        "localClient.post",
    }
    assert all(call.feature_key == "http_client.request" for call in calls)
    assert spec.base_confidence is not None and spec.base_confidence < 0.70
    assert all(
        call.metadata["call_match_policy_version"] == "v2_import_guarded_regex"
        for call in calls
    )
    assert all(call.metadata["matched_absolute_path"] == "" for call in calls)


def test_import_guarded_regex_preserves_aliased_exact_import_fallback() -> None:
    source_code = """
import http from "axios"

http({ url: "/users", method: "GET" })
"""

    context = TypeScriptSourceContext.from_bytes(source_code.encode("utf-8"))
    detections = TypeScriptTreeSitterFrameworkDetector().detect(
        context, [_build_axios_spec()]
    )

    assert len(detections) == 1
    call = cast(CallExpressionInfo, detections[0])
    assert call.callee == "http"
    assert call.metadata["call_match_kind"] == "default_import_exact"
    assert call.metadata["matched_absolute_path"] == "axios.default"
    assert call.metadata["call_match_policy_version"] == "v1_import_bound"


def test_import_guarded_regex_accepts_ambiguous_unbound_receiver_candidates() -> None:
    source_code = """
import axios from "axios"

const repository = {
  get: () => "value",
  post: () => "value",
}
repository.get()
repository.post()
"""

    context = TypeScriptSourceContext.from_bytes(source_code.encode("utf-8"))
    detections = TypeScriptTreeSitterFrameworkDetector().detect(
        context, [_build_axios_spec()]
    )

    assert {cast(CallExpressionInfo, item).callee for item in detections} == {
        "repository.get",
        "repository.post",
    }


def test_import_guarded_regex_rejects_imported_local_receiver_collision() -> None:
    source_code = """
import axios from "axios"
import { apiClient } from "./api/clients"

apiClient.get("/users")
"""

    context = TypeScriptSourceContext.from_bytes(source_code.encode("utf-8"))
    detections = TypeScriptTreeSitterFrameworkDetector().detect(
        context, [_build_axios_spec()]
    )

    assert detections == []


def test_import_guarded_regex_requires_framework_import() -> None:
    source_code = """
const localClient = { get: (path: string) => path }

localClient.get("/users")
"""

    context = TypeScriptSourceContext.from_bytes(source_code.encode("utf-8"))
    detections = TypeScriptTreeSitterFrameworkDetector().detect(
        context, [_build_axios_spec()]
    )

    assert detections == []


def test_import_guarded_regex_is_framework_agnostic() -> None:
    source_code = """
import { Session } from "exampledb"

function run(session: Session) {
  return session.execute("select 1")
}
"""
    spec = FeatureSpec(
        capability_key="relational_database",
        operation_key="execute",
        library="exampledb",
        description="Generic receiver execution",
        absolute_paths=["exampledb.Session"],
        target_level=TargetLevel.FUNCTION,
        concept=Concept.CALL_EXPRESSION,
        locator_strategy=LocatorStrategy.DIRECT,
        construct_query={
            "match_policy": "import_guarded_regex",
            "callee_regex": r"^(?:[A-Za-z_$][A-Za-z0-9_$]*\.)+execute$",
        },
        base_confidence=0.5,
    )

    context = TypeScriptSourceContext.from_bytes(source_code.encode("utf-8"))
    detections = TypeScriptTreeSitterFrameworkDetector().detect(context, [spec])

    assert len(detections) == 1
    call = cast(CallExpressionInfo, detections[0])
    assert call.callee == "session.execute"
    assert call.metadata["call_match_kind"] == "import_guarded_regex"
    assert call.metadata["matched_absolute_path"] == ""


def test_detector_detects_react_db_live_query_hooks() -> None:
    source_code = """
import {
  useLiveQuery,
  useLiveInfiniteQuery as useInfinite,
} from "@tanstack/react-db"

const users = useLiveQuery((query) => query.from({ users }))
const pages = useInfinite((query) => query.from({ users }), { pageSize: 20 })
"""
    specs = [
        FeatureSpec(
            capability_key="realtime_sync",
            operation_key="live_query",
            library="@tanstack/react-db",
            description="Live query",
            absolute_paths=["@tanstack/react-db.useLiveQuery"],
            target_level=TargetLevel.FUNCTION,
            concept=Concept.CALL_EXPRESSION,
            locator_strategy=LocatorStrategy.DIRECT,
            base_confidence=0.98,
        ),
        FeatureSpec(
            capability_key="realtime_sync",
            operation_key="live_infinite_query",
            library="@tanstack/react-db",
            description="Infinite live query",
            absolute_paths=["@tanstack/react-db.useLiveInfiniteQuery"],
            target_level=TargetLevel.FUNCTION,
            concept=Concept.CALL_EXPRESSION,
            locator_strategy=LocatorStrategy.DIRECT,
            base_confidence=0.98,
        ),
    ]

    context = TypeScriptSourceContext.from_bytes(source_code.encode("utf-8"))
    detections = TypeScriptTreeSitterFrameworkDetector().detect(context, specs)

    assert {
        (d.feature_key, cast(CallExpressionInfo, d).callee) for d in detections
    } == {
        ("realtime_sync.live_query", "useLiveQuery"),
        ("realtime_sync.live_infinite_query", "useInfinite"),
    }


def test_function_definition_query_emits_single_raw_match_for_exported_function() -> (
    None
):
    source_code = """
import type { NextRequest } from "next/server"

export async function GET(_request: NextRequest): Promise<Response> {
  return Response.json({ ok: true })
}
"""

    context = TypeScriptSourceContext.from_bytes(
        source_code.encode("utf-8", errors="ignore")
    )
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

    context = TypeScriptSourceContext.from_bytes(
        source_code.encode("utf-8", errors="ignore")
    )
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

    context = TypeScriptSourceContext.from_bytes(
        source_code.encode("utf-8", errors="ignore")
    )
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

    context = TypeScriptSourceContext.from_bytes(
        source_code.encode("utf-8", errors="ignore")
    )
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

    context = TypeScriptSourceContext.from_bytes(
        source_code.encode("utf-8", errors="ignore")
    )
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

    context = TypeScriptSourceContext.from_bytes(
        source_code.encode("utf-8", errors="ignore")
    )
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

    context = TypeScriptSourceContext.from_bytes(
        source_code.encode("utf-8", errors="ignore")
    )
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

    context = TypeScriptSourceContext.from_bytes(
        source_code.encode("utf-8", errors="ignore")
    )
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
