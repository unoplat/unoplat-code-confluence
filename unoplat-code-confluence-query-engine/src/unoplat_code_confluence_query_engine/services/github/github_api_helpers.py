"""Shared GitHub API helpers used by both workflow activities and API endpoints."""

from __future__ import annotations

from collections.abc import Mapping
from urllib.parse import urlparse

from unoplat_code_confluence_commons.credential_enums import ProviderKey


def resolve_github_host(
    provider_key: ProviderKey,
    metadata: Mapping[str, object] | None,
) -> str:
    """Resolve the GitHub API host URL for the given provider.

    Args:
        provider_key: Repository provider identifier.
        metadata: Optional credential metadata (needed for enterprise).

    Returns:
        Full GitHub API host URL.

    Raises:
        ValueError: If provider is unsupported or enterprise metadata is invalid.
    """
    if provider_key == ProviderKey.GITHUB_OPEN:
        return "https://api.github.com"

    if provider_key != ProviderKey.GITHUB_ENTERPRISE:
        raise ValueError(
            f"Unsupported repository provider '{provider_key.value}'"
        )

    if metadata is None:
        raise ValueError(
            "Missing metadata for github_enterprise credentials"
        )

    enterprise_url = _get_string_field(metadata, "url")
    if enterprise_url is None:
        raise ValueError(
            "Missing enterprise URL in github_enterprise credentials metadata"
        )

    parsed = urlparse(enterprise_url)
    host = f"{parsed.scheme}://{parsed.netloc}" if parsed.netloc else ""
    if not host:
        raise ValueError(
            "Invalid enterprise URL in github_enterprise credentials metadata"
        )

    if enterprise_url.rstrip("/").endswith("/api/v3"):
        return enterprise_url.rstrip("/")
    return f"{host}/api/v3"


def extract_http_error_status(error: Exception) -> int | None:
    """Extract HTTP status code from a ghapi exception.

    ghapi exceptions store the status code in a ``status`` or ``code`` attribute.

    Args:
        error: Exception raised by a ghapi call.

    Returns:
        Integer status code, or None if not found.
    """
    for attribute in ("status", "code"):
        value = getattr(error, attribute, None)
        if isinstance(value, int):
            return value
    return None


def is_http_not_found(error: Exception) -> bool:
    """Check whether a ghapi exception represents an HTTP 404."""
    return extract_http_error_status(error) == 404


def _get_string_field(payload: Mapping[str, object], key: str) -> str | None:
    """Extract a non-empty string field from a mapping."""
    value = payload.get(key)
    if isinstance(value, str) and value.strip():
        return value
    return None
