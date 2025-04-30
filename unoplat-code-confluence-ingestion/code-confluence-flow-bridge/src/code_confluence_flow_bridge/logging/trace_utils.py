# trace_utils.py
from __future__ import annotations

import contextvars
from typing import TYPE_CHECKING, Any, Mapping, Optional
import uuid

from loguru import logger

if TYPE_CHECKING:
    from loguru import Logger

trace_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar("trace_id", default="")

def build_trace_id(repo: str | None, owner: str | None) -> str:
    return f"{repo}__{owner}" if repo and owner else str(uuid.uuid4())

def bind_logger(trace_id: str) -> "Logger":
    """
    Return a Loguru logger with .extra.app_trace_id already set.
    """
    return logger.bind(app_trace_id=trace_id)

# ---------------- Context helpers ---------------- #
def seed_trace_id(trace_id: str) -> None:
    """
    Set the trace_id in the ContextVar for the current task/thread.
    """
    trace_id_var.set(trace_id)


def seed_trace_id_from_headers(headers: Mapping[str, Any]) -> Optional[str]:
    """
    Extract and seed the trace_id from a headers mapping.
    """
    if headers:
        hv = headers.get("trace-id")
        if hv:
            trace = getattr(hv, "text_value", None) or str(hv)
            trace_id_var.set(trace)
            return trace
    return None


# ---------------------------------------------------------------
# Helper: seed ContextVar and return bound logger in one step
def seed_and_bind_logger_from_trace_id(trace_id: str) -> "Logger":
    """
    Seed the ContextVar and return a bound Loguru Logger with .extra.app_trace_id set.
    """
    seed_trace_id(trace_id)
    return bind_logger(trace_id)