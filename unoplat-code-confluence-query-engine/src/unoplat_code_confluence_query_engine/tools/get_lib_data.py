"""Tool for retrieving library/framework documentation using LibraryDocumentationService."""

from typing import Optional

from pydantic_ai import RunContext

from unoplat_code_confluence_query_engine.models.agent_dependencies import (
    AgentDependencies,
)


async def get_lib_data(
    ctx: RunContext[AgentDependencies],
    lib_name: str,
    programming_language: str,
    feature_description: Optional[str] = None,
) -> str:
    """Get concise library/framework documentation summary.

    This tool provides access to library documentation
    through a simplified interface. Returns concise 3-5 line summaries.

    Args:
        lib_name: Name of the library/framework (e.g., "fastapi", "react", "sqlalchemy").
        programming_language: Programming language context (e.g., "python", "javascript").
        feature_description: Optional description of specific feature or aspect needed
            (e.g., "APIRouter", "hooks", "database connections", "testing commands").

    Returns:
        Concise summary of the library/framework or specific feature.

    Examples:
        await get_lib_data(ctx, "fastapi", "python")
        await get_lib_data(ctx, "fastapi", "python", feature_description="APIRouter")
        await get_lib_data(ctx, "pytest", "python", feature_description="testing commands")
        await get_lib_data(ctx, "react", "javascript", feature_description="hooks")
    """

    try:
        # Always create a fresh Context7 agent via the factory to prevent
        # CancelScope clashes when tool calls run in parallel.
        if not hasattr(ctx.deps, "context7_agent_factory"):
            raise RuntimeError(
                "context7_agent_factory is required on deps for get_lib_data"
            )
        context7_agent = ctx.deps.context7_agent_factory()

        # Use the service to get documentation with the Context7 agent
        result = await ctx.deps.library_documentation_service.get_library_documentation(
            context7_agent=context7_agent,
            lib_name=lib_name,
            programming_language=programming_language,
            feature_description=feature_description,
        )

        return result

    except Exception as e:
        # Return a helpful error message
        error_context = (
            f" for feature '{feature_description}'" if feature_description else ""
        )
        return f"Error retrieving documentation for {lib_name}{error_context}: {str(e)}"
