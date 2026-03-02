"""Tree-sitter based TypeScript framework detector for framework features."""

from __future__ import annotations

from typing import Dict, List, Optional, Set, Tuple

from loguru import logger
import tree_sitter
from unoplat_code_confluence_commons.base_models import (
    AnnotationLikeInfo,
    CallExpressionInfo,
    Concept,
    Detection,
    FeatureSpec,
    InheritanceInfo,
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


def _matches_callee(
    callee_text: str,
    absolute_paths: List[str],
    import_aliases: Dict[str, str],
) -> bool:
    for absolute_path in absolute_paths:
        path_parts = absolute_path.split(".")
        short_name = path_parts[-1]
        module_path = ".".join(path_parts[:-1])

        if callee_text == short_name or callee_text.endswith(f".{short_name}"):
            return True

        if absolute_path in import_aliases:
            alias = import_aliases[absolute_path]
            if callee_text == alias or callee_text.endswith(f".{alias}"):
                return True

        if module_path and module_path in import_aliases:
            module_alias = import_aliases[module_path]
            if short_name == "default":
                if callee_text == module_alias:
                    return True
            elif callee_text == f"{module_alias}.{short_name}":
                return True

    return False


def _matches_superclass(
    superclass_text: str,
    absolute_paths: List[str],
    import_aliases: Dict[str, str],
) -> bool:
    for absolute_path in absolute_paths:
        path_parts = absolute_path.split(".")
        short_name = path_parts[-1]
        module_path = ".".join(path_parts[:-1])

        if superclass_text == short_name or superclass_text.endswith(f".{short_name}"):
            return True

        if absolute_path in import_aliases:
            alias = import_aliases[absolute_path]
            if superclass_text == alias:
                return True

        if module_path and module_path in import_aliases:
            module_alias = import_aliases[module_path]
            if short_name == "default":
                if superclass_text == module_alias:
                    return True
            elif superclass_text == f"{module_alias}.{short_name}":
                return True

    return False


def _resolve_annotation_parts(
    source_bytes: bytes,
    captures: Dict[str, List[tree_sitter.Node]],
) -> tuple[str, str]:
    decorator_object_node = _first_capture(captures, "decorator_object")
    decorator_method_node = _first_capture(captures, "decorator_method")
    decorator_name_node = _first_capture(captures, "decorator_name")

    if decorator_method_node is not None:
        annotation_name = _extract_node_text(source_bytes, decorator_method_node)
        if decorator_object_node is not None:
            bound_object = _extract_node_text(source_bytes, decorator_object_node)
            return bound_object, annotation_name

        if decorator_name_node is not None:
            decorator_name = _extract_node_text(source_bytes, decorator_name_node)
            if "." in decorator_name:
                bound_object = decorator_name.rsplit(".", 1)[0]
                return bound_object, annotation_name
        return "", annotation_name

    if decorator_name_node is None:
        return "", ""

    decorator_name = _extract_node_text(source_bytes, decorator_name_node)
    if "." in decorator_name:
        bound_object, annotation_name = decorator_name.rsplit(".", 1)
        return bound_object, annotation_name
    return "", decorator_name


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
        query = self._query_builder.build_query(spec)
        cursor = tree_sitter.QueryCursor(query)
        matches = cursor.matches(context.root_node)

        if spec.concept == Concept.FUNCTION_DEFINITION:
            return self._detect_function_definition(context, spec, matches)
        if spec.concept == Concept.CALL_EXPRESSION:
            return self._detect_call_expression(context, spec, matches)
        if spec.concept == Concept.INHERITANCE:
            return self._detect_inheritance(context, spec, matches)
        if spec.concept == Concept.ANNOTATION_LIKE:
            return self._detect_annotation_like(context, spec, matches)

        logger.debug(
            "Skipping unsupported concept in TypeScript detector | concept={}",
            spec.concept,
        )
        return []

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

    def _detect_call_expression(
        self,
        context: TypeScriptSourceContext,
        spec: FeatureSpec,
        matches: List[Tuple[int, Dict[str, List[tree_sitter.Node]]]],
    ) -> List[Detection]:
        detections: List[Detection] = []
        seen: Set[Tuple[str, str, int, int]] = set()
        source_bytes = context.source_bytes

        for _pattern_index, captures in matches:
            call_expression_node = _first_capture(captures, "call_expression")
            callee_node = _first_capture(captures, "callee")
            call_args_node = _first_capture(captures, "call_args")

            if call_expression_node is None or callee_node is None:
                continue

            callee_text = _extract_node_text(source_bytes, callee_node)
            if not _matches_callee(
                callee_text, spec.absolute_paths, context.import_aliases
            ):
                continue

            start_line = call_expression_node.start_point[0] + 1
            end_line = call_expression_node.end_point[0] + 1
            dedup_key = (spec.library, spec.feature_key, start_line, end_line)
            if dedup_key in seen:
                continue
            seen.add(dedup_key)

            args_text = ""
            if call_args_node is not None:
                args_text = _extract_node_text(source_bytes, call_args_node)

            detections.append(
                CallExpressionInfo(
                    feature_key=spec.feature_key,
                    library=spec.library,
                    match_text=_extract_node_text(source_bytes, call_expression_node),
                    start_line=start_line,
                    end_line=end_line,
                    callee=callee_text,
                    args_text=args_text,
                    metadata={
                        "concept": "CallExpression",
                        "source": "tree_sitter",
                        "match_confidence": spec.base_confidence,
                    },
                )
            )

        return detections

    def _detect_inheritance(
        self,
        context: TypeScriptSourceContext,
        spec: FeatureSpec,
        matches: List[Tuple[int, Dict[str, List[tree_sitter.Node]]]],
    ) -> List[Detection]:
        detections: List[Detection] = []
        seen: Set[Tuple[str, str, int, int]] = set()
        source_bytes = context.source_bytes

        for _pattern_index, captures in matches:
            class_definition_node = _first_capture(captures, "class_definition")
            class_name_node = _first_capture(captures, "class_name")
            superclass_node = _first_capture(captures, "superclass")

            if (
                class_definition_node is None
                or class_name_node is None
                or superclass_node is None
            ):
                continue

            superclass_text = _extract_node_text(source_bytes, superclass_node)
            if not _matches_superclass(
                superclass_text,
                spec.absolute_paths,
                context.import_aliases,
            ):
                continue

            start_line = class_definition_node.start_point[0] + 1
            end_line = class_definition_node.end_point[0] + 1
            dedup_key = (spec.library, spec.feature_key, start_line, end_line)
            if dedup_key in seen:
                continue
            seen.add(dedup_key)

            detections.append(
                InheritanceInfo(
                    feature_key=spec.feature_key,
                    library=spec.library,
                    match_text=_extract_node_text(source_bytes, class_definition_node),
                    start_line=start_line,
                    end_line=end_line,
                    subclass=_extract_node_text(source_bytes, class_name_node),
                    superclass=superclass_text,
                    metadata={
                        "concept": "Inheritance",
                        "source": "tree_sitter",
                        "match_confidence": spec.base_confidence,
                    },
                )
            )

        return detections

    def _detect_annotation_like(
        self,
        context: TypeScriptSourceContext,
        spec: FeatureSpec,
        matches: List[Tuple[int, Dict[str, List[tree_sitter.Node]]]],
    ) -> List[Detection]:
        detections: List[Detection] = []
        seen: Set[Tuple[str, str, int, int]] = set()
        source_bytes = context.source_bytes

        for _pattern_index, captures in matches:
            decorator_node = _first_capture(captures, "decorator")
            definition_node = _first_capture(captures, "definition")
            decorator_call_node = _first_capture(captures, "decorator_call")

            if decorator_node is None or definition_node is None:
                continue

            start_line = decorator_node.start_point[0] + 1
            end_line = definition_node.end_point[0] + 1
            dedup_key = (spec.library, spec.feature_key, start_line, end_line)
            if dedup_key in seen:
                continue
            seen.add(dedup_key)

            match_text_node = decorator_call_node or decorator_node
            bound_object, annotation_name = _resolve_annotation_parts(
                source_bytes,
                captures,
            )

            detections.append(
                AnnotationLikeInfo(
                    feature_key=spec.feature_key,
                    library=spec.library,
                    match_text=_extract_node_text(source_bytes, match_text_node),
                    start_line=start_line,
                    end_line=end_line,
                    bound_object=bound_object,
                    annotation_name=annotation_name,
                    metadata={
                        "concept": "AnnotationLike",
                        "source": "tree_sitter",
                        "match_confidence": spec.base_confidence,
                    },
                )
            )

        return detections
