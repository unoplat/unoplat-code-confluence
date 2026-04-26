"""Deterministic OpenMetadata-safe names for Code Confluence entities."""

from __future__ import annotations

import hashlib
import re
from collections.abc import Mapping, Sequence
from typing import Any

_MAX_ENTITY_NAME_LENGTH = 120
_SAFE_CHARS = re.compile(r"[^A-Za-z0-9_.-]+")
_REPEATED_SEPARATORS = re.compile(r"[_.-]{2,}")


def safe_entity_name(value: str, *, fallback: str = "code-confluence") -> str:
    """Return a deterministic name accepted by OpenMetadata EntityName fields."""

    cleaned = _SAFE_CHARS.sub("-", value.strip())
    cleaned = _REPEATED_SEPARATORS.sub("-", cleaned).strip("._-")
    if not cleaned:
        cleaned = fallback
    if len(cleaned) <= _MAX_ENTITY_NAME_LENGTH:
        return cleaned

    digest = short_hash(cleaned)
    keep = _MAX_ENTITY_NAME_LENGTH - len(digest) - 1
    return f"{cleaned[:keep].rstrip('._-')}-{digest}"


def repository_service_name(repository: str, explicit_service_name: str | None = None) -> str:
    """Build the APIService name for a repository snapshot."""

    if explicit_service_name:
        return safe_entity_name(explicit_service_name)
    return safe_entity_name(f"code-confluence-{repository.replace('/', '-')}")


def codebase_collection_name(codebase_name: str) -> str:
    """Build the APICollection name for a codebase."""

    return safe_entity_name(codebase_name, fallback="codebase")


def collection_fqn(service_name: str, collection_name: str) -> str:
    """Build the fully qualified collection name used by endpoint requests."""

    return f"{service_name}.{collection_name}"


def endpoint_name(construct_kind: str, library: str | None, match_pattern: Mapping[str, Sequence[str]]) -> str:
    """Build a stable APIEndpoint name from HTTP construct evidence."""

    evidence = _canonical_evidence(match_pattern)
    route_hint = _route_hint(evidence) or construct_kind
    prefix = "-".join(part for part in [construct_kind, library, route_hint] if part)
    return safe_entity_name(f"{prefix}-{short_hash(evidence or prefix)}", fallback="endpoint")


def short_hash(value: str, *, length: int = 10) -> str:
    """Return a short deterministic SHA-256 hash for disambiguating generated names."""

    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:length]


def _canonical_evidence(match_pattern: Mapping[str, Sequence[str]]) -> str:
    parts: list[str] = []
    for path in sorted(match_pattern):
        parts.append(path)
        parts.extend(str(item) for item in match_pattern[path])
    return "|".join(parts)


def _route_hint(evidence: str) -> str | None:
    if not evidence:
        return None

    route_match = re.search(r"[\"'](/[^\"']*)[\"']", evidence)
    if route_match:
        return route_match.group(1).strip("/").replace("/", "-") or "root"

    function_match = re.search(r"def\s+([A-Za-z_][A-Za-z0-9_]*)", evidence)
    if function_match:
        return function_match.group(1)

    return None


def first_evidence_path(match_pattern: Mapping[str, Any]) -> str | None:
    """Return the first deterministic file path from a construct evidence mapping."""

    return next(iter(sorted(match_pattern)), None)
