"""Neo4j repository for querying data model files.

Follows the same async session + execute_read pattern as framework_overview_repository.
"""

from __future__ import annotations

from collections import defaultdict
from typing import DefaultDict, Dict, Tuple

from neo4j import AsyncManagedTransaction
from unoplat_code_confluence_commons.base_models import DataModelPosition

from unoplat_code_confluence_query_engine.db.neo4j.connection_manager import (
    CodeConfluenceGraphQueryEngine,
)

DataModelSpanMap = Dict[str, Dict[str, Tuple[int, int]]]


async def _txn_get_data_model_files(
    tx: AsyncManagedTransaction, codebase_path: str
) -> DataModelSpanMap:
    """Fetch data model spans for a codebase grouped by file."""

    grouped_spans: DefaultDict[str, Dict[str, Tuple[int, int]]] = defaultdict(dict)

    direct_query = """
    MATCH (f:CodeConfluenceFile)
    WHERE f.file_path STARTS WITH $codebase_path
      AND coalesce(f.has_data_model, false)
    RETURN f.file_path AS path, coalesce(f.data_model_positions, {}) AS positions
    """

    direct_result = await tx.run(direct_query, {"codebase_path": codebase_path})
    direct_records = await direct_result.data()

    for record in direct_records:
        path = record["path"]
        raw_positions = record.get("positions")

        if not raw_positions:
            continue

        # Deserialize DataModelPosition from JSON string
        try:
            data_model_pos = DataModelPosition.model_validate_json(raw_positions)
        except Exception:
            continue

        for identifier, span in data_model_pos.positions.items():
            if not identifier:
                continue
            start, end = span
            if start == end:
                continue
            grouped_spans[path][str(identifier)] = span

    feature_query = """
    MATCH (f:CodeConfluenceFile)-[rel:USES_FEATURE]->(feat:CodeConfluenceFrameworkFeature)
    WHERE f.file_path STARTS WITH $codebase_path
      AND feat.feature_key IN ['data_model', 'db_data_model']
    RETURN
        f.file_path AS path,
        rel.match_text AS match_text,
        rel.start_line AS start_line,
        rel.end_line AS end_line,
        feat.feature_key AS feature_key
    """

    feature_result = await tx.run(feature_query, {"codebase_path": codebase_path})
    feature_records = await feature_result.data()

    for record in feature_records:
        path = record["path"]
        match_text = (record.get("match_text") or "").strip()
        feature_key = record.get("feature_key") or "data_model"
        identifier = (
            match_text or f"feature:{feature_key}:{record.get('start_line', 'unknown')}"
        )

        if not identifier:
            continue

        # Direct integer properties from Neo4j relationship
        start_line = record.get("start_line")
        end_line = record.get("end_line")

        if start_line is None or end_line is None:
            continue

        start = int(start_line)
        end = int(end_line)

        if start == end:
            continue

        grouped_spans[path][identifier] = (start, end)

    return {
        file_path: dict(sorted(models.items()))
        for file_path, models in sorted(grouped_spans.items())
        if models
    }


async def db_get_data_model_files(
    neo4j_manager: CodeConfluenceGraphQueryEngine,
    codebase_path: str,
) -> DataModelSpanMap:
    """Public API to fetch data model spans for a codebase."""
    async with neo4j_manager.get_session() as session:
        return await session.execute_read(_txn_get_data_model_files, codebase_path)
