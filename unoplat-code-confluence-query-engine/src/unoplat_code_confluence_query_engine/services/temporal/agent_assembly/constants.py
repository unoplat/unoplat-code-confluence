from __future__ import annotations

DEPENDENCY_OVERVIEW_ARTIFACT = "dependencies_overview.md"
BUSINESS_DOMAIN_REFERENCES_ARTIFACT = "business_domain_references.md"
APP_INTERFACES_ARTIFACT = "app_interfaces.md"

ARCHITECTURE_SOURCE_ARTIFACT = "architecture.d2"
ARCHITECTURE_RENDER_ARTIFACT = "architecture.svg"

# The Architecture agent authors only the D2 source. The rendered SVG is also
# managed by the workflow.
ARCHITECTURE_AUTHORED_ARTIFACTS: tuple[str, ...] = (ARCHITECTURE_SOURCE_ARTIFACT,)
ARCHITECTURE_MANAGED_ARTIFACTS: tuple[str, ...] = (
    ARCHITECTURE_SOURCE_ARTIFACT,
    ARCHITECTURE_RENDER_ARTIFACT,
)

ARCHITECTURE_CONSOLE_TOOLSET_ID = "console__architecture"
ARCHITECTURE_SKILL_TOOLSET_ID = "skills__architecture"

BUSINESS_DOMAIN_CONSOLE_TOOLSET_ID = "console__business_domain_guide"
DEPENDENCY_GUIDE_CONSOLE_TOOLSET_ID = "console__dependency_guide"
DEVELOPMENT_WORKFLOW_CONSOLE_TOOLSET_ID = "console__development_workflow_guide"
DEVELOPMENT_WORKFLOW_LOCAL_WEB_SEARCH_TOOLSET_ID = (
    "web_search__development_workflow_guide"
)
DEVELOPMENT_WORKFLOW_LOCAL_WEB_FETCH_TOOLSET_ID = (
    "web_fetch__development_workflow_guide"
)
DEVELOPMENT_WORKFLOW_EXA_TOOLSET_ID = "exa__development_workflow_guide"
DEPENDENCY_GUIDE_LOCAL_WEB_SEARCH_TOOLSET_ID = "web_search__dependency_guide"
DEPENDENCY_GUIDE_LOCAL_WEB_FETCH_TOOLSET_ID = "web_fetch__dependency_guide"
DEPENDENCY_GUIDE_EXA_TOOLSET_ID = "exa__dependency_guide"
CALL_EXPRESSION_DISCOVERER_CONSOLE_TOOLSET_ID = "console__call_expression_discoverer"
TS_MONOREPO_DYNAMIC_TOOLSET_ID = "ts_monorepo_dynamic__development_workflow_guide"
TS_MONOREPO_TOOLSET_ID = "ts_monorepo__development_workflow_guide"
