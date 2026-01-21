"""Dynamic tree-sitter query builder for Python framework detection."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Dict, Optional

import tree_sitter
from tree_sitter_language_pack import get_language
from unoplat_code_confluence_commons.base_models import (
    Concept,
    ConstructQueryConfig,
    FeatureSpec,
    TargetLevel,
)


_TEMPLATE_DIR = Path(__file__).resolve().parent / "queries"
_TEMPLATE_PATHS = {
    "annotation_function": _TEMPLATE_DIR / "annotation_function_like.scm",
    "annotation_class": _TEMPLATE_DIR / "annotation_class_like.scm",
    "call_expression": _TEMPLATE_DIR / "call_expression.scm",
    "inheritance": _TEMPLATE_DIR / "inheritance.scm",
}

_QUERY_CACHE: Dict[str, tree_sitter.Query] = {}


def _escape_query_regex(regex: str) -> str:
    return regex.replace("\\", "\\\\").replace('"', '\\"')


def _render_predicate(capture_name: str, regex: Optional[str]) -> str:
    if not regex:
        return ""
    safe_regex = _escape_query_regex(regex)
    return f'(#match? {capture_name} "{safe_regex}")'


def _render_template(template: str, replacements: Dict[str, str]) -> str:
    rendered = template
    for key, value in replacements.items():
        rendered = rendered.replace(f"{{{{{key}}}}}", value)
    return rendered


def _load_template(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _definition_hash(feature_spec: FeatureSpec) -> str:
    payload = {
        "feature_key": feature_spec.feature_key,
        "library": feature_spec.library,
        "absolute_paths": feature_spec.absolute_paths,
        "target_level": feature_spec.target_level.value,
        "concept": feature_spec.concept.value,
        "locator_strategy": feature_spec.locator_strategy.value,
        "construct_query": feature_spec.construct_query,
    }
    payload_json = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload_json.encode("utf-8")).hexdigest()


class PythonFrameworkQueryBuilder:
    """Builds tree-sitter queries for Python framework detection."""

    def __init__(self) -> None:
        self._language = get_language("python")  # type: ignore[arg-type]

    def build_query(self, feature_spec: FeatureSpec) -> tree_sitter.Query:
        template_key = self._select_template_key(feature_spec)
        template_path = _TEMPLATE_PATHS[template_key]
        template = _load_template(template_path)
        query_source = self._render_query(template, feature_spec)
        cache_key = f"{template_key}:{_definition_hash(feature_spec)}"

        if cache_key not in _QUERY_CACHE:
            _QUERY_CACHE[cache_key] = tree_sitter.Query(self._language, query_source)

        return _QUERY_CACHE[cache_key]

    def _select_template_key(self, feature_spec: FeatureSpec) -> str:
        if feature_spec.concept == Concept.ANNOTATION_LIKE:
            if feature_spec.target_level == TargetLevel.CLASS:
                return "annotation_class"
            return "annotation_function"
        if feature_spec.concept == Concept.CALL_EXPRESSION:
            return "call_expression"
        if feature_spec.concept == Concept.INHERITANCE:
            return "inheritance"
        raise ValueError(f"Unsupported concept: {feature_spec.concept}")

    def _render_query(self, template: str, feature_spec: FeatureSpec) -> str:
        construct_query = self._construct_query_config(feature_spec)

        method_regex = construct_query.method_regex or construct_query.attribute_regex
        annotation_regex = construct_query.annotation_name_regex
        callee_regex = construct_query.callee_regex
        superclass_regex = construct_query.superclass_regex

        annotation_call_block = self._build_annotation_call_block(method_regex)
        annotation_name_block = self._build_annotation_name_block(annotation_regex)

        replacements = {
            "ANNOTATION_CALL_BLOCK": annotation_call_block,
            "ANNOTATION_NAME_BLOCK": annotation_name_block,
            "CALLEE_PREDICATE": _render_predicate("@callee", callee_regex),
            "SUPERCLASS_PREDICATE": _render_predicate("@superclass", superclass_regex),
        }

        return _render_template(template, replacements)

    def _construct_query_config(self, feature_spec: FeatureSpec) -> ConstructQueryConfig:
        construct_query = feature_spec.construct_query_typed
        if construct_query is not None:
            return construct_query
        return ConstructQueryConfig()

    def _build_annotation_call_block(self, method_regex: Optional[str]) -> str:
        predicate = _render_predicate("@decorator_method", method_regex)
        predicate_line = f"\n  {predicate}" if predicate else ""
        return f"""
(
  (decorated_definition
    (decorator
      (call
        function: (attribute
          object: (_) @decorator_object
          attribute: (identifier) @decorator_method
        )
        arguments: (argument_list)? @decorator_args
      ) @decorator_call
    ) @decorator
    definition: (_) @definition
  ) @decorated_definition{predicate_line}
)
"""

    def _build_annotation_name_block(self, annotation_regex: Optional[str]) -> str:
        if not annotation_regex:
            return ""
        predicate = _render_predicate("@decorator_name", annotation_regex)
        predicate_line = f"\n  {predicate}" if predicate else ""
        return f"""
(
  (decorated_definition
    (decorator
      (identifier) @decorator_name
    ) @decorator
    definition: (_) @definition
  ) @decorated_definition{predicate_line}
)
"""
