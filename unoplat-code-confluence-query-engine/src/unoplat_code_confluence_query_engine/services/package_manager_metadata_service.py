"""Service for fetching package manager metadata from Neo4j graph."""

from typing import Optional

from loguru import logger
from neo4j import AsyncManagedTransaction, Record

from unoplat_code_confluence_query_engine.db.neo4j.connection_manager import (
    CodeConfluenceGraphQueryEngine,
)
from unoplat_code_confluence_query_engine.models.agent_md_output import (
    PackageManagerOutput,
    ProgrammingLanguageMetadataOutput,
)


async def _fetch_package_manager_metadata_txn(
    tx: AsyncManagedTransaction, repository_qualified_name: str, codebase_path: str
) -> Optional[Record]:
    """
    Transaction function for fetching package manager metadata from Neo4j.

    Args:
        tx: Neo4j async transaction
        repository_qualified_name: Repository identifier (e.g., "owner/repo")
        codebase_path: Path to the codebase within the repository

    Returns:
        Record with programming language metadata or None if not found
    """
    query = """
    MATCH (repo:CodeConfluenceGitRepository {qualified_name: $qualified_name})
    -[:CONTAINS_CODEBASE]->(codebase:CodeConfluenceCodebase {codebase_path: $codebase_path})
    -[:HAS_PACKAGE_MANAGER_METADATA]->(pm:CodeConfluencePackageManagerMetadata)
    RETURN pm.programming_language as language,
           pm.programming_language_version as version,
           pm.package_manager as package_manager
    LIMIT 1
    """

    result = await tx.run(
        query,
        {"qualified_name": repository_qualified_name, "codebase_path": codebase_path},
    )
    return await result.single()


async def fetch_programming_language_metadata(
    neo4j_manager: CodeConfluenceGraphQueryEngine,
    repository_qualified_name: str,
    codebase_path: str,
) -> Optional[ProgrammingLanguageMetadataOutput]:
    """
    Fetch programming language metadata from Neo4j and convert to output model.

    This function queries the Neo4j graph to retrieve package manager metadata
    associated with a specific codebase and maps it to the ProgrammingLanguageMetadataOutput
    model required by the agent.

    Args:
        neo4j_manager: Neo4j connection manager
        repository_qualified_name: Repository identifier (convention: "owner_repo")
        codebase_path: Path to the codebase within the repository

    Returns:
        ProgrammingLanguageMetadataOutput if found, None otherwise
    """
    try:
        async with neo4j_manager.get_session() as session:
            record = await session.execute_read(
                _fetch_package_manager_metadata_txn,
                repository_qualified_name,
                codebase_path,
            )

            if not record:
                logger.error(
                    "No package manager metadata found for repository: {} codebase: {}",
                    repository_qualified_name,
                    codebase_path,
                )
                return None

            # Extract data from record
            language = record["language"]
            version = record["version"]
            package_manager = record["package_manager"]

            if not language or not package_manager:
                logger.error(
                    "Incomplete package manager metadata for repository: {} codebase: {}",
                    repository_qualified_name,
                    codebase_path,
                )
                return None

            # Create PackageManagerOutput using the package_manager value directly from Neo4j
            package_manager_output = PackageManagerOutput(package_type=package_manager)

            # Create and return ProgrammingLanguageMetadataOutput
            return ProgrammingLanguageMetadataOutput(
                primary_language=language,
                package_manager=package_manager_output,
                version_requirement=version,
            )

    except Exception as e:
        logger.error(
            "Error fetching programming language metadata for repository: {} codebase: {}: {}",
            repository_qualified_name,
            codebase_path,
            str(e),
        )
        return None
