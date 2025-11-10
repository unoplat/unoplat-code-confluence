from __future__ import annotations

"""Helper utilities used by the analytics sub-package."""

# ---------------------------------------------------------------------------
# Global state
# ---------------------------------------------------------------------------

STATS_ENABLED: bool = True  # Toggle for statistics computation


# ---------------------------------------------------------------------------
# Global functions
# ---------------------------------------------------------------------------


def compute_stats(numbers: list[int]) -> dict[str, int | float | None]:
    """Compute basic statistics for *numbers*.

    Returns a mapping containing the element *count*, the *sum* and the
    arithmetic *average*.
    """
    if not numbers:
        return {"count": 0, "sum": 0, "avg": None}

    total: int = sum(numbers)
    return {"count": len(numbers), "sum": total, "avg": total / len(numbers)}


# ---------------------------------------------------------------------------
# Classes
# ---------------------------------------------------------------------------


class StatsManager:
    """Wrap statistics operations for a numeric data-set."""

    def __init__(self, data: list[int]) -> None:
        self._data: list[int] = data

    # Guard clauses used to simplify branch logic
    def _guard_empty(self) -> None:
        if not self._data:
            raise ValueError("Dataset must contain at least one element.")

    def minimum(self) -> int:
        """Return the minimum value in *data*."""
        self._guard_empty()
        return min(self._data)

    def maximum(self) -> int:
        """Return the maximum value in *data*."""
        self._guard_empty()
        return max(self._data)

    def average(self) -> float:
        """Return the arithmetic mean of *data*."""
        self._guard_empty()
        return sum(self._data) / len(self._data)
