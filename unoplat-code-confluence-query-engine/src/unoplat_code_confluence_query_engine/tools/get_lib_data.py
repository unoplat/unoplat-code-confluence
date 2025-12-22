"""Tool for retrieving library/framework documentation using LibraryDocumentationService."""

from loguru import logger
from pydantic_ai import ModelRetry, RunContext

from unoplat_code_confluence_query_engine.models.runtime.agent_dependencies import (
    AgentDependencies,
)
from unoplat_code_confluence_query_engine.services.temporal.service_registry import (
    get_context7_agent,
    get_library_documentation_service,
)


async def get_lib_data(
    ctx: RunContext[AgentDependencies],
    lib_name: str,
    programming_language: str,
    feature_description: str | None = None,
) -> str:
    """Get concise library/framework documentation summary.

    This tool provides access to library documentation through a simplified interface.
    Returns concise 3-5 line summaries.

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
    logger.info(
        "get_lib_data - Start - lib={}, lang={}, feature={}",
        lib_name,
        programming_language,
        feature_description,
    )

    try:
        # Get singleton Context7 Agent from ServiceRegistry.
        # The agent is initialized at worker startup with its MCPServer and model configuration.
        # Using a singleton avoids connection overhead of creating fresh MCPServer per call.
        logger.debug("[get_lib_data] Getting singleton Context7 Agent from registry...")
        context7_agent = get_context7_agent()
        logger.debug("[get_lib_data] Context7 Agent retrieved successfully")

        logger.debug("[get_lib_data] Fetching LibraryDocumentationService...")
        library_service = get_library_documentation_service()
        logger.debug(
            "[get_lib_data] LibraryDocumentationService retrieved successfully"
        )

        logger.info(
            "[get_lib_data] Calling Context7 Agent for {} ({})...",
            lib_name,
            programming_language,
        )

        result = await library_service.get_library_documentation(
            context7_agent=context7_agent,
            lib_name=lib_name,
            programming_language=programming_language,
            feature_description=feature_description,
        )

        # Log result preview (first 200 chars)
        result_preview = result[:200] + "..." if len(result) > 200 else result
        logger.info(
            f"[get_lib_data] SUCCESS - {lib_name} ({programming_language}): {len(result)} chars"
        )
        logger.debug(f"[get_lib_data] Result preview: {result_preview}")
        return result

    except RuntimeError as e:
        # ServiceRegistry not initialized or missing service
        logger.error("[get_lib_data] ServiceRegistry error: {}", str(e))
        raise ModelRetry(f"Service not initialized: {str(e)}")
    except Exception as e:
        error_context = (
            f" for feature '{feature_description}'" if feature_description else ""
        )
        logger.error(f"[get_lib_data] Error for {lib_name}{error_context}: {e!s}")
        return f"Error retrieving documentation for {lib_name}{error_context}: {e!s}"
