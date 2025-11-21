# trace_utils.py
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
activity_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "activity_id", default=None
)
activity_name_var: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "activity_name", default=None
)


def build_trace_id(repo: str | None, owner: str | None) -> str:
    """
    Build a trace ID from repository and owner information.

    Args:
        repo (str | None): The repository name
        owner (str | None): The owner of the repository

    Returns:
        str: A trace ID in the format "repo__owner" if both repo and owner are provided,
             otherwise returns a UUID4 string
    """
    return f"{repo}__{owner}" if repo and owner else str(uuid.uuid4())


def bind_trace_id_logger(trace_id: str):
    return logger.bind(app_trace_id=trace_id)


def bind_logger(
    trace_id: str,
    workflow_id: str,
    workflow_run_id: str,
    activity_id: Optional[str] = None,
    activity_name: Optional[str] = None,
) -> "Logger":
    """
    Create a Loguru logger instance with bound context variables.

    Args:
        trace_id (str): The trace ID to bind to the logger
        workflow_id (str): The workflow ID to bind to the logger
        workflow_run_id (str): The workflow run ID to bind to the logger
        activity_id (str, optional): The activity ID to bind to the logger, if applicable
        activity_name (str, optional): The activity name to bind to the logger, if applicable

    Returns:
        Logger: A Loguru logger instance with appropriate context variables bound
    """
    log_context = {}
    if trace_id:
        log_context["app_trace_id"] = trace_id
    if workflow_id:
        log_context["workflow_id"] = workflow_id
    if workflow_run_id:
        log_context["workflow_run_id"] = workflow_run_id

    if activity_id:
        log_context["activity_id"] = activity_id

    if activity_name:
        log_context["activity_name"] = activity_name

    return logger.bind(**log_context)


# ---------------- Context helpers ---------------- #
def seed_ids(
    trace_id: str,
    workflow_id: str,
    workflow_run_id: str,
    activity_id: Optional[str] = None,
    activity_name: Optional[str] = None,
) -> None:
    """
    Set the trace_id, workflow_id, workflow_run_id, and optionally activity_id in their respective ContextVars.

    This function sets up context variables for the current task/thread, making these IDs
    available throughout the execution context.

    Args:
        trace_id (str): The trace ID to set in the context
        workflow_id (str): The workflow ID to set in the context
        workflow_run_id (str): The workflow run ID to set in the context
        activity_id (str, optional): The activity ID to set in the context, if applicable
        activity_name (str, optional): The activity name to set in the context, if applicable

    Returns:
        None
    """
    if trace_id:
        trace_id_var.set(trace_id)
    if workflow_id:
        workflow_id_var.set(workflow_id)
    if workflow_run_id:
        workflow_run_id_var.set(workflow_run_id)
    if activity_id:
        activity_id_var.set(activity_id)
    if activity_name:
        activity_name_var.set(activity_name)


# ---------------------------------------------------------------
# Helper: seed ContextVar and return bound logger in one step
def seed_and_bind_logger_from_trace_id(
    trace_id: Optional[str] = None,
    workflow_id: Optional[str] = None,
    workflow_run_id: Optional[str] = None,
    activity_id: Optional[str] = None,
    activity_name: Optional[str] = None,
) -> "Logger":
    """
    Initialize context variables and create a bound logger in a single operation.

    This is a convenience function that combines the functionality of seed_ids() and
    bind_logger functions into a single call. It supports both workflow and activity contexts.

    Args:
        trace_id (str): The trace ID to set in context and bind to logger
        workflow_id (str): The workflow ID to set in context and bind to logger
        workflow_run_id (str): The workflow run ID to set in context and bind to logger
        activity_id (str, optional): The activity ID to set in context and bind to logger, if applicable
        activity_name (str, optional): The activity name to set in context and bind to logger, if applicable

    Returns:
        Logger: A Loguru logger instance with appropriate context variables bound
    """
    seed_ids(trace_id, workflow_id, workflow_run_id, activity_id, activity_name)  # type: ignore
    return bind_logger(
        trace_id, workflow_id, workflow_run_id, activity_id, activity_name
    )  # type: ignore
