"""Service to fetch baseline frameworks from Neo4j and map to output models.

Produces List[FrameworkLibraryOutput] so it can be merged with agent results.
"""

from __future__ import annotations

from typing import Dict, List

from loguru import logger
from sqlalchemy import select
from unoplat_code_confluence_commons.base_models import Framework, FrameworkFeature

from unoplat_code_confluence_query_engine.db.neo4j.connection_manager import (
    CodeConfluenceGraphQueryEngine,
)
from unoplat_code_confluence_query_engine.db.neo4j.framework_overview_repository import (
    db_get_framework_with_features,
    db_list_framework_libraries,
)
from unoplat_code_confluence_query_engine.db.postgres.db import get_session
from unoplat_code_confluence_query_engine.models.agent_md_output import (
    FeatureLocationOutput,
    FeatureUsageOutput,
    FrameworkLibraryOutput,
)


async def _fetch_framework_metadata_from_postgres(
    library_names: List[str], language: str = "python"
) -> Dict[str, Dict[str, str]]:
    """Fetch framework metadata from PostgreSQL for given library names.
    
    Args:
        library_names: List of library names to fetch metadata for
        language: Programming language (defaults to "python")
        
    Returns:
        Dict mapping library name to metadata dict with 'description' and 'docs_url'
    """
    if not library_names:
        return {}
        
    metadata = {}
    
    try:
        async with get_session() as session:
            
                        
            stmt = select(Framework).where(
                Framework.language == language,
                Framework.library.in_(library_names)
            )
            
            
            result = await session.execute(stmt)
            frameworks: List[Framework] = result.scalars().all()
            
            # Build metadata dictionary
            for fw in frameworks:
                metadata[fw.library] = {
                    "description": fw.description,
                    "docs_url": fw.docs_url
                }
                
    except Exception as e:  # noqa: BLE001
        logger.warning("Failed to fetch framework metadata from PostgreSQL: {}", e)
        
    return metadata


async def _fetch_feature_entrypoints_from_postgres(
    library_names: List[str], language: str = "python"
) -> Dict[str, Dict[str, bool]]:
    """Fetch feature-level entry point flags from PostgreSQL.

    Returns a nested mapping: {library: {feature_key: startpoint_bool}}
    """
    if not library_names:
        return {}

    entrypoints: Dict[str, Dict[str, bool]] = {}
    try:
        async with get_session() as session:
            stmt = select(FrameworkFeature).where(
                FrameworkFeature.language == language,
                FrameworkFeature.library.in_(library_names),
            )
            result = await session.execute(stmt)
            features: List[FrameworkFeature] = result.scalars().all()

            for feat in features:
                lib_map = entrypoints.setdefault(feat.library, {})
                lib_map[feat.feature_key] = bool(feat.startpoint)
    except Exception as e:  # noqa: BLE001
        logger.warning(
            "Failed to fetch feature entrypoints from PostgreSQL: {}", e
        )

    return entrypoints


async def fetch_baseline_frameworks_as_outputs(
    neo4j_manager: CodeConfluenceGraphQueryEngine,
    codebase_path: str,
    programming_language: str = "python",
) -> List[FrameworkLibraryOutput]:
    """Fetch baseline frameworks from Neo4j and map to FrameworkLibraryOutput.

    - Includes only frameworks with at least one feature that has ≥1 usage location.
    - Sets FeatureLocationOutput.is_entry_point from PostgreSQL `framework_feature.startpoint`.
    - Leaves documentation_url unset (None); description is a concise default.
    """
    try:
        libraries = await db_list_framework_libraries(neo4j_manager, codebase_path)
    except Exception as e:  # noqa: BLE001
        logger.warning("Baseline fetch failed for {}: {}", codebase_path, e)
        return []

    outputs: List[FrameworkLibraryOutput] = []

    # Fetch framework metadata from PostgreSQL
    framework_metadata = await _fetch_framework_metadata_from_postgres(
        libraries, programming_language
    )

    # Fetch feature entry point flags from PostgreSQL
    feature_entrypoints = await _fetch_feature_entrypoints_from_postgres(
        libraries, programming_language
    )

    for lib in libraries:
        try:
            data = await db_get_framework_with_features(neo4j_manager, codebase_path, lib)
        except Exception as e:  # noqa: BLE001
            logger.debug("Failed to get features for {} in {}: {}", lib, codebase_path, e)
            continue

        features_used: List[FeatureUsageOutput] = []
        for feat in data.get("features", []) or []:
            usages = feat.get("usages", []) or []
            feature_key = feat.get("feature_key")
            is_entry_point_flag = bool(
                feature_entrypoints.get(lib, {}).get(feature_key or "", False)
            )
            # Build locations; skip features with no file-backed usages
            locations = [
                FeatureLocationOutput(
                    file_path=u["file_path"],
                    is_entry_point=is_entry_point_flag,
                )
                for u in usages
                if u and u.get("file_path")
            ]
            if not locations:
                continue
            features_used.append(
                FeatureUsageOutput(
                    feature_name=feature_key or lib,
                    description=feat.get("description") or "",
                    locations=locations,
                )
            )

        # Only include the library if at least one feature has locations
        if not features_used:
            continue

        # Get metadata from PostgreSQL or use fallback
        lib_metadata = framework_metadata.get(lib, {})
        description = lib_metadata.get("description") or f"Detected usage of {lib} via knowledge graph."
        docs_url = lib_metadata.get("docs_url")

        outputs.append(
            FrameworkLibraryOutput(
                name=lib,
                description=description,
                documentation_url=docs_url,
                features_used=features_used,
            )
        )

    return outputs
