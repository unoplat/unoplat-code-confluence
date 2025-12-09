"""Fetch files that contain data models (core business logic roots) for a codebase.

This tool returns a mapping of file paths to detected data model definitions
with the precise line spans that should be read. Detections combine:
- Files directly marked as data model files (has_data_model=true)
- Framework features 'data_model' or 'db_data_model' captured via USES_FEATURE

Each entry contains the data model identifier (class name, match text, etc.)
paired with a tuple of (start_line, end_line).

Agents should:
1) Call this tool to get the mapping of candidate model spans grouped by file path
2) Use read_file_content (get_content_file) with the provided line ranges to inspect only the relevant sections
3) Identify relevant data model definitions inside each snippet and summarize responsibilities per file
4) Only then group files into domains and write descriptions based on actual inspected content
"""

from __future__ import annotations

from loguru import logger
from pydantic_ai import ModelRetry, RunContext

from unoplat_code_confluence_query_engine.db.neo4j.business_logic_repository import (
    DataModelSpanMap,
    db_get_data_model_files,
)
from unoplat_code_confluence_query_engine.models.runtime.agent_dependencies import (
    AgentDependencies,
)
from unoplat_code_confluence_query_engine.services.temporal.service_registry import (
    get_neo4j_manager,
)


async def get_data_model_files(
    ctx: RunContext[AgentDependencies],
) -> DataModelSpanMap:
    """Fetch data model spans for the current codebase.

    Returns:
        Mapping[path][model_identifier] = (start_line, end_line)

    Raises:
        ModelRetry: If there's an error retrieving data model spans from the database.
    """
    codebase_path = ctx.deps.codebase_metadata.codebase_path
    codebase_name = ctx.deps.codebase_metadata.codebase_name

    logger.debug(
        "[get_data_model_files] Called for codebase={}, path={}",
        codebase_name,
        codebase_path,
    )

    try:
        neo4j_manager = get_neo4j_manager()
        logger.debug("[get_data_model_files] Neo4j manager acquired successfully")

        result = await db_get_data_model_files(neo4j_manager, codebase_path)

        logger.info(
            "[get_data_model_files] Found {} files with data models for {}",
            len(result),
            codebase_name,
        )

        # Log first few entries for debugging
        for file_path, models in list(result.items())[:3]:
            logger.debug(
                "[get_data_model_files]   File: {}, models: {}",
                file_path,
                list(models.keys()),
            )

        return result

    except RuntimeError as e:
        logger.error(
            "[get_data_model_files] ServiceRegistry error for {}: {}",
            codebase_name,
            str(e),
        )
        raise ModelRetry(f"Service not initialized: {str(e)}")
    except Exception as e:
        logger.error(
            "[get_data_model_files] Unexpected error for {}: {} - {}",
            codebase_name,
            type(e).__name__,
            str(e),
        )
        raise ModelRetry(
            f"Error retrieving data model files for {codebase_path}: {str(e)}"
        )
