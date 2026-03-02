"""Tree-sitter based TypeScript framework detector for FunctionDefinition detection."""

from __future__ import annotations

from typing import Dict, List, Optional, Set, Tuple

from loguru import logger
import tree_sitter
from unoplat_code_confluence_commons.base_models import (
    Concept,
    Detection,
    FeatureSpec,
)

from src.code_confluence_flow_bridge.engine.programming_language.typescript.typescript_framework_query_builder import (
    TypeScriptFrameworkQueryBuilder,
)
from src.code_confluence_flow_bridge.engine.programming_language.typescript.typescript_source_context import (
    TypeScriptSourceContext,
)


def _extract_node_text(source_bytes: bytes, node: tree_sitter.Node) -> str:
    return source_bytes[node.start_byte : node.end_byte].decode(
        "utf-8", errors="ignore"
    )


def _is_feature_imported(
    absolute_paths: List[str], import_aliases: Dict[str, str]
) -> bool:
    for absolute_path in absolute_paths:
        if absolute_path in import_aliases:
            return True
        parts = absolute_path.split(".")
        for idx in range(1, len(parts)):
            prefix = ".".join(parts[:idx])
            if prefix in import_aliases:
                return True
    return False


def _first_capture(
    captures: Dict[str, List[tree_sitter.Node]], name: str
) -> Optional[tree_sitter.Node]:
    nodes = captures.get(name)
    if nodes:
        return nodes[0]
    return None


class TypeScriptTreeSitterFrameworkDetector:
    """Detect TypeScript framework features using tree-sitter queries."""

    def __init__(self) -> None:
        self._query_builder = TypeScriptFrameworkQueryBuilder()

    def detect(
        self, context: TypeScriptSourceContext, feature_specs: List[FeatureSpec]
    ) -> List[Detection]:
        detections: List[Detection] = []
        for spec in feature_specs:
            try:
                if not _is_feature_imported(
                    spec.absolute_paths, context.import_aliases
                ):
                    logger.opt(lazy=True).debug(
                        "Skipping feature; import not found | library={} | feature_key={} | paths={} | aliases={}",
                        lambda: spec.library,
                        lambda: spec.feature_key,
                        lambda: spec.absolute_paths,
                        lambda: sorted(context.import_aliases.keys()),
                    )
                    continue
                feature_detections = self._detect_feature(context, spec)
                if feature_detections:
                    logger.opt(lazy=True).debug(
                        "Feature detections | library={} | feature_key={} | count={}",
                        lambda: spec.library,
                        lambda: spec.feature_key,
                        lambda: len(feature_detections),
                    )
                detections.extend(feature_detections)
            except Exception as exc:
                logger.warning(
                    "TypeScript framework detection failed | feature_key={} | error={}",
                    spec.feature_key,
                    exc,
                )
        return detections

    def _detect_feature(
        self, context: TypeScriptSourceContext, spec: FeatureSpec
    ) -> List[Detection]:
        if spec.concept != Concept.FUNCTION_DEFINITION:
            logger.debug(
                "Skipping unsupported concept in TypeScript detector | concept={}",
                spec.concept,
            )
            return []

        query = self._query_builder.build_query(spec)
        cursor = tree_sitter.QueryCursor(query)
        matches = cursor.matches(context.root_node)
        return self._detect_function_definition(context, spec, matches)

    def _detect_function_definition(
        self,
        context: TypeScriptSourceContext,
        spec: FeatureSpec,
        matches: List[Tuple[int, Dict[str, List[tree_sitter.Node]]]],
    ) -> List[Detection]:
        detections: List[Detection] = []
        seen: Set[Tuple[str, str, int, int]] = set()
        source_bytes = context.source_bytes

        for _pattern_index, captures in matches:
            function_name_node = _first_capture(captures, "function_name")
            export_statement_node = _first_capture(captures, "export_statement")

            if function_name_node is None or export_statement_node is None:
                continue

            function_name_text = _extract_node_text(source_bytes, function_name_node)
            match_text = _extract_node_text(source_bytes, export_statement_node)
            start_line = export_statement_node.start_point[0] + 1
            end_line = export_statement_node.end_point[0] + 1

            dedup_key = (spec.library, spec.feature_key, start_line, end_line)
            if dedup_key in seen:
                continue
            seen.add(dedup_key)

            detections.append(
                Detection(
                    feature_key=spec.feature_key,
                    library=spec.library,
                    match_text=match_text,
                    start_line=start_line,
                    end_line=end_line,
                    metadata={
                        "concept": "FunctionDefinition",
                        "source": "tree_sitter",
                        "function_name": function_name_text,
                        "export_name": function_name_text,
                        "match_confidence": spec.base_confidence,
                    },
                )
            )

        return detections
