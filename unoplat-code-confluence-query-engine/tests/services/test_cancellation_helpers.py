from __future__ import annotations

import asyncio

from temporalio.exceptions import CancelledError

from unoplat_code_confluence_query_engine.services.temporal.cancellation_helpers import (
    is_temporal_cancellation_exception,
)


def build_wrapped_temporal_cancelled_exception() -> RuntimeError:
    try:
        raise CancelledError()
    except CancelledError as cancelled_error:
        try:
            raise ValueError("inner") from cancelled_error
        except ValueError as inner_error:
            try:
                raise RuntimeError("outer") from inner_error
            except RuntimeError as wrapped_error:
                return wrapped_error

    raise AssertionError("Expected wrapped cancellation exception")


def test_detects_direct_temporal_cancelled_error() -> None:
    assert is_temporal_cancellation_exception(CancelledError()) is True


def test_detects_direct_asyncio_cancelled_error() -> None:
    assert is_temporal_cancellation_exception(asyncio.CancelledError()) is True


def test_detects_wrapped_temporal_cancelled_error() -> None:
    wrapped_error = build_wrapped_temporal_cancelled_exception()
    assert is_temporal_cancellation_exception(wrapped_error) is True


def test_ignores_non_cancelled_exception() -> None:
    assert is_temporal_cancellation_exception(RuntimeError("boom")) is False
