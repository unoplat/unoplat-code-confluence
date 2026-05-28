"""TypeScript-specific data model detection strategy."""

from __future__ import annotations

from pathlib import Path
import re
from typing import Dict, Optional, Tuple

import tree_sitter
from tree_sitter import QueryCursor
from tree_sitter_language_pack import get_language
from unoplat_code_confluence_commons.base_models import DataModelPosition

from code_confluence_flow_bridge.engine.detector.data_model_detector_strategy import (
    DataModelDetectorStrategy,
)
from code_confluence_flow_bridge.engine.programming_language.common.source_context import (
    BaseSourceContext,
)


class TypeScriptDataModelDetectorStrategy(DataModelDetectorStrategy):
    """Detects TypeScript data models with the active types.scm query."""

    _LANGUAGE_NAME = "typescript"
    _TYPES_QUERY_PATH = Path(__file__).resolve().parent / "queries" / "types.scm"

    def detect(
        self,
        source_context: BaseSourceContext,
    ) -> Tuple[bool, DataModelPosition]:
        """
        Detect TypeScript data models from the parsed tree-sitter root.

        Args:
            source_context: Pre-parsed source context containing source
                bytes, imports, import aliases, and the tree-sitter root.

        Returns:
            Tuple containing:
                - bool: True if TypeScript data models are detected
                - DataModelPosition: Positions keyed by model name
        """
        positions = self._detect_from_root(
            source_context.root_node, source_context.source_bytes
        )
        has_data_model = bool(positions)
        return (has_data_model, DataModelPosition(positions=positions))

    def _detect_from_root(
        self, root_node: tree_sitter.Node, source_bytes: bytes
    ) -> Dict[str, Tuple[int, int]]:
        """Run the types.scm query against an existing parsed root node."""
        try:
            query = _get_typescript_types_query(
                self._TYPES_QUERY_PATH, self._LANGUAGE_NAME
            )
        except Exception:
            return {}

        positions: Dict[str, Tuple[int, int]] = {}
        cursor = QueryCursor(query)
        captures_dict = cursor.captures(root_node)  # type: ignore[attr-defined]

        for node in captures_dict.get("type_alias", []):
            name = self._extract_name_from_node(
                node, source_bytes, fallback_keyword="type"
            )
            if name:
                positions[name] = (
                    node.start_point[0] + 1,
                    node.end_point[0] + 1,
                )

        for node in captures_dict.get("interface", []):
            name = self._extract_name_from_node(
                node, source_bytes, fallback_keyword="interface"
            )
            if name:
                positions[name] = (
                    node.start_point[0] + 1,
                    node.end_point[0] + 1,
                )

        return positions

    def _extract_name_from_node(
        self, node: tree_sitter.Node, source_bytes: bytes, fallback_keyword: str
    ) -> Optional[str]:
        """Extract identifier from a captured AST node."""
        name_node = node.child_by_field_name("name")
        if name_node is not None:
            return self._slice_source(source_bytes, name_node).strip()

        node_text = self._slice_source(source_bytes, node)
        return self._extract_declared_name(node_text, keyword=fallback_keyword)

    def _slice_source(self, source_bytes: bytes, node: tree_sitter.Node) -> str:
        """Slice raw source text for a node."""
        return source_bytes[node.start_byte : node.end_byte].decode(
            "utf-8", errors="ignore"
        )

    @staticmethod
    def _extract_declared_name(signature: str, keyword: str) -> Optional[str]:
        """Extract declared identifier name from a signature snippet."""
        pattern = re.compile(
            rf"\b(?:export\s+|declare\s+)*{keyword}\s+([A-Za-z_$][\w$]*)"
        )
        match = pattern.search(signature)
        if match:
            return match.group(1)
        return None


def _get_typescript_types_query(
    query_path: Path, language_name: str
) -> tree_sitter.Query:
    """Load the TypeScript language and compile the types.scm query."""
    language = get_language(language_name)  # type: ignore[arg-type]
    query_source = query_path.read_text(encoding="utf-8")
    return tree_sitter.Query(language, query_source)
