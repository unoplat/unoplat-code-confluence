"""Debug-only Temporal timeout helpers.

These helpers allow long-running profiling runs to relax Temporal
start-to-close timeouts without changing normal defaults.

Use only for fresh debug runs. Changing timeout env vars while replaying an
existing workflow can affect deterministic scheduling decisions.
"""

from __future__ import annotations

import os
from datetime import timedelta

_TRUTHY_VALUES = frozenset({"1", "true", "yes", "on"})


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def debug_timeout(default: timedelta, *, env_name: str | None = None) -> timedelta:
    """Return a timeout adjusted by debug env vars.

    Env controls:
    - ``QUERY_ENGINE_TEMPORAL_ACTIVITY_TIMEOUT_MULTIPLIER`` multiplies any
      default timeout. Example: ``10`` turns 30s into 300s.
    - A caller-specific ``env_name`` may override the final value in seconds.
      Example: ``QUERY_ENGINE_TEMPORAL_DB_ACTIVITY_TIMEOUT_SECONDS=600``.
    """
    if env_name:
        override_seconds = _env_int(env_name, 0)
        if override_seconds > 0:
            return timedelta(seconds=override_seconds)

    multiplier = max(1, _env_int("QUERY_ENGINE_TEMPORAL_ACTIVITY_TIMEOUT_MULTIPLIER", 1))
    return default * multiplier


def temporal_debug_mode_enabled() -> bool:
    """Return whether Temporal worker debug mode is enabled via query-engine env."""
    return os.getenv("QUERY_ENGINE_TEMPORAL_DEBUG_MODE", "").strip().lower() in _TRUTHY_VALUES
