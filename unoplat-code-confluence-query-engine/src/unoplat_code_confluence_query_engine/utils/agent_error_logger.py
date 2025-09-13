from datetime import datetime
import json
from typing import Any, Dict, List

from loguru import logger
from pydantic_ai.exceptions import UnexpectedModelBehavior


def _clip_text(text: str, max_len: int = 800) -> str:
    """Clip long text for safe log output."""
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."


def _serialize_node(node: Any) -> Dict[str, Any]:
    """Best-effort serialization of an agent node for logging."""
    try:
        if hasattr(node, "model_dump_json"):
            data = json.loads(node.model_dump_json())  # type: ignore[attr-defined]
        elif hasattr(node, "model_dump"):
            data = node.model_dump()  # type: ignore[attr-defined]
        else:
            data = str(node)
    except Exception as e:  # noqa: BLE001
        data = {"error": str(e), "repr": repr(node)}

    # Clip very large payloads to keep logs readable
    try:
        s = json.dumps(data, ensure_ascii=False, default=str)
        s = _clip_text(s, 2000)
        data = json.loads(s)
    except Exception:
        # Fall back to string if JSON dumps/loads fails
        data = _clip_text(str(data), 2000)

    return {"type": type(node).__name__, "data": data}


def log_agent_error(
    error: UnexpectedModelBehavior,
    *,
    context: Dict[str, Any] | None = None,
    messages: List[Any] | None = None,
) -> None:
    """
    Log agent errors with consistent, richer context for debugging.

    Args:
        error: UnexpectedModelBehavior exception from PydanticAI
        context: Optional context dict (agent_name, codebase, repository, model info)
        messages: Optional list of message nodes for debugging context
    """
    timestamp = datetime.now().isoformat()
    ctx = context or {}
    agent_name = ctx.get("agent_name", "unknown")

    # Main error line
    logger.error("Agent '{}' failed at {}: {}", agent_name, timestamp, str(error))

    # Context block
    if ctx:
        logger.error("Context: {}", ctx)

    # Underlying cause, if present
    if error.__cause__:
        logger.error("Error cause: {}", repr(error.__cause__))

    # Include a compact node summary to aid diagnosis
    if messages:
        try:
            total = len(messages)
            tail = messages[-5:]  # last few nodes
            summary = [_serialize_node(n) for n in tail]
            logger.debug(
                "Recent nodes (showing last {} of {}): {}",
                len(tail),
                total,
                summary,
            )
        except Exception as e:  # noqa: BLE001
            logger.debug("Failed to serialize nodes for error context: {}", e)
