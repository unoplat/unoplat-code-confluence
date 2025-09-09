"""Tool message policies for consistent messaging across agents."""

from unoplat_code_confluence_query_engine.models.agent_execution_request import (
    ToolMessagePolicyProtocol,
)


class DefaultToolMessagePolicy(ToolMessagePolicyProtocol):
    """Default tool message policy with agent-specific overrides."""
    
    DEFAULT_CALL = "🔧 Calling {tool}"
    DEFAULT_RESULT = "✅ Step complete"
    
    # Tool-specific call message overrides (exact replicas from existing services)
    CALL_OVERRIDES = {
        "get_directory_tree": "🔍 Exploring directory structure: {args}",
        "read_file_content": "📖 Reading config file: {args}",
        "get_content_file": "📖 Reading package files: {args}",
        "search_across_codebase": "🔎 Searching for framework usage: {args}",
        "get_structural_signature": "🏗️ Analyzing file structure: {args}",
    }
    
    # Agent-specific result message overrides (exact replicas from existing services)
    RESULT_OVERRIDES = {
        "framework_explorer": "✅ Framework analysis step complete",
        "project_configuration_agent": "✅ Structure analysis complete",
    }
    
    def message_for_tool_call(
        self, 
        agent_name: str, 
        tool_name: str, 
        args_preview: str
    ) -> str:
        """Generate message when agent calls a tool."""
        if tool_name in self.CALL_OVERRIDES:
            return self.CALL_OVERRIDES[tool_name].format(args=args_preview)
        return self.DEFAULT_CALL.format(tool=tool_name)
    
    def message_for_tool_result(
        self, 
        agent_name: str, 
        tool_name: str
    ) -> str:
        """Generate message when tool call completes."""
        if agent_name in self.RESULT_OVERRIDES:
            return self.RESULT_OVERRIDES[agent_name]
        return self.DEFAULT_RESULT