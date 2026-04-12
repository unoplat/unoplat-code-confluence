"""Dynamic tree-sitter query builder for TypeScript framework detection."""

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
)

_TEMPLATE_DIR = Path(__file__).resolve().parent / "queries"
_TEMPLATE_PATHS = {
    "function_definition": _TEMPLATE_DIR / "function_definition.scm",
    "call_expression": _TEMPLATE_DIR / "call_expression.scm",
    "inheritance": _TEMPLATE_DIR / "inheritance.scm",
    "annotation_like": _TEMPLATE_DIR / "annotation_function_like.scm",
}

# Module-level cache: avoids recompiling identical tree-sitter queries across calls.
_QUERY_CACHE: Dict[str, tree_sitter.Query] = {}


def _escape_query_regex(regex: str) -> str:
    """Escape backslashes and double-quotes for safe embedding in tree-sitter regex literals."""
    return regex.replace("\\", "\\\\").replace('"', '\\"')


def _render_predicate(capture_name: str, regex: Optional[str]) -> str:
    """Build a tree-sitter ``#match?`` predicate string, or return empty if *regex* is falsy."""
    if not regex:
        return ""
    safe_regex = _escape_query_regex(regex)
    return f'(#match? {capture_name} "{safe_regex}")'


def _render_template(template: str, replacements: Dict[str, str]) -> str:
    """Substitute ``{{KEY}}`` placeholders in *template* with values from *replacements*."""
    rendered = template
    for key, value in replacements.items():
        # Placeholders use double-brace syntax, e.g. {{CALLEE_PREDICATE}}
        rendered = rendered.replace(f"{{{{{key}}}}}", value)
    return rendered


def _load_template(path: Path) -> str:
    """Read a ``.scm`` template file from disk."""
    return path.read_text(encoding="utf-8")


def _definition_hash(feature_spec: FeatureSpec) -> str:
    """Compute a deterministic SHA-256 hex digest for cache-key derivation.

    Args:
        feature_spec: The feature specification whose fields are serialised
            into a canonical JSON payload before hashing.

    Returns:
        A 64-character lowercase hex string uniquely identifying the spec.
    """
    payload = {
        "capability_key": feature_spec.capability_key,
        "operation_key": feature_spec.operation_key,
        "library": feature_spec.library,
        "absolute_paths": feature_spec.absolute_paths,
        "target_level": feature_spec.target_level.value,
        "concept": feature_spec.concept.value,
        "locator_strategy": feature_spec.locator_strategy.value,
        "construct_query": feature_spec.construct_query,
    }
    # sort_keys + compact separators guarantee a stable byte representation.
    payload_json = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload_json.encode("utf-8")).hexdigest()


class TypeScriptFrameworkQueryBuilder:
    """Builds tree-sitter queries for TypeScript framework detection."""

    def __init__(self) -> None:
        self._language = get_language("typescript")  # type: ignore[arg-type]

    def build_query(self, feature_spec: FeatureSpec) -> tree_sitter.Query:
        """Build (or retrieve from cache) a compiled tree-sitter query for a feature.

        Args:
            feature_spec: Declarative specification describing which syntactic
                construct to match (decorator, call expression, inheritance, etc.).

        Returns:
            A compiled ``tree_sitter.Query`` ready to execute against a parse tree.

        Raises:
            ValueError: If the concept in *feature_spec* is not supported.
            KeyError: If the resolved template key has no corresponding template file.
        """
        template_key = self._resolve_template_key(feature_spec.concept)
        template_path = _TEMPLATE_PATHS[template_key]
        template = _load_template(template_path)
        query_source = self._render_query(template, feature_spec)
        cache_key = f"{template_key}:{_definition_hash(feature_spec)}"

        if cache_key not in _QUERY_CACHE:
            _QUERY_CACHE[cache_key] = tree_sitter.Query(self._language, query_source)

        return _QUERY_CACHE[cache_key]

    def _construct_query_config(
        self, feature_spec: FeatureSpec
    ) -> ConstructQueryConfig:
        """Extract a typed ConstructQueryConfig, falling back to an empty default."""
        construct_query = feature_spec.construct_query_typed
        if construct_query is not None:
            return construct_query
        return ConstructQueryConfig.model_validate({})

    def _render_query(self, template: str, feature_spec: FeatureSpec) -> str:
        """Build predicate strings from the feature spec and render the template."""
        construct_query = self._construct_query_config(feature_spec)

        export_name_predicate = _render_predicate(
            "@export_name", construct_query.export_name_regex
        )
        function_name_predicate = _render_predicate(
            "@function_name", construct_query.function_name_regex
        )
        callee_predicate = _render_predicate("@callee", construct_query.callee_regex)
        superclass_predicate = _render_predicate(
            "@superclass", construct_query.superclass_regex
        )
        # annotation_name_regex takes precedence; method_regex is the fallback.
        annotation_regex = (
            construct_query.annotation_name_regex or construct_query.method_regex
        )
        annotation_name_predicate = _render_predicate(
            "@decorator_name", annotation_regex
        )
        annotation_method_predicate = _render_predicate(
            "@decorator_method", annotation_regex
        )

        replacements = {
            "EXPORT_NAME_PREDICATE": export_name_predicate,
            "FUNCTION_NAME_PREDICATE": function_name_predicate,
            "CALLEE_PREDICATE": callee_predicate,
            "SUPERCLASS_PREDICATE": superclass_predicate,
            "ANNOTATION_NAME_PREDICATE": annotation_name_predicate,
            "ANNOTATION_METHOD_PREDICATE": annotation_method_predicate,
        }

        return _render_template(template, replacements)

    def _resolve_template_key(self, concept: Concept) -> str:
        """Map a Concept enum value to the corresponding template key.

        Args:
            concept: The syntactic concept to resolve.

        Returns:
            A string key present in ``_TEMPLATE_PATHS``.

        Raises:
            ValueError: If *concept* is not handled by this builder.
        """
        if concept == Concept.FUNCTION_DEFINITION:
            return "function_definition"
        if concept == Concept.CALL_EXPRESSION:
            return "call_expression"
        if concept == Concept.INHERITANCE:
            return "inheritance"
        if concept == Concept.ANNOTATION_LIKE:
            return "annotation_like"
        raise ValueError(
            f"TypeScriptFrameworkQueryBuilder does not support concept: {concept.value}"
        )
