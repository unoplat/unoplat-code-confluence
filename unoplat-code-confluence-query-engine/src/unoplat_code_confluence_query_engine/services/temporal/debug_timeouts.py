"""Temporal debug mode helpers."""

from __future__ import annotations

import os

_TRUTHY_VALUES = frozenset({"1", "true", "yes", "on"})


def temporal_debug_mode_enabled() -> bool:
    """Return whether Temporal worker debug mode is enabled via query-engine env."""
    return os.getenv("QUERY_ENGINE_TEMPORAL_DEBUG_MODE", "").strip().lower() in _TRUTHY_VALUES
