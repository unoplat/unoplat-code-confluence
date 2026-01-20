from typing import List, Optional

from fastapi import HTTPException
from loguru import logger
from sqlalchemy import select
from unoplat_code_confluence_commons.base_models import (
    CodebaseConfigSQLModel,
    Repository,
)

from unoplat_code_confluence_query_engine.db.postgres.db import get_startup_session
from unoplat_code_confluence_query_engine.models.repository.repository_ruleset_metadata import (
    CodebaseMetadata,
    RepositoryRulesetMetadata,
)
from unoplat_code_confluence_query_engine.services.repository.codebase_path_resolver import (
    CodebasePathResolver,
)
from unoplat_code_confluence_query_engine.services.repository.package_manager_metadata_service import (
    fetch_programming_language_metadata,
)


async def fetch_repository_metadata(
    owner_name: str, repo_name: str
) -> RepositoryRulesetMetadata:
    """
    Fetch repository and codebase configuration data from PostgreSQL and resolve
    absolute paths from PostgreSQL.

    Args:
        owner_name: Repository owner name
        repo_name: Repository name
    Returns:
        RepositoryRulesetMetadata with populated codebase metadata including
        absolute paths

    Raises:
        HTTPException: If repository is not found or a database error occurs
    """
    try:
        # First, fetch repository and codebase configurations from PostgreSQL
        codebase_configs = None
        async with get_startup_session() as session:
            # Fetch repository
            repository_stmt = select(Repository).where(
                Repository.repository_name == repo_name,
                Repository.repository_owner_name == owner_name,
            )
            repository_result = await session.execute(repository_stmt)
            repository = repository_result.scalar_one_or_none()

            if not repository:
                raise HTTPException(
                    status_code=404,
                    detail=f"Repository not found: {owner_name}/{repo_name}",
                )

            # Fetch codebase configurations for this repository
            codebase_configs_stmt = select(CodebaseConfigSQLModel).where(
                CodebaseConfigSQLModel.repository_name == repo_name,
                CodebaseConfigSQLModel.repository_owner_name == owner_name,
            )
            codebase_configs_result = await session.execute(codebase_configs_stmt)
            codebase_configs = codebase_configs_result.scalars().all()

            if not codebase_configs:
                raise HTTPException(
                    status_code=404,
                    detail=(
                        f"No codebase configurations found for repository: "
                        f"{owner_name}/{repo_name}"
                    ),
                )

        # Extract relative paths for codebase path resolution
        relative_paths = [config.codebase_folder for config in codebase_configs]

        # Resolve absolute paths from PostgreSQL using qualified name format: {owner_name}_{repo_name}
        repository_qualified_name = f"{owner_name}_{repo_name}"
        path_resolver = CodebasePathResolver()

        try:
            path_mapping = await path_resolver.resolve_codebase_absolute_paths(
                repository_qualified_name, relative_paths
            )
        except Exception as e:
            logger.warning("Failed to resolve absolute paths from Postgres: {}", e)
            # Create empty mapping - will use relative paths as fallback
            path_mapping = {path: None for path in relative_paths}

        # Convert to CodebaseMetadata objects
        codebase_metadata_list: List[CodebaseMetadata] = []
        for config in codebase_configs:
            # Get absolute path from Postgres mapping, fallback to relative path if not found
            relative_path = config.codebase_folder
            absolute_path = path_mapping.get(relative_path)

            if absolute_path is None:
                logger.warning(
                    "No absolute path found for codebase {}, using relative path as fallback",
                    relative_path,
                )
                absolute_path = relative_path

            # Fetch programming language metadata using absolute path
            prog_lang_metadata = await fetch_programming_language_metadata(absolute_path)

            logger.info(
                "Fetched programming language metadata for {}/{}: {}",
                repository_qualified_name,
                relative_path,
                prog_lang_metadata.model_dump_json()
                if prog_lang_metadata
                else "None",
            )

            if not prog_lang_metadata:
                raise HTTPException(
                    status_code=404,
                    detail=(
                        f"Programming language metadata not found for codebase: "
                        f"{relative_path}"
                    ),
                )

            codebase_metadata = CodebaseMetadata(
                codebase_name=relative_path,
                codebase_path=absolute_path,
                codebase_programming_language=prog_lang_metadata.primary_language,
                codebase_package_manager=prog_lang_metadata.package_manager,
            )
            codebase_metadata_list.append(codebase_metadata)

        # Create and return RepositoryRulesetMetadata with proper qualified name format
        return RepositoryRulesetMetadata(
            repository_qualified_name=f"{owner_name}/{repo_name}",
            codebase_metadata=codebase_metadata_list,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Database error while fetching repository metadata: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch repository metadata: {str(e)}"
        )
