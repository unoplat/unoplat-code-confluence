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


async def db_get_all_framework_features_for_codebase(
    codebase_path: str,
    programming_language: str = "python",
) -> list[dict[str, object]]:
    """Fetch all framework features with usage locations for a codebase.

    Args:
        codebase_path: Path to the codebase for lookup
        programming_language: Programming language filter (default: python)

    Returns:
        List of dicts containing library, feature_key, startpoint, file_path,
        start_line, end_line, and match_text for each feature usage.
    """
    if not codebase_path:
        return []

    async with get_startup_session() as session:
        stmt = (
            select(
                FrameworkFeature.library,
                FrameworkFeature.feature_key,
                FrameworkFeature.startpoint,
                UnoplatCodeConfluenceFileFrameworkFeature.file_path,
                UnoplatCodeConfluenceFileFrameworkFeature.start_line,
                UnoplatCodeConfluenceFileFrameworkFeature.end_line,
                UnoplatCodeConfluenceFileFrameworkFeature.match_text,
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
            .where(FrameworkFeature.language == programming_language)
            .where(~FrameworkFeature.feature_key.in_(["data_model", "db_data_model"]))
        )

        result = await session.execute(stmt)
        rows = result.all()

    if not rows:
        logger.debug(
            "No framework features found for codebase_path={} language={}",
            codebase_path,
            programming_language,
        )
        return []

    features: list[dict[str, object]] = []
    for library, feature_key, startpoint, file_path, start_line, end_line, match_text in rows:
        if file_path is None or start_line is None or end_line is None:
            continue

        features.append({
            "library": library,
            "feature_key": feature_key,
            "startpoint": bool(startpoint) if startpoint is not None else False,
            "file_path": file_path,
            "start_line": int(start_line),
            "end_line": int(end_line),
            "match_text": match_text,
        })

    logger.debug(
        "Fetched {} framework features for codebase_path={} language={}",
        len(features),
        codebase_path,
        programming_language,
    )

    return features
