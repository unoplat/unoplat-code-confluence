"""Environment-configurable HTTP client with robust retry logic.

Follows PydanticAI's retry guidance using Tenacity-based transports:
https://ai.pydantic.dev/retries
"""

from typing import Optional, Sequence

from httpx import (
    AsyncClient,
    ConnectError,
    HTTPStatusError,
    Response,
    TimeoutException,
)
from loguru import logger
from pydantic_ai.retries import AsyncTenacityTransport, RetryConfig, wait_retry_after
from tenacity import RetryCallState, stop_after_attempt, wait_exponential

from unoplat_code_confluence_query_engine.config.settings import EnvironmentSettings


def validate_response(response: Response, retry_status_codes: Sequence[int]) -> None:
    """
    Generic response validator usable across providers.

    Detects common failure modes that should trigger a retry:
    - HTTP status errors configured for retry (e.g., 429/5xx)
    - Completely empty response content

    Args:
        response: The HTTP response from any AI provider.
        retry_status_codes: HTTP status codes that should trigger retry.

    Raises:
        HTTPStatusError: For HTTP status codes that should trigger retry.
        ValueError: For empty/null responses that should trigger retry.
    """
    # Check HTTP status codes that should trigger retry
    if response.status_code in retry_status_codes:
        logger.warning(
            f"Provider HTTP error {response.status_code}: {response.text[:200]}"
        )
        response.raise_for_status()

    # Check for completely empty response content
    if not response.content or len(response.content.strip()) == 0:
        logger.warning("Received completely empty response from provider")
        raise ValueError("Empty response content from provider")


def create_retry_client(settings: EnvironmentSettings) -> Optional[AsyncClient]:
    """
    Create an AsyncClient with retry configuration based on environment settings.

    This client handles:
    - Rate limiting (429) with Retry-After header respect
    - Server errors (502, 503, 504) with exponential backoff
    - Empty/null model responses with immediate retry
    - Connection errors with network-level retries

    Args:
        settings: Environment settings containing retry configuration

    Returns:
        Configured AsyncClient with retry transport, or None if retry is disabled
    """
    if not settings.retry_enabled:
        logger.debug("HTTP retry is disabled, returning None")
        return None

    # Tenacity-compatible retry predicate, capturing settings in closure
    def should_retry_state(state: RetryCallState) -> bool:
        """Determine if a failure should trigger a retry.

        Follows PydanticAI's guidance:
        - Retry on configured HTTP errors (via HTTPStatusError)
        - Retry on timeouts and connection errors
        - Retry on explicit empty-response ValueError raised by validator
        """
        exc = state.outcome.exception() if state.outcome else None
        if exc is None:
            return False
        if isinstance(exc, HTTPStatusError):
            return exc.response.status_code in settings.retry_status_codes_list
        if isinstance(exc, (TimeoutException, ConnectError)):
            return True
        if isinstance(exc, ValueError):
            return True
        return False

    # Configure retry behavior following PydanticAI best practices
    retry_config: RetryConfig = RetryConfig(
        retry=should_retry_state,
        wait=wait_retry_after(
            fallback_strategy=wait_exponential(
                multiplier=settings.retry_base_wait,
                max=settings.retry_max_wait,
            ),
            # Allow longer waits when server provides Retry-After
            max_wait=float(settings.retry_max_wait * 2),
        ),
        stop=stop_after_attempt(settings.retry_max_attempts),
        reraise=True,
    )

    # Create response validator with configured status codes
    def response_validator(response: Response) -> None:
        validate_response(response, settings.retry_status_codes_list)

    # Create transport with retry logic
    transport = AsyncTenacityTransport(
        config=retry_config, validate_response=response_validator
    )

    # Create client with custom transport
    client = AsyncClient(
        transport=transport,
        timeout=settings.retry_timeout,
    )

    logger.info(
        "Created retry HTTP client: "
        f"max_attempts={settings.retry_max_attempts}, "
        f"timeout={settings.retry_timeout}s, "
        f"max_wait={settings.retry_max_wait}s, "
        f"retry_codes={settings.retry_status_codes}"
    )
    return client
