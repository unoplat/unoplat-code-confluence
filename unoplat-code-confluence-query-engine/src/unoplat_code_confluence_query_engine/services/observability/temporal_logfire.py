"""Logfire integration for the Temporal worker."""

from __future__ import annotations

import logfire
from loguru import logger

from unoplat_code_confluence_query_engine.config.settings import EnvironmentSettings


SERVICE_NAME = "unoplat-code-confluence-query-engine-worker"


def setup_temporal_logfire(settings: EnvironmentSettings) -> logfire.Logfire:
    """Configure and return the Logfire instance used by the Temporal worker."""
    if settings.logfire_sdk_write_key:
        instance = logfire.configure(
            token=settings.logfire_sdk_write_key.get_secret_value(),
            service_name=SERVICE_NAME,
            environment=settings.environment,
            send_to_logfire=True,
        )
        logger.debug("[temporal_logfire] Logfire configured with SDK write key")
    else:
        instance = logfire.configure(
            service_name=SERVICE_NAME,
            environment=settings.environment,
            send_to_logfire="if-token-present",
        )
    logfire.instrument_pydantic_ai()
    return instance


__all__ = ["setup_temporal_logfire", "SERVICE_NAME"]
