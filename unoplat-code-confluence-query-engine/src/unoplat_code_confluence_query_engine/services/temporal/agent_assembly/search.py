from __future__ import annotations

from dataclasses import dataclass

from pydantic_ai import RunContext
from pydantic_ai.builtin_tools import WebFetchTool, WebSearchTool
from pydantic_ai.tools import AgentBuiltinTool

from unoplat_code_confluence_query_engine.models.runtime.agent_dependencies import (
    AgentDependencies,
)

WEB_SEARCH_BUILTIN_PROVIDER_KEYS = frozenset(
    {"anthropic", "codex_openai", "google", "grok", "groq", "openrouter"}
)
WEB_FETCH_BUILTIN_PROVIDER_KEYS = frozenset({"anthropic", "google"})


@dataclass(frozen=True, slots=True)
class SearchRuntimePolicy:
    """Resolved external web-tool policy for a Temporal assembly run."""

    include_exa_toolsets: bool = False
    include_prepared_builtin_web_search: bool = False
    include_prepared_builtin_web_fetch: bool = False


@dataclass(frozen=True, slots=True)
class PreparedWebSearchTool:
    """Prepared builtin helper that resolves to a web-search tool or None."""

    enabled: bool = False

    async def __call__(
        self,
        ctx: RunContext[AgentDependencies],
    ) -> WebSearchTool | None:
        _ = ctx
        if not self.enabled:
            return None
        return WebSearchTool()


@dataclass(frozen=True, slots=True)
class PreparedWebFetchTool:
    """Prepared builtin helper that resolves to a web-fetch tool or None."""

    enabled: bool = False

    async def __call__(
        self,
        ctx: RunContext[AgentDependencies],
    ) -> WebFetchTool | None:
        _ = ctx
        if not self.enabled:
            return None
        return WebFetchTool()


def provider_supports_builtin_web_search(provider_key: str | None) -> bool:
    """Return whether the provider can use PydanticAI's builtin web-search tool."""

    return provider_key in WEB_SEARCH_BUILTIN_PROVIDER_KEYS


def provider_supports_builtin_web_fetch(provider_key: str | None) -> bool:
    """Return whether the provider can use PydanticAI's builtin web-fetch tool."""

    return provider_key in WEB_FETCH_BUILTIN_PROVIDER_KEYS


def resolve_search_runtime_policy(
    provider_key: str | None,
    exa_configured: bool,
) -> SearchRuntimePolicy:
    """Resolve the shared runtime web-tool policy for assembled Temporal agents."""

    return SearchRuntimePolicy(
        include_exa_toolsets=exa_configured,
        include_prepared_builtin_web_search=(
            not exa_configured and provider_supports_builtin_web_search(provider_key)
        ),
        include_prepared_builtin_web_fetch=provider_supports_builtin_web_fetch(
            provider_key
        ),
    )


def should_include_prepared_builtin_web_search(
    *,
    allow_builtin_web_search: bool,
    runtime_policy: SearchRuntimePolicy,
) -> bool:
    """Return whether prepared builtin web search should resolve to a tool."""

    return (
        allow_builtin_web_search
        and runtime_policy.include_prepared_builtin_web_search
    )


def should_include_prepared_builtin_web_fetch(
    *,
    allow_builtin_web_fetch: bool,
    runtime_policy: SearchRuntimePolicy,
) -> bool:
    """Return whether prepared builtin web fetch should resolve to a tool."""

    return allow_builtin_web_fetch and runtime_policy.include_prepared_builtin_web_fetch


def resolve_builtin_search_tools(
    *,
    allow_builtin_web_search: bool,
    runtime_policy: SearchRuntimePolicy,
    allow_builtin_web_fetch: bool = False,
) -> tuple[AgentBuiltinTool[AgentDependencies], ...]:
    """Return shared prepared builtin web tools for the assembled agent."""

    builtin_tools: list[AgentBuiltinTool[AgentDependencies]] = []
    if allow_builtin_web_search:
        builtin_tools.append(
            PreparedWebSearchTool(
                enabled=should_include_prepared_builtin_web_search(
                    allow_builtin_web_search=allow_builtin_web_search,
                    runtime_policy=runtime_policy,
                )
            )
        )
    if allow_builtin_web_fetch:
        builtin_tools.append(
            PreparedWebFetchTool(
                enabled=should_include_prepared_builtin_web_fetch(
                    allow_builtin_web_fetch=allow_builtin_web_fetch,
                    runtime_policy=runtime_policy,
                )
            )
        )
    return tuple(builtin_tools)


def should_include_exa_toolsets(runtime_policy: SearchRuntimePolicy) -> bool:
    """Return whether Exa-backed toolsets should be attached."""

    return runtime_policy.include_exa_toolsets
