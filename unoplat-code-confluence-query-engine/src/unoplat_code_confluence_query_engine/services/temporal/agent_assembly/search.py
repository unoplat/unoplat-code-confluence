from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from pydantic_ai.builtin_tools import AbstractBuiltinTool, WebSearchTool

WEB_SEARCH_BUILTIN_PROVIDER_KEYS = frozenset(
    {"codex_openai", "anthropic", "grok", "groq"}
)


class ExternalSearchMode(str, Enum):
    """Single search boundary selected for a Temporal assembly run."""

    EXA = "exa"
    BUILTIN_WEB_SEARCH = "builtin_web_search"
    DUCKDUCKGO = "duckduckgo"


@dataclass(frozen=True, slots=True)
class SearchRuntimePolicy:
    """Resolved runtime choice between Exa, builtin web search, and DuckDuckGo."""

    mode: ExternalSearchMode
    include_exa_toolsets: bool = False
    include_builtin_web_search: bool = False
    include_duckduckgo_fallback: bool = False


def provider_supports_builtin_web_search(provider_key: str | None) -> bool:
    """Return whether the provider can use PydanticAI's builtin web-search tool."""

    return provider_key in WEB_SEARCH_BUILTIN_PROVIDER_KEYS


def resolve_search_runtime_policy(
    provider_key: str | None,
    exa_configured: bool,
) -> SearchRuntimePolicy:
    """Resolve the single runtime search mode for assembled Temporal agents."""

    if exa_configured:
        return SearchRuntimePolicy(
            mode=ExternalSearchMode.EXA,
            include_exa_toolsets=True,
        )
    if provider_supports_builtin_web_search(provider_key):
        return SearchRuntimePolicy(
            mode=ExternalSearchMode.BUILTIN_WEB_SEARCH,
            include_builtin_web_search=True,
        )
    return SearchRuntimePolicy(
        mode=ExternalSearchMode.DUCKDUCKGO,
        include_duckduckgo_fallback=True,
    )


def resolve_builtin_search_tools(
    *,
    allow_builtin_web_search: bool,
    runtime_policy: SearchRuntimePolicy,
) -> tuple[AbstractBuiltinTool, ...]:
    """Return builtin search tools permitted by both runtime and agent logic."""

    if runtime_policy.include_builtin_web_search and allow_builtin_web_search:
        return (WebSearchTool(),)
    return ()


def should_include_duckduckgo_search(
    runtime_policy: SearchRuntimePolicy,
) -> bool:
    """Return whether the DuckDuckGo fallback tool should be attached."""

    return runtime_policy.include_duckduckgo_fallback


def should_include_exa_toolsets(runtime_policy: SearchRuntimePolicy) -> bool:
    """Return whether Exa-backed toolsets should be attached."""

    return runtime_policy.include_exa_toolsets
