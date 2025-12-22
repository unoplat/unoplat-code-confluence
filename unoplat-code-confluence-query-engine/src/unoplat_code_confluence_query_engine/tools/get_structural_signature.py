from typing import List, Optional, Union

from aiopath import AsyncPath
from neo4j import AsyncManagedTransaction, Record
from pydantic import BaseModel, Field
from pydantic_ai import ModelRetry, RunContext
from unoplat_code_confluence_commons.base_models import (
    PythonStructuralSignature,
    TypeScriptStructuralSignature,
    deserialize_structural_signature,
)

from unoplat_code_confluence_query_engine.models.runtime.agent_dependencies import (
    AgentDependencies,
)


class FileStructuralInfo(BaseModel):
    """Complete structural information for a source file including imports."""

    structural_signature: Union[
        PythonStructuralSignature, TypeScriptStructuralSignature
    ] = Field(
        ...,
        description="Language-specific structural signature with functions, classes, variables",
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
        abs_path: **ABSOLUTE PATH REQUIRED** - Full filesystem path starting with /.
                  Examples: /opt/unoplat/repositories/my-repo/src/module.py, /opt/unoplat/repositories/my-repo/service.ts
                  Do NOT use relative paths like 'src/file.py', 'module.py', or './config.ts'

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

                # Get programming language from codebase metadata (agent dependencies)
                language = ctx.deps.codebase_metadata.programming_language.value

                try:
                    # Use language-aware deserialization helper
                    structural_signature = deserialize_structural_signature(
                        structural_signature_data, language
                    )
                except ValueError as e:
                    raise ModelRetry(
                        f"Unsupported language for file {abs_path}: {str(e)}"
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
