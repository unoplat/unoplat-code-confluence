"""Event stream handler for Temporal durable agents.

Handles streaming events from PydanticAI agents with DB-first stateless tracking.
Persists events to PostgreSQL via atomic CTEs for progress tracking.
"""

import os
from collections.abc import AsyncIterable
import json
from typing import Any

from loguru import logger
from pydantic_ai import AgentStreamEvent, RunContext
from pydantic_ai.messages import (
    FinalResultEvent,
    FunctionToolCallEvent,
    FunctionToolResultEvent,
    RetryPromptPart,
    ToolReturnPart,
)

from unoplat_code_confluence_query_engine.models.runtime.agent_dependencies import (
    AgentDependencies,
)
from unoplat_code_confluence_query_engine.utils.framework_feature_language_support import (
    is_app_interfaces_supported,
)

# Agent names that contribute to progress calculation
BASE_COMPLETION_NAMESPACES: frozenset[str] = frozenset(
    {
        "development_workflow_guide",
        "dependency_guide",
        "business_domain_guide",
    }
)

_DEBUG_EVENT_TRACE = os.getenv("TEMPORAL_EVENT_DEBUG", "false").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}


def get_completion_namespaces(
    codebase_programming_language: str | None,
) -> frozenset[str]:
    """Return completion namespaces based on the codebase programming language."""
    language = codebase_programming_language or ""
    if is_app_interfaces_supported(language):
        return BASE_COMPLETION_NAMESPACES | {"app_interfaces_agent"}
    return BASE_COMPLETION_NAMESPACES


def _map_event_to_phase(event: AgentStreamEvent) -> str | None:
    """Map PydanticAI stream event to DB phase string.

    Args:
        event: The stream event to map

    Returns:
        Phase string or None if event should be skipped
    """
    if isinstance(event, FunctionToolCallEvent):
        return "tool.call"
    if isinstance(event, FunctionToolResultEvent):
        return "tool.result"
    if isinstance(event, FinalResultEvent):
        return "result"
    return None


def _extract_tool_call_id(event: AgentStreamEvent) -> str | None:
    """Extract tool call identifier when present."""
    if isinstance(event, FunctionToolCallEvent):
        return event.part.tool_call_id
    if isinstance(event, FunctionToolResultEvent):
        return event.tool_call_id
    return None


def _extract_tool_name(event: AgentStreamEvent) -> str | None:
    """Extract tool name when present."""
    if isinstance(event, FunctionToolCallEvent):
        return event.part.tool_name
    if isinstance(event, FinalResultEvent):
        return event.tool_name
    return None


def _extract_tool_args(event: AgentStreamEvent) -> dict[str, Any] | None:
    """Extract tool arguments as a dict when present."""
    if isinstance(event, FunctionToolCallEvent):
        args = event.part.args
        if isinstance(args, dict):
            return args
        if isinstance(args, str):
            if not args:
                empty_args: dict[str, Any] = {}
                return empty_args
            try:
                parsed_args = json.loads(args)
            except json.JSONDecodeError:
                logger.warning(
                    "[event_stream] Invalid tool args JSON for tool={} call_id={}; skipping tool_args",
                    event.part.tool_name,
                    event.part.tool_call_id,
                )
                return None
            if isinstance(parsed_args, dict):
                return parsed_args
            logger.warning(
                "[event_stream] Ignoring non-object tool args for tool={} call_id={} parsed_type={}",
                event.part.tool_name,
                event.part.tool_call_id,
                type(parsed_args).__name__,
            )
    return None


def _render_tool_result_content(event: FunctionToolResultEvent) -> str:
    """Render a PydanticAI tool result using its model-facing API."""
    result = event.result
    if isinstance(result, ToolReturnPart):
        return result.model_response_str()
    if isinstance(result, RetryPromptPart):
        return result.model_response()


def _extract_tool_result_content(rendered_tool_result_content: str | None) -> str | None:
    """Extract raw tool result content capped at 100_000 chars."""
    if rendered_tool_result_content is None:
        return None
    return rendered_tool_result_content[:100_000]


def _extract_event_message(
    event: AgentStreamEvent,
    rendered_tool_result_content: str | None,
) -> str | None:
    """Extract human-readable message from stream event.

    Args:
        event: The stream event
        rendered_tool_result_content: Rendered result content for tool result events

    Returns:
        Message string or None
    """
    if isinstance(event, FunctionToolCallEvent):
        return f"Calling {event.part.tool_name}"
    if isinstance(event, FunctionToolResultEvent):
        preview = (rendered_tool_result_content or "")[:200]
        return f"Tool result: {preview}"
    if isinstance(event, FinalResultEvent):
        return (
            f"Final result via {event.tool_name}" if event.tool_name else "Final result"
        )
    return None


async def event_stream_handler(
    ctx: RunContext[AgentDependencies],
    event_stream: AsyncIterable[AgentStreamEvent],
) -> None:
    """Handle streaming events with DB-first stateless tracking.

    This handler runs in the Temporal activity process.
    Persists events to PostgreSQL via atomic CTEs for progress tracking.
    Falls back to logging-only if deps are not properly configured.
    """
    # Import here to avoid circular imports
    from unoplat_code_confluence_query_engine.services.temporal.service_registry import (  # noqa: PLC0415
        get_snapshot_writer,
    )

    deps = ctx.deps
    codebase = deps.codebase_metadata.codebase_name if deps else "unknown"

    # Check if DB tracking is configured
    db_tracking_enabled = bool(
        deps
        and deps.repository_workflow_run_id
        and deps.agent_name
        and deps.repository_qualified_name
    )

    # Parse owner/repo for DB persistence
    owner_name: str | None = None
    repo_name: str | None = None
    if db_tracking_enabled and deps:
        qualified = deps.repository_qualified_name
        if "/" in qualified:
            parts = qualified.split("/", 1)
            owner_name = parts[0]
            repo_name = parts[1]
        else:
            logger.warning(
                "[{}] Invalid repository_qualified_name format: {}",
                codebase,
                qualified,
            )
            db_tracking_enabled = False

    async for event in event_stream:
        phase = _map_event_to_phase(event)
        if phase is None:
            del event
            continue

        rendered_tool_result_content = (
            _render_tool_result_content(event)
            if isinstance(event, FunctionToolResultEvent)
            else None
        )
        message = _extract_event_message(event, rendered_tool_result_content)
        tool_call_id = _extract_tool_call_id(event)
        tool_name = _extract_tool_name(event)
        tool_args = _extract_tool_args(event)
        tool_result_content = _extract_tool_result_content(rendered_tool_result_content)
        event_kind = type(event).__name__

        if _DEBUG_EVENT_TRACE:
            logger.debug(
                "[{}] EVENT TRACE: agent={} phase={} event_kind={} tool_name={} tool_call_id={} run_id={}",
                codebase,
                deps.agent_name if deps else None,
                phase,
                event_kind,
                tool_name,
                tool_call_id,
                deps.repository_workflow_run_id if deps else None,
            )

        # Persist to DB if tracking is enabled
        if db_tracking_enabled and deps and owner_name and repo_name:
            try:
                writer = get_snapshot_writer()
                event_id = await writer.append_event_atomic(
                    owner_name=owner_name,
                    repo_name=repo_name,
                    codebase_name=codebase,
                    agent_name=deps.agent_name,
                    phase=phase,
                    message=message,
                    tool_name=tool_name,
                    tool_call_id=tool_call_id,
                    tool_args=tool_args,
                    tool_result_content=tool_result_content,
                    completion_namespaces=set(
                        get_completion_namespaces(
                            deps.codebase_metadata.codebase_programming_language
                        )
                    ),
                    repository_workflow_run_id=deps.repository_workflow_run_id,
                )
                if _DEBUG_EVENT_TRACE:
                    logger.debug(
                        "[{}] EVENT PERSISTED: agent={} phase={} event_kind={} tool_name={} tool_call_id={} event_id={} run_id={}",
                        codebase,
                        deps.agent_name,
                        phase,
                        event_kind,
                        tool_name,
                        tool_call_id,
                        event_id,
                        deps.repository_workflow_run_id,
                    )
            except Exception as e:
                # Log but don't crash - event tracking is non-critical
                logger.error(
                    "[{}] Failed to persist event to DB: {} - {} (agent={}, phase={}, event_kind={}, tool_name={}, tool_call_id={}, run_id={})",
                    codebase,
                    type(e).__name__,
                    str(e),
                    deps.agent_name,
                    phase,
                    event_kind,
                    tool_name,
                    tool_call_id,
                    deps.repository_workflow_run_id,
                )

        # Drop large per-event temporaries before awaiting the next stream event.
        del event, rendered_tool_result_content, message, tool_args, tool_result_content
