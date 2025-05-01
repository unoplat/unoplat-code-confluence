# src/my_project/config/retries.py

from datetime import timedelta

from temporalio.common import RetryPolicy


class ActivityRetriesConfig:
    """Collection of reusable Temporal retry policies."""

    DEFAULT: RetryPolicy = RetryPolicy(
        maximum_attempts=3,
        initial_interval=timedelta(seconds=1),
        backoff_coefficient=2.0,
        maximum_interval=timedelta(seconds=10),
    )

    @staticmethod
    def for_quick_retries(attempts: int = 5) -> RetryPolicy:
        """Example of a factory for a different retry pattern."""
        return RetryPolicy(
            maximum_attempts=attempts,
            initial_interval=timedelta(milliseconds=100),
            backoff_coefficient=1.5,
            maximum_interval=timedelta(seconds=5),
        )