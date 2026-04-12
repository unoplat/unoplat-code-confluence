"""
Service for querying framework features from PostgreSQL database.
This module bridges the ingestion layer and the query/detection engine.
"""

from typing import cast

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from unoplat_code_confluence_commons.base_models import (
    Concept,
    FeatureAbsolutePath,
    FeatureSpec,
    FrameworkFeature,
)


def _resolve_base_confidence(feature: FrameworkFeature) -> float | None:
    if feature.concept != Concept.CALL_EXPRESSION:
        return None

    raw_value = feature.feature_definition.get("base_confidence")
    if raw_value is None:
        return None
    if isinstance(raw_value, (int, float)) and not isinstance(raw_value, bool):
        numeric_value = float(raw_value)
        if 0.0 <= numeric_value <= 1.0:
            return numeric_value
    return None


def _build_feature_spec(
    feature: FrameworkFeature,
    absolute_paths: list[str],
    base_confidence: float | None,
) -> FeatureSpec:
    payload: dict[str, object] = {
<<<<<<< HEAD
        "capability_key": feature.capability_key,
        "operation_key": feature.operation_key,
=======
        "feature_key": feature.feature_key,
>>>>>>> origin/main
        "library": feature.library,
        "absolute_paths": absolute_paths,
        "target_level": feature.target_level,
        "concept": feature.concept,
        "locator_strategy": feature.locator_strategy,
        "construct_query": feature.construct_query,
        "description": feature.description,
        "startpoint": feature.startpoint,
    }
    if base_confidence is not None:
        payload["base_confidence"] = base_confidence
    return FeatureSpec.model_validate(payload)


async def get_framework_features_for_imports(
    session: AsyncSession, language: str, imports: list[str]
) -> list[FeatureSpec]:
    """
    Query framework features that match the given imports for a specific language.

    Args:
        session: Database session
        language: Programming language (e.g., "python")
        imports: List of import statements from the file

    Returns:
        List of FeatureSpec objects for matching framework features
    """
    if not imports:
        return []

    try:
        # Query for framework features that have absolute paths matching any of the imports
        # Use selectinload to eagerly load the absolute_paths relationship
        query = (
            select(FrameworkFeature)
            .options(selectinload(FrameworkFeature.absolute_paths))
            .join(FeatureAbsolutePath)
            .where(
                FrameworkFeature.language == language,
                FeatureAbsolutePath.absolute_path.in_(imports),
            )
            .distinct()
        )

        # When using selectinload() with asyncio, we must call .unique() on the
        # ScalarResult before fully materialising it in order to guarantee that
        # SQLAlchemy has consumed the *entire* first result set **before** it
        # issues the secondary SELECT statements required by the select-in-load
        # strategy (see https://docs.sqlalchemy.org/en/20/orm/queryguide/relationships.html#selectin-eager-loading-with-asyncio).
        # Failing to do so may lead to the infamous
        #     asyncpg.exceptions._base.InterfaceError: another operation is in progress
        # error because the ORM tries to run a second query on the very same
        # connection while the first one is still being iterated over.

        result = await session.execute(query)
        framework_features = cast(
            list[FrameworkFeature], result.scalars().unique().all()
        )

        # Convert to FeatureSpec objects
        feature_specs: list[FeatureSpec] = []
        for feature in framework_features:
            # Extract absolute paths from the loaded relationship
            absolute_paths = [path.absolute_path for path in feature.absolute_paths]
            base_confidence = _resolve_base_confidence(feature)

            feature_spec = _build_feature_spec(
                feature,
                absolute_paths,
                base_confidence,
            )
            feature_specs.append(feature_spec)

        logger.debug(
            f"Found {len(feature_specs)} framework features for language={language} "
            f"with {len(imports)} imports"
        )

        return feature_specs

    except Exception as e:
        logger.error("Failed to query framework features: {}", e)
        return []


async def get_all_framework_features_for_language(
    session: AsyncSession, language: str
) -> list[FeatureSpec]:
    """
    Query all framework features for a specific language.

    Args:
        session: Database session
        language: Programming language (e.g., "python")

    Returns:
        List of all FeatureSpec objects for the language
    """
    try:
        query = (
            select(FrameworkFeature)
            .options(selectinload(FrameworkFeature.absolute_paths))
            .where(FrameworkFeature.language == language)
        )

        # See comment above regarding .unique() – the same rationale applies
        # here as well when eager-loading relationships via selectinload().

        result = await session.execute(query)
        framework_features = cast(
            list[FrameworkFeature], result.scalars().unique().all()
        )

        # Convert to FeatureSpec objects
        feature_specs: list[FeatureSpec] = []
        for feature in framework_features:
            absolute_paths = [path.absolute_path for path in feature.absolute_paths]
            base_confidence = _resolve_base_confidence(feature)

            feature_spec = _build_feature_spec(
                feature,
                absolute_paths,
                base_confidence,
            )
            feature_specs.append(feature_spec)

        logger.debug(
            f"Found {len(feature_specs)} total framework features for language={language}"
        )

        return feature_specs

    except Exception as e:
        logger.error(
            f"Failed to query all framework features for language {language}: {e}"
        )
        return []
