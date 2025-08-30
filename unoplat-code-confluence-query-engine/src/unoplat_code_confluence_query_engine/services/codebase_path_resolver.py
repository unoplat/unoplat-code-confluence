"""Service for resolving absolute codebase paths from Neo4j graph database."""

from typing import Dict, List, Optional

from loguru import logger

from unoplat_code_confluence_query_engine.db.neo4j.connection_manager import (
    CodeConfluenceGraphQueryEngine,
)


class CodebasePathResolver:
    """
    Service for resolving absolute codebase paths from Neo4j graph database.

    This service queries the Neo4j graph to find repository nodes by qualified name
    and retrieves the absolute paths for connected codebase nodes.
    """

    def __init__(self, neo4j_manager: CodeConfluenceGraphQueryEngine):
        self.neo4j_manager = neo4j_manager

    async def resolve_codebase_absolute_paths(
        self, repository_qualified_name: str, relative_codebase_paths: List[str]
    ) -> Dict[str, Optional[str]]:
        """
        Resolve absolute paths for codebases from Neo4j graph database.

        Args:
            repository_qualified_name: Repository qualified name (format: {owner_name}_{repo_name})
            relative_codebase_paths: List of relative paths from PostgreSQL

        Returns:
            Dictionary mapping relative paths to absolute paths
            Returns None for absolute path if not found in Neo4j

        Raises:
            Exception: If Neo4j query fails
        """
        try:
            async with self.neo4j_manager.get_session() as session:
                result = await session.execute_read(
                    self._query_codebase_paths, repository_qualified_name
                )

                # Create mapping from results
                path_mapping: Dict[str, Optional[str]] = {}

                # Initialize all relative paths to None
                for relative_path in relative_codebase_paths:
                    path_mapping[relative_path] = None

                # Update with found absolute paths
                for record in result:
                    codebase_name = record.get("codebase_name")
                    codebase_path = record.get("codebase_path")

                    # Try to match with relative paths using codebase name or path matching logic
                    for relative_path in relative_codebase_paths:
                        if self._match_codebase_path(
                            relative_path, codebase_name, codebase_path
                        ):
                            path_mapping[relative_path] = codebase_path
                            break

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

    def _match_codebase_path(
        self,
        relative_path: str,
        codebase_name: Optional[str],
        absolute_path: Optional[str],
    ) -> bool:
        """
        Match a relative path with a codebase from Neo4j.

        This method implements the matching logic to connect PostgreSQL relative paths
        with Neo4j codebase nodes.

        Args:
            relative_path: Relative path from PostgreSQL
            codebase_name: Codebase name from Neo4j
            absolute_path: Absolute path from Neo4j

        Returns:
            True if the paths match, False otherwise
        """
        if not absolute_path:
            return False

        # Primary matching: check if the relative path is at the end of absolute path
        if absolute_path.endswith(relative_path):
            return True

        # Secondary matching: check if codebase name contains the relative path
        if codebase_name and relative_path in codebase_name:
            return True

        # Tertiary matching: normalize paths and compare
        normalized_relative = relative_path.strip("/").replace("\\", "/")
        normalized_absolute = absolute_path.strip("/").replace("\\", "/")

        if normalized_absolute.endswith(normalized_relative):
            return True

        return False

    @staticmethod
    async def _query_codebase_paths(tx, repository_qualified_name: str):
        """
        Neo4j transaction function to query codebase paths.

        Args:
            tx: Neo4j transaction
            repository_qualified_name: Repository qualified name

        Returns:
            Query result with codebase names and paths
        """
        query = """
        MATCH (repo:CodeConfluenceGitRepository {qualified_name: $repo_qualified_name})
        -[:CONTAINS_CODEBASE]->(codebase:CodeConfluenceCodebase)
        RETURN codebase.name AS codebase_name, 
               codebase.codebase_path AS codebase_path
        """

        result = await tx.run(query, repo_qualified_name=repository_qualified_name)
        records = await result.data()
        return records
