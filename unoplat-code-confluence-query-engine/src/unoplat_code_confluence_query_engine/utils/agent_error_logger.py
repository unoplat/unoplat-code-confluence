from datetime import datetime
from typing import Any, Dict, List

from loguru import logger
from pydantic_ai.exceptions import UnexpectedModelBehavior


def log_agent_error(error: UnexpectedModelBehavior, *, context: Dict[str, Any] | None = None, messages: List[Any] | None = None) -> None:
    """
    Log agent errors with consistent format for debugging.
    
    Args:
        error: UnexpectedModelBehavior exception from PydanticAI
        context: Optional context dict with agent_name, codebase, repository info
        messages: Optional list of message nodes for debugging context
    """
    timestamp = datetime.now().isoformat()
    agent_name = context.get("agent_name", "unknown") if context else "unknown"
    
    # Log the main error
    logger.error(
        "Agent '{}' failed at {}: {}",
        agent_name,
        timestamp,
        str(error)
    )
    
    # Log context information if provided
    if context:
        logger.error("Context: {}", context)
    
    # Log the cause if available
    if error.__cause__:
        logger.error("Error cause: {}", repr(error.__cause__))
    
    # Log message history if provided for debugging
    if messages:
        logger.debug("Message history for debugging (total {} nodes): {}", len(messages), messages)