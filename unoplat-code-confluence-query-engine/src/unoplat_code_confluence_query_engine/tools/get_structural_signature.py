from typing import List, Optional

from aiopath import AsyncPath
from neo4j import AsyncManagedTransaction, Record
from pydantic import BaseModel, Field
from pydantic_ai import ModelRetry, RunContext
from unoplat_code_confluence_commons import StructuralSignature

from unoplat_code_confluence_query_engine.models.agent_dependencies import (
    AgentDependencies,
)


class FileStructuralInfo(BaseModel):
    """Complete structural information for a source file including imports."""

    structural_signature: StructuralSignature = Field(
        ...,
        description="Parsed structural signature with functions, classes, variables",
    )
    imports: List[str] = Field(
        default_factory=list, description="List of import statements in the file"
    )


async def _get_file_structural_info_txn(
    tx: AsyncManagedTransaction, file_path: str
) -> Optional[Record]:
    """Transaction function for getting CodeConfluenceFile structural information.

    Args:
        tx: Neo4j managed transaction instance.
        file_path: Absolute path to the source file to query.

    Returns:
        Neo4j record containing structural signature and imports, or None if not found.
    """
    query = """
    MATCH (f:CodeConfluenceFile {file_path: $file_path})
    RETURN f.structural_signature as structural_signature, f.imports as imports
    """
    result = await tx.run(query, {"file_path": file_path})
    return await result.single()


async def get_structural_signature(
    ctx: RunContext[AgentDependencies], abs_path: str
) -> FileStructuralInfo:
    """Get structural signature and imports for a source file from the Neo4j knowledge graph.

    This tool retrieves pre-analyzed structural information about a source file including:
    - Complete structural signature (functions, classes, variables with line positions)
    - Import statements used in the file

    Args:
        abs_path: Absolute path to the source file.

    Returns:
        Complete structural information including signature and imports.

    Raises:
        ModelRetry: If file path is not absolute, file not found in knowledge graph,
            or structural signature parsing fails.
    """
    # Validate file path security
    path = AsyncPath(abs_path)

    # Check if path is absolute
    if not path.is_absolute():
        raise ModelRetry(
            f"File path must be absolute. Please provide an absolute path instead of: {abs_path}"
        )

    try:
        # Initialize Neo4j connection manager
        try:
            # Use session context manager with managed transaction
            async with ctx.deps.neo4j_conn_manager.get_session() as session:
                # Execute read transaction to get file structural information
                file_record = await session.execute_read(
                    _get_file_structural_info_txn, abs_path
                )

                if file_record is None:
                    raise ModelRetry(
                        f"File not found in knowledge graph: {abs_path}. The path may be incorrect."
                    )

                # Extract structural signature JSON and convert to model
                structural_signature_data = file_record["structural_signature"]
                if not structural_signature_data:
                    raise ModelRetry(
                        f"No structural signature available for file: {abs_path}."
                    )

                try:
                    structural_signature = StructuralSignature.model_validate_json(
                        structural_signature_data
                    )
                except Exception as e:
                    raise ModelRetry(
                        f"Failed to parse structural signature for file {abs_path}: {str(e)}. The data may be corrupted."
                    )

                # Extract imports (default to empty list if None)
                imports = file_record["imports"] or []

                return FileStructuralInfo(
                    structural_signature=structural_signature, imports=imports
                )

        finally:
            await ctx.deps.neo4j_conn_manager.close()

    except ModelRetry:
        # Re-raise ModelRetry exceptions as they contain user-friendly messages
        raise
    except Exception as e:
        raise ModelRetry(
            f"Unexpected error retrieving structural signature for {abs_path}: {str(e)}. Please try again or check if the file has been ingested into the knowledge graph."
        )
