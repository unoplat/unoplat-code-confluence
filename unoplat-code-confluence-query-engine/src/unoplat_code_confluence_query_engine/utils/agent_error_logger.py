from datetime import datetime
import json

from loguru import logger
from pydantic import BaseModel
from pydantic_ai.exceptions import (
    FallbackExceptionGroup,
    ModelAPIError,
    ModelHTTPError,
    UnexpectedModelBehavior,
)

JsonPrimitive = str | int | float | bool | None


def _to_json_value(value: object) -> object:
    """Coerce a value into a JSON-serializable structure.

    Args:
        value: Value to coerce

    Returns:
        JSON-safe value
    """
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if isinstance(value, BaseModel):
        return json.loads(value.model_dump_json())
    try:
        return json.loads(json.dumps(value, default=str))
    except TypeError:
        return str(value)
    return str(value)


def _to_json_dict(value: dict[object, object]) -> dict[str, object]:
    """Coerce a dict into JSON-safe values.

    Args:
        value: Dictionary to coerce

    Returns:
        Dict with string keys and JSON-safe values
    """
    normalized = json.loads(json.dumps(value, default=str))
    if isinstance(normalized, dict):
        return normalized
    return {"value": normalized}


def _serialize_node(node: BaseModel) -> dict[str, object]:
    """Best-effort serialization of an agent node for logging."""
    try:
        data = _to_json_value(json.loads(node.model_dump_json()))
    except Exception as e:  # noqa: BLE001
        data = _to_json_value({"error": str(e), "repr": repr(node)})

    return {"type": type(node).__name__, "data": data}


def _normalize_error_body(body: object | None) -> object | None:
    """Normalize error bodies into JSON-serializable structures without clipping.

    Args:
        body: Raw error body from a provider response

    Returns:
        JSON-serializable body or a safe string fallback
    """
    if body is None:
        return None
    if isinstance(body, bytes):
        return body.decode("utf-8", errors="replace")
    if isinstance(body, BaseModel):
        try:
            return _to_json_value(json.loads(body.model_dump_json()))
        except Exception:
            return body.model_dump_json()
    return _to_json_value(body)


def log_model_api_error(
    error: ModelHTTPError | ModelAPIError,
    *,
    context: dict[str, object] | None = None,
) -> dict[str, object]:
    """Log ModelHTTPError or ModelAPIError with full response body (no clipping).

    Args:
        error: ModelHTTPError or ModelAPIError exception from pydantic-ai
        context: Optional context dict (agent_name, codebase, repository, model info)

    Returns:
        Dictionary containing error details for metadata enrichment
    """
    timestamp = datetime.now().isoformat()
    ctx = context or {}
    agent_name = ctx.get("agent_name", "unknown")
    codebase = ctx.get("codebase", "unknown")

    error_details: dict[str, object] = {
        "error_type": type(error).__name__,
        "model_name": error.model_name,
        "message": str(error),
        "timestamp": timestamp,
    }

    if context:
        error_details["agent_name"] = str(agent_name)
        error_details["codebase"] = str(codebase)

    if isinstance(error, ModelHTTPError):
        error_details["status_code"] = error.status_code
        # Log full body without clipping (AC#1)
        normalized_body = _normalize_error_body(error.body)
        error_details["body"] = normalized_body

        logger.error(
            "Model HTTP error: agent='{}' codebase='{}' status_code={} model='{}' timestamp={}",
            agent_name,
            codebase,
            error.status_code,
            error.model_name,
            timestamp,
        )
        # Log full body at ERROR level without clipping
        logger.error(
            "Model HTTP error body (full): {}",
            normalized_body,
        )
    else:
        logger.error(
            "Model API error: agent='{}' codebase='{}' model='{}' message='{}' timestamp={}",
            agent_name,
            codebase,
            error.model_name,
            str(error),
            timestamp,
        )

    return error_details


def log_fallback_exception_group(
    exc_group: FallbackExceptionGroup,
    *,
    context: dict[str, object] | None = None,
) -> list[dict[str, object]]:
    """Handle FallbackExceptionGroup by logging each contained model error.

    Args:
        exc_group: FallbackExceptionGroup containing multiple exceptions
        context: Optional context dict (agent_name, codebase, repository)

    Returns:
        List of error details dicts from each contained exception
    """
    error_details_list: list[dict[str, object]] = []
    ctx = context or {}
    agent_name = ctx.get("agent_name", "unknown")

    logger.error(
        "All fallback models failed: {} exception(s) for agent '{}'",
        len(exc_group.exceptions),
        agent_name,
    )

    for exc in exc_group.exceptions:
        if isinstance(exc, (ModelHTTPError, ModelAPIError)):
            details = log_model_api_error(exc, context=context)
            error_details_list.append(details)
        else:
            # Log non-model errors as well
            logger.error(
                "Fallback exception (non-model): type='{}' message='{}'",
                type(exc).__name__,
                str(exc),
            )
            error_details_list.append(
                {
                    "error_type": type(exc).__name__,
                    "message": str(exc),
                }
            )

    return error_details_list


def extract_model_error_from_exception(
    exception: BaseException,
    *,
    context: dict[str, object] | None = None,
) -> dict[str, object] | None:
    """Extract model error details from any exception, traversing cause chain.

    Handles:
    - ModelHTTPError: Returns dict with status_code, model_name, body
    - ModelAPIError: Returns dict with model_name, message
    - FallbackExceptionGroup: Returns dict with list of fallback errors
    - Generic BaseExceptionGroup: Iterates and collects model errors
    - Traverses __cause__ chain recursively

    Args:
        exception: Any exception to extract model error from
        context: Optional context dict for logging

    Returns:
        Dictionary with model error details or None if no model error found
    """
    # Direct ModelHTTPError
    if isinstance(exception, ModelHTTPError):
        details = log_model_api_error(exception, context=context)
        return details

    # Direct ModelAPIError (non-HTTP)
    if isinstance(exception, ModelAPIError):
        details = log_model_api_error(exception, context=context)
        return details

    # FallbackExceptionGroup (AC#2)
    if isinstance(exception, FallbackExceptionGroup):
        fallback_errors = log_fallback_exception_group(exception, context=context)
        return {
            "error_type": "FallbackExceptionGroup",
            "fallback_errors": fallback_errors,
        }

    # Generic BaseExceptionGroup (iterate exceptions)
    if isinstance(exception, BaseExceptionGroup):
        model_errors: list[dict[str, object]] = []
        for exc in exception.exceptions:
            if isinstance(exc, BaseException):
                nested_result = extract_model_error_from_exception(exc, context=context)
                if nested_result:
                    model_errors.append(nested_result)
        if model_errors:
            return {
                "error_type": "ExceptionGroup",
                "contained_errors": model_errors,
            }

    # Traverse __cause__ chain recursively
    if exception.__cause__ is not None:
        return extract_model_error_from_exception(exception.__cause__, context=context)

    return None


def extract_model_error_from_details(details: object) -> dict[str, object] | None:
    """Extract model error details from ApplicationError.details payloads.

    Args:
        details: ApplicationError.details payload

    Returns:
        Model error details dict when present
    """
    if isinstance(details, dict):
        details_dict: dict[object, object] = {
            key: value for key, value in details.items()
        }
        if "model_error_details" in details_dict and isinstance(
            details_dict["model_error_details"], dict
        ):
            return _to_json_dict(details_dict["model_error_details"])
        if "model_error" in details_dict and isinstance(
            details_dict["model_error"], dict
        ):
            return _to_json_dict(details_dict["model_error"])
    if isinstance(details, (list, tuple)):
        for raw_item in details:
            if isinstance(raw_item, dict):
                item_dict: dict[object, object] = {
                    key: value for key, value in raw_item.items()
                }
                if "model_error_details" in item_dict and isinstance(
                    item_dict["model_error_details"], dict
                ):
                    return _to_json_dict(item_dict["model_error_details"])
                if "model_error" in item_dict and isinstance(
                    item_dict["model_error"], dict
                ):
                    return _to_json_dict(item_dict["model_error"])
    return None


def log_agent_error(
    error: UnexpectedModelBehavior,
    *,
    context: dict[str, object] | None = None,
    messages: list[object] | None = None,
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
            summary: list[dict[str, object]] = []
            for node in tail:
                if isinstance(node, BaseModel):
                    summary.append(_serialize_node(node))
            logger.debug(
                "Recent nodes (showing last {} of {}): {}",
                len(tail),
                total,
                summary,
            )
        except Exception as e:  # noqa: BLE001
<<<<<<< HEAD
            logger.debug("Failed to serialize nodes for error context: {}", e)
=======
            logger.debug(f"Failed to serialize nodes for error context: {e}")
>>>>>>> origin/main
