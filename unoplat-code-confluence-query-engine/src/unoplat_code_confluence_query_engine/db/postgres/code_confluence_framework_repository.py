"""PostgreSQL repository for framework feature usage queries."""

from __future__ import annotations

import os
from collections import defaultdict
from pathlib import Path
from typing import AsyncIterator, Dict, List, Set, cast

from loguru import logger
from sqlalchemy import Float, and_, cast as sql_cast, not_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from unoplat_code_confluence_commons.base_models import (
    Concept,
    FrameworkFeature,
    ValidationStatus,
)
from unoplat_code_confluence_commons.relational_models import (
    UnoplatCodeConfluenceCodebase,
    UnoplatCodeConfluenceCodebaseFramework,
    UnoplatCodeConfluenceFile,
    UnoplatCodeConfluenceFileFrameworkFeature,
)

from unoplat_code_confluence_query_engine.db.postgres.db import get_startup_session
from unoplat_code_confluence_query_engine.models.repository.framework_feature_validation_models import (
    CallExpressionDiscoveryExistingSpan,
    CallExpressionDiscoveryOperation,
    CallExpressionDiscoveryTarget,
    DiscoveredFrameworkFeatureUsagesUpsertRequest,
    DiscoveredFrameworkFeatureUsagesUpsertResult,
    FrameworkFeatureIdentity,
    FrameworkFeatureUsageIdentity,
)
from unoplat_code_confluence_query_engine.services.repository.app_interfaces_mapper import (
    AppInterfaceFeatureRow,
)

LOW_CONFIDENCE_DISCOVERY_THRESHOLD = 0.70
_DATA_MODEL_CAPABILITY_KEYS: tuple[str, ...] = (
    "data_model",
    "relational_database",
    "data_validation",
)
_DATA_MODEL_OPERATION_KEYS: tuple[str, ...] = (
    "data_model",
    "db_data_model",
)


def _compose_feature_key(capability_key: str, operation_key: str) -> str:
    return f"{capability_key}.{operation_key}"


def _data_model_family_predicate(
    capability_column: object,
    operation_column: object,
) -> object:
    return and_(
        capability_column.in_(_DATA_MODEL_CAPABILITY_KEYS),
        operation_column.in_(_DATA_MODEL_OPERATION_KEYS),
    )


def _coerce_validation_status_or_pending(value: object) -> ValidationStatus:
    if isinstance(value, str):
        try:
            return ValidationStatus(value)
        except ValueError:
            return ValidationStatus.PENDING
    return ValidationStatus.PENDING


def _should_include_in_app_interface_mapping(
    *,
    concept: str,
    validation_status: ValidationStatus,
) -> bool:
    """CallExpression rows are accepted only after discovery completes."""
    return (
        concept != Concept.CALL_EXPRESSION.value
        or validation_status == ValidationStatus.COMPLETED
    )


def _coerce_validation_status(value: str) -> ValidationStatus:
    try:
        return ValidationStatus(value)
    except ValueError as exc:
        raise ValueError(f"Unsupported validation status value: {value!r}") from exc


def _is_transition_allowed(
    current_status: ValidationStatus,
    target_status: ValidationStatus,
) -> bool:
    transitions: dict[ValidationStatus, set[ValidationStatus]] = {
        ValidationStatus.PENDING: {
            ValidationStatus.COMPLETED,
            ValidationStatus.NEEDS_REVIEW,
        },
        ValidationStatus.NEEDS_REVIEW: {
            ValidationStatus.COMPLETED,
            ValidationStatus.NEEDS_REVIEW,
        },
        ValidationStatus.COMPLETED: {ValidationStatus.COMPLETED},
    }
    return target_status in transitions[current_status]


async def _get_framework_usage_row(
    session: AsyncSession,
    codebase_path: str,
    identity: FrameworkFeatureUsageIdentity,
) -> UnoplatCodeConfluenceFileFrameworkFeature | None:
    stmt = (
        select(UnoplatCodeConfluenceFileFrameworkFeature)
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
            UnoplatCodeConfluenceFileFrameworkFeature.file_path == identity.file_path
        )
        .where(
            UnoplatCodeConfluenceFileFrameworkFeature.feature_language
            == identity.feature_language
        )
        .where(
            UnoplatCodeConfluenceFileFrameworkFeature.feature_library
            == identity.feature_library
        )
        .where(
            UnoplatCodeConfluenceFileFrameworkFeature.feature_capability_key
            == identity.feature_capability_key
        )
        .where(
            UnoplatCodeConfluenceFileFrameworkFeature.feature_operation_key
            == identity.feature_operation_key
        )
        .where(
            UnoplatCodeConfluenceFileFrameworkFeature.start_line == identity.start_line
        )
        .where(UnoplatCodeConfluenceFileFrameworkFeature.end_line == identity.end_line)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def db_get_framework_with_features(
    codebase_path: str,
    library: str,
    programming_language: str | None = None,
) -> Dict[str, object]:
    """Fetch framework features and usage locations for a codebase/library.

    Returns a dict compatible with legacy consumers while carrying structured identity:
    {
      "library": str,
      "features": [
        {
          "feature_capability_key": str,
          "feature_operation_key": str,
          "feature_key": str,  # display convenience
          "startpoint": bool,
          "usages": [...],
        }
      ],
    }
    """
    if not codebase_path or not library:
        return {"library": library, "features": []}

    async with get_startup_session() as session:
        stmt = (
            select(
                FrameworkFeature.capability_key,
                FrameworkFeature.operation_key,
                FrameworkFeature.startpoint_sql_expression().label("startpoint"),
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
                        FrameworkFeature.capability_key
                        == UnoplatCodeConfluenceFileFrameworkFeature.feature_capability_key
                    )
                    & (
                        FrameworkFeature.operation_key
                        == UnoplatCodeConfluenceFileFrameworkFeature.feature_operation_key
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
            .where(
                not_(
                    _data_model_family_predicate(
                        FrameworkFeature.capability_key,
                        FrameworkFeature.operation_key,
                    )
                )
            )
        )

        if programming_language:
            stmt = stmt.where(FrameworkFeature.language == programming_language)

        result = await session.execute(stmt)
        rows = result.all()

    if not rows:
        return {"library": library, "features": []}

    feature_map: Dict[str, Dict[str, object]] = {}
    usage_seen: Dict[str, Set[tuple[str, int, int]]] = defaultdict(set)

    for (
        capability_key,
        operation_key,
        startpoint,
        file_path,
        start_line,
        end_line,
    ) in rows:
        feature_key_value = _compose_feature_key(
            str(capability_key),
            str(operation_key),
        )

        if not isinstance(startpoint, bool):
            raise TypeError(
                f"Invalid startpoint value for feature '{feature_key_value}': {startpoint!r}"
            )

        feature_entry = feature_map.setdefault(
            feature_key_value,
            {
                "feature_capability_key": str(capability_key),
                "feature_operation_key": str(operation_key),
                "feature_key": feature_key_value,
                "startpoint": startpoint,
                "usages": [],
            },
        )

        if file_path is None or start_line is None or end_line is None:
            continue

        usage_key = (file_path, int(start_line), int(end_line))
        if usage_key in usage_seen[feature_key_value]:
            continue

        usage_seen[feature_key_value].add(usage_key)
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


async def db_stream_all_framework_features_for_codebase(
    codebase_path: str,
    programming_language: str = "python",
) -> AsyncIterator[AppInterfaceFeatureRow]:
    """Stream app-interface-relevant framework feature usage rows for a codebase.

    This replaces the previous list materialization path. Rows are fetched through
    SQLAlchemy async streaming and yielded only after repository-level validation
    and app-interface inclusion filtering.
    """
    if not codebase_path:
        return

    streamed_rows = 0
    yielded_rows = 0

    async with get_startup_session() as session:
        stmt = (
            select(
                FrameworkFeature.library,
                FrameworkFeature.capability_key,
                FrameworkFeature.operation_key,
                FrameworkFeature.concept_sql_expression().label("concept"),
                FrameworkFeature.startpoint_sql_expression().label("startpoint"),
                UnoplatCodeConfluenceFileFrameworkFeature.file_path,
                UnoplatCodeConfluenceFileFrameworkFeature.start_line,
                UnoplatCodeConfluenceFileFrameworkFeature.end_line,
                UnoplatCodeConfluenceFileFrameworkFeature.match_text,
                UnoplatCodeConfluenceFileFrameworkFeature.match_confidence,
                UnoplatCodeConfluenceFileFrameworkFeature.validation_status,
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
                        FrameworkFeature.capability_key
                        == UnoplatCodeConfluenceFileFrameworkFeature.feature_capability_key
                    )
                    & (
                        FrameworkFeature.operation_key
                        == UnoplatCodeConfluenceFileFrameworkFeature.feature_operation_key
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
            .where(
                not_(
                    _data_model_family_predicate(
                        FrameworkFeature.capability_key,
                        FrameworkFeature.operation_key,
                    )
                )
            )
        )

        result = await session.stream(stmt)
        try:
            async for (
                library,
                capability_key,
                operation_key,
                concept,
                startpoint,
                file_path,
                start_line,
                end_line,
                match_text,
                match_confidence,
                validation_status,
            ) in result:
                streamed_rows += 1
                feature_capability_key = str(capability_key)
                feature_operation_key = str(operation_key)
                feature_key_value = _compose_feature_key(
                    feature_capability_key,
                    feature_operation_key,
                )

                if not isinstance(startpoint, bool):
                    raise TypeError(
                        "Invalid startpoint value for feature "
                        f"'{feature_key_value}': {startpoint!r}"
                    )

                if file_path is None or start_line is None or end_line is None:
                    continue

                if not _should_include_in_app_interface_mapping(
                    concept=str(concept),
                    validation_status=_coerce_validation_status_or_pending(
                        validation_status
                    ),
                ):
                    continue

                yielded_rows += 1
                yield AppInterfaceFeatureRow(
                    library=str(library) if library else None,
                    feature_capability_key=feature_capability_key,
                    feature_operation_key=feature_operation_key,
                    file_path=str(file_path),
                    start_line=int(start_line),
                    end_line=int(end_line),
                    match_text=str(match_text) if match_text else None,
                )
        finally:
            await result.close()

    if streamed_rows == 0:
        logger.debug(
            "No framework features found for codebase_path={} language={}",
            codebase_path,
            programming_language,
        )
    else:
        logger.debug(
            "Streamed {} framework feature rows and yielded {} app-interface rows "
            "for codebase_path={} language={}",
            streamed_rows,
            yielded_rows,
            codebase_path,
            programming_language,
        )


async def db_get_call_expression_discovery_targets(
    *,
    codebase_path: str,
    programming_language: str = "python",
) -> list[CallExpressionDiscoveryTarget]:
    """Return eligible catalog operations grouped under their capabilities.

    Catalog selection is deliberately independent of usage rows so an operation
    with no static spans is still examined once by the discoverer.
    """
    if not codebase_path:
        return []

    async with get_startup_session() as session:
        feature_stmt = (
            select(FrameworkFeature)
            .join(
                UnoplatCodeConfluenceCodebaseFramework,
                (
                    FrameworkFeature.language
                    == UnoplatCodeConfluenceCodebaseFramework.framework_language
                )
                & (
                    FrameworkFeature.library
                    == UnoplatCodeConfluenceCodebaseFramework.framework_library
                ),
            )
            .join(
                UnoplatCodeConfluenceCodebase,
                UnoplatCodeConfluenceCodebase.qualified_name
                == UnoplatCodeConfluenceCodebaseFramework.codebase_qualified_name,
            )
            .where(UnoplatCodeConfluenceCodebase.codebase_path == codebase_path)
            .where(FrameworkFeature.language == programming_language)
            .where(
                FrameworkFeature.concept_sql_expression()
                == Concept.CALL_EXPRESSION.value
            )
            .where(
                sql_cast(
                    FrameworkFeature.feature_definition["base_confidence"].astext, Float
                )
                < LOW_CONFIDENCE_DISCOVERY_THRESHOLD
            )
            .options(selectinload(FrameworkFeature.absolute_paths))
            .order_by(
                FrameworkFeature.library,
                FrameworkFeature.capability_key,
                FrameworkFeature.operation_key,
            )
        )
        features = list((await session.execute(feature_stmt)).scalars().unique())

        usage_stmt = (
            select(UnoplatCodeConfluenceFileFrameworkFeature)
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
                UnoplatCodeConfluenceFileFrameworkFeature.feature_language
                == programming_language
            )
            .order_by(
                UnoplatCodeConfluenceFileFrameworkFeature.feature_library,
                UnoplatCodeConfluenceFileFrameworkFeature.feature_capability_key,
                UnoplatCodeConfluenceFileFrameworkFeature.feature_operation_key,
                UnoplatCodeConfluenceFileFrameworkFeature.file_path,
                UnoplatCodeConfluenceFileFrameworkFeature.start_line,
                UnoplatCodeConfluenceFileFrameworkFeature.end_line,
            )
        )
        spans_by_operation: dict[
            tuple[str, str, str, str], list[CallExpressionDiscoveryExistingSpan]
        ] = defaultdict(list)
        for usage in (await session.execute(usage_stmt)).scalars():
            identity = (
                usage.feature_language,
                usage.feature_library,
                usage.feature_capability_key,
                usage.feature_operation_key,
            )
            spans_by_operation[identity].append(
                CallExpressionDiscoveryExistingSpan.model_validate(
                    usage, from_attributes=True
                )
            )

    grouped: dict[tuple[str, str, str], list[CallExpressionDiscoveryOperation]] = (
        defaultdict(list)
    )
    for feature in features:
        identity = (
            feature.language,
            feature.library,
            feature.capability_key,
            feature.operation_key,
        )
        grouped[identity[:3]].append(
            CallExpressionDiscoveryOperation(
                feature_operation_key=feature.operation_key,
                definition=feature.feature_definition,
                absolute_paths=[
                    path.absolute_path
                    for path in feature.absolute_paths
                    if isinstance(path.absolute_path, str)
                ],
                existing_spans=spans_by_operation[identity],
            )
        )
    targets = [
        CallExpressionDiscoveryTarget(
            feature_language=language,
            feature_library=library,
            feature_capability_key=capability,
            operations=operations,
        )
        for (language, library, capability), operations in grouped.items()
    ]
    logger.info(
        "Fetched {} CallExpression discovery capabilities for codebase_path={} language={}",
        len(targets),
        codebase_path,
        programming_language,
    )
    return targets


def _resolve_discovered_file_path(codebase_path: str, file_path: str) -> str:
    """Normalize a discovered path and require it to remain inside the codebase."""
    codebase_root = Path(os.path.abspath(codebase_path))
    candidate_path = Path(file_path)
    if not candidate_path.is_absolute():
        candidate_path = codebase_root / candidate_path
    normalized_path = Path(os.path.abspath(candidate_path))

    resolved_root = codebase_root.resolve(strict=False)
    resolved_path = normalized_path.resolve(strict=False)
    try:
        resolved_path.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError(
            f"Discovered usage path is outside the codebase: {file_path!r}"
        ) from exc
    return str(normalized_path)


async def _require_discovery_target_feature(
    session: AsyncSession,
    codebase_path: str,
    target: FrameworkFeatureIdentity,
) -> None:
    """Require a catalog feature whose library is evidenced for the codebase."""
    stmt = (
        select(FrameworkFeature.language)
        .join(
            UnoplatCodeConfluenceCodebaseFramework,
            (
                FrameworkFeature.language
                == UnoplatCodeConfluenceCodebaseFramework.framework_language
            )
            & (
                FrameworkFeature.library
                == UnoplatCodeConfluenceCodebaseFramework.framework_library
            ),
        )
        .join(
            UnoplatCodeConfluenceCodebase,
            UnoplatCodeConfluenceCodebase.qualified_name
            == UnoplatCodeConfluenceCodebaseFramework.codebase_qualified_name,
        )
        .where(UnoplatCodeConfluenceCodebase.codebase_path == codebase_path)
        .where(FrameworkFeature.language == target.feature_language)
        .where(FrameworkFeature.library == target.feature_library)
        .where(FrameworkFeature.capability_key == target.feature_capability_key)
        .where(FrameworkFeature.operation_key == target.feature_operation_key)
        .where(
            FrameworkFeature.feature_definition["concept"].astext
            == Concept.CALL_EXPRESSION.value
        )
        .where(
            sql_cast(
                FrameworkFeature.feature_definition["base_confidence"].astext,
                Float,
            )
            < LOW_CONFIDENCE_DISCOVERY_THRESHOLD
        )
    )
    if (await session.scalar(stmt)) is None:
        raise ValueError(
            "Discovery target feature is not cataloged for an evidenced codebase "
            f"framework: {target.feature_language}:{target.feature_library}:"
            f"{target.feature_key}"
        )


async def _require_codebase_file(
    session: AsyncSession,
    codebase_path: str,
    file_path: str,
) -> None:
    stmt = (
        select(UnoplatCodeConfluenceFile.file_path)
        .join(
            UnoplatCodeConfluenceCodebase,
            UnoplatCodeConfluenceCodebase.qualified_name
            == UnoplatCodeConfluenceFile.codebase_qualified_name,
        )
        .where(UnoplatCodeConfluenceCodebase.codebase_path == codebase_path)
        .where(UnoplatCodeConfluenceFile.file_path == file_path)
    )
    if (await session.scalar(stmt)) is None:
        raise ValueError(
            "Discovered usage file is not registered in the provided codebase: "
            f"{file_path}"
        )


async def db_upsert_discovered_framework_feature_usages(
    *,
    codebase_path: str,
    request: DiscoveredFrameworkFeatureUsagesUpsertRequest,
) -> DiscoveredFrameworkFeatureUsagesUpsertResult:
    """Persist confirmed discovered spans for an authorized framework feature."""
    async with get_startup_session() as session:
        target = request.target_feature_identity
        await _require_discovery_target_feature(session, codebase_path, target)

        created_count = 0
        updated_count = 0
        resolved_span_keys: set[tuple[str, int, int]] = set()

        for usage in request.usages:
            try:
                resolved_file_path = _resolve_discovered_file_path(
                    codebase_path,
                    usage.file_path,
                )
            except ValueError as exc:
                logger.error(
                    "Skipping discovered usage with path outside codebase: "
                    "submitted_path={} start_line={} end_line={} reason={}",
                    usage.file_path,
                    usage.start_line,
                    usage.end_line,
                    str(exc),
                )
                continue
            resolved_span_key = (
                resolved_file_path,
                usage.start_line,
                usage.end_line,
            )
            if resolved_span_key in resolved_span_keys:
                logger.error(
                    "Skipping duplicate discovered usage span after path resolution: "
                    "file_path={} start_line={} end_line={} submitted_path={}",
                    resolved_file_path,
                    usage.start_line,
                    usage.end_line,
                    usage.file_path,
                )
                continue
            resolved_span_keys.add(resolved_span_key)
            try:
                await _require_codebase_file(
                    session,
                    codebase_path,
                    resolved_file_path,
                )
            except ValueError as exc:
                logger.error(
                    "Skipping discovered usage with unregistered codebase file: "
                    "file_path={} start_line={} end_line={} submitted_path={} reason={}",
                    resolved_file_path,
                    usage.start_line,
                    usage.end_line,
                    usage.file_path,
                    str(exc),
                )
                continue
            identity = FrameworkFeatureUsageIdentity(
                file_path=resolved_file_path,
                feature_language=target.feature_language,
                feature_library=target.feature_library,
                feature_capability_key=target.feature_capability_key,
                feature_operation_key=target.feature_operation_key,
                start_line=usage.start_line,
                end_line=usage.end_line,
            )
            usage_row = await _get_framework_usage_row(
                session,
                codebase_path,
                identity,
            )
            if usage_row is None:
                usage_row = UnoplatCodeConfluenceFileFrameworkFeature(
                    file_path=identity.file_path,
                    feature_language=identity.feature_language,
                    feature_library=identity.feature_library,
                    feature_capability_key=identity.feature_capability_key,
                    feature_operation_key=identity.feature_operation_key,
                    start_line=identity.start_line,
                    end_line=identity.end_line,
                    match_text=usage.match_text,
                    match_confidence=usage.final_confidence,
                    validation_status=ValidationStatus.COMPLETED.value,
                    evidence_json=None,
                )
                session.add(usage_row)
                created_count += 1
            else:
                usage_row.match_text = usage.match_text
                usage_row.match_confidence = usage.final_confidence
                usage_row.validation_status = ValidationStatus.COMPLETED.value
                updated_count += 1
        return DiscoveredFrameworkFeatureUsagesUpsertResult(
            created_count=created_count,
            updated_count=updated_count,
        )
