"""Tree-sitter based Python framework detector using dynamic queries."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Literal, Optional

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

from src.code_confluence_flow_bridge.engine.programming_language.python.python_framework_query_builder import (
    PythonFrameworkQueryBuilder,
)
from src.code_confluence_flow_bridge.engine.programming_language.python.python_source_context import (
    PythonSourceContext,
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


CallMatchKind = Literal[
    "no_match",
    "symbol_exact",
    "import_alias_exact",
    "module_member_exact",
    "root_module_member_exact",
]


@dataclass(frozen=True)
class CallMatchEvidence:
    matched: bool
    match_kind: CallMatchKind
    matched_absolute_path: str
    matched_alias: str | None


NO_CALL_MATCH_EVIDENCE = CallMatchEvidence(
    matched=False,
    match_kind="no_match",
    matched_absolute_path="",
    matched_alias=None,
)

CALL_EXPRESSION_MATCH_POLICY_VERSION = "v1_import_bound"


def _resolve_call_expression_confidence(spec: FeatureSpec) -> float:
    return float(spec.base_confidence)


def _build_call_expression_metadata(
    *,
    spec: FeatureSpec,
    call_match_evidence: CallMatchEvidence,
) -> dict[str, object]:
    metadata: dict[str, object] = {
        "concept": "CallExpression",
        "source": "tree_sitter",
        "match_confidence": _resolve_call_expression_confidence(spec),
        "call_match_kind": call_match_evidence.match_kind,
        "matched_absolute_path": call_match_evidence.matched_absolute_path,
        "call_match_policy_version": CALL_EXPRESSION_MATCH_POLICY_VERSION,
    }
    if call_match_evidence.matched_alias is not None:
        metadata["matched_alias"] = call_match_evidence.matched_alias
    return metadata


def _matches_callee(
    callee_text: str, absolute_paths: List[str], import_aliases: Dict[str, str]
) -> CallMatchEvidence:
    for abs_path in absolute_paths:
        path_parts = abs_path.split(".")
        short_name = path_parts[-1]
        module_path = ".".join(path_parts[:-1])

        if abs_path in import_aliases:
            alias = import_aliases[abs_path]
            if callee_text == alias:
                match_kind: CallMatchKind = (
                    "symbol_exact" if alias == short_name else "import_alias_exact"
                )
                return CallMatchEvidence(
                    matched=True,
                    match_kind=match_kind,
                    matched_absolute_path=abs_path,
                    matched_alias=alias,
                )

        if module_path and module_path in import_aliases:
            module_alias = import_aliases[module_path]
            if callee_text == f"{module_alias}.{short_name}":
                return CallMatchEvidence(
                    matched=True,
                    match_kind="module_member_exact",
                    matched_absolute_path=abs_path,
                    matched_alias=module_alias,
                )

        root_module = path_parts[0]
        if root_module in import_aliases:
            root_module_alias = import_aliases[root_module]
            if callee_text == f"{root_module_alias}.{short_name}":
                return CallMatchEvidence(
                    matched=True,
                    match_kind="root_module_member_exact",
                    matched_absolute_path=abs_path,
                    matched_alias=root_module_alias,
                )

    return NO_CALL_MATCH_EVIDENCE


def _matches_superclass(
    superclass_text: str, absolute_paths: List[str], import_aliases: Dict[str, str]
) -> bool:
    for abs_path in absolute_paths:
        path_parts = abs_path.split(".")
        short_name = path_parts[-1]
        module_path = ".".join(path_parts[:-1])

        if abs_path in import_aliases and superclass_text == import_aliases[abs_path]:
            return True

        if module_path and module_path in import_aliases:
            module_alias = import_aliases[module_path]
            if superclass_text == f"{module_alias}.{short_name}":
                return True

    return False


class PythonTreeSitterFrameworkDetector:
    """Detect framework features using tree-sitter queries on shared source."""

    def __init__(self) -> None:
        self._query_builder = PythonFrameworkQueryBuilder()

    def detect(
        self, context: PythonSourceContext, feature_specs: List[FeatureSpec]
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
                    "Framework detection failed | feature_key={} | error={}",
                    spec.feature_key,
                    exc,
                )
        return detections

    def _detect_feature(
        self, context: PythonSourceContext, spec: FeatureSpec
    ) -> List[Detection]:
        query = self._query_builder.build_query(spec)
        cursor = tree_sitter.QueryCursor(query)
        matches = cursor.matches(context.root_node)

        if spec.concept == Concept.ANNOTATION_LIKE:
            return self._detect_annotation_like(context, spec, matches)
        if spec.concept == Concept.CALL_EXPRESSION:
            return self._detect_call_expression(context, spec, matches)
        if spec.concept == Concept.INHERITANCE:
            return self._detect_inheritance(context, spec, matches)

        return []

    def _detect_annotation_like(
        self,
        context: PythonSourceContext,
        spec: FeatureSpec,
        matches: List[tuple[int, Dict[str, List[tree_sitter.Node]]]],
    ) -> List[Detection]:
        detections: List[Detection] = []

        for _pattern_index, captures in matches:
            decorator_call = self._first_capture(captures, "decorator_call")
            decorator_name = self._first_capture(captures, "decorator_name")
            decorator_object = self._first_capture(captures, "decorator_object")
            decorator_method = self._first_capture(captures, "decorator_method")
            definition = self._first_capture(captures, "definition")
            decorator = self._first_capture(captures, "decorator")

            if definition is None or decorator is None:
                continue

            start_line = decorator.start_point[0] + 1
            end_line = definition.end_point[0] + 1

            match_text_node = decorator or decorator_call or decorator_name
            match_text = (
                _extract_node_text(context.source_bytes, match_text_node)
                if match_text_node
                else ""
            )

            bound_object = ""
            annotation_name = ""
            if decorator_method is not None:
                annotation_name = _extract_node_text(
                    context.source_bytes, decorator_method
                )
                if decorator_object is not None:
                    bound_object = _extract_node_text(
                        context.source_bytes, decorator_object
                    )
            elif decorator_name is not None:
                annotation_name = _extract_node_text(
                    context.source_bytes, decorator_name
                )

            detections.append(
                AnnotationLikeInfo(
                    feature_key=spec.feature_key,
                    library=spec.library,
                    match_text=match_text,
                    start_line=start_line,
                    end_line=end_line,
                    bound_object=bound_object,
                    annotation_name=annotation_name,
                    metadata={
                        "concept": "AnnotationLike",
                        "source": "tree_sitter",
                    },
                )
            )

        return detections

    def _detect_call_expression(
        self,
        context: PythonSourceContext,
        spec: FeatureSpec,
        matches: List[tuple[int, Dict[str, List[tree_sitter.Node]]]],
    ) -> List[Detection]:
        detections: List[Detection] = []

        for _pattern_index, captures in matches:
            call_expression = self._first_capture(captures, "call_expression")
            callee = self._first_capture(captures, "callee")
            call_args = self._first_capture(captures, "call_args")

            if call_expression is None or callee is None:
                continue

            callee_text = _extract_node_text(context.source_bytes, callee)
            call_match_evidence = _matches_callee(
                callee_text, spec.absolute_paths, context.import_aliases
            )
            if not call_match_evidence.matched:
                continue

            match_text = _extract_node_text(context.source_bytes, call_expression)
            args_text = (
                _extract_node_text(context.source_bytes, call_args)
                if call_args is not None
                else ""
            )

            detections.append(
                CallExpressionInfo(
                    feature_key=spec.feature_key,
                    library=spec.library,
                    match_text=match_text,
                    start_line=call_expression.start_point[0] + 1,
                    end_line=call_expression.end_point[0] + 1,
                    callee=callee_text,
                    args_text=args_text,
                    metadata=_build_call_expression_metadata(
                        spec=spec,
                        call_match_evidence=call_match_evidence,
                    ),
                )
            )

        return detections

    def _detect_inheritance(
        self,
        context: PythonSourceContext,
        spec: FeatureSpec,
        matches: List[tuple[int, Dict[str, List[tree_sitter.Node]]]],
    ) -> List[Detection]:
        detections: List[Detection] = []

        for _pattern_index, captures in matches:
            class_definition = self._first_capture(captures, "class_definition")
            class_name = self._first_capture(captures, "class_name")
            superclass = self._first_capture(captures, "superclass")

            if class_definition is None or class_name is None or superclass is None:
                continue

            superclass_text = _extract_node_text(context.source_bytes, superclass)
            if not _matches_superclass(
                superclass_text, spec.absolute_paths, context.import_aliases
            ):
                continue

            detections.append(
                InheritanceInfo(
                    feature_key=spec.feature_key,
                    library=spec.library,
                    match_text=_extract_node_text(
                        context.source_bytes, class_definition
                    ),
                    start_line=class_definition.start_point[0] + 1,
                    end_line=class_definition.end_point[0] + 1,
                    subclass=_extract_node_text(context.source_bytes, class_name),
                    superclass=superclass_text,
                    metadata={
                        "concept": "Inheritance",
                        "source": "tree_sitter",
                    },
                )
            )

        return detections

    def _first_capture(
        self, captures: Dict[str, List[tree_sitter.Node]], name: str
    ) -> Optional[tree_sitter.Node]:
        nodes = captures.get(name)
        if nodes:
            return nodes[0]
        return None
