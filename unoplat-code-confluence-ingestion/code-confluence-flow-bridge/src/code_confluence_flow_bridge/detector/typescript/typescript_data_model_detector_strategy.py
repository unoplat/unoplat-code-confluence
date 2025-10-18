"""TypeScript-specific data model detection strategy."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import re
from typing import Dict, List, Optional, Tuple

import tree_sitter
from tree_sitter_language_pack import get_language, get_parser
from unoplat_code_confluence_commons.base_models import (
    DataModelPosition,
    TypeScriptStructuralSignature,
)

from src.code_confluence_flow_bridge.detector.data_model_detector_strategy import (
    DataModelDetectorStrategy,
)


class TypeScriptDataModelDetectorStrategy(DataModelDetectorStrategy):
    """Detects TypeScript data models (interfaces, types, Zod schemas, class-validator, etc.)."""

    _LANGUAGE_NAME = "typescript"
    _TYPES_QUERY_PATH = Path(__file__).resolve().parents[2] / "parser" / "queries" / "typescript" / "types.scm"

    def detect(
        self,
        source_code: str,
        imports: Optional[List[str]] = None,
        structural_signature: Optional[object] = None,
    ) -> Tuple[bool, DataModelPosition]:
        """
        Detect TypeScript data models.
        Currently focuses on structural constructs that map closely to data
        transfer models: interfaces and type aliases. Both structural signatures
        (if available) and direct Tree-sitter query execution (types.scm) are
        supported so detection works in standalone contexts.

        Args:
            source_code: The source code content
            imports: Optional list of import statement strings
            structural_signature: Optional structural signature for advanced detection

        Returns:
            Tuple containing:
                - bool: True if TypeScript data models are detected
                - DataModelPosition: Positions keyed by model name
        """
        positions: Dict[str, Tuple[int, int]] = {}

        if structural_signature is not None:
            positions.update(
                self._detect_from_structural_signature(structural_signature)
            )

        if not positions and source_code:
            positions.update(self._detect_with_tree_sitter(source_code))

        has_data_model = bool(positions)
        return (has_data_model, DataModelPosition(positions=positions))

    def _detect_from_structural_signature(
        self, structural_signature: object
    ) -> Dict[str, Tuple[int, int]]:
        """Extract interface/type alias metadata from TypeScript structural signature."""
        try:
            if isinstance(structural_signature, TypeScriptStructuralSignature):
                signature_obj = structural_signature
            elif isinstance(structural_signature, dict):
                signature_obj = TypeScriptStructuralSignature.model_validate(
                    structural_signature
                )
            elif isinstance(structural_signature, str):
                signature_obj = TypeScriptStructuralSignature.model_validate_json(
                    structural_signature
                )
            else:
                return {}
        except Exception:
            return {}

        positions: Dict[str, Tuple[int, int]] = {}

        for type_alias in signature_obj.type_aliases:
            if type_alias.signature is None or type_alias.start_line is None or type_alias.end_line is None:
                continue
            alias_name = self._extract_declared_name(
                type_alias.signature, keyword="type"
            )
            if alias_name:
                positions[alias_name] = (type_alias.start_line, type_alias.end_line)

        for interface in signature_obj.interfaces:
            if (
                interface.signature is None
                or interface.start_line is None
                or interface.end_line is None
            ):
                continue
            interface_name = self._extract_declared_name(
                interface.signature, keyword="interface"
            )
            if interface_name:
                positions[interface_name] = (interface.start_line, interface.end_line)

        return positions

    def _detect_with_tree_sitter(self, source_code: str) -> Dict[str, Tuple[int, int]]:
        """Run the types.scm query to extract interface/type alias ranges."""
        try:
            parser, query = _get_typescript_parser_and_query(self._TYPES_QUERY_PATH, self._LANGUAGE_NAME)
        except Exception:
            return {}

        source_bytes = source_code.encode("utf-8", errors="ignore")
        tree = parser.parse(source_bytes)
        root_node = tree.root_node

        positions: Dict[str, Tuple[int, int]] = {}

        for node, capture_name in query.captures(root_node):
            if capture_name == "type_alias":
                name = self._extract_name_from_node(
                    node, source_bytes, fallback_keyword="type"
                )
            elif capture_name == "interface":
                name = self._extract_name_from_node(
                    node, source_bytes, fallback_keyword="interface"
                )
            else:
                name = None

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

        # Fall back to parsing the raw text when field metadata is absent
        node_text = self._slice_source(source_bytes, node)
        return self._extract_declared_name(node_text, keyword=fallback_keyword)

    def _slice_source(self, source_bytes: bytes, node: tree_sitter.Node) -> str:
        """Slice raw source text for a node."""
        return source_bytes[node.start_byte : node.end_byte].decode("utf-8", errors="ignore")

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


@lru_cache(maxsize=1)
def _get_typescript_parser_and_query(
    query_path: Path, language_name: str
) -> Tuple[tree_sitter.Parser, tree_sitter.Query]:
    """Load the TypeScript parser and compile the types.scm query (cached)."""
    language = get_language(language_name)  # type: ignore[arg-type]
    parser = get_parser(language_name)  # type: ignore[arg-type]
    query_source = query_path.read_text(encoding="utf-8")
    query = language.query(query_source)
    return parser, query
