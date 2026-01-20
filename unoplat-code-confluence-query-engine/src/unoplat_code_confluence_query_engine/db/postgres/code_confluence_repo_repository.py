"""PostgreSQL repository helpers for Code Confluence repositories."""

from __future__ import annotations

from typing import Dict, List, Optional

from sqlalchemy import select

from unoplat_code_confluence_commons.relational_models import (
    UnoplatCodeConfluenceCodebase,
)
from unoplat_code_confluence_query_engine.db.postgres.db import get_startup_session


async def resolve_codebase_paths(
    repository_qualified_name: str,
    codebase_folders: List[str],
) -> Dict[str, Optional[str]]:
    """Resolve absolute codebase paths from PostgreSQL for given folders."""
    mapping: Dict[str, Optional[str]] = {folder: None for folder in codebase_folders}
    if not repository_qualified_name or not codebase_folders:
        return mapping

    async with get_startup_session() as session:
        stmt = select(
            UnoplatCodeConfluenceCodebase.codebase_folder,
            UnoplatCodeConfluenceCodebase.codebase_path,
        ).where(
            UnoplatCodeConfluenceCodebase.repository_qualified_name
            == repository_qualified_name,
            UnoplatCodeConfluenceCodebase.codebase_folder.in_(codebase_folders),
        )
        result = await session.execute(stmt)
        for codebase_folder, codebase_path in result.tuples().all():
            mapping[codebase_folder] = codebase_path

    return mapping
