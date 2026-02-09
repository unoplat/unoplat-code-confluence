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
    """Fetch unique runtime dependency names for a codebase from PostgreSQL.

    Queries the UnoplatCodeConfluencePackageManagerMetadata table for dependencies
    associated with the given codebase path. The dependencies JSONB column has
    the structure: Dict[group_name, Dict[package_name, UnoplatProjectDependency]].

    Only the "default" group (runtime dependencies) is extracted. Dev, peer,
    optional, bundled, and override groups are excluded because they represent
    build-tooling concerns and are not useful for understanding the project's
    runtime functionality.

    Args:
        codebase_path: Absolute path to the codebase (e.g., /opt/unoplat/repositories/owner/repo/src)

    Returns:
        List of unique runtime package names. Returns empty list if:
        - codebase_path is empty
        - No metadata found for the codebase
        - Dependencies field is empty or None
        - No "default" group exists in the dependencies
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

    # Extract only "default" (runtime) dependency names — dev/peer/optional/bundled/override
    # dependencies are build-tooling concerns and not useful for project understanding
    dependencies_dict: DependenciesJsonb = row  # type: ignore[assignment]
    default_group: dict[str, object] = dependencies_dict.get("default", {})
    dependency_names: set[str] = set(default_group.keys())

    logger.info(
        "[fetch_codebase_dependencies] Found {} dependencies for codebase_path={}",
        len(dependency_names),
        codebase_path,
    )

    return list(dependency_names)
