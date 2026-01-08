"""Parallel source-based detection path for Python."""

from __future__ import annotations

import asyncio
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Tuple

import tree_sitter
from tree_sitter_language_pack import get_language
from unoplat_code_confluence_commons.base_models import (
    DataModelPosition,
    Detection,
    FeatureSpec,
)

from src.code_confluence_flow_bridge.engine.programming_language.python.python_source_context import (
    PythonSourceContext,
)
from src.code_confluence_flow_bridge.engine.programming_language.python.python_tree_sitter_framework_detector import (
    PythonTreeSitterFrameworkDetector,
)

_DATACLASS_QUERY_PATH = Path(__file__).resolve().parent / "queries" / "dataclasses.scm"


@lru_cache(maxsize=1)
def _get_dataclass_query() -> tree_sitter.Query:
    language = get_language("python")  # type: ignore[arg-type]
    query_source = _DATACLASS_QUERY_PATH.read_text(encoding="utf-8")
    return tree_sitter.Query(language, query_source)


def _detect_dataclasses(context: PythonSourceContext) -> DataModelPosition:
    cursor = tree_sitter.QueryCursor(_get_dataclass_query())
    matches = cursor.matches(context.root_node)

    positions: Dict[str, Tuple[int, int]] = {}

    for _pattern_index, captures in matches:
        class_nodes = captures.get("dataclass_definition")
        name_nodes = captures.get("dataclass_name")
        if not class_nodes or not name_nodes:
            continue

        class_node = class_nodes[0]
        name_node = name_nodes[0]

        name = context.source_bytes[name_node.start_byte : name_node.end_byte].decode(
            "utf-8", errors="ignore"
        )

        start_line = class_node.start_point[0] + 1
        end_line = class_node.end_point[0] + 1

        positions[name] = (start_line, end_line)

    return DataModelPosition(positions=positions)


async def detect_python_source_features(
    source_code: str, feature_specs: List[FeatureSpec]
) -> Tuple[List[Detection], bool, DataModelPosition, PythonSourceContext]:
    context = PythonSourceContext.from_source(source_code)
    detector = PythonTreeSitterFrameworkDetector()

    framework_task = asyncio.to_thread(detector.detect, context, feature_specs)
    dataclass_task = asyncio.to_thread(_detect_dataclasses, context)

    detections, data_model_positions = await asyncio.gather(
        framework_task, dataclass_task
    )

    has_data_model = bool(data_model_positions.positions)
    return detections, has_data_model, data_model_positions, context
