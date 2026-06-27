from __future__ import annotations

from typing import Any, Protocol

from pydantic import BaseModel, ConfigDict


class HttpResponse(BaseModel):
    """Library-neutral HTTP response data used by backend clients."""

    model_config = ConfigDict(frozen=True)

    status_code: int
    text: str
    body: Any | None = None


class HttpClient(Protocol):
    """Shared HTTP abstraction used by backend-specific clients.

    Backend clients pass exactly one configured base URL. Implementations own
    transport-level exception handling, optional loopback alias probing,
    response-status handling, and backend error-detail extraction.
    """

    def get(
        self,
        *,
        base_url: str,
        path: str,
        timeout: float,
        action: str,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        follow_redirects: bool = False,
        allow_statuses: set[int] | None = None,
    ) -> HttpResponse: ...

    def post(
        self,
        *,
        base_url: str,
        path: str,
        json: dict[str, Any],
        timeout: float,
        action: str,
        detail_statuses: set[int] | None = None,
    ) -> HttpResponse: ...

    def extract_error_detail(self, response: HttpResponse) -> str | None: ...
