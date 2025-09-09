from typing import Optional

from fastapi import HTTPException
from loguru import logger
from sqlalchemy import select
from unoplat_code_confluence_commons.base_models import (
    CodebaseConfigSQLModel,
    ProgrammingLanguageMetadata,
    Repository,
)

from unoplat_code_confluence_query_engine.db.neo4j.connection_manager import (
    CodeConfluenceGraphQueryEngine,
)
from unoplat_code_confluence_query_engine.db.postgres.db import get_session
from unoplat_code_confluence_query_engine.models.agent_md_output import (
    ProgrammingLanguageMetadataOutput,
)
from unoplat_code_confluence_query_engine.models.repository_ruleset_metadata import (
    CodebaseMetadata,
    RepositoryRulesetMetadata,
)
from unoplat_code_confluence_query_engine.services.codebase_path_resolver import (
    CodebasePathResolver,
)
from unoplat_code_confluence_query_engine.services.package_manager_metadata_service import (
    fetch_programming_language_metadata,
)


async def fetch_repository_metadata(
    owner_name: str, repo_name: str, neo4j_manager: CodeConfluenceGraphQueryEngine
) -> RepositoryRulesetMetadata:
    """
    Fetch repository and codebase configuration data from PostgreSQL and resolve
    absolute paths from Neo4j.

    Args:
        owner_name: Repository owner name
        repo_name: Repository name
        neo4j_manager: Neo4j connection manager for resolving absolute paths

    Returns:
        RepositoryRulesetMetadata with populated codebase metadata including
        absolute paths

    Raises:
        HTTPException: If repository is not found or a database error occurs
    """
    try:
        # First, fetch repository and codebase configurations from PostgreSQL
        codebase_configs = None
        async with get_session() as session:
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

        # Extract relative paths for Neo4j query
        relative_paths = [config.codebase_folder for config in codebase_configs]

        # Resolve absolute paths from Neo4j using qualified name format: {owner_name}_{repo_name}
        # Keep this separate from PostgreSQL session to avoid context manager conflicts
        neo4j_qualified_name = f"{owner_name}_{repo_name}"
        path_resolver = CodebasePathResolver(neo4j_manager)

        try:
            path_mapping = await path_resolver.resolve_codebase_absolute_paths(
                neo4j_qualified_name, relative_paths
            )
        except Exception as e:
            logger.warning("Failed to resolve absolute paths from Neo4j: {}", e)
            # Create empty mapping - will use relative paths as fallback
            path_mapping = {path: None for path in relative_paths}

        # Convert to CodebaseMetadata objects
        codebase_metadata_list = []
        for config in codebase_configs:
            # Parse programming_language_metadata JSON field
            prog_lang_metadata = ProgrammingLanguageMetadata(
                **config.programming_language_metadata
            )

            # Get absolute path from Neo4j mapping, fallback to relative path if not found
            relative_path = config.codebase_folder
            absolute_path = path_mapping.get(relative_path)

            if absolute_path is None:
                logger.warning(
                    "No absolute path found for codebase {}, using relative path as fallback",
                    relative_path,
                )
                absolute_path = relative_path

            # Fetch programming language metadata using absolute path (falls back to relative if needed)
            neo4j_prog_lang_metadata: Optional[ProgrammingLanguageMetadataOutput] = await fetch_programming_language_metadata(
                neo4j_manager, neo4j_qualified_name, absolute_path
            )

            # Log the fetched metadata
            logger.info(
                "Fetched programming language metadata from Neo4j for {}/{}: {}",
                neo4j_qualified_name,
                relative_path,
                neo4j_prog_lang_metadata.model_dump_json()
                if neo4j_prog_lang_metadata
                else "None",
            )

            codebase_metadata = CodebaseMetadata(
                codebase_name=relative_path,  # Use relative path as identifier
                codebase_path=absolute_path,  # Use absolute path from Neo4j
                codebase_programming_language=prog_lang_metadata.language.value,
            )
            codebase_metadata_list.append(codebase_metadata)

        # Create and return RepositoryRulesetMetadata with proper qualified name format
        repository_qualified_name = f"{owner_name}/{repo_name}"
        return RepositoryRulesetMetadata(
            repository_qualified_name=repository_qualified_name,
            codebase_metadata=codebase_metadata_list,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Database error while fetching repository metadata: {}", e)
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch repository metadata: {str(e)}"
        )

