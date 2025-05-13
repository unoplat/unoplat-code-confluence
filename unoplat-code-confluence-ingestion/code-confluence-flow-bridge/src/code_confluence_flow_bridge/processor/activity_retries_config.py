# src/my_project/config/retries.py

import os
from datetime import timedelta
from typing import Optional

from temporalio.common import RetryPolicy


class ActivityRetriesConfig:
    """Collection of reusable Temporal retry policies."""

    # Default retry values configurable via environment variables
    DEFAULT_MAX_ATTEMPTS = int(os.getenv("ACTIVITY_RETRY_MAX_ATTEMPTS", "4"))
    DEFAULT_INITIAL_INTERVAL_S = float(os.getenv("ACTIVITY_RETRY_INITIAL_INTERVAL_S", "3"))
    DEFAULT_BACKOFF_COEFFICIENT = float(os.getenv("ACTIVITY_RETRY_BACKOFF_COEFFICIENT", "2.0"))
    DEFAULT_MAX_INTERVAL_S = float(os.getenv("ACTIVITY_RETRY_MAX_INTERVAL_S", "60"))

    DEFAULT: RetryPolicy = RetryPolicy(
        maximum_attempts=DEFAULT_MAX_ATTEMPTS,
        initial_interval=timedelta(seconds=DEFAULT_INITIAL_INTERVAL_S),
        backoff_coefficient=DEFAULT_BACKOFF_COEFFICIENT,
        maximum_interval=timedelta(seconds=DEFAULT_MAX_INTERVAL_S),
    )

    @staticmethod
    def for_quick_retries(attempts: Optional[int] = None) -> RetryPolicy:
        """Factory for quick retry pattern configurable via environment."""
        max_attempts = attempts if attempts is not None else int(os.getenv("ACTIVITY_QUICK_RETRIES_ATTEMPTS", "5"))
        initial_interval_ms = float(os.getenv("ACTIVITY_QUICK_INITIAL_INTERVAL_MS", "100"))
        backoff_coefficient = float(os.getenv("ACTIVITY_QUICK_BACKOFF_COEFFICIENT", "1.5"))
        max_interval_s = float(os.getenv("ACTIVITY_QUICK_MAX_INTERVAL_S", "5"))
        return RetryPolicy(
            maximum_attempts=max_attempts,
            initial_interval=timedelta(milliseconds=initial_interval_ms),
            backoff_coefficient=backoff_coefficient,
            maximum_interval=timedelta(seconds=max_interval_s),
        )