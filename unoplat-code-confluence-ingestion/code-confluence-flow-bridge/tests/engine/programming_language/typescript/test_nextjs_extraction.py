"""Unit tests for Next.js extraction in the TypeScript detector pipeline."""

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


def _build_nextjs_get_spec() -> FeatureSpec:
    return FeatureSpec(
        feature_key="http_endpoint.get",
        capability_key="http_endpoint",
        operation_key="get",
        library="nextjs",
        description="Next.js App Router GET handler",
        absolute_paths=["next/server.NextRequest", "next/server.NextResponse"],
        target_level=TargetLevel.FUNCTION,
        concept=Concept.FUNCTION_DEFINITION,
        locator_strategy=LocatorStrategy.VARIABLE_BOUND,
        construct_query={
            "function_name_regex": "^GET$",
            "export_name_regex": "^GET$",
        },
        startpoint=True,
    )


def _build_nextjs_post_spec() -> FeatureSpec:
    return FeatureSpec(
        feature_key="http_endpoint.post",
        capability_key="http_endpoint",
        operation_key="post",
        library="nextjs",
        description="Next.js App Router POST handler",
        absolute_paths=["next/server.NextRequest", "next/server.NextResponse"],
        target_level=TargetLevel.FUNCTION,
        concept=Concept.FUNCTION_DEFINITION,
        locator_strategy=LocatorStrategy.VARIABLE_BOUND,
        construct_query={
            "function_name_regex": "^POST$",
            "export_name_regex": "^POST$",
        },
        startpoint=True,
    )


def test_source_context_extracts_nextjs_import_aliases() -> None:
    source_code = """
import { NextRequest, NextResponse as Resp } from "next/server"
import type { NextFetchEvent } from "next/server"
"""

    context = TypeScriptSourceContext.from_source(source_code)

    assert len(context.imports) == 2
    assert context.import_aliases["next/server.NextRequest"] == "NextRequest"
    assert context.import_aliases["next/server.NextResponse"] == "Resp"
    assert context.import_aliases["next/server.NextFetchEvent"] == "NextFetchEvent"


def test_detector_detects_exported_get_with_next_server_import() -> None:
    source_code = """
import { NextRequest, NextResponse } from "next/server"

export async function GET(request: NextRequest) {
  return NextResponse.json({ ok: true })
}
"""

    context = TypeScriptSourceContext.from_source(source_code)
    detector = TypeScriptTreeSitterFrameworkDetector()

    detections = detector.detect(context, [_build_nextjs_get_spec()])

    assert len(detections) == 1
    detection = detections[0]
    assert detection.feature_key == "http_endpoint.get"
    assert detection.library == "nextjs"
    assert "export async function GET" in detection.match_text
    assert detection.metadata["function_name"] == "GET"
    assert detection.metadata["export_name"] == "GET"


def test_detector_skips_exported_get_without_next_server_import() -> None:
    source_code = """
export async function GET() {
  return Response.json({ ok: true })
}
"""

    context = TypeScriptSourceContext.from_source(source_code)
    detector = TypeScriptTreeSitterFrameworkDetector()

    detections = detector.detect(context, [_build_nextjs_get_spec()])

    assert detections == []


def test_detector_skips_non_http_export_name_with_import_gate() -> None:
    source_code = """
import { NextRequest, NextResponse } from "next/server"

export async function handler(request: NextRequest) {
  return NextResponse.json({ ok: true })
}
"""

    context = TypeScriptSourceContext.from_source(source_code)
    detector = TypeScriptTreeSitterFrameworkDetector()

    detections = detector.detect(context, [_build_nextjs_get_spec(), _build_nextjs_post_spec()])

    assert detections == []


def test_detector_allows_aliased_named_import_for_import_gate() -> None:
    source_code = """
import { NextResponse as Resp } from "next/server"

export function POST() {
  return Resp.json({ created: true })
}
"""

    context = TypeScriptSourceContext.from_source(source_code)
    detector = TypeScriptTreeSitterFrameworkDetector()

    detections = detector.detect(context, [_build_nextjs_post_spec()])

    assert len(detections) == 1
    assert detections[0].metadata["function_name"] == "POST"


def test_detector_namespace_import_does_not_satisfy_gate_in_v1() -> None:
    source_code = """
import * as nextServer from "next/server"

export async function GET() {
  return nextServer.NextResponse.json({ ok: true })
}
"""

    context = TypeScriptSourceContext.from_source(source_code)
    detector = TypeScriptTreeSitterFrameworkDetector()

    detections = detector.detect(context, [_build_nextjs_get_spec()])

    assert detections == []
