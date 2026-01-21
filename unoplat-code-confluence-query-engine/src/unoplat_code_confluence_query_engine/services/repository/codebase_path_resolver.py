"""Service for resolving absolute codebase paths from PostgreSQL."""

from typing import Dict, List, Optional

from loguru import logger
from unoplat_code_confluence_query_engine.db.postgres.code_confluence_repo_repository import (
    resolve_codebase_paths,
)


class CodebasePathResolver:
    """
    Service for resolving absolute codebase paths from PostgreSQL.
    """

    def __init__(self) -> None:
        pass

    async def resolve_codebase_absolute_paths(
        self, repository_qualified_name: str, relative_codebase_paths: List[str]
    ) -> Dict[str, Optional[str]]:
        """
        Resolve absolute paths for codebases from PostgreSQL.

        Args:
            repository_qualified_name: Repository qualified name (format: {owner_name}_{repo_name})
            relative_codebase_paths: List of relative paths from PostgreSQL

        Returns:
            Dictionary mapping relative paths to absolute paths
            Returns None for absolute path if not found in Postgres

        Raises:
            Exception: If Postgres query fails
        """
        try:
            path_mapping = await resolve_codebase_paths(
                repository_qualified_name, relative_codebase_paths
            )
            logger.info(
                "Resolved {} out of {} codebase paths for repository {}",
                len([p for p in path_mapping.values() if p is not None]),
                len(relative_codebase_paths),
                repository_qualified_name,
            )
            return path_mapping
        except Exception as e:
            logger.error(
                "Failed to resolve codebase paths for repository {}: {}",
                repository_qualified_name,
                e,
            )
            raise
