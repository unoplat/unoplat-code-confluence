"""Core types and protocols for unified agent execution service."""

from dataclasses import dataclass
from typing import Any, Dict, Optional, Protocol, Union

from fastapi import Request
from pydantic import BaseModel
from pydantic_ai import Agent


@dataclass
class AgentExecutionRequest:
    """Request configuration for agent execution.
    
    Args:
        agent_name: Identifier for the agent (e.g., "framework_explorer", "project_configuration_agent")
        agent: The pydantic-ai Agent instance to run
        fastapi_request: FastAPI request object for accessing app.state dependencies
        event_namespace: Optional override for event prefix in SSE streams
        extra_prompt_context: Optional extra context to pass to prompt registry
    """
    agent_name: str
    agent: Agent[Any, Any]
    fastapi_request: Request
    event_namespace: Optional[str] = None
    postprocess_enabled: bool = False
    postprocess_options: Optional[Dict[str, Any]] = None
    extra_prompt_context: Optional[Dict[str, Any]] = None


class PromptProviderProtocol(Protocol):
    """Protocol for providing agent-specific prompt templates."""
    
    def get_user_message(
        self,
        agent_name: str,
        repository_qualified_name: str,
        codebase_name: str,
        codebase_path: str,
        codebase_language: str,
        extra_prompt_context: Optional[Dict[str, Union[BaseModel, list[BaseModel], str]]] = None,
    ) -> str:
        """Generate user message prompt for the given agent and codebase context."""
        ...


class ToolMessagePolicyProtocol(Protocol):
    """Protocol for providing consistent tool call/result messages."""
    
    def message_for_tool_call(
        self, 
        agent_name: str, 
        tool_name: str, 
        args_preview: str
    ) -> str:
        """Generate message when agent calls a tool."""
        ...
    
    def message_for_tool_result(
        self, 
        agent_name: str, 
        tool_name: str
    ) -> str:
        """Generate message when tool call completes."""
        ...