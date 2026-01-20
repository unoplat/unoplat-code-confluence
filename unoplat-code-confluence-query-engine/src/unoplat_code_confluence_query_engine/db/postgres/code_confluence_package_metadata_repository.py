"""PostgreSQL repository for codebase package metadata."""

from __future__ import annotations

from typing import Optional

from sqlalchemy import select

from unoplat_code_confluence_commons.relational_models import (
    UnoplatCodeConfluenceCodebase,
    UnoplatCodeConfluencePackageManagerMetadata,
)
from unoplat_code_confluence_query_engine.db.postgres.db import get_startup_session
from unoplat_code_confluence_query_engine.models.output.agent_md_output import (
    ProgrammingLanguageMetadataOutput,
)


async def fetch_programming_language_metadata(
    codebase_path: str,
) -> Optional[ProgrammingLanguageMetadataOutput]:
    """Fetch programming language metadata from PostgreSQL for a codebase path."""
    if not codebase_path:
        return None

    async with get_startup_session() as session:
        stmt = (
            select(
                UnoplatCodeConfluenceCodebase.programming_language,
                UnoplatCodeConfluencePackageManagerMetadata.programming_language,
                UnoplatCodeConfluencePackageManagerMetadata.package_manager,
            )
            .join(
                UnoplatCodeConfluencePackageManagerMetadata,
                UnoplatCodeConfluencePackageManagerMetadata.codebase_qualified_name
                == UnoplatCodeConfluenceCodebase.qualified_name,
                isouter=True,
            )
            .where(UnoplatCodeConfluenceCodebase.codebase_path == codebase_path)
            .limit(1)
        )
        result = await session.execute(stmt)
        row = result.first()

    if not row:
        return None

    codebase_language, metadata_language, package_manager = row
    language = metadata_language or codebase_language

    if not language or not package_manager:
        return None

    return ProgrammingLanguageMetadataOutput(
        primary_language=language,
        package_manager=package_manager,
    )
