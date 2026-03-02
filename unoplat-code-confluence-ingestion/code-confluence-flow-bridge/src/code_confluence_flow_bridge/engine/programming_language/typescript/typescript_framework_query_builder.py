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


class TypeScriptFrameworkQueryBuilder:
    """Builds tree-sitter queries for TypeScript framework detection."""

    def __init__(self) -> None:
        self._language = get_language("typescript")  # type: ignore[arg-type]

    def build_query(self, feature_spec: FeatureSpec) -> tree_sitter.Query:
        if feature_spec.concept != Concept.FUNCTION_DEFINITION:
            raise ValueError(
                f"TypeScriptFrameworkQueryBuilder only supports FunctionDefinition concept, "
                f"got: {feature_spec.concept}"
            )

        template_path = _TEMPLATE_PATHS["function_definition"]
        template = _load_template(template_path)
        query_source = self._render_query(template, feature_spec)
        cache_key = f"function_definition:{_definition_hash(feature_spec)}"

        if cache_key not in _QUERY_CACHE:
            _QUERY_CACHE[cache_key] = tree_sitter.Query(self._language, query_source)

        return _QUERY_CACHE[cache_key]

    def _construct_query_config(
        self, feature_spec: FeatureSpec
    ) -> ConstructQueryConfig:
        construct_query = feature_spec.construct_query_typed
        if construct_query is not None:
            return construct_query
        return ConstructQueryConfig.model_validate({})

    def _render_query(self, template: str, feature_spec: FeatureSpec) -> str:
        construct_query = self._construct_query_config(feature_spec)

        export_name_predicate = _render_predicate(
            "@export_name", construct_query.export_name_regex
        )
        function_name_predicate = _render_predicate(
            "@function_name", construct_query.function_name_regex
        )

        replacements = {
            "EXPORT_NAME_PREDICATE": export_name_predicate,
            "FUNCTION_NAME_PREDICATE": function_name_predicate,
        }

        return _render_template(template, replacements)
