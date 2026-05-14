"""Serialization helpers for OpenMetadata custom property extension payloads."""

from __future__ import annotations

import json
from typing import Any

DEFAULT_MAX_EXTENSION_VALUE_BYTES = 32_000
TRUNCATED_MARKER = "...[truncated]"


def json_string(value: Any, *, max_bytes: int = DEFAULT_MAX_EXTENSION_VALUE_BYTES) -> str:
    """Serialize a value as compact JSON string with byte-size safeguards."""

    serialized = json.dumps(value, default=str, ensure_ascii=False, separators=(",", ":"))
    return truncate_utf8(serialized, max_bytes=max_bytes)


def extension_value(value: Any, *, max_bytes: int = DEFAULT_MAX_EXTENSION_VALUE_BYTES) -> str:
    """Return the custom-property value for Code Confluence metadata.

    OpenMetadata 1.12 custom properties are commonly configured as string fields
    for portable demos, so the connector stores rich dict/list payloads as compact
    JSON strings. Keeping this behind a helper lets us switch to native JSON
    custom fields later without touching the mapper.
    """

    return json_string(value, max_bytes=max_bytes)


def compact_model_dump(value: Any) -> Any:
    """Return a JSON-serializable representation of Pydantic models or primitives."""

    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json", exclude_none=True)
    return value


def truncate_utf8(value: str, *, max_bytes: int) -> str:
    """Truncate a string to at most ``max_bytes`` UTF-8 bytes."""

    encoded = value.encode("utf-8")
    if len(encoded) <= max_bytes:
        return value

    marker = TRUNCATED_MARKER.encode("utf-8")
    keep = max(max_bytes - len(marker), 0)
    truncated = encoded[:keep]
    while truncated:
        try:
            return truncated.decode("utf-8") + TRUNCATED_MARKER
        except UnicodeDecodeError:
            truncated = truncated[:-1]
    return TRUNCATED_MARKER[:max_bytes]


def collection_extension(
    *,
    engineering_workflow: Any,
    dependency_guide: Any,
    business_logic: Any,
    inbound_constructs: Any,
    outbound_constructs: Any,
    internal_constructs: Any,
) -> dict[str, str]:
    """Build APICollection extension fields documented for the connector."""

    extension = {
        "codeConfluenceDevelopmentWorkflow": extension_value(compact_model_dump(engineering_workflow)),
        "codeConfluenceDependencies": extension_value(compact_model_dump(dependency_guide)),
        "codeConfluenceBusinessLogic": extension_value(compact_model_dump(business_logic)),
        "codeConfluenceInboundConstructs": extension_value(compact_model_dump(inbound_constructs)),
        "codeConfluenceOutboundConstructs": extension_value(compact_model_dump(outbound_constructs)),
        "codeConfluenceInternalConstructs": extension_value(compact_model_dump(internal_constructs)),
    }
    return extension


def endpoint_extension(construct: Any) -> dict[str, str]:
    """Build APIEndpoint extension fields for a HTTP inbound construct."""

    return {"codeConfluenceHttpEndpoint": extension_value(compact_model_dump(construct))}
