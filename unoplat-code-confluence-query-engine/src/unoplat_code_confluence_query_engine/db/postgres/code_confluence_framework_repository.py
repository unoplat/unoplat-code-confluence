"""PostgreSQL repository for framework feature usage queries."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import AsyncIterator, Dict, List, Mapping, Set, cast

from loguru import logger
from sqlalchemy import and_, not_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from unoplat_code_confluence_commons.base_models import (
    Concept,
    FrameworkFeature,
    ValidationStatus,
)
from unoplat_code_confluence_commons.relational_models import (
    UnoplatCodeConfluenceCodebase,
    UnoplatCodeConfluenceFile,
    UnoplatCodeConfluenceFileFrameworkFeature,
)

from unoplat_code_confluence_query_engine.db.postgres.db import get_startup_session
from unoplat_code_confluence_query_engine.models.repository.framework_feature_validation_models import (
    FrameworkFeatureUsageIdentity,
    FrameworkFeatureValidationCandidate,
    FrameworkFeatureValidationDecision,
    FrameworkFeatureValidationEvidenceUpsertRequest,
    FrameworkFeatureValidationEvidenceUpsertResult,
    FrameworkFeatureValidationStatusTransitionRequest,
    FrameworkFeatureValidationStatusTransitionResult,
)
from unoplat_code_confluence_query_engine.services.repository.app_interfaces_mapper import (
    AppInterfaceFeatureRow,
)

LOW_CONFIDENCE_VALIDATION_THRESHOLD = 0.70
VALIDATOR_ACCEPT_DECISIONS: frozenset[str] = frozenset({"confirm", "correct"})
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


def _copy_mapping(payload: Mapping[str, object]) -> dict[str, object]:
    return {key: value for key, value in payload.items()}


def _build_validator_payload(
    *,
    decision: FrameworkFeatureValidationDecision,
    final_confidence: float,
    evidence_json: Mapping[str, object],
    corrected_file_path: str | None = None,
    corrected_start_line: int | None = None,
    corrected_end_line: int | None = None,
    corrected_match_text: str | None = None,
) -> dict[str, object]:
    payload = _copy_mapping(evidence_json)
    payload["decision"] = decision.value
    payload["final_confidence"] = float(final_confidence)
    payload["recorded_at_utc"] = datetime.now(timezone.utc).isoformat()
    if corrected_file_path is not None:
        payload["corrected_file_path"] = corrected_file_path
    if corrected_start_line is not None:
        payload["corrected_start_line"] = corrected_start_line
    if corrected_end_line is not None:
        payload["corrected_end_line"] = corrected_end_line
    if corrected_match_text is not None:
        payload["corrected_match_text"] = corrected_match_text
    return payload


def _merge_evidence_json(
    existing_evidence: object,
    validator_payload: Mapping[str, object],
) -> dict[str, object]:
    merged: dict[str, object] = {}
    if isinstance(existing_evidence, dict):
        existing_map = cast(dict[str, object], existing_evidence)
        for key, value in existing_map.items():
            merged[key] = value
    merged["validator"] = _copy_mapping(validator_payload)
    return merged


def _extract_validator_decision(evidence_json: object) -> str | None:
    if not isinstance(evidence_json, dict):
        return None

    evidence_map = cast(dict[str, object], evidence_json)
    validator_payload = evidence_map.get("validator")
    if isinstance(validator_payload, dict):
        validator_map = cast(dict[str, object], validator_payload)
        decision = validator_map.get("decision")
        if isinstance(decision, str):
            return decision

    root_decision = evidence_map.get("decision")
    if isinstance(root_decision, str):
        return root_decision

    return None


def _coerce_validation_status_or_pending(value: object) -> ValidationStatus:
    if isinstance(value, str):
        try:
            return ValidationStatus(value)
        except ValueError:
            return ValidationStatus.PENDING
    return ValidationStatus.PENDING


def _require_call_expression_base_confidence(feature: FrameworkFeature) -> float:
    return float(feature.base_confidence)


def _should_include_in_app_interface_mapping(
    *,
    concept: str,
    match_confidence: float,
    validation_status: ValidationStatus,
    evidence_json: object,
) -> bool:
    if concept != Concept.CALL_EXPRESSION.value:
        return True

    decision = _extract_validator_decision(evidence_json)
    if decision is not None:
        if validation_status != ValidationStatus.COMPLETED:
            return False
        return decision in VALIDATOR_ACCEPT_DECISIONS

    if match_confidence >= LOW_CONFIDENCE_VALIDATION_THRESHOLD:
        return True

    return False


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
                UnoplatCodeConfluenceFileFrameworkFeature.evidence_json,
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
                evidence_json,
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
                    match_confidence=float(match_confidence),
                    validation_status=_coerce_validation_status_or_pending(
                        validation_status
                    ),
                    evidence_json=evidence_json,
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


async def db_get_low_confidence_call_expression_candidates(
    *,
    codebase_path: str,
    programming_language: str = "python",
    confidence_threshold: float = LOW_CONFIDENCE_VALIDATION_THRESHOLD,
) -> list[FrameworkFeatureValidationCandidate]:
    """Fetch low-confidence CallExpression rows that require validator execution."""
    if not codebase_path:
        return []

    async with get_startup_session() as session:
        stmt = (
            select(
                FrameworkFeature,
                UnoplatCodeConfluenceFileFrameworkFeature,
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
                FrameworkFeature.concept_sql_expression()
                == Concept.CALL_EXPRESSION.value
            )
            .where(
                UnoplatCodeConfluenceFileFrameworkFeature.match_confidence
                < confidence_threshold
            )
            .where(
                UnoplatCodeConfluenceFileFrameworkFeature.validation_status.in_(
                    [
                        ValidationStatus.PENDING.value,
                        ValidationStatus.NEEDS_REVIEW.value,
                    ]
                )
            )
            .options(selectinload(FrameworkFeature.absolute_paths))
        )

        result = await session.execute(stmt)
        rows = result.all()

        candidates: list[FrameworkFeatureValidationCandidate] = []
        for feature, usage in rows:
            feature_definition = (
                cast(dict[str, object], feature.feature_definition)
                if isinstance(feature.feature_definition, dict)
                else {}
            )

            notes_raw = feature_definition.get("notes")
            notes = notes_raw if isinstance(notes_raw, str) else None

            construct_query_raw = feature_definition.get("construct_query")
            construct_query = (
                cast(dict[str, object], construct_query_raw)
                if isinstance(construct_query_raw, dict)
                else None
            )

            evidence_json = (
                cast(dict[str, object], usage.evidence_json)
                if isinstance(usage.evidence_json, dict)
                else None
            )

            absolute_paths = [
                absolute_path.absolute_path
                for absolute_path in feature.absolute_paths
                if isinstance(absolute_path.absolute_path, str)
            ]

            candidates.append(
                FrameworkFeatureValidationCandidate(
                    identity=FrameworkFeatureUsageIdentity(
                        file_path=usage.file_path,
                        feature_language=usage.feature_language,
                        feature_library=usage.feature_library,
                        feature_capability_key=usage.feature_capability_key,
                        feature_operation_key=usage.feature_operation_key,
                        start_line=usage.start_line,
                        end_line=usage.end_line,
                    ),
                    concept=feature.concept,
                    match_confidence=usage.match_confidence,
                    validation_status=_coerce_validation_status_or_pending(
                        usage.validation_status
                    ),
                    match_text=usage.match_text,
                    evidence_json=evidence_json,
                    base_confidence=_require_call_expression_base_confidence(feature),
                    notes=notes,
                    construct_query=construct_query,
                    absolute_paths=absolute_paths,
                )
            )

    logger.info(
        "Fetched {} low-confidence CallExpression candidates for codebase_path={} language={}",
        len(candidates),
        codebase_path,
        programming_language,
    )
    return candidates


async def db_upsert_framework_feature_validation_evidence(
    *,
    codebase_path: str,
    request: FrameworkFeatureValidationEvidenceUpsertRequest,
) -> FrameworkFeatureValidationEvidenceUpsertResult:
    """Persist validator evidence/confidence and apply in-place location corrections."""
    async with get_startup_session() as session:
        source_row = await _get_framework_usage_row(
            session,
            codebase_path,
            request.identity,
        )
        if source_row is None:
            raise ValueError(
                "Framework usage row not found for provided identity/codebase context"
            )

        current_identity = request.identity
        if request.decision == FrameworkFeatureValidationDecision.CORRECT:
            current_identity = request.build_updated_identity()
            if current_identity != request.identity:
                conflicting_row = await _get_framework_usage_row(
                    session,
                    codebase_path,
                    current_identity,
                )
                if conflicting_row is not None:
                    raise ValueError(
                        "Corrected location already exists on a different framework usage row"
                    )

        validator_payload = _build_validator_payload(
            decision=request.decision,
            final_confidence=request.final_confidence,
            evidence_json=request.evidence_json,
            corrected_file_path=request.corrected_file_path,
            corrected_start_line=request.corrected_start_line,
            corrected_end_line=request.corrected_end_line,
            corrected_match_text=request.corrected_match_text,
        )
        if request.decision == FrameworkFeatureValidationDecision.CORRECT:
            validator_payload["corrected_from"] = {
                "file_path": request.identity.file_path,
                "start_line": request.identity.start_line,
                "end_line": request.identity.end_line,
                "match_text": source_row.match_text,
            }

        source_row.match_confidence = request.final_confidence
        source_row.evidence_json = _merge_evidence_json(
            source_row.evidence_json,
            validator_payload,
        )

        if request.decision == FrameworkFeatureValidationDecision.CORRECT:
            source_row.file_path = current_identity.file_path
            source_row.start_line = current_identity.start_line
            source_row.end_line = current_identity.end_line
            if request.corrected_match_text is not None:
                source_row.match_text = request.corrected_match_text

        return FrameworkFeatureValidationEvidenceUpsertResult(
            source_row_updated=True,
            current_identity=current_identity,
        )


async def db_set_framework_feature_validation_status(
    *,
    codebase_path: str,
    request: FrameworkFeatureValidationStatusTransitionRequest,
) -> FrameworkFeatureValidationStatusTransitionResult:
    """Set framework usage validation status with transition guards."""
    async with get_startup_session() as session:
        usage_row = await _get_framework_usage_row(
            session,
            codebase_path,
            request.identity,
        )
        if usage_row is None:
            raise ValueError(
                "Framework usage row not found for provided identity/codebase context"
            )

        current_status = _coerce_validation_status(usage_row.validation_status)

        if (
            request.expected_current_status is not None
            and current_status != request.expected_current_status
        ):
            raise ValueError(
                "Current status mismatch: "
                f"expected={request.expected_current_status.value}, "
                f"actual={current_status.value}"
            )

        if not _is_transition_allowed(current_status, request.target_status):
            raise ValueError(
                "Invalid validation_status transition: "
                f"{current_status.value} -> {request.target_status.value}"
            )

        if current_status == request.target_status:
            return FrameworkFeatureValidationStatusTransitionResult(
                status="no_op",
                previous_status=current_status,
                current_status=current_status,
            )

        usage_row.validation_status = request.target_status.value
        return FrameworkFeatureValidationStatusTransitionResult(
            status="updated",
            previous_status=current_status,
            current_status=request.target_status,
        )
