"""Custom AsyncOpenAI client wiring for Codex OAuth request rewriting."""

from __future__ import annotations

import httpx
from openai import AsyncOpenAI

from unoplat_code_confluence_query_engine.config.settings import EnvironmentSettings
from unoplat_code_confluence_query_engine.db.postgres.db import get_startup_session
from unoplat_code_confluence_query_engine.services.config.codex_oauth_service import (
    CodexOAuthService,
)


class CodexOAuthTransport(httpx.AsyncBaseTransport):
    """HTTPX transport that injects OAuth headers + rewrites chat/responses paths."""

    def __init__(self, oauth_service: CodexOAuthService) -> None:
        self._oauth_service = oauth_service
        self._inner = httpx.AsyncHTTPTransport()

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        async with get_startup_session() as session:
            auth_context = await self._oauth_service.ensure_valid_access_token(session)

        rewritten_url = request.url
        if (
            "/chat/completions" in request.url.path
            or "/v1/responses" in request.url.path
            or request.url.path.endswith("/responses")
        ):
            rewritten_url = httpx.URL(self._oauth_service.codex_api_endpoint)

        content = await request.aread()
        headers = httpx.Headers(request.headers)
        headers["Authorization"] = f"Bearer {auth_context.access_token}"
        if auth_context.account_id:
            headers["ChatGPT-Account-Id"] = auth_context.account_id
        if "host" in headers:
            del headers["host"]

        rewritten_request = httpx.Request(
            method=request.method,
            url=rewritten_url,
            headers=headers,
            content=content,
            extensions=request.extensions,
        )
        return await self._inner.handle_async_request(rewritten_request)

    async def aclose(self) -> None:
        await self._inner.aclose()


def create_codex_async_openai_client(settings: EnvironmentSettings) -> AsyncOpenAI:
    """Create AsyncOpenAI client with Codex OAuth auth + URL rewrite transport."""
    oauth_service = CodexOAuthService(settings)
    timeout = settings.retry_timeout if settings.retry_enabled else 30.0
    http_client = httpx.AsyncClient(
        transport=CodexOAuthTransport(oauth_service),
        timeout=timeout,
    )
    # api_key is still required by SDK constructor; transport overwrites Authorization.
    return AsyncOpenAI(
        api_key="codex-oauth-placeholder",
        base_url=settings.codex_openai_api_endpoint,
        http_client=http_client,
        max_retries=0,
    )
