"""Python-specific data model detection strategy."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING, Dict, Optional, Tuple

import tree_sitter
from tree_sitter_language_pack import get_language, get_parser
from unoplat_code_confluence_commons.base_models import DataModelPosition

from src.code_confluence_flow_bridge.engine.detector.data_model_detector_strategy import (
    DataModelDetectorStrategy,
)
from src.code_confluence_flow_bridge.engine.programming_language.python.python_source_context import (
    PythonSourceContext,
)

if TYPE_CHECKING:
    from src.code_confluence_flow_bridge.engine.programming_language.typescript.typescript_source_context import (
        TypeScriptSourceContext,
    )


class PythonDataModelDetectorStrategy(DataModelDetectorStrategy):
    """Detects Python dataclass models via Tree-sitter queries."""

    _LANGUAGE_NAME = "python"
    _DATACLASS_QUERY_PATH = (
        Path(__file__).resolve().parent / "queries" / "dataclasses.scm"
    )

    def detect(
        self,
        source_context: "PythonSourceContext | TypeScriptSourceContext",
        structural_signature: Optional[object] = None,
    ) -> Tuple[bool, DataModelPosition]:
        """
        Detect Python dataclasses.

        Returns detections based on a dedicated Tree-sitter query.

        Args:
            source_context: Pre-parsed Python context. The existing tree is reused
                so the source is not re-parsed.
            structural_signature: Optional structural signature (unused)

        Returns:
            Tuple containing:
                - bool: True if dataclasses are detected
                - DataModelPosition: Positions keyed by dataclass name
        """
        _ = structural_signature  # unused in current detection path

        if not isinstance(source_context, PythonSourceContext):
            return False, DataModelPosition()

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
            _, query = _get_python_parser_and_query(
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
