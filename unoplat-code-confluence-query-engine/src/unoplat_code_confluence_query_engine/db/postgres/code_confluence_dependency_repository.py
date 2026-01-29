"""PostgreSQL repository for fetching codebase dependencies."""

from __future__ import annotations

from loguru import logger
from sqlalchemy import select
from unoplat_code_confluence_commons.relational_models import (
    UnoplatCodeConfluenceCodebase,
    UnoplatCodeConfluencePackageManagerMetadata,
)

from unoplat_code_confluence_query_engine.db.postgres.db import get_startup_session

# Type alias for the dependencies JSONB structure:
# Dict[group_name, Dict[package_name, serialized_UnoplatProjectDependency]]
# Groups: default, dev, peer, optional, bundled, override
# We only need package names, so inner value is typed as object
DependenciesJsonb = dict[str, dict[str, object]]


async def fetch_codebase_dependencies(codebase_path: str) -> list[str]:
    """Fetch unique dependency names for a codebase from PostgreSQL.

    Queries the UnoplatCodeConfluencePackageManagerMetadata table for dependencies
    associated with the given codebase path. The dependencies JSONB column has
    the structure: Dict[group_name, Dict[package_name, UnoplatProjectDependency]].

    Args:
        codebase_path: Absolute path to the codebase (e.g., /opt/unoplat/repositories/owner/repo/src)

    Returns:
        List of unique package names. Returns empty list if:
        - codebase_path is empty
        - No metadata found for the codebase
        - Dependencies field is empty or None
    """
    if not codebase_path:
        logger.debug("[fetch_codebase_dependencies] Empty codebase_path provided")
        return []

    async with get_startup_session() as session:
        stmt = (
            select(UnoplatCodeConfluencePackageManagerMetadata.dependencies)
            .join(
                UnoplatCodeConfluenceCodebase,
                UnoplatCodeConfluencePackageManagerMetadata.codebase_qualified_name
                == UnoplatCodeConfluenceCodebase.qualified_name,
            )
            .where(UnoplatCodeConfluenceCodebase.codebase_path == codebase_path)
            .limit(1)
        )
        result = await session.execute(stmt)
        row = result.scalar_one_or_none()

    if not row:
        logger.debug(
            "[fetch_codebase_dependencies] No package metadata found for codebase_path={}",
            codebase_path,
        )
        return []

    # Flatten Dict[group_name, Dict[package_name, ...]] to unique package names
    dependency_names: set[str] = set()
    dependencies_dict: DependenciesJsonb = row  # type: ignore[assignment]

    for group_packages in dependencies_dict.values():
        dependency_names.update(group_packages.keys())

    logger.info(
        "[fetch_codebase_dependencies] Found {} dependencies for codebase_path={}",
        len(dependency_names),
        codebase_path,
    )

    return list(dependency_names)
