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

from pydantic_ai import ModelRetry, RunContext

from unoplat_code_confluence_query_engine.db.neo4j.business_logic_repository import (
    DataModelSpanMap,
    db_get_data_model_files,
)
from unoplat_code_confluence_query_engine.models.agent_dependencies import (
    AgentDependencies,
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

    try:
        result = await db_get_data_model_files(
            ctx.deps.neo4j_conn_manager, codebase_path
        )
        return result
    except Exception as e:
        raise ModelRetry(
            f"Unexpected error retrieving data model files for {codebase_path}: {str(e)}"
        )
    finally:
        # Do not close the shared Neo4j connection manager here; lifecycle is managed at the app level.
        # Closing it here can break subsequent DB-dependent steps (e.g., post-processing or repeated tool calls).
        pass
