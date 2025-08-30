"""Fetch files that contain data models (core business logic roots) for a codebase.

This tool returns a normalized list of files that either:
- Are directly marked as data model files (has_data_model=true), or
- Use standardized framework features 'data_model' or 'db_data_model'.

Agents should:
1) Call this tool to get candidate model files
2) Use read_file_content (get_content_file) to open each file
3) Identify relevant data model definitions inside each file and summarize responsibilities per file
4) Only then group files into domains and write descriptions based on actual inspected content
"""

from __future__ import annotations

from typing import Any, Dict, List

from pydantic_ai import ModelRetry, RunContext

from unoplat_code_confluence_query_engine.db.neo4j.business_logic_repository import (
    db_get_core_files_with_context,
)
from unoplat_code_confluence_query_engine.models.agent_dependencies import (
    AgentDependencies,
)


async def get_core_files(
    ctx: RunContext[AgentDependencies],
) -> List[Dict[str, Any]]:
    """Fetch core files (data models) with context for the current codebase.

    Args:
        domain_filter: Optional substring to filter package qualified_name

    Returns:
        List of dict items with keys: path, has_data_model, package, features, signature, imports
    """
    codebase_path = ctx.deps.codebase_metadata.codebase_path

    try:
        result = await db_get_core_files_with_context(
            ctx.deps.neo4j_conn_manager, codebase_path
        )
        return result
    except Exception as e:
        raise ModelRetry(
            f"Unexpected error retrieving core files for {codebase_path}: {str(e)}"
        )
    finally:
        await ctx.deps.neo4j_conn_manager.close()


