from __future__ import annotations

from unoplat_code_confluence_query_engine.utils.agent_error_logger import (
    extract_model_error_from_exception,
)


def enrich_agent_error_with_model_details(
    error_dict: dict[str, object],
    exception: BaseException,
    agent_name: str,
    codebase_name: str,
) -> dict[str, object]:
    """Enrich an agent error dict with model error details if present."""
    context: dict[str, object] = {
        "agent_name": agent_name,
        "codebase": codebase_name,
    }
    model_error_details = extract_model_error_from_exception(exception, context=context)
    if model_error_details:
        error_dict["model_error_details"] = model_error_details
    return error_dict
