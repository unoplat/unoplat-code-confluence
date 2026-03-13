from __future__ import annotations

import asyncio

from temporalio.exceptions import CancelledError, FailureError

MAX_EXCEPTION_CAUSE_DEPTH = 8


def is_temporal_cancellation_exception(exception: BaseException) -> bool:
    """Return whether an exception represents Temporal workflow cancellation."""
    current_exception = exception

    for _ in range(MAX_EXCEPTION_CAUSE_DEPTH):
        if isinstance(current_exception, (CancelledError, asyncio.CancelledError)):
            return True

        next_exception: BaseException | None = None
        if isinstance(current_exception, FailureError) and current_exception.cause:
            next_exception = current_exception.cause
        elif isinstance(current_exception.__cause__, BaseException):
            next_exception = current_exception.__cause__

        if next_exception is None or next_exception is current_exception:
            return False

        current_exception = next_exception

    return False
