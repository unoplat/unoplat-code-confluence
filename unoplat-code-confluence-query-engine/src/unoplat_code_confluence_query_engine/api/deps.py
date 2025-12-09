"""FastAPI dependencies for trace context."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import Query, Request

from unoplat_code_confluence_query_engine.utils.trace_utils import (
    bind_trace_id_logger,
    build_trace_id,
    trace_id_var,
)

if TYPE_CHECKING:
    from loguru import Logger


async def trace_dependency(
    request: Request,
    owner_name: str = Query(..., description="Repository owner name"),
    repo_name: str = Query(..., description="Repository name"),
) -> "Logger":
    """Build trace_id from query params and set in context.

    This dependency:
    - Runs before the endpoint handler
    - Extracts repo/owner from query parameters
    - Sets ContextVar so every log line has the same trace_id
    - Exposes request.state.logger and request.state.trace_id for handler code

    Args:
        request: FastAPI request object
        owner_name: Repository owner name from query params
        repo_name: Repository name from query params

    Returns:
        A bound logger with trace_id context
    """
    trace_id = build_trace_id(repo_name, owner_name)
    trace_id_var.set(trace_id)

    bound_logger = bind_trace_id_logger(trace_id)
    request.state.logger = bound_logger
    request.state.trace_id = trace_id

    return bound_logger
