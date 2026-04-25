from __future__ import annotations

from dataclasses import dataclass

from pydantic_ai.capabilities import (
    AbstractCapability,
    CombinedCapability,
    WebFetch,
    WebSearch,
)
from pydantic_ai.toolsets.function import FunctionToolset

from unoplat_code_confluence_query_engine.models.runtime.agent_dependencies import (
    AgentDependencies,
)


@dataclass(frozen=True, slots=True)
class SearchRuntimePolicy:
    """Resolved external web-tool policy for a Temporal assembly run."""

    include_exa_toolsets: bool = False


def resolve_search_runtime_policy(
    provider_key: str | None,
    exa_configured: bool,
) -> SearchRuntimePolicy:
    """Resolve the shared runtime web-tool policy for assembled Temporal agents.

    ``provider_key`` is accepted for API compatibility and logging context only.
    Web capability availability is delegated to provider-adaptive Pydantic AI
    capabilities rather than a query-engine allowlist.
    """

    _ = provider_key
    return SearchRuntimePolicy(include_exa_toolsets=exa_configured)


def _build_local_web_search_toolset(toolset_id: str) -> FunctionToolset[AgentDependencies]:
    """Return a Temporal-safe local fallback toolset for web search."""

    from pydantic_ai.common_tools.duckduckgo import duckduckgo_search_tool

    return FunctionToolset([duckduckgo_search_tool()], id=toolset_id)



def _build_local_web_fetch_toolset(toolset_id: str) -> FunctionToolset[AgentDependencies]:
    """Return a Temporal-safe local fallback toolset for web fetch."""

    from pydantic_ai.common_tools.web_fetch import web_fetch_tool

    return FunctionToolset([web_fetch_tool()], id=toolset_id)



def resolve_search_capability(
    *,
    allow_builtin_web_search: bool,
    allow_builtin_web_fetch: bool = False,
    local_web_search_toolset_id: str | None = None,
    local_web_fetch_toolset_id: str | None = None,
) -> AbstractCapability[AgentDependencies] | None:
    """Return direct WebSearch/WebFetch capabilities for an agent.

    We intentionally attach the Pydantic AI capabilities directly so builtin-tool
    support and local fallback behavior stay owned by the library rather than a
    query-engine-side runtime wrapper.

    Because these agents run through Temporal, any local fallback toolset must be
    a leaf toolset with a stable ID so Temporal can register deterministic
    activity names at worker startup.
    """

    capabilities: list[AbstractCapability[AgentDependencies]] = []
    if allow_builtin_web_search:
        if not local_web_search_toolset_id:
            raise ValueError(
                "local_web_search_toolset_id is required when web search is enabled"
            )
        capabilities.append(
            WebSearch(
                local=_build_local_web_search_toolset(local_web_search_toolset_id)
            )
        )
    if allow_builtin_web_fetch:
        if not local_web_fetch_toolset_id:
            raise ValueError(
                "local_web_fetch_toolset_id is required when web fetch is enabled"
            )
        capabilities.append(
            WebFetch(local=_build_local_web_fetch_toolset(local_web_fetch_toolset_id))
        )
    if not capabilities:
        return None
    if len(capabilities) == 1:
        return capabilities[0]
    return CombinedCapability(capabilities)


def should_include_exa_toolsets(runtime_policy: SearchRuntimePolicy) -> bool:
    """Return whether Exa-backed toolsets should be attached."""

    return runtime_policy.include_exa_toolsets
