"""Python-specific data model detection strategy."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import tree_sitter
from tree_sitter_language_pack import get_language, get_parser
from unoplat_code_confluence_commons.base_models import DataModelPosition

from src.code_confluence_flow_bridge.detector.data_model_detector_strategy import (
    DataModelDetectorStrategy,
)


class PythonDataModelDetectorStrategy(DataModelDetectorStrategy):
    """Detects Python dataclass models via Tree-sitter queries."""

    _LANGUAGE_NAME = "python"
    _DATACLASS_QUERY_PATH = (
        Path(__file__).resolve().parents[2]
        / "parser"
        / "queries"
        / "python"
        / "dataclasses.scm"
    )

    def detect(
        self,
        source_code: str,
        imports: Optional[List[str]] = None,
        structural_signature: Optional[object] = None,
    ) -> Tuple[bool, DataModelPosition]:
        """
        Detect Python dataclasses.

        Returns detections based on a dedicated Tree-sitter query.

        Args:
            source_code: The Python source code to analyze
            imports: Optional list of import statements (unused)
            structural_signature: Optional structural signature (unused)

        Returns:
            Tuple containing:
                - bool: True if dataclasses are detected
                - DataModelPosition: Positions keyed by dataclass name
        """
        _ = imports, structural_signature  # unused in current detection path
        positions = self._detect_dataclasses_with_tree_sitter(source_code)

        has_data_model = bool(positions)
        return has_data_model, DataModelPosition(positions=positions)

    def _detect_dataclasses_with_tree_sitter(
        self, source_code: str
    ) -> Dict[str, Tuple[int, int]]:
        """Use Tree-sitter query to locate dataclass definitions."""
        if not source_code.strip():
            return {}

        try:
            parser, query = _get_python_parser_and_query(
                self._DATACLASS_QUERY_PATH, self._LANGUAGE_NAME
            )
        except Exception:
            return {}

        source_bytes = source_code.encode("utf-8", errors="ignore")
        tree = parser.parse(source_bytes)
        root_node = tree.root_node

        cursor = tree_sitter.QueryCursor(query)
        matches = cursor.matches(root_node)

        positions: Dict[str, Tuple[int, int]] = {}

        for _, captures in matches:
            class_nodes = captures.get("dataclass_definition")
            name_nodes = captures.get("dataclass_name")

            if not class_nodes or not name_nodes:
                continue

            class_node = class_nodes[0]
            name_node = name_nodes[0]

            name = source_bytes[name_node.start_byte:name_node.end_byte].decode(
                "utf-8", errors="ignore"
            )

            start_line = class_node.start_point[0] + 1
            end_line = class_node.end_point[0] + 1

            positions[name] = (start_line, end_line)

        return positions


@lru_cache(maxsize=1)
def _get_python_parser_and_query(
    query_path: Path, language_name: str
) -> Tuple[tree_sitter.Parser, tree_sitter.Query]:
    """Load the Python parser and compile the dataclass query."""
    language = get_language(language_name)  # type: ignore[arg-type]
    parser = get_parser(language_name)  # type: ignore[arg-type]
    query_source = query_path.read_text(encoding="utf-8")
    query = tree_sitter.Query(language, query_source)
    return parser, query
