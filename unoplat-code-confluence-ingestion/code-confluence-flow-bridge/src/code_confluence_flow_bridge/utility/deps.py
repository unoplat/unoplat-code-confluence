from fastapi import HTTPException, Request

from code_confluence_flow_bridge.logging.logger_protocol import StructuredLogger
from code_confluence_flow_bridge.logging.trace_utils import (
    bind_trace_id_logger,
    build_trace_id,
    trace_id_var,
)
from code_confluence_flow_bridge.models.github.repository_git_url import (
    parse_repository_git_url,
)


async def trace_dependency(request: Request) -> StructuredLogger:
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
        repository_git_url = body.get("repository_git_url")
        if not isinstance(repository_git_url, str):
            raise HTTPException(
                400, "repository_git_url is required to derive repository identity"
            )
        parsed = parse_repository_git_url(repository_git_url)
        repo = repo or parsed.repository_name
        owner = owner or parsed.repository_owner_name

    trace_id = build_trace_id(repo, owner)
    trace_id_var.set(trace_id)  # <-- key line

    request.state.logger = bind_trace_id_logger(trace_id)
    return request.state.logger  # value is optionally injectable
