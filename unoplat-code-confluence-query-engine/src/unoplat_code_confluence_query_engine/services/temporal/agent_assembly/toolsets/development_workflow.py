from __future__ import annotations

from pydantic_ai import RunContext
from pydantic_ai.toolsets.abstract import AbstractToolset

from unoplat_code_confluence_query_engine.models.runtime.agent_dependencies import (
    AgentDependencies,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.constants import (
    DEVELOPMENT_WORKFLOW_EXA_TOOLSET_ID,
    TS_MONOREPO_TOOLSET_ID,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.toolsets.exa import (
    get_exa_toolset,
)
from unoplat_code_confluence_query_engine.skills.typescript_monorepo_skill import (
    create_typescript_monorepo_toolset,
)


def build_development_workflow_exa_toolset() -> AbstractToolset[AgentDependencies]:
    return get_exa_toolset(DEVELOPMENT_WORKFLOW_EXA_TOOLSET_ID)


def maybe_get_typescript_monorepo_toolset(
    ctx: RunContext[AgentDependencies],
) -> AbstractToolset[AgentDependencies] | None:
    if ctx.deps.codebase_metadata.codebase_package_manager_provenance == "inherited":
        return create_typescript_monorepo_toolset(TS_MONOREPO_TOOLSET_ID)
    return None


async def maybe_get_typescript_monorepo_instructions(
    ctx: RunContext[AgentDependencies],
) -> str | None:
    if ctx.deps.codebase_metadata.codebase_package_manager_provenance != "inherited":
        return None
    toolset = create_typescript_monorepo_toolset(TS_MONOREPO_TOOLSET_ID)
    return await toolset.get_instructions(ctx)
