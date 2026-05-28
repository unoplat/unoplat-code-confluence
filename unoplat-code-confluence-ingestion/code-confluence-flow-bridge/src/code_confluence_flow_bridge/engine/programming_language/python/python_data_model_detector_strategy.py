"""Python-specific data model detection strategy."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple, override

import tree_sitter
from tree_sitter_language_pack import get_language
from unoplat_code_confluence_commons.base_models import DataModelPosition

from code_confluence_flow_bridge.engine.detector.data_model_detector_strategy import (
    DataModelDetectorStrategy,
)
from code_confluence_flow_bridge.engine.programming_language.common.source_context import (
    BaseSourceContext,
)


class PythonDataModelDetectorStrategy(DataModelDetectorStrategy):
    """Detects Python dataclass models via Tree-sitter queries."""

    _LANGUAGE_NAME = "python"
    _DATACLASS_QUERY_PATH = (
        Path(__file__).resolve().parent / "queries" / "dataclasses.scm"
    )

    @override
    def detect(
        self,
        source_context: BaseSourceContext,
    ) -> Tuple[bool, DataModelPosition]:
        """
        Detect Python dataclasses.

        Returns detections based on a dedicated Tree-sitter query.

        Args:
            source_context: Pre-parsed source context. The existing tree is reused
                so the source is not re-parsed.

        Returns:
            Tuple containing:
                - bool: True if dataclasses are detected
                - DataModelPosition: Positions keyed by dataclass name
        """
        positions = self._detect_dataclasses_from_root(
            source_context.root_node, source_context.source_bytes
        )

        has_data_model = bool(positions)
        return has_data_model, DataModelPosition(positions=positions)

    def _detect_dataclasses_from_root(
        self, root_node: tree_sitter.Node, source_bytes: bytes
    ) -> Dict[str, Tuple[int, int]]:
        """Run the dataclass query against an existing parsed root node."""
        try:
            query = _get_python_dataclass_query(
                self._DATACLASS_QUERY_PATH, self._LANGUAGE_NAME
            )
        except Exception:
            return {}

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

            name = source_bytes[name_node.start_byte : name_node.end_byte].decode(
                "utf-8", errors="ignore"
            )

            start_line = class_node.start_point[0] + 1
            end_line = class_node.end_point[0] + 1

            positions[name] = (start_line, end_line)

        return positions


def _get_python_dataclass_query(
    query_path: Path, language_name: str
) -> tree_sitter.Query:
    """Load the Python language and compile the dataclass query."""
    language = get_language(language_name)  # type: ignore[arg-type]
    query_source = query_path.read_text(encoding="utf-8")
    return tree_sitter.Query(language, query_source)
