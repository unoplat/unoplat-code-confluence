from __future__ import annotations

"""Report generation logic for analytics.

This module contains multiple classes, global functions, and global variables to
exercise the GenericCodebaseParser structural-signature extraction logic in the
test suite.
"""

# ---------------------------------------------------------------------------
# Global variables / constants
# ---------------------------------------------------------------------------

GLOBAL_CONSTANT: int = 42  # Arbitrary constant used for demonstration purposes


# ---------------------------------------------------------------------------
# Global functions
# ---------------------------------------------------------------------------

def generate_summary(data: dict[str, int]) -> dict[str, int | float]:
    """Generate a simple numeric summary from *data*.

    Args:
        data: A mapping of keys to numeric values.

    Returns:
        A dictionary containing the *count* of elements and the *total* sum as
        well as the *average* value.
    """
    if not data:
        return {"count": 0, "total": 0, "average": 0.0}

    total: int = sum(data.values())
    return {"count": len(data), "total": total, "average": total / len(data)}


# ---------------------------------------------------------------------------
# Classes
# ---------------------------------------------------------------------------

class ReportGenerator:
    """Generate reports based on provided *data*."""

    def __init__(self, data: dict[str, int]) -> None:
        self._data: dict[str, int] = data

    def generate(self) -> dict[str, int | float]:
        """Return a computed summary report."""
        return generate_summary(self._data)


class SummaryReport:
    """Encapsulates a summary report and exposes a *to_json* serializer."""

    def __init__(self, summary: dict[str, int | float]) -> None:
        self._summary: dict[str, int | float] = summary

    def to_json(self) -> str:  # noqa: D401 – simple serializer
        """Return the summary report as a JSON string."""
        import json

        return json.dumps(self._summary, separators=(",", ":")) 