"""PostgreSQL repository for data model file queries."""

from __future__ import annotations

from collections import defaultdict
from typing import DefaultDict, Dict, Iterable, List, Mapping, Sequence, Tuple

from loguru import logger
from pydantic import BaseModel, Field, ValidationError, field_validator, model_validator
from sqlalchemy import select

from unoplat_code_confluence_commons.relational_models import (
    UnoplatCodeConfluenceCodebase,
    UnoplatCodeConfluenceFile,
    UnoplatCodeConfluenceFileFrameworkFeature,
)
from unoplat_code_confluence_query_engine.db.postgres.db import get_startup_session

DataModelSpanMap = Dict[str, Dict[str, Tuple[int, int]]]


class _DataModelSpan(BaseModel):
    file_path: str
    start_line: int
    end_line: int
    identifier: str | None = None


class _DataModelPositionsPayload(BaseModel):
    positions: dict[str, tuple[int, int]] = Field(default_factory=dict)

    @model_validator(mode="before")
    @classmethod
    def normalize_payload(cls, data: object) -> object:
        if isinstance(data, Mapping):
            if "positions" in data:
                return data
            return {"positions": data}
        return data

    @field_validator("positions", mode="before")
    @classmethod
    def normalize_positions(cls, value: object) -> dict[str, tuple[int, int]]:
        if not isinstance(value, Mapping):
            return {}
        positions: dict[str, tuple[int, int]] = {}
        for key, entry in value.items():
            if not isinstance(key, str):
                continue
            if not isinstance(entry, Sequence) or isinstance(entry, (str, bytes)):
                continue
            if len(entry) != 2:
                continue
            start_val = entry[0]
            end_val = entry[1]
            if not isinstance(start_val, int) or not isinstance(end_val, int):
                continue
            if start_val == end_val:
                continue
            positions[key] = (start_val, end_val)
        return positions


def _parse_data_model_positions(
    file_path: str, raw_positions: object | None
) -> List[_DataModelSpan]:
    if raw_positions is None:
        return []

    try:
        if isinstance(raw_positions, str):
            payload = _DataModelPositionsPayload.model_validate_json(raw_positions)
        else:
            payload = _DataModelPositionsPayload.model_validate(raw_positions)
    except ValidationError:
        return []

    spans: List[_DataModelSpan] = []
    for identifier, (start_line, end_line) in payload.positions.items():
        spans.append(
            _DataModelSpan(
                file_path=file_path,
                start_line=start_line,
                end_line=end_line,
                identifier=identifier,
            )
        )
    return spans


def _deduplicate_spans(spans: Iterable[_DataModelSpan]) -> List[_DataModelSpan]:
    span_map: dict[tuple[str, int, int], _DataModelSpan] = {}
    for span in spans:
        key = (span.file_path, span.start_line, span.end_line)
        existing = span_map.get(key)
        if existing is None:
            span_map[key] = span
        elif existing.identifier is None and span.identifier is not None:
            span_map[key] = span
    return list(span_map.values())


async def db_get_data_model_files(codebase_path: str) -> DataModelSpanMap:
    """Fetch data model spans for a codebase grouped by file."""
    if not codebase_path:
        return {}

    spans: List[_DataModelSpan] = []

    async with get_startup_session() as session:
        direct_stmt = (
            select(
                UnoplatCodeConfluenceFile.file_path,
                UnoplatCodeConfluenceFile.data_model_positions,
            )
            .join(
                UnoplatCodeConfluenceCodebase,
                UnoplatCodeConfluenceCodebase.qualified_name
                == UnoplatCodeConfluenceFile.codebase_qualified_name,
            )
            .where(UnoplatCodeConfluenceCodebase.codebase_path == codebase_path)
            .where(UnoplatCodeConfluenceFile.has_data_model.is_(True))
        )
        direct_result = await session.execute(direct_stmt)
        for file_path, raw_positions in direct_result.tuples().all():
            spans.extend(_parse_data_model_positions(file_path, raw_positions))

        feature_stmt = (
            select(
                UnoplatCodeConfluenceFileFrameworkFeature.file_path,
                UnoplatCodeConfluenceFileFrameworkFeature.start_line,
                UnoplatCodeConfluenceFileFrameworkFeature.end_line,
                UnoplatCodeConfluenceFileFrameworkFeature.match_text,
                UnoplatCodeConfluenceFileFrameworkFeature.feature_key,
            )
            .join(
                UnoplatCodeConfluenceFile,
                UnoplatCodeConfluenceFile.file_path
                == UnoplatCodeConfluenceFileFrameworkFeature.file_path,
            )
            .join(
                UnoplatCodeConfluenceCodebase,
                UnoplatCodeConfluenceCodebase.qualified_name
                == UnoplatCodeConfluenceFile.codebase_qualified_name,
            )
            .where(UnoplatCodeConfluenceCodebase.codebase_path == codebase_path)
            .where(
                UnoplatCodeConfluenceFileFrameworkFeature.feature_key.in_(
                    ["data_model", "db_data_model"]
                )
            )
        )
        feature_result = await session.execute(feature_stmt)
        for file_path, start_line, end_line, match_text, feature_key in (
            feature_result.tuples().all()
        ):
            if start_line is None or end_line is None:
                continue
            identifier = (match_text or "").strip()
            if not identifier:
                identifier = f"feature:{feature_key}:{start_line}"
            spans.append(
                _DataModelSpan(
                    file_path=file_path,
                    start_line=int(start_line),
                    end_line=int(end_line),
                    identifier=identifier,
                )
            )

    deduped = _deduplicate_spans(spans)
    grouped: DefaultDict[str, Dict[str, Tuple[int, int]]] = defaultdict(dict)
    for span in deduped:
        if not span.identifier:
            continue
        grouped[span.file_path][span.identifier] = (span.start_line, span.end_line)

    final_result = {
        file_path: dict(sorted(models.items()))
        for file_path, models in sorted(grouped.items())
        if models
    }

    logger.info(
        "[db_get_data_model_files] Final result: {} files with data models",
        len(final_result),
    )
    return final_result
