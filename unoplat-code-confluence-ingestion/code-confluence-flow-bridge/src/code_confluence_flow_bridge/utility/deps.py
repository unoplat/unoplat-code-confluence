# deps.py
from src.code_confluence_flow_bridge.logging.trace_utils import (
    bind_trace_id_logger,
    build_trace_id,
    trace_id_var,
)

from typing import TYPE_CHECKING

from fastapi import HTTPException, Request

if TYPE_CHECKING:
    from loguru import Logger

async def trace_dependency(request: Request) -> "Logger":
    """
    • Runs **before** the endpoint handler<br>
    • Extracts repo/owner from JSON body (or headers, query – adjust as needed)<br>
    • Sets ContextVar so *every* log line has the same trace_id<br>
    • Exposes `request.state.logger` for handler code
    """
    body = await request.json()
    repo = body.get("repository_name")
    owner = body.get("repository_owner_name")
    if not (repo and owner):
        raise HTTPException(400, "repository_name / repository_owner_name are required")

    trace_id = build_trace_id(repo, owner)
    trace_id_var.set(trace_id)                 # <-- key line

    request.state.logger = bind_trace_id_logger(trace_id)
    return request.state.logger                # value is optionally injectable