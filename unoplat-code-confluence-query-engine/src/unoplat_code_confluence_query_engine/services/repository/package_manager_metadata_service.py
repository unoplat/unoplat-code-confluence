"""Service for fetching package manager metadata from PostgreSQL."""

from typing import Optional

from loguru import logger
from unoplat_code_confluence_query_engine.db.postgres.code_confluence_package_metadata_repository import (
    fetch_programming_language_metadata as fetch_programming_language_metadata_pg,
)
from unoplat_code_confluence_query_engine.models.output.agent_md_output import (
    ProgrammingLanguageMetadataOutput,
)
async def fetch_programming_language_metadata(
    codebase_path: str,
) -> Optional[ProgrammingLanguageMetadataOutput]:
    """Fetch programming language metadata from PostgreSQL and convert to output model."""
    try:
        metadata = await fetch_programming_language_metadata_pg(codebase_path)
        if not metadata:
            logger.error(
                "No package manager metadata found for codebase: {}",
                codebase_path,
            )
        return metadata
    except Exception as e:
        logger.error(
            "Error fetching programming language metadata for codebase {}: {}",
            codebase_path,
            str(e),
        )
        return None
