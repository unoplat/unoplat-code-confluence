"""Neo4j repository for querying data model files.

Follows the same async session + execute_read pattern as framework_overview_repository.
"""

from __future__ import annotations

from typing import List

from neo4j import AsyncManagedTransaction

from unoplat_code_confluence_query_engine.db.neo4j.connection_manager import (
    CodeConfluenceGraphQueryEngine,
)


async def _txn_get_data_model_files(
    tx: AsyncManagedTransaction, codebase_path: str
) -> List[str]:
    """Fetch data model files for a codebase.

    Uses two identification strategies:
    - Direct: CodeConfluenceFile.has_data_model = true
    - Feature-based: Uses features with feature_key in ['data_model', 'db_data_model']

    Returns list of file paths only.
    """

    # Approach notes:
    # - We scope files to the codebase using file_path STARTS WITH codebase_path because file nodes are absolute paths.
    # - We UNION the direct and feature-based detections to get a unified distinct set of file paths.
    query = """
    // Direct detection: has_data_model = true
    MATCH (f:CodeConfluenceFile)
    WHERE f.file_path STARTS WITH $codebase_path
      AND coalesce(f.has_data_model, false)
    RETURN f.file_path AS path

    UNION

    MATCH (f:CodeConfluenceFile)-[:USES_FEATURE]->(feat:CodeConfluenceFrameworkFeature)
    WHERE f.file_path STARTS WITH $codebase_path
      AND feat.feature_key IN ['data_model', 'db_data_model']
    RETURN f.file_path AS path

    ORDER BY path
    """

    result = await tx.run(query, {"codebase_path": codebase_path})
    records = await result.data()
    # Extract just the file paths from the records
    return [record["path"] for record in records]


async def db_get_data_model_files(
    neo4j_manager: CodeConfluenceGraphQueryEngine,
    codebase_path: str,
) -> List[str]:
    """Public API to fetch data model file paths for a codebase.

    Mirrors the execute_read usage pattern elsewhere in the project.
    """
    async with neo4j_manager.get_session() as session:
        return await session.execute_read(
            _txn_get_data_model_files, codebase_path
        )


