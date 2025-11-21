"""Generic, language-agnostic filter utilities used by the concept-centric grammar engine.

Each function receives the canonical `MatchInfo` dictionary emitted by a `ConceptQuery` adapter
and returns a boolean indicating whether the match should be kept. These helpers are composed by
higher-level engines (e.g. PythonGrammarEngine) before persisting detections.

This module replaces ad-hoc inline filtering logic previously scattered across language engines.
It MUST NOT import any language-specific modules (keep this layer pure Python).
"""

from __future__ import annotations

import re
from typing import Any, Dict

__all__ = [
    "object_allowed",
    "annotation_allowed",
]


# ---------------------------------------------------------------------------
# Helper filters
# ---------------------------------------------------------------------------


def object_allowed(
    info: Dict[str, Any], ctx
) -> bool:  # ctx: RuntimeContext but avoid circular import
    """Return True if the object/variable captured in *info* is within *ctx.allowed_objects*.

    A match has a key ``"object"`` when the underlying concept is *AnnotationLike* or another
    concept that decorates / qualifies a target via an object (e.g. ``app.get`` in FastAPI).
    The runtime context exposes a pre-computed ``allowed_objects`` set determined by the
    locator strategy.  If the key is missing we treat the filter as **passed** (non-applicable).
    """

    obj = info.get("object")
    if obj is None:
        return True  # filter not relevant

    allowed = getattr(ctx, "allowed_objects", None)
    if allowed is None:
        return True

    return obj in allowed


def annotation_allowed(info: Dict[str, Any], allowed_regex: str | re.Pattern) -> bool:
    """Validate the annotation/decorator name against *allowed_regex*.

    *info* must contain ``"annotation_name"`` key as populated by an *AnnotationLike* adapter.
    The *allowed_regex* is typically derived from ``construct_query`` tweaks inside the schema
    (e.g. restricting HTTP verb names).
    """

    name = info.get("annotation_name")
    if name is None:
        return True  # nothing to validate

    pattern = (
        re.compile(allowed_regex) if isinstance(allowed_regex, str) else allowed_regex
    )
    return pattern.fullmatch(name) is not None
