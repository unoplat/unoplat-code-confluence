"""Service for handling library documentation lookups using Context7 Agent."""

from loguru import logger
from pydantic_ai import Agent


class LibraryDocumentationService:
    """Service for retrieving library documentation using plain Context7 Agent.

    Uses plain Agent (NOT TemporalAgent) to execute MCP calls directly within
    the calling async context, avoiding cancel scope conflicts when running
    under Temporal activities.
    """

    async def get_library_documentation(
        self,
        context7_agent: Agent[None, str],
        lib_name: str,
        programming_language: str,
        feature_description: str | None = None,
        tool_type: str | None = None,
    ) -> str:
        """Get concise library/framework documentation summary.

        Args:
            context7_agent: Plain Context7 Agent for MCP-based lookups.
            lib_name: Name of the library/framework
            programming_language: Programming language context (required)
            feature_description: Optional specific feature name or functionality description
            tool_type: Optional hint for developer tools (linter, test-runner, build-tool, etc.)

        Returns:
            Concise summary of the library/framework or feature.
            For developer tools, returns commands and config information.
        """
        try:
            # Construct the user message based on context
            if tool_type:
                # For developer tools, request commands and configuration info
                tool_context = f" as a {tool_type}" if tool_type else ""
                if feature_description:
                    user_message = (
                        f"Provide commands and configuration for '{feature_description}' "
                        f"in {lib_name}{tool_context} for {programming_language}. "
                        f"Focus on official documentation for commands, config files, and usage."
                    )
                else:
                    user_message = (
                        f"Provide commands and configuration for {lib_name}{tool_context} "
                        f"for {programming_language}. Focus on official documentation for "
                        f"common commands, config files, installation, and typical usage patterns."
                    )
            elif feature_description:
                # Standard feature description request
                user_message = (
                    f"Provide a concise summary about '{feature_description}' "
                    f"in the {lib_name} library/framework for {programming_language}. "
                    f"This could be an exact feature name or a description of functionality. "
                    f"Focus on: 1) What this feature/functionality does, "
                    f"2) Its main use case, 3) Key benefit or characteristic."
                )
            else:
                # Standard library/framework overview request
                user_message = (
                    f"Provide a concise overview of the {lib_name} library/framework "
                    f"for {programming_language}. "
                    f"Focus on: 1) Core functionality, "
                    f"2) Primary use case, 3) Key differentiator."
                )

            # Run the Context7 Agent (plain execution, avoids CancelScope conflicts)
            
            final_result = await context7_agent.run(user_message)

            # Extract and return the response
            if final_result and final_result.output:
                return str(final_result.output)
            else:
                return f"Unable to retrieve documentation for {lib_name}"

        except Exception as e:
            logger.error(
                "Error retrieving library documentation for {}: {}", lib_name, str(e)
            )
            # Return a fallback message
            if feature_description:
                return f"Documentation unavailable for '{feature_description}' in {lib_name}"
            else:
                return f"Documentation unavailable for {lib_name}"
