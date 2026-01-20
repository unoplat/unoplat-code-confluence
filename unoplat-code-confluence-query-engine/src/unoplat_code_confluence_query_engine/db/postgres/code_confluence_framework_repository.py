"""PostgreSQL repository for framework feature usage queries."""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Set, cast

from loguru import logger
from sqlalchemy import select
from unoplat_code_confluence_commons.base_models import FrameworkFeature
from unoplat_code_confluence_commons.relational_models import (
    UnoplatCodeConfluenceCodebase,
    UnoplatCodeConfluenceFile,
    UnoplatCodeConfluenceFileFrameworkFeature,
)

from unoplat_code_confluence_query_engine.db.postgres.db import get_startup_session


async def db_get_framework_with_features(
    codebase_path: str,
    library: str,
    programming_language: str | None = None,
) -> Dict[str, object]:
    """Fetch framework features and usage locations for a codebase/library.

    Returns a dict shaped like the legacy graph repository:
    {"library": str, "features": [{"feature_key": str, "startpoint": bool, "usages": [...] }]}
    """
    if not codebase_path or not library:
        return {"library": library, "features": []}

    async with get_startup_session() as session:
        stmt = (
            select(
                FrameworkFeature.feature_key,
                FrameworkFeature.startpoint,
                UnoplatCodeConfluenceFileFrameworkFeature.file_path,
                UnoplatCodeConfluenceFileFrameworkFeature.start_line,
                UnoplatCodeConfluenceFileFrameworkFeature.end_line,
            )
            .join(
                UnoplatCodeConfluenceFileFrameworkFeature,
                (
                    (
                        FrameworkFeature.language
                        == UnoplatCodeConfluenceFileFrameworkFeature.feature_language
                    )
                    & (
                        FrameworkFeature.library
                        == UnoplatCodeConfluenceFileFrameworkFeature.feature_library
                    )
                    & (
                        FrameworkFeature.feature_key
                        == UnoplatCodeConfluenceFileFrameworkFeature.feature_key
                    )
                ),
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
            .where(FrameworkFeature.library == library)
            .where(~FrameworkFeature.feature_key.in_(["data_model", "db_data_model"]))
        )

        if programming_language:
            stmt = stmt.where(FrameworkFeature.language == programming_language)

        result = await session.execute(stmt)
        rows = result.all()

    if not rows:
        return {"library": library, "features": []}

    feature_map: Dict[str, Dict[str, object]] = {}
    usage_seen: Dict[str, Set[tuple[str, int, int]]] = defaultdict(set)

    for feature_key, startpoint, file_path, start_line, end_line in rows:
        feature_entry = feature_map.setdefault(
            feature_key,
            {
                "feature_key": feature_key,
                "startpoint": bool(startpoint),
                "usages": [],
            },
        )

        if file_path is None or start_line is None or end_line is None:
            continue

        usage_key = (file_path, int(start_line), int(end_line))
        if usage_key in usage_seen[feature_key]:
            continue

        usage_seen[feature_key].add(usage_key)
        usages = cast(List[Dict[str, int | str]], feature_entry["usages"])
        usages.append(
            {
                "file_path": file_path,
                "start_line": int(start_line),
                "end_line": int(end_line),
            }
        )

    features = list(feature_map.values())
    logger.debug(
        "Fetched {} features for library={} codebase_path={}",
        len(features),
        library,
        codebase_path,
    )

    return {"library": library, "features": features}
