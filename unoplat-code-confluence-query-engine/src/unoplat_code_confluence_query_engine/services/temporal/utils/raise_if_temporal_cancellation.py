from __future__ import annotations

from loguru import logger

from unoplat_code_confluence_query_engine.services.temporal.cancellation_helpers import (
    is_temporal_cancellation_exception,
)


def raise_if_temporal_cancellation(exception: BaseException) -> None:
    """Re-raise cancellation-shaped exceptions so workflow cancel is preserved."""
    if is_temporal_cancellation_exception(exception):
        logger.info("[workflow] Cancellation detected, re-raising")
        raise exception
