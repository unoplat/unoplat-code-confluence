"""Fetch files that contain data models (core business logic roots) for a codebase.

This tool returns a normalized list of file paths that either:
- Are directly marked as data model files (has_data_model=true), or
- Use standardized framework features 'data_model' or 'db_data_model'.

Agents should:
1) Call this tool to get candidate model file paths
2) Use read_file_content (get_content_file) to open each file
3) Identify relevant data model definitions inside each file and summarize responsibilities per file
4) Only then group files into domains and write descriptions based on actual inspected content
"""

from __future__ import annotations

from typing import List

from pydantic_ai import ModelRetry, RunContext

from unoplat_code_confluence_query_engine.db.neo4j.business_logic_repository import (
    db_get_data_model_files,
)
from unoplat_code_confluence_query_engine.models.agent_dependencies import (
    AgentDependencies,
)


async def get_data_model_files(
    ctx: RunContext[AgentDependencies],
) -> List[str]:
    """Fetch data model file paths for the current codebase.

    This tool returns file paths containing both local data models (domain entities,
    value objects) and database data models (ORM models, database schemas).

    Returns:
        List of absolute file paths containing data models.

    Raises:
        ModelRetry: If there's an error retrieving data model files from the database.
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
