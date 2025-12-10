"""Trace utilities for distributed tracing and logging context."""

from __future__ import annotations

import contextvars
from typing import TYPE_CHECKING, Optional
import uuid

from loguru import logger

if TYPE_CHECKING:
    from loguru import Logger

trace_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "trace_id", default=None
)
workflow_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "workflow_id", default=None
)
workflow_run_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "workflow_run_id", default=None
)


def build_trace_id(repo: str | None, owner: str | None) -> str:
    """Build a trace ID from repository and owner information.

    Args:
        repo: The repository name
        owner: The owner of the repository

    Returns:
        A trace ID in the format "repo__owner" if both repo and owner are provided,
        otherwise returns a UUID4 string
    """
    return f"{repo}__{owner}" if repo and owner else str(uuid.uuid4())


def bind_trace_id_logger(trace_id: str) -> "Logger":
    """Create a logger bound with trace_id.

    Args:
        trace_id: The trace ID to bind to the logger

    Returns:
        A Loguru logger instance with trace_id bound
    """
    return logger.bind(app_trace_id=trace_id)


def bind_logger(
    trace_id: str,
    workflow_id: str,
    workflow_run_id: str,
) -> "Logger":
    """Create a Loguru logger instance with bound context variables.

    Args:
        trace_id: The trace ID to bind to the logger
        workflow_id: The workflow ID to bind to the logger
        workflow_run_id: The workflow run ID to bind to the logger

    Returns:
        A Loguru logger instance with appropriate context variables bound
    """
    log_context: dict[str, str] = {}
    if trace_id:
        log_context["app_trace_id"] = trace_id
    if workflow_id:
        log_context["workflow_id"] = workflow_id
    if workflow_run_id:
        log_context["workflow_run_id"] = workflow_run_id

    return logger.bind(**log_context)


def seed_ids(
    trace_id: str,
    workflow_id: str,
    workflow_run_id: str,
) -> None:
    """Set the trace_id, workflow_id, and workflow_run_id in their respective ContextVars.

    This function sets up context variables for the current task/thread, making these IDs
    available throughout the execution context.

    Args:
        trace_id: The trace ID to set in the context
        workflow_id: The workflow ID to set in the context
        workflow_run_id: The workflow run ID to set in the context
    """
    if trace_id:
        trace_id_var.set(trace_id)
    if workflow_id:
        workflow_id_var.set(workflow_id)
    if workflow_run_id:
        workflow_run_id_var.set(workflow_run_id)


def seed_and_bind_logger(
    trace_id: Optional[str] = None,
    workflow_id: Optional[str] = None,
    workflow_run_id: Optional[str] = None,
) -> "Logger":
    """Initialize context variables and create a bound logger in a single operation.

    This is a convenience function that combines the functionality of seed_ids() and
    bind_logger functions into a single call.

    Args:
        trace_id: The trace ID to set in context and bind to logger
        workflow_id: The workflow ID to set in context and bind to logger
        workflow_run_id: The workflow run ID to set in context and bind to logger

    Returns:
        A Loguru logger instance with appropriate context variables bound
    """
    seed_ids(trace_id or "", workflow_id or "", workflow_run_id or "")
    return bind_logger(trace_id or "", workflow_id or "", workflow_run_id or "")
