"""Tree-sitter based TypeScript framework detector for framework features."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Literal, Optional, Set, Tuple

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
    """Extract UTF-8 text from a tree-sitter node using its byte offsets."""
    return source_bytes[node.start_byte : node.end_byte].decode(
        "utf-8", errors="ignore"
    )


def _is_feature_imported(
    absolute_paths: List[str], import_aliases: Dict[str, str]
) -> bool:
    """Check whether any of a feature's import paths appear in the recorded imports."""
    for absolute_path in absolute_paths:
        if absolute_path in import_aliases:
            return True
        # Check progressively longer prefixes (e.g. "react" then "react.useState")
        # so namespace-level imports like `import * as React from 'react'` still match.
        parts = absolute_path.split(".")
        for idx in range(1, len(parts)):
            prefix = ".".join(parts[:idx])
            if prefix in import_aliases:
                return True
    return False


def _first_capture(
    captures: Dict[str, List[tree_sitter.Node]], name: str
) -> Optional[tree_sitter.Node]:
    """Return the first node for a named capture, or None if the capture is absent."""
    nodes = captures.get(name)
    if nodes:
        return nodes[0]
    return None


CallMatchKind = Literal[
    "no_match",
    "symbol_exact",
    "import_alias_exact",
    "module_member_exact",
    "default_import_exact",
    "root_module_member_exact",
]


@dataclass(frozen=True)
class CallMatchEvidence:
    """Immutable evidence record produced when a callee is matched against imports.

    Attributes:
        matched: Whether the callee was successfully matched.
        match_kind: Discriminator indicating how the match was resolved.
        matched_absolute_path: The fully-qualified import path that matched.
        matched_alias: The local alias used in source, if any.
    """

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
    """Map a feature spec to its call-expression confidence score."""
    return float(spec.base_confidence)


def _build_call_expression_metadata(
    *,
    spec: FeatureSpec,
    call_match_evidence: CallMatchEvidence,
) -> dict[str, object]:
    """Build the metadata dict attached to a CallExpression detection.

    Args:
        spec: The feature specification that triggered the match.
        call_match_evidence: Evidence describing how the callee was matched.

    Returns:
        A metadata dictionary containing match kind, confidence, and
        policy version fields.
    """
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
    callee_text: str,
    absolute_paths: List[str],
    import_aliases: Dict[str, str],
) -> CallMatchEvidence:
    """Validate a callee expression against imported symbols.

    Tries several resolution strategies per absolute path:
    1. Direct symbol or alias match (``symbol_exact`` / ``import_alias_exact``).
    2. Namespace member access via the parent module alias
       (``module_member_exact``), with special handling for default exports
       (``default_import_exact``).
    3. Root-module member access when only the top-level package is imported
       (``root_module_member_exact``).

    Args:
        callee_text: The raw callee text extracted from the call expression node.
        absolute_paths: Fully-qualified import paths declared by the feature spec.
        import_aliases: Mapping of absolute import paths to their local aliases.

    Returns:
        A ``CallMatchEvidence`` describing the match, or ``NO_CALL_MATCH_EVIDENCE``
        if no strategy succeeded.
    """
    for absolute_path in absolute_paths:
        path_parts = absolute_path.split(".")
        short_name = path_parts[-1]
        module_path = ".".join(path_parts[:-1])

        # Strategy 1: the full absolute path was imported directly.
        if absolute_path in import_aliases:
            alias = import_aliases[absolute_path]
            if callee_text == alias:
                match_kind: CallMatchKind = (
                    "symbol_exact" if alias == short_name else "import_alias_exact"
                )
                return CallMatchEvidence(
                    matched=True,
                    match_kind=match_kind,
                    matched_absolute_path=absolute_path,
                    matched_alias=alias,
                )

        # Strategy 2: the parent module was imported; callee uses `module.member`.
        if module_path and module_path in import_aliases:
            module_alias = import_aliases[module_path]
            # Default exports are accessed via the module alias alone.
            if short_name == "default":
                if callee_text == module_alias:
                    return CallMatchEvidence(
                        matched=True,
                        match_kind="default_import_exact",
                        matched_absolute_path=absolute_path,
                        matched_alias=module_alias,
                    )
            elif callee_text == f"{module_alias}.{short_name}":
                return CallMatchEvidence(
                    matched=True,
                    match_kind="module_member_exact",
                    matched_absolute_path=absolute_path,
                    matched_alias=module_alias,
                )

        # Strategy 3: only the root package was imported (e.g. `import * as pkg`).
        root_module = path_parts[0]
        if root_module in import_aliases:
            root_module_alias = import_aliases[root_module]
            if callee_text == f"{root_module_alias}.{short_name}":
                return CallMatchEvidence(
                    matched=True,
                    match_kind="root_module_member_exact",
                    matched_absolute_path=absolute_path,
                    matched_alias=root_module_alias,
                )

    return NO_CALL_MATCH_EVIDENCE


def _matches_superclass(
    superclass_text: str,
    absolute_paths: List[str],
    import_aliases: Dict[str, str],
) -> bool:
    """Validate a superclass identifier against imported symbols.

    Uses the same resolution strategies as ``_matches_callee`` (direct alias,
    namespace member, default export) but returns a simple boolean since
    inheritance detections do not carry match-kind evidence.

    Args:
        superclass_text: The raw superclass text from the class heritage clause.
        absolute_paths: Fully-qualified import paths declared by the feature spec.
        import_aliases: Mapping of absolute import paths to their local aliases.

    Returns:
        True if the superclass text resolves to any of the given import paths.
    """
    for absolute_path in absolute_paths:
        path_parts = absolute_path.split(".")
        short_name = path_parts[-1]
        module_path = ".".join(path_parts[:-1])

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
    """Resolve the bound object and annotation name from decorator captures.

    Handles three tree-sitter capture layouts:
    - ``@obj.method(...)`` → decorator_object + decorator_method captures.
    - ``@method(...)`` with a dotted decorator_name fallback.
    - Plain ``@Name`` with no call expression.

    Args:
        source_bytes: Raw source bytes for text extraction.
        captures: Named captures from a tree-sitter decorator query match.

    Returns:
        A ``(bound_object, annotation_name)`` tuple.  ``bound_object`` is
        empty when the decorator is unqualified.
    """
    decorator_object_node = _first_capture(captures, "decorator_object")
    decorator_method_node = _first_capture(captures, "decorator_method")
    decorator_name_node = _first_capture(captures, "decorator_name")

    if decorator_method_node is not None:
        annotation_name = _extract_node_text(source_bytes, decorator_method_node)
        if decorator_object_node is not None:
            bound_object = _extract_node_text(source_bytes, decorator_object_node)
            return bound_object, annotation_name

        # Fallback: infer bound_object from a dotted decorator_name when
        # the query didn't produce a separate decorator_object capture.
        if decorator_name_node is not None:
            decorator_name = _extract_node_text(source_bytes, decorator_name_node)
            if "." in decorator_name:
                bound_object = decorator_name.rsplit(".", 1)[0]
                return bound_object, annotation_name
        return "", annotation_name

    if decorator_name_node is None:
        return "", ""

    # Simple decorator: split on the last dot to separate namespace from name.
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
        """Run all feature specs against a parsed TypeScript source and return detections.

        Each spec is first checked for an import presence guard: if none of the
        spec's absolute paths appear in the source imports, the spec is skipped.
        Specs that pass are dispatched to concept-specific detection methods.

        Args:
            context: Pre-parsed TypeScript source with import alias mapping.
            feature_specs: Feature specifications to detect.

        Returns:
            Aggregated list of Detection objects across all matched specs.
        """
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
        """Build a tree-sitter query for the spec and dispatch to the concept-specific handler."""
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
        """Extract exported function definition detections from tree-sitter query matches."""
        detections: List[Detection] = []
<<<<<<< HEAD
=======
        seen: Set[Tuple[str, str, int, int]] = set()
>>>>>>> origin/main
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

<<<<<<< HEAD
            detections.append(
                Detection(
                    capability_key=spec.capability_key,
                    operation_key=spec.operation_key,
=======
            dedup_key = (spec.library, spec.feature_key, start_line, end_line)
            if dedup_key in seen:
                continue
            seen.add(dedup_key)

            detections.append(
                Detection(
                    feature_key=spec.feature_key,
>>>>>>> origin/main
                    library=spec.library,
                    match_text=match_text,
                    start_line=start_line,
                    end_line=end_line,
                    metadata={
                        "concept": "FunctionDefinition",
                        "source": "tree_sitter",
                        "function_name": function_name_text,
                        "export_name": function_name_text,
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
        """Process matched call expressions and verify callees against imports."""
        detections: List[Detection] = []
<<<<<<< HEAD
        seen: Set[Tuple[str, str, str, int, int]] = set()
=======
        seen: Set[Tuple[str, str, int, int]] = set()
>>>>>>> origin/main
        source_bytes = context.source_bytes

        for _pattern_index, captures in matches:
            call_expression_node = _first_capture(captures, "call_expression")
            callee_node = _first_capture(captures, "callee")
            call_args_node = _first_capture(captures, "call_args")

            if call_expression_node is None or callee_node is None:
                continue

            callee_text = _extract_node_text(source_bytes, callee_node)
            call_match_evidence = _matches_callee(
                callee_text, spec.absolute_paths, context.import_aliases
            )
            if not call_match_evidence.matched:
                continue

            start_line = call_expression_node.start_point[0] + 1
            end_line = call_expression_node.end_point[0] + 1
<<<<<<< HEAD
            dedup_key = (
                spec.library,
                spec.capability_key,
                spec.operation_key,
                start_line,
                end_line,
            )
=======
            dedup_key = (spec.library, spec.feature_key, start_line, end_line)
>>>>>>> origin/main
            if dedup_key in seen:
                continue
            seen.add(dedup_key)

            args_text = ""
            if call_args_node is not None:
                args_text = _extract_node_text(source_bytes, call_args_node)

            detections.append(
                CallExpressionInfo(
<<<<<<< HEAD
                    capability_key=spec.capability_key,
                    operation_key=spec.operation_key,
=======
                    feature_key=spec.feature_key,
>>>>>>> origin/main
                    library=spec.library,
                    match_text=_extract_node_text(source_bytes, call_expression_node),
                    start_line=start_line,
                    end_line=end_line,
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
        context: TypeScriptSourceContext,
        spec: FeatureSpec,
        matches: List[Tuple[int, Dict[str, List[tree_sitter.Node]]]],
    ) -> List[Detection]:
        """Process class inheritance matches and verify superclasses against imports."""
        detections: List[Detection] = []
<<<<<<< HEAD
=======
        seen: Set[Tuple[str, str, int, int]] = set()
>>>>>>> origin/main
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
<<<<<<< HEAD

            detections.append(
                InheritanceInfo(
                    capability_key=spec.capability_key,
                    operation_key=spec.operation_key,
=======
            dedup_key = (spec.library, spec.feature_key, start_line, end_line)
            if dedup_key in seen:
                continue
            seen.add(dedup_key)

            detections.append(
                InheritanceInfo(
                    feature_key=spec.feature_key,
>>>>>>> origin/main
                    library=spec.library,
                    match_text=_extract_node_text(source_bytes, class_definition_node),
                    start_line=start_line,
                    end_line=end_line,
                    subclass=_extract_node_text(source_bytes, class_name_node),
                    superclass=superclass_text,
                    metadata={
                        "concept": "Inheritance",
                        "source": "tree_sitter",
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
        """Detect decorator / annotation-like patterns from tree-sitter matches."""
        detections: List[Detection] = []
<<<<<<< HEAD
=======
        seen: Set[Tuple[str, str, int, int]] = set()
>>>>>>> origin/main
        source_bytes = context.source_bytes

        for _pattern_index, captures in matches:
            decorator_node = _first_capture(captures, "decorator")
            definition_node = _first_capture(captures, "definition")
            decorator_call_node = _first_capture(captures, "decorator_call")

            if decorator_node is None or definition_node is None:
                continue

            start_line = decorator_node.start_point[0] + 1
            end_line = definition_node.end_point[0] + 1
<<<<<<< HEAD
=======
            dedup_key = (spec.library, spec.feature_key, start_line, end_line)
            if dedup_key in seen:
                continue
            seen.add(dedup_key)
>>>>>>> origin/main

            # Prefer the call node (includes arguments) over the bare decorator node.
            match_text_node = decorator_call_node or decorator_node
            bound_object, annotation_name = _resolve_annotation_parts(
                source_bytes,
                captures,
            )

            detections.append(
                AnnotationLikeInfo(
<<<<<<< HEAD
                    capability_key=spec.capability_key,
                    operation_key=spec.operation_key,
=======
                    feature_key=spec.feature_key,
>>>>>>> origin/main
                    library=spec.library,
                    match_text=_extract_node_text(source_bytes, match_text_node),
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
