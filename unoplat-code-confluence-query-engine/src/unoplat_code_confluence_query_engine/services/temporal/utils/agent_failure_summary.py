from __future__ import annotations

from unoplat_code_confluence_commons.workflow_models import workflow_failure_entry

from unoplat_code_confluence_query_engine.utils.agent_error_logger import (
    extract_model_error_from_exception,
)


def summarize_agent_failure(
    exception: BaseException,
    *,
    agent_name: str,
    codebase_name: str | None = None,
) -> dict[str, object]:
    """Log provider details, then return only allowlisted failure metadata."""
    extract_model_error_from_exception(
        exception,
        context={"agent_name": agent_name, "codebase": codebase_name or "unknown"},
    )
    return workflow_failure_entry(exception, agent=agent_name, codebase=codebase_name)
