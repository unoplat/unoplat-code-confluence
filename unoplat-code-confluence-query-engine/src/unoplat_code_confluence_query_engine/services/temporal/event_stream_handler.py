"""Event stream handler for Temporal durable agents.

Handles streaming events from PydanticAI agents with DB-first stateless tracking.
Persists events to PostgreSQL via atomic CTEs for progress tracking.
"""

from collections.abc import AsyncIterable

from loguru import logger
from pydantic_ai import AgentStreamEvent, RunContext
from pydantic_ai.messages import (
    FinalResultEvent,
    FunctionToolCallEvent,
    FunctionToolResultEvent,
)

from unoplat_code_confluence_query_engine.models.runtime.agent_dependencies import (
    AgentDependencies,
)

# Agent names that contribute to progress calculation
COMPLETION_NAMESPACES: frozenset[str] = frozenset(
    {
        "project_configuration_agent",
        "development_workflow_agent",
        "dependency_guide_agent",
        "business_logic_domain_agent",
    }
)


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


def _extract_event_message(event: AgentStreamEvent) -> str | None:
    """Extract human-readable message from stream event.

    Args:
        event: The stream event

    Returns:
        Message string or None
    """
    if isinstance(event, FunctionToolCallEvent):
        return f"Calling {event.part.tool_name}"
    if isinstance(event, FunctionToolResultEvent):
        preview = str(event.result.content)[:100]
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
            continue

        message = _extract_event_message(event)

        # Always log for observability
        if isinstance(event, FunctionToolCallEvent):
            logger.info(
                f"[{codebase}] TOOL CALL: name={event.part.tool_name}, args={event.part.args}, id={event.part.tool_call_id}"
            )
        elif isinstance(event, FunctionToolResultEvent):
            result_preview = str(event.result.content)[:200]
            logger.info(
                "[{}] TOOL RESULT: id={}, result_preview={}",
                codebase,
                event.tool_call_id,
                result_preview,
            )
        elif isinstance(event, FinalResultEvent):
            logger.info(f"[{codebase}] FINAL RESULT: tool_name={event.tool_name}")

        # Persist to DB if tracking is enabled
        if db_tracking_enabled and deps and owner_name and repo_name:
            try:
                writer = get_snapshot_writer()
                await writer.append_event_atomic(
                    owner_name=owner_name,
                    repo_name=repo_name,
                    codebase_name=codebase,
                    agent_name=deps.agent_name,
                    phase=phase,
                    message=message,
                    completion_namespaces=set(COMPLETION_NAMESPACES),
                    repository_workflow_run_id=deps.repository_workflow_run_id,
                )
            except Exception as e:
                # Log but don't crash - event tracking is non-critical
                logger.error(
                    "[{}] Failed to persist event to DB: {} - {}",
                    codebase,
                    type(e).__name__,
                    str(e),
                )
