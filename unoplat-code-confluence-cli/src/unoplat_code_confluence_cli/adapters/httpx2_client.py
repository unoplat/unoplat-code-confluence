from __future__ import annotations

import json as json_lib
from typing import Any
from urllib.parse import SplitResult, urlsplit, urlunsplit

import httpx2

from unoplat_code_confluence_cli.errors import NetworkError
from unoplat_code_confluence_cli.ports.http_client import HttpResponse


class Httpx2HttpClient:
    """HTTP client adapter backed by httpx2.

    This adapter centralizes httpx2 calls, transport exception handling, loopback
    alias probing, and backend error-detail extraction so concrete backend
    clients only specify their base URL, endpoint path, and payload.
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
    ) -> HttpResponse:
        response: httpx2.Response | None = None
        last_error: httpx2.HTTPError | None = None
        for candidate_base_url in self._probe_base_urls(base_url):
            try:
                response = httpx2.get(
                    f"{candidate_base_url}{path}",
                    params=params,
                    headers=headers,
                    follow_redirects=follow_redirects,
                    timeout=timeout,
                )
                break
            except httpx2.HTTPError as exc:
                last_error = exc
                continue

        if response is None:
            raise NetworkError(f"Unable to reach service to {action}: {last_error}")

        response_data = self._to_response_data(response)
        if allow_statuses is not None and response.status_code in allow_statuses:
            return response_data

        self._raise_for_status(response, response_data=response_data, action=action)
        return response_data

    def post(
        self,
        *,
        base_url: str,
        path: str,
        json: dict[str, Any],
        timeout: float,
        action: str,
        detail_statuses: set[int] | None = None,
    ) -> HttpResponse:
        response: httpx2.Response | None = None
        last_error: httpx2.HTTPError | None = None
        for candidate_base_url in self._probe_base_urls(base_url):
            try:
                response = httpx2.post(
                    f"{candidate_base_url}{path}",
                    json=json,
                    timeout=timeout,
                )
                break
            except httpx2.HTTPError as exc:
                last_error = exc
                continue

        if response is None:
            raise NetworkError(f"Unable to reach service to {action}: {last_error}")

        response_data = self._to_response_data(response)
        if detail_statuses is not None and response.status_code in detail_statuses:
            detail = self.extract_error_detail(response_data)
            raise NetworkError(detail or f"Unable to {action}.")

        self._raise_for_status(response, response_data=response_data, action=action)
        return response_data

    def extract_error_detail(self, response: HttpResponse) -> str | None:
        payload = response.body
        if not isinstance(payload, dict):
            return None

        detail = payload.get("detail")
        if isinstance(detail, str):
            return detail
        if isinstance(detail, list):
            return "; ".join(str(item) for item in detail)
        if isinstance(detail, dict):
            return str(detail)
        return None

    def _to_response_data(self, response: httpx2.Response) -> HttpResponse:
        return HttpResponse(
            status_code=response.status_code,
            text=response.text,
            body=self._parse_json_body(response.text),
        )

    def _parse_json_body(self, text: str) -> Any | None:
        if not text:
            return None
        try:
            return json_lib.loads(text)
        except ValueError:
            return None

    def _raise_for_status(
        self,
        response: httpx2.Response,
        *,
        response_data: HttpResponse,
        action: str,
    ) -> None:
        try:
            response.raise_for_status()
        except httpx2.HTTPError as exc:
            detail = self.extract_error_detail(response_data)
            raise NetworkError(detail or f"Unable to {action}: {exc}") from exc

    def _probe_base_urls(self, base_url: str) -> tuple[str, ...]:
        parsed = urlsplit(base_url)
        hostname = parsed.hostname
        if hostname not in {"localhost", "127.0.0.1", "::1"}:
            return (base_url,)

        hosts = ("localhost", "127.0.0.1")
        urls: list[str] = []
        if base_url not in urls:
            urls.append(base_url)
        for host in hosts:
            candidate = self._replace_url_host(parsed, host)
            if candidate not in urls:
                urls.append(candidate)
        return tuple(urls)

    def _replace_url_host(self, parsed_url: SplitResult, host: str) -> str:
        port = f":{parsed_url.port}" if parsed_url.port is not None else ""
        netloc = f"{host}{port}"
        return urlunsplit(
            (
                parsed_url.scheme,
                netloc,
                parsed_url.path.rstrip("/"),
                parsed_url.query,
                parsed_url.fragment,
            )
        )
