"""
Service for querying framework features from PostgreSQL database.
"""

from typing import List

from code_confluence_flow_bridge.engine.models import FeatureSpec
from code_confluence_flow_bridge.processor.db.postgres.custom_grammar_metadata import (
    FeatureAbsolutePath,
    FrameworkFeature,
)
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


async def get_framework_features_for_imports(
    session: AsyncSession, language: str, imports: List[str]
) -> List[FeatureSpec]:
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
        framework_features = result.scalars().unique().all()

        # Convert to FeatureSpec objects
        feature_specs = []
        for feature in framework_features:
            # Extract absolute paths from the loaded relationship
            absolute_paths = [path.absolute_path for path in feature.absolute_paths]

            feature_spec = FeatureSpec(
                feature_key=feature.feature_key,
                library=feature.library,
                absolute_paths=absolute_paths,
                target_level=feature.target_level,
                concept=feature.concept,
                locator_strategy=feature.locator_strategy,
                construct_query=feature.construct_query,
                description=feature.description,
            )
            feature_specs.append(feature_spec)

        logger.debug(
            f"Found {len(feature_specs)} framework features for language={language} "
            f"with {len(imports)} imports"
        )

        return feature_specs

    except Exception as e:
        logger.error(f"Failed to query framework features: {e}")
        return []


async def get_all_framework_features_for_language(
    session: AsyncSession, language: str
) -> List[FeatureSpec]:
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
        framework_features = result.scalars().unique().all()

        # Convert to FeatureSpec objects
        feature_specs = []
        for feature in framework_features:
            absolute_paths = [path.absolute_path for path in feature.absolute_paths]

            feature_spec = FeatureSpec(
                feature_key=feature.feature_key,
                library=feature.library,
                absolute_paths=absolute_paths,
                target_level=feature.target_level,
                concept=feature.concept,
                locator_strategy=feature.locator_strategy,
                construct_query=feature.construct_query,
                description=feature.description,
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
