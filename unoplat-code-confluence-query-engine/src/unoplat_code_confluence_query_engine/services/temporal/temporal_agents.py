<<<<<<< HEAD
"""Temporal durable agent registry and workflow-facing helpers."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from loguru import logger
from pydantic import BaseModel, ConfigDict
=======
"""Temporal durable agents with dynamic model configuration.

This module defines all agents wrapped with TemporalAgent for durable execution.
Uses ModelFactory to build models dynamically from database configuration.
"""

from datetime import timedelta
from enum import Enum
from typing import Literal, TypeAlias, TypedDict, cast

from loguru import logger
from pydantic_ai import Agent, ModelRetry, RunContext, Tool
from pydantic_ai.builtin_tools import AbstractBuiltinTool, WebSearchTool
from pydantic_ai.common_tools.duckduckgo import (
    duckduckgo_search_tool,  # pyright: ignore[reportUnknownVariableType]
)
>>>>>>> origin/main
from pydantic_ai.durable_exec.temporal import TemporalAgent
from pydantic_ai.models import Model
from pydantic_ai.settings import ModelSettings
from pydantic_ai.usage import UsageLimits
<<<<<<< HEAD

=======
from pydantic_ai_skills import SkillsToolset
from temporalio.workflow import ActivityConfig

from unoplat_code_confluence_query_engine.agents.code_confluence_agents import (
    SEARCH_MODE_BUILTIN_WEB_SEARCH,
    SEARCH_MODE_DUCKDUCKGO,
    SEARCH_MODE_EXA,
    get_engineering_citation_instructions,
    get_official_docs_search_instruction,
    get_official_docs_workflow_steps,
    per_language_development_workflow_prompt,
)
>>>>>>> origin/main
from unoplat_code_confluence_query_engine.config.settings import EnvironmentSettings
from unoplat_code_confluence_query_engine.models.output.agent_md_output import (
    DependencyGuideEntry,
)
from unoplat_code_confluence_query_engine.models.output.agents_md_updater_output import (
    AgentsMdUpdaterOutput,
<<<<<<< HEAD
=======
    SectionId,
>>>>>>> origin/main
)
from unoplat_code_confluence_query_engine.models.output.engineering_workflow_output import (
    EngineeringWorkflow,
)
from unoplat_code_confluence_query_engine.models.repository.framework_feature_validation_models import (
    CallExpressionValidationAgentOutput,
)
from unoplat_code_confluence_query_engine.models.runtime.agent_dependencies import (
    AgentDependencies,
)
<<<<<<< HEAD
from unoplat_code_confluence_query_engine.services.temporal.activity_retry_config import (
    TemporalAgentRetryConfig,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly import (
    DEFAULT_ENABLED_AGENT_TYPES,
    AgentType,
    assemble_enabled_temporal_agents,
    build_enabled_agent_builders,
    create_assembly_context,
    provider_supports_builtin_web_search,
)


class TemporalAgentRegistry(BaseModel):
    """Precise registry model for enabled Temporal agents."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    development_workflow_guide: (
        TemporalAgent[AgentDependencies, EngineeringWorkflow] | None
    ) = None
    dependency_guide: TemporalAgent[AgentDependencies, DependencyGuideEntry] | None = (
        None
    )
    business_domain_guide: TemporalAgent[AgentDependencies, str] | None = None
    agents_md_updater: TemporalAgent[AgentDependencies, AgentsMdUpdaterOutput] | None = (
        None
    )
    call_expression_validator: (
        TemporalAgent[AgentDependencies, CallExpressionValidationAgentOutput] | None
    ) = None

    def iter_agents(self) -> Iterator[TemporalAgent[AgentDependencies, Any]]:
        """Yield all enabled temporal agents."""
        for field_name in type(self).model_fields:
            agent = getattr(self, field_name)
            if agent is not None:
                yield agent

    def iter_agent_names(self) -> Iterator[str]:
        """Yield field names for all enabled temporal agents."""
        for field_name in type(self).model_fields:
            if getattr(self, field_name) is not None:
                yield field_name

    def enabled_agent_names(self) -> list[str]:
        """Return enabled temporal agent names in declaration order."""
        return list(self.iter_agent_names())

    def enabled_agent_count(self) -> int:
        """Return the number of enabled temporal agents."""
        return len(self.enabled_agent_names())


ENABLED_AGENTS: frozenset[AgentType] = DEFAULT_ENABLED_AGENT_TYPES
=======
from unoplat_code_confluence_query_engine.services.agents_md.managed_block import (
    MANAGED_BLOCK_BEGIN,
    MANAGED_BLOCK_END,
)
from unoplat_code_confluence_query_engine.services.repository.engineering_workflow_service import (
    CONFIDENCE_THRESHOLD,
    is_valid_working_directory,
)
from unoplat_code_confluence_query_engine.services.temporal.activity_retry_config import (
    TemporalAgentRetryConfig,
)
from unoplat_code_confluence_query_engine.services.temporal.event_stream_handler import (
    event_stream_handler,
)
from unoplat_code_confluence_query_engine.services.temporal.service_registry import (
    get_mcp_server_manager,
)
from unoplat_code_confluence_query_engine.skills.typescript_monorepo_skill import (
    create_typescript_monorepo_toolset,
)
from unoplat_code_confluence_query_engine.tools.agents_md_updater_tools import (
    updater_apply_patch,
    updater_edit_file,
    updater_read_file,
)
from unoplat_code_confluence_query_engine.tools.framework_feature_validation_tools import (
    set_framework_feature_validation_status,
    upsert_framework_feature_validation_evidence,
)
from unoplat_code_confluence_query_engine.tools.get_content_file import (
    read_file_content,
)
from unoplat_code_confluence_query_engine.tools.get_data_model_files import (
    get_data_model_files,
)
from unoplat_code_confluence_query_engine.tools.get_directory_tree import (
    get_directory_tree,
)
from unoplat_code_confluence_query_engine.tools.search_across_codebase import (
    search_across_codebase,
)

EXA_MCP_SERVER_NAME = "exa"
WEB_SEARCH_BUILTIN_PROVIDER_KEYS = frozenset(
    {"codex_openai", "anthropic", "grok", "groq"}
)

CALL_EXPRESSION_VALIDATOR_CANDIDATE_FIELDS: tuple[str, ...] = (
    "identity",
    "concept",
    "match_confidence",
    "validation_status",
    "match_text",
    "evidence_json",
    "base_confidence",
    "notes",
    "construct_query",
    "absolute_paths",
)
CALL_EXPRESSION_VALIDATOR_IDENTITY_FIELDS: tuple[str, ...] = (
    "file_path",
    "feature_language",
    "feature_library",
    "feature_key",
    "start_line",
    "end_line",
)
CALL_EXPRESSION_VALIDATOR_EVIDENCE_FIELDS: tuple[str, ...] = (
    "concept",
    "source",
    "match_confidence",
    "call_match_kind",
    "matched_absolute_path",
    "matched_alias",
    "call_match_policy_version",
    "callee",
    "args_text",
    "validator",
)

ToolActivityOverride: TypeAlias = ActivityConfig | Literal[False]
ToolActivityConfigMap: TypeAlias = dict[str, ToolActivityOverride]
ToolsetActivityConfigMap: TypeAlias = dict[str, ActivityConfig]
ToolsetToolActivityConfigMap: TypeAlias = dict[str, ToolActivityConfigMap]


class TemporalAgentRegistry(TypedDict, total=False):
    """Precise registry type for enabled Temporal agents."""

    development_workflow_guide: TemporalAgent[AgentDependencies, EngineeringWorkflow]
    dependency_guide: TemporalAgent[AgentDependencies, DependencyGuideEntry]
    business_domain_guide: TemporalAgent[AgentDependencies, str]
    agents_md_updater: TemporalAgent[AgentDependencies, AgentsMdUpdaterOutput]
    call_expression_validator: TemporalAgent[
        AgentDependencies, CallExpressionValidationAgentOutput
    ]


def _get_exa_mcp_server(toolset_id: str):
    mcp_server = get_mcp_server_manager().get_server_by_name(
        EXA_MCP_SERVER_NAME, id_override=toolset_id
    )
    if not mcp_server:
        raise RuntimeError(
            f"Exa MCP server '{EXA_MCP_SERVER_NAME}' not configured in MCP servers config"
        )
    return mcp_server


class AgentType(Enum):
    """Enum for available agent types."""

    DEVELOPMENT_WORKFLOW = "development_workflow_guide"
    DEPENDENCY = "dependency_guide"
    BUSINESS_DOMAIN = "business_domain_guide"
    AGENTS_MD_UPDATER = "agents_md_updater"
    CALL_EXPRESSION_VALIDATOR = "call_expression_validator"


def _get_web_search_builtin_tools(
    provider_key: str | None,
) -> list[AbstractBuiltinTool]:
    """Build provider-compatible built-in web-search tools."""
    if provider_key in WEB_SEARCH_BUILTIN_PROVIDER_KEYS:
        return [WebSearchTool()]
    return []


def _supports_builtin_web_search_with_function_tools(provider_key: str | None) -> bool:
    """Return whether provider can mix built-in web search with function tools."""
    return provider_key in WEB_SEARCH_BUILTIN_PROVIDER_KEYS


def _get_duckduckgo_search_tool() -> Tool[AgentDependencies]:
    """Build DuckDuckGo common-tool fallback for official-doc lookups."""
    return cast(Tool[AgentDependencies], duckduckgo_search_tool(max_results=5))


def _resolve_search_mode(provider_key: str | None, exa_configured: bool) -> str:
    """Resolve external search mode for agent prompts/tooling."""
    if exa_configured:
        return SEARCH_MODE_EXA
    if provider_key in WEB_SEARCH_BUILTIN_PROVIDER_KEYS:
        return SEARCH_MODE_BUILTIN_WEB_SEARCH
    return SEARCH_MODE_DUCKDUCKGO


SECTION_UPDATER_AGENT_NAMES: dict[SectionId, str] = {
    SectionId.ENGINEERING_WORKFLOW: "development_workflow_agents_md_updater",
    SectionId.DEPENDENCY_GUIDE: "dependency_guide_agents_md_updater",
    SectionId.BUSINESS_DOMAIN: "business_domain_agents_md_updater",
    SectionId.APP_INTERFACES: "app_interfaces_agents_md_updater",
}

SECTION_HEADINGS: dict[SectionId, str] = {
    SectionId.ENGINEERING_WORKFLOW: "## Engineering Workflow",
    SectionId.DEPENDENCY_GUIDE: "## Dependency Guide",
    SectionId.BUSINESS_DOMAIN: "## Business Logic Domain",
    SectionId.APP_INTERFACES: "## App Interfaces",
}

DEPENDENCY_OVERVIEW_ARTIFACT = "dependencies_overview.md"
BUSINESS_LOGIC_REFERENCES_ARTIFACT = "business_logic_references.md"
APP_INTERFACES_ARTIFACT = "app_interfaces.md"

SECTION_ARTIFACTS: dict[SectionId, list[str]] = {
    SectionId.ENGINEERING_WORKFLOW: ["AGENTS.md"],
    SectionId.DEPENDENCY_GUIDE: ["AGENTS.md", DEPENDENCY_OVERVIEW_ARTIFACT],
    SectionId.BUSINESS_DOMAIN: ["AGENTS.md", BUSINESS_LOGIC_REFERENCES_ARTIFACT],
    SectionId.APP_INTERFACES: ["AGENTS.md", APP_INTERFACES_ARTIFACT],
}

SECTION_COMPANION_ARTIFACTS: dict[SectionId, str] = {
    SectionId.DEPENDENCY_GUIDE: DEPENDENCY_OVERVIEW_ARTIFACT,
    SectionId.BUSINESS_DOMAIN: BUSINESS_LOGIC_REFERENCES_ARTIFACT,
    SectionId.APP_INTERFACES: APP_INTERFACES_ARTIFACT,
}


def _build_section_extra_requirements(section_id: SectionId) -> str:
    """Build section-specific updater requirements."""
    requirements: list[str] = []
    companion_artifact = SECTION_COMPANION_ARTIFACTS.get(section_id)

    if companion_artifact is not None:
        requirements.extend(
            [
                "- In `AGENTS.md`, write ONLY a concise description of "
                f"`{companion_artifact}` and a markdown link to it.",
                "- Keep the `AGENTS.md` section body to 1-2 short sentences total.",
                "- Do NOT include tables, bullet inventories, endpoint lists, file maps, "
                "dependency catalogs, or detailed prose in `AGENTS.md`.",
                f"- Write all detailed section content in `{companion_artifact}`.",
                f"- Treat `{companion_artifact}` as the source-of-truth artifact for this section.",
            ]
        )

    if section_id == SectionId.DEPENDENCY_GUIDE:
        requirements.append(
            f"- Put full dependency purpose/usage entries only in `{DEPENDENCY_OVERVIEW_ARTIFACT}`."
        )

    return "\n".join(requirements)


def build_section_updater_prompt(
    section_id: SectionId,
    codebase_path: str,
    programming_language_metadata: dict[str, object],
    section_data: object,
) -> str:
    """Build the prompt for a section-scoped AGENTS.md updater run."""
    heading = SECTION_HEADINGS[section_id]
    artifacts = SECTION_ARTIFACTS[section_id]
    artifacts_instruction = "\n".join(f"- {a}" for a in artifacts)
    section_specific_requirements = _build_section_extra_requirements(section_id)
    section_specific_instruction = ""
    if section_specific_requirements:
        section_specific_instruction = (
            f"Section-specific requirements:\n{section_specific_requirements}\n\n"
        )

    return (
        f"Update the '{heading}' section in codebase-local AGENTS.md.\n"
        f"Modify only the content under '{heading}'.\n"
        "Do not change any other AGENTS.md section.\n\n"
        f"Expected managed files:\n{artifacts_instruction}\n\n"
        f"{section_specific_instruction}"
        f"Codebase path: {codebase_path}\n"
        f"Programming language metadata: {programming_language_metadata}\n"
        f"Section data:\n{section_data}\n\n"
        "Return summary metadata only (no raw file content)."
    )


def _get_dependency_guide_instructions(search_mode: str) -> str:
    """Build dependency-guide instructions based on available web-search mode."""
    workflow_steps = get_official_docs_workflow_steps(
        search_mode,
        target="the library/tool",
        unresolved_outcome="mark as internal dependency",
    )

    return f"""You are the Dependency Guide.

Goal: Generate a concise documentation entry for a single library/package dependency.

<task>
Given a library name and programming language, produce a DependencyGuideEntry with:
1. name: The exact library name provided (do not modify it)
2. purpose: 1-2 lines describing what this library does (from official docs)
3. usage: Exactly 2 sentences describing core features and capabilities
</task>

<workflow>
{workflow_steps}
</workflow>

<handling_internal_dependencies>
IMPORTANT: If available search/documentation tools return an error, "not found", or empty/minimal info, this is likely an INTERNAL/PRIVATE dependency.

For internal dependencies, return:
- name: The exact library name provided
- purpose: "INTERNAL_DEPENDENCY_SKIP"
- usage: "INTERNAL_DEPENDENCY_SKIP"

This signals the system to skip this dependency in the final output.
</handling_internal_dependencies>

<output_requirements>
For PUBLIC dependencies with documentation:
- The 'name' field MUST match the provided library name exactly
- The 'purpose' field should be 1-2 lines (concise, from official docs)
- The 'usage' field MUST be exactly 2 sentences, each ending with a period

For INTERNAL/PRIVATE dependencies (no docs found):
- Set both 'purpose' and 'usage' to "INTERNAL_DEPENDENCY_SKIP"
</output_requirements>
"""


# Stable, per-agent Exa MCP toolset IDs for Temporal activity naming.
EXA_TOOLSET_IDS = {
    # Reuse the existing workflow Exa toolset ID so current MCP routing/credentials remain valid.
    AgentType.DEVELOPMENT_WORKFLOW: "exa__development_workflow_guide",
    AgentType.DEPENDENCY: "exa__dependency_guide",
    AgentType.CALL_EXPRESSION_VALIDATOR: "exa__call_expression_validator",
}

TS_MONOREPO_DYNAMIC_TOOLSET_ID = "ts_monorepo_dynamic__development_workflow_guide"
TS_MONOREPO_TOOLSET_ID = "ts_monorepo__development_workflow_guide"


# Toggle agents here - comment/uncomment to enable/disable
ENABLED_AGENTS: set[AgentType] = {
    AgentType.DEVELOPMENT_WORKFLOW,
    AgentType.DEPENDENCY,
    AgentType.BUSINESS_DOMAIN,
    AgentType.AGENTS_MD_UPDATER,
    AgentType.CALL_EXPRESSION_VALIDATOR,
}


def validate_engineering_development_workflow_output(
    output: EngineeringWorkflow,
) -> EngineeringWorkflow:
    if not output.commands:
        raise ModelRetry(
            "engineering_workflow.commands is empty. Re-scan command sources "
            "(Taskfile/Makefile/package scripts/tool configs) and return commands."
        )

    for command in output.commands:
        if not command.command.strip():
            raise ModelRetry(
                "Found command with empty command string. Return non-empty runnable commands."
            )
        if command.config_file.startswith("/") or command.config_file.startswith("../"):
            raise ModelRetry(
                f"config_file '{command.config_file}' must be repo-relative without leading '/' or '../'. "
                "Use 'unknown' if no config file applies."
            )
        if command.confidence < 0.0 or command.confidence > 1.0:
            raise ModelRetry(
                f"confidence {command.confidence} for command '{command.command}' must be between 0.0 and 1.0."
            )
        if command.working_directory is not None and not is_valid_working_directory(
            command.working_directory
        ):
            raise ModelRetry(
                "working_directory must be omitted/null for codebase root, '.' for repository root, "
                "or a repo-relative POSIX path without backslashes, absolute prefixes, or traversal."
            )
    if not any(
        command.confidence >= CONFIDENCE_THRESHOLD for command in output.commands
    ):
        raise ModelRetry(
            "All engineering workflow commands are below confidence threshold "
            f"({CONFIDENCE_THRESHOLD}). Re-validate against official citations and return at least one command >= threshold."
        )
    return output


def validate_business_logic_domain_output(output: str) -> str:
    """Validate business logic domain output.

    Ensures the model returns a non-empty plain text description
    of the business domain (2-4 sentences as requested in the prompt).
    """
    if not output or not output.strip():
        raise ModelRetry(
            "Output is empty. Return a plain text description (2-4 sentences) "
            "summarizing the business logic domain based on the data models analyzed."
        )
    # Check if model returned JSON/structured content instead of plain text
    stripped = output.strip()
    if stripped.startswith("{") or stripped.startswith("["):
        raise ModelRetry(
            "Return ONLY plain text (2-4 sentences), NOT JSON or structured data. "
            "Summarize the business logic domain in natural language."
        )
    return output


def validate_agents_md_updater_output(
    output: AgentsMdUpdaterOutput,
) -> AgentsMdUpdaterOutput:
    """Validate updater output contract."""
    if not output.touched_file_paths:
        raise ModelRetry("touched_file_paths cannot be empty")
    if not output.file_changes:
        raise ModelRetry("file_changes cannot be empty")

    if output.status == "no_changes":
        for file_change in output.file_changes:
            if file_change.changed:
                raise ModelRetry(
                    "status no_changes requires file_changes[].changed to be false"
                )
            if file_change.change_type != "unchanged":
                raise ModelRetry(
                    "status no_changes requires file_changes[].change_type to be 'unchanged'"
                )

    if output.status == "updated":
        has_changed_file = any(
            file_change.changed for file_change in output.file_changes
        )
        if not has_changed_file:
            raise ModelRetry(
                "status updated requires at least one file_changes[].changed to be true"
            )

        has_mutation_change_type = any(
            file_change.change_type in {"created", "updated"}
            for file_change in output.file_changes
        )
        if not has_mutation_change_type:
            raise ModelRetry(
                "status updated requires at least one file_changes[].change_type in {'created','updated'}"
            )

    return output


# ──────────────────────────────────────────────
# Agent Definitions
# ──────────────────────────────────────────────


def create_engineering_development_workflow_agent(
    model: Model,
    model_settings: ModelSettings | None = None,
    builtin_tools: list[AbstractBuiltinTool] | None = None,
    include_exa_toolset: bool = True,
    search_mode: str = SEARCH_MODE_EXA,
) -> Agent[AgentDependencies, EngineeringWorkflow]:
    """Create canonical engineering development workflow agent.

    Args:
        model: Configured Model instance from ModelFactory
        model_settings: Optional model settings (temperature, etc.)
        builtin_tools: Optional built-in tools (e.g. WebSearchTool)
        include_exa_toolset: Whether to include Exa MCP toolset
        search_mode: Resolved search mode ('exa', 'builtin_web_search', 'duckduckgo', or 'none')

    Returns:
        Engineering development workflow agent instance
    """
    citation_instructions = get_engineering_citation_instructions(search_mode)
    exa_id = EXA_TOOLSET_IDS[AgentType.DEVELOPMENT_WORKFLOW]
    tools = [
        Tool(get_directory_tree, takes_ctx=True, max_retries=3),
        Tool(read_file_content, takes_ctx=True, max_retries=3),
        Tool(search_across_codebase, takes_ctx=True, max_retries=3),
    ]
    if search_mode == SEARCH_MODE_DUCKDUCKGO:
        tools.append(_get_duckduckgo_search_tool())

    agent = Agent(
        model,
        name="development_workflow_guide",
        instructions=f"<role>Engineering Workflow Synthesizer</role>\n{citation_instructions}",
        deps_type=AgentDependencies,
        toolsets=[_get_exa_mcp_server(exa_id)] if include_exa_toolset else [],
        tools=tools,
        builtin_tools=builtin_tools or [],
        output_type=EngineeringWorkflow,
        output_retries=2,
        model_settings=model_settings,
        event_stream_handler=event_stream_handler,
    )
    agent.output_validator(validate_engineering_development_workflow_output)
    # Attach dynamic per-language instructions (always enabled)
    agent.instructions(per_language_development_workflow_prompt)

    # Conditional TypeScript monorepo skill via @agent.toolset
    ts_monorepo_toolset = create_typescript_monorepo_toolset(TS_MONOREPO_TOOLSET_ID)

    @agent.toolset(  # pyright: ignore[reportUntypedFunctionDecorator]
        id=TS_MONOREPO_DYNAMIC_TOOLSET_ID,
        per_run_step=False,
    )
    def monorepo_skill_toolset(  # pyright: ignore[reportUnusedFunction]
        ctx: RunContext[AgentDependencies],
    ) -> SkillsToolset | None:
        if (
            ctx.deps.codebase_metadata.codebase_package_manager_provenance
            == "inherited"
        ):
            return ts_monorepo_toolset
        return None

    @agent.instructions  # pyright: ignore[reportUntypedFunctionDecorator]
    async def add_skill_instructions(ctx: RunContext[AgentDependencies]) -> str | None:  # pyright: ignore[reportUnusedFunction]
        if (
            ctx.deps.codebase_metadata.codebase_package_manager_provenance
            == "inherited"
        ):
            return await ts_monorepo_toolset.get_instructions(ctx)
        return None

    logger.debug("Dynamic instructions attached to development_workflow_guide")

    return agent


# Marker for internal/private dependencies that should be skipped
INTERNAL_DEPENDENCY_SKIP_MARKER = "INTERNAL_DEPENDENCY_SKIP"


def create_dependency_guide_agent(
    model: Model,
    model_settings: ModelSettings | None = None,
    builtin_tools: list[AbstractBuiltinTool] | None = None,
    include_exa_toolset: bool = True,
    search_mode: str = SEARCH_MODE_EXA,
) -> Agent[AgentDependencies, DependencyGuideEntry]:
    """Create dependency guide agent.

    This agent documents a single library/package dependency using official docs.

    Args:
        model: Configured Model instance from ModelFactory
        model_settings: Optional model settings (temperature, etc.)

    Returns:
        Dependency guide agent instance
    """
    # TODO: Add output validator for DependencyGuideEntry to ensure:
    # - purpose is 1-2 lines (not empty/too short)
    # - usage contains exactly 2 sentences
    # - name matches the input dependency name
    exa_id = EXA_TOOLSET_IDS[AgentType.DEPENDENCY]
    dependency_toolsets = [_get_exa_mcp_server(exa_id)] if include_exa_toolset else []
    dependency_tools: list[Tool[AgentDependencies]] = []
    if search_mode == SEARCH_MODE_DUCKDUCKGO:
        dependency_tools.append(_get_duckduckgo_search_tool())
    agent = Agent(
        model,
        name="dependency_guide",
        instructions=_get_dependency_guide_instructions(search_mode),
        deps_type=AgentDependencies,
        toolsets=dependency_toolsets,
        tools=dependency_tools,
        builtin_tools=builtin_tools or [],
        output_type=DependencyGuideEntry,
        output_retries=2,
        model_settings=model_settings,
        event_stream_handler=event_stream_handler,
    )

    return agent


def create_business_logic_domain_agent(
    model: Model,
    model_settings: ModelSettings | None = None,
    builtin_tools: list[AbstractBuiltinTool] | None = None,
) -> Agent[AgentDependencies, str]:
    """Create business logic domain agent.

    Args:
        model: Configured Model instance from ModelFactory
        model_settings: Optional model settings (temperature, etc.)

    Returns:
        Business logic domain agent instance
    """
    agent = Agent(
        model,
        name="business_domain_guide",
        instructions=r"""You are the Business Domain Guide.

Goal: Analyze data models across this codebase and return a 2-4 sentence description of the dominant business logic domain.

<file_path_requirements>
CRITICAL: When calling read_file_content or any tool that accepts file paths:
- ALWAYS use ABSOLUTE paths starting with / (e.g., /opt/unoplat/repositories/my-repo/src/models.py)
- NEVER use relative paths (e.g., models.py, src/models.py, ./file.py)
- The file_path values returned by get_data_model_files are already absolute - use them exactly as provided
</file_path_requirements>

Strict workflow:
1) Call get_data_model_files to retrieve all data model file paths and their (start_line, end_line) spans
2) Create a coverage checklist from ALL returned (file_path, model_identifier) pairs and process UNTIL NONE REMAIN
3) After inspecting ALL spans, synthesize the overall business domain they represent
4) Return ONLY a plain text description (2-4 sentences) summarizing the domain

<output_format>
IMPORTANT: Your final output must be PLAIN TEXT only (2-4 sentences).
- Do NOT return JSON, markdown, or structured data
- Do NOT wrap your response in quotes or code blocks
- Simply write the domain description as natural language text
</output_format>
""",
        deps_type=AgentDependencies,
        tools=[
            Tool(get_data_model_files, takes_ctx=True, max_retries=3),
            Tool(read_file_content, takes_ctx=True, max_retries=3),
        ],
        builtin_tools=builtin_tools or [],
        output_type=str,
        output_retries=3,
        model_settings=model_settings,
        event_stream_handler=event_stream_handler,
    )
    agent.output_validator(validate_business_logic_domain_output)
    return agent


def create_call_expression_validator_agent(
    model: Model,
    model_settings: ModelSettings | None = None,
    builtin_tools: list[AbstractBuiltinTool] | None = None,
    include_exa_toolset: bool = True,
    search_mode: str = SEARCH_MODE_EXA,
) -> Agent[AgentDependencies, CallExpressionValidationAgentOutput]:
    """Create low-confidence CallExpression validator agent.

    Args:
        model: Configured Model instance from ModelFactory.
        model_settings: Optional model settings (temperature, etc.).
        builtin_tools: Optional built-in provider tools.
        include_exa_toolset: Whether Exa MCP toolset should be enabled.
        search_mode: Resolved external search mode.

    Returns:
        Configured CallExpression validator agent.
    """
    exa_id = EXA_TOOLSET_IDS[AgentType.CALL_EXPRESSION_VALIDATOR]
    docs_instruction = get_official_docs_search_instruction(
        search_mode,
        target="framework API usage for the candidate call",
    )
    docs_workflow = get_official_docs_workflow_steps(
        search_mode,
        target="the claimed framework method/API for the candidate call",
        unresolved_outcome="set decision=needs_review and target_status=needs_review",
    )
    validator_tools = [
        Tool(read_file_content, takes_ctx=True, max_retries=3),
        Tool(search_across_codebase, takes_ctx=True, max_retries=3),
        Tool(
            upsert_framework_feature_validation_evidence,
            takes_ctx=True,
            max_retries=3,
            docstring_format="google",
            require_parameter_descriptions=True,
        ),
        Tool(
            set_framework_feature_validation_status,
            takes_ctx=True,
            max_retries=3,
            docstring_format="google",
            require_parameter_descriptions=True,
        ),
    ]
    if search_mode == SEARCH_MODE_DUCKDUCKGO:
        validator_tools.append(_get_duckduckgo_search_tool())

    agent = Agent(
        model,
        name="call_expression_validator",
        instructions=_get_call_expression_validator_instructions(
            docs_instruction=docs_instruction,
            docs_workflow=docs_workflow,
        ),
        deps_type=AgentDependencies,
        toolsets=[_get_exa_mcp_server(exa_id)] if include_exa_toolset else [],
        tools=validator_tools,
        builtin_tools=builtin_tools or [],
        output_type=CallExpressionValidationAgentOutput,
        output_retries=2,
        model_settings=model_settings,
        event_stream_handler=event_stream_handler,
    )
    return agent


def _format_validator_field_list(fields: tuple[str, ...]) -> str:
    return ", ".join(fields)


def _get_call_expression_validator_instructions(
    *,
    docs_instruction: str,
    docs_workflow: str,
) -> str:
    candidate_fields = _format_validator_field_list(
        CALL_EXPRESSION_VALIDATOR_CANDIDATE_FIELDS
    )
    identity_fields = _format_validator_field_list(
        CALL_EXPRESSION_VALIDATOR_IDENTITY_FIELDS
    )
    evidence_fields = _format_validator_field_list(
        CALL_EXPRESSION_VALIDATOR_EVIDENCE_FIELDS
    )
    return (
        "You validate one low-confidence CallExpression usage candidate at a time.\n"
        "Return a strict structured decision with auditable evidence.\n\n"
        "Candidate payload fields provided to you:\n"
        f"- Top-level fields: {candidate_fields}.\n"
        f"- identity fields: {identity_fields}.\n"
        "- evidence_json contains detector/runtime evidence and may be absent or partial.\n"
        f"- When evidence_json comes from CallExpression detection, it may include: {evidence_fields}.\n"
        "- Treat detector metadata as hints to verify, not as proof by itself.\n\n"
        "Required process:\n"
        f"1. {docs_instruction}\n"
        "2. Read local file context around the candidate span using read_file_content.\n"
        "3. Expand nearby symbol/object evidence using search_across_codebase.\n"
        "4. Compare official docs expectations against candidate metadata, evidence_json, and local code evidence.\n"
        "5. Explicitly identify gaps/mismatches before deciding (for example: import-binding mismatch, alias/path mismatch, API-shape mismatch, insufficient provenance, unsupported argument shape, or docs mismatch).\n"
        "6. Persist evidence/confidence with upsert_framework_feature_validation_evidence.\n"
        "7. Persist status transition with set_framework_feature_validation_status.\n"
        "8. Return output contract only after write operations complete.\n\n"
        "Evidence payload expectations for upsert_framework_feature_validation_evidence:\n"
        "- Include structured findings for documentation review, metadata review, local code review, gap analysis, and final rationale.\n"
        "- Record which metadata fields were present/missing and whether they aligned with official docs.\n"
        "- Record why provenance is sufficient or insufficient for confirm/reject/correct/needs_review.\n\n"
        "External docs verification workflow:\n"
        f"{docs_workflow}\n\n"
        "Tool workflow example (confirm path):\n"
        "- Call upsert_framework_feature_validation_evidence with request {identity, decision='confirm', final_confidence, evidence_json}.\n"
        "- Then call set_framework_feature_validation_status with request {identity, target_status='completed'}.\n"
        "- Return CallExpressionValidationAgentOutput for the same identity.\n\n"
        "Tool workflow example (needs_review path):\n"
        "- Call upsert_framework_feature_validation_evidence with request {identity, decision='needs_review', final_confidence, evidence_json}.\n"
        "- Then call set_framework_feature_validation_status with request {identity, target_status='needs_review'}.\n"
        "- Return CallExpressionValidationAgentOutput for the same identity.\n\n"
        "Decision policy:\n"
        "- confirm/reject/correct => target_status must be completed\n"
        "- needs_review => target_status must be needs_review\n"
        "- correct requires updated_feature_key different from source feature_key"
    )


def create_agents_md_updater_agent(
    model: Model,
    model_settings: ModelSettings | None = None,
) -> Agent[AgentDependencies, AgentsMdUpdaterOutput]:
    """Create AGENTS.md updater agent.

    Optionally create or update companion artifacts.
    """
    agent = Agent(
        model,
        name="agents_md_updater",
        instructions=f"""You are the AGENTS.md section updater.

Goal:
- Create or update a SPECIFIC SECTION of codebase-local AGENTS.md using safe and minimal edits.
- Create/update companion artifact files when instructed (dependencies_overview.md, business_logic_references.md, app_interfaces.md).

Managed block awareness:
- All generated sections live inside a managed block delimited by {MANAGED_BLOCK_BEGIN} and {MANAGED_BLOCK_END}.
- Your assigned section heading already exists inside the managed block. Update the content under it.
- NEVER modify the block markers.
- NEVER modify the <CRITICAL_INSTRUCTION> block — it contains freshness metadata managed separately.
- NEVER add commit SHA, branch name, or generation timestamps to your section content.
- Treat other ## headings inside the managed block as read-only.

Section scoping:
- You will be told which section heading you own (e.g., "## Engineering Workflow").
- Update content under your assigned heading.
- NEVER modify content outside your assigned section boundary.

Companion artifact policy:
- Some sections have a companion artifact file (for example `{DEPENDENCY_OVERVIEW_ARTIFACT}`, `{BUSINESS_LOGIC_REFERENCES_ARTIFACT}`, `{APP_INTERFACES_ARTIFACT}`).
- If your assigned section has a companion artifact, `AGENTS.md` is pointer-only.
- In `AGENTS.md`, write only a concise description of the companion artifact and a markdown link to it.
- Keep the `AGENTS.md` section body to 1-2 short sentences total.
- NEVER copy tables, bullet inventories, endpoint lists, file maps, dependency catalogs, or detailed summaries into `AGENTS.md`.
- Put detailed content in the companion artifact and treat that artifact as the source-of-truth.
- Sections without a companion artifact may store their section content directly in `AGENTS.md`.

Root-scope safety (hard invariant):
- ALL file operations MUST use absolute paths within the current codebase root.
- NEVER read, write, or reference files outside the codebase root directory.
- Relative paths are rejected. Paths escaping the root are rejected.
- This is enforced at the tool level — violations raise out_of_scope errors.

Tooling constraints:
- Use only updater_read_file, updater_edit_file, updater_apply_patch.
- Always pass absolute file paths.
- Operate only within the current codebase root.
- Prefer updater_apply_patch for creates and structured updates.
- Read the target section first, then compute the expected section body from section_data.
- Compare before write: if content is already equivalent, do not call write tools and return status="no_changes".
- Call updater_apply_patch/updater_edit_file only when an actual diff exists.

Output constraints:
- Return summary metadata only.
- Do not include raw file content in the output.
- Include touched_file_paths for all files involved in final update decisions.
- Include file_changes with changed flag, change_type, concise change_summary, and optional content_sha256.
""",
        deps_type=AgentDependencies,
        tools=[
            Tool(updater_read_file, takes_ctx=True, max_retries=2),
            Tool(updater_edit_file, takes_ctx=True, max_retries=2),
            Tool(
                updater_apply_patch,
                takes_ctx=True,
                max_retries=4,
                docstring_format="google",
            ),
        ],
        output_type=AgentsMdUpdaterOutput,
        output_retries=2,
        model_settings=model_settings,
        event_stream_handler=event_stream_handler,
    )
    agent.output_validator(validate_agents_md_updater_output)
    return agent


# ──────────────────────────────────────────────
# TemporalAgent Wrappers
# ──────────────────────────────────────────────
>>>>>>> origin/main


def create_temporal_agents(
    model: Model,
    retry_config: TemporalAgentRetryConfig,
    model_settings: ModelSettings | None = None,
    provider_key: str | None = None,
    exa_configured: bool = False,
) -> TemporalAgentRegistry:
    """Create enabled agents wrapped with TemporalAgent for durable execution.

    Only creates agents that are listed in ENABLED_AGENTS.
<<<<<<< HEAD
    """
    assembly_context = create_assembly_context(
        model=model,
        retry_config=retry_config,
        model_settings=model_settings,
        provider_key=provider_key,
        exa_configured=exa_configured,
    )
    logger.info(
        "Agent external search wiring resolved: provider_key={}, exa_configured={}, supports_builtin_web_search={}, use_exa_tools={}, use_builtin_web_search={}, use_duckduckgo_search={}",
        provider_key,
        exa_configured,
        provider_supports_builtin_web_search(provider_key),
        assembly_context.search_policy.include_exa_toolsets,
        assembly_context.search_policy.include_builtin_web_search,
        assembly_context.search_policy.include_duckduckgo_fallback,
    )
    assembled_agents = assemble_enabled_temporal_agents(
        agent_builders=build_enabled_agent_builders(ENABLED_AGENTS),
        context=assembly_context,
    )
    agents = TemporalAgentRegistry.model_validate(
        {
            agent_type.value: temporal_agent
            for agent_type, temporal_agent in assembled_agents.items()
        }
    )
    for agent_name in agents.iter_agent_names():
        logger.info("Created {}", agent_name)
    logger.info("Enabled agents: {}", agents.enabled_agent_names())
=======

    Args:
        model: Configured Model instance from ModelFactory
        retry_config: Retry policy configuration for activities
        model_settings: Optional model settings (temperature, etc.)
        provider_key: Provider identifier for built-in web-search compatibility
        exa_configured: Whether Exa tool credentials are configured for this worker

    Returns:
        Dictionary mapping agent names to TemporalAgent instances
    """
    agents: TemporalAgentRegistry = {}

    # Base activity configuration with bounded retry policy
    base_activity_config = ActivityConfig(
        start_to_close_timeout=timedelta(seconds=300),
        retry_policy=retry_config.base_retry_policy,
    )

    # Model activity configuration (higher retries for LLM calls)
    model_activity_config = ActivityConfig(
        start_to_close_timeout=timedelta(seconds=300),
        retry_policy=retry_config.model_retry_policy,
    )

    # Toolset activity configuration (moderate retries for tool operations)
    toolset_activity_config = ActivityConfig(
        start_to_close_timeout=timedelta(seconds=120),
        retry_policy=retry_config.toolset_retry_policy,
    )

    # Tool activity configuration (conservative retries for individual tools)
    tool_activity_config_base = ActivityConfig(
        start_to_close_timeout=timedelta(seconds=120),
        retry_policy=retry_config.tool_retry_policy,
    )

    # Pydantic AI names the default function toolset as "<agent>".
    # Use that exact ID when configuring activity overrides.
    default_toolset_id = "<agent>"
    search_mode = _resolve_search_mode(provider_key, exa_configured)
    supports_builtin_web_search = _supports_builtin_web_search_with_function_tools(
        provider_key
    )
    use_exa_tools = search_mode == SEARCH_MODE_EXA
    use_builtin_web_search = search_mode == SEARCH_MODE_BUILTIN_WEB_SEARCH
    use_duckduckgo_search = search_mode == SEARCH_MODE_DUCKDUCKGO
    builtin_web_search_tools = (
        _get_web_search_builtin_tools(provider_key) if use_builtin_web_search else []
    )
    logger.info(
        "Agent external search mode resolved: provider_key={}, exa_configured={}, supports_builtin_web_search={}, selected_search_mode={}",
        provider_key,
        exa_configured,
        supports_builtin_web_search,
        search_mode,
    )

    # Conditionally create agents based on ENABLED_AGENTS
    if AgentType.DEVELOPMENT_WORKFLOW in ENABLED_AGENTS:
        exa_toolset_id = EXA_TOOLSET_IDS[AgentType.DEVELOPMENT_WORKFLOW]
        engineering_agent = create_engineering_development_workflow_agent(
            model,
            model_settings,
            builtin_tools=builtin_web_search_tools if use_builtin_web_search else None,
            include_exa_toolset=use_exa_tools,
            search_mode=search_mode,
        )
        engineering_tool_activity_config: ToolActivityConfigMap = {
            "get_directory_tree": tool_activity_config_base,
            "read_file_content": tool_activity_config_base,
            "search_across_codebase": tool_activity_config_base,
        }
        if use_duckduckgo_search:
            engineering_tool_activity_config["duckduckgo_search"] = (
                tool_activity_config_base
            )
        engineering_toolset_activity_config: ToolsetActivityConfigMap = {
            default_toolset_id: toolset_activity_config
        }
        engineering_toolset_tool_activity_config: ToolsetToolActivityConfigMap = {
            default_toolset_id: engineering_tool_activity_config
        }
        # Register both the dynamic toolset wrapper and the returned SkillsToolset.
        engineering_toolset_activity_config[TS_MONOREPO_DYNAMIC_TOOLSET_ID] = (
            toolset_activity_config
        )
        engineering_toolset_tool_activity_config[TS_MONOREPO_DYNAMIC_TOOLSET_ID] = {}
        engineering_toolset_activity_config[TS_MONOREPO_TOOLSET_ID] = (
            toolset_activity_config
        )
        engineering_toolset_tool_activity_config[TS_MONOREPO_TOOLSET_ID] = {}
        if use_exa_tools:
            engineering_toolset_activity_config[exa_toolset_id] = (
                toolset_activity_config
            )
            engineering_toolset_tool_activity_config[exa_toolset_id] = {}
        agents[AgentType.DEVELOPMENT_WORKFLOW.value] = TemporalAgent(
            engineering_agent,
            activity_config=base_activity_config,
            model_activity_config=model_activity_config,
            toolset_activity_config=engineering_toolset_activity_config,
            tool_activity_config=engineering_toolset_tool_activity_config,
        )
        logger.info("Created development_workflow_guide")

    if AgentType.DEPENDENCY in ENABLED_AGENTS:
        exa_toolset_id = EXA_TOOLSET_IDS[AgentType.DEPENDENCY]
        include_exa_dependency_toolset = use_exa_tools
        dependency_guide_agent = create_dependency_guide_agent(
            model,
            model_settings,
            builtin_tools=builtin_web_search_tools if use_builtin_web_search else None,
            include_exa_toolset=include_exa_dependency_toolset,
            search_mode=search_mode,
        )
        dependency_toolset_activity_config: ToolsetActivityConfigMap = {
            default_toolset_id: toolset_activity_config
        }
        dependency_tool_activity_config_for_agent: ToolActivityConfigMap = {}
        if use_duckduckgo_search:
            dependency_tool_activity_config_for_agent["duckduckgo_search"] = (
                tool_activity_config_base
            )
        dependency_tool_activity_config: ToolsetToolActivityConfigMap = {
            default_toolset_id: dependency_tool_activity_config_for_agent
        }
        if include_exa_dependency_toolset:
            dependency_toolset_activity_config[exa_toolset_id] = toolset_activity_config
            dependency_tool_activity_config[exa_toolset_id] = {}

        agents[AgentType.DEPENDENCY.value] = TemporalAgent(
            dependency_guide_agent,
            activity_config=base_activity_config,
            model_activity_config=model_activity_config,
            toolset_activity_config=dependency_toolset_activity_config,
            tool_activity_config=dependency_tool_activity_config,
        )
        logger.info("Created dependency_guide")

    if AgentType.CALL_EXPRESSION_VALIDATOR in ENABLED_AGENTS:
        exa_toolset_id = EXA_TOOLSET_IDS[AgentType.CALL_EXPRESSION_VALIDATOR]
        call_expression_validator_agent = create_call_expression_validator_agent(
            model,
            model_settings,
            builtin_tools=builtin_web_search_tools if use_builtin_web_search else None,
            include_exa_toolset=use_exa_tools,
            search_mode=search_mode,
        )
        call_expression_tool_activity_config: ToolActivityConfigMap = {
            "read_file_content": tool_activity_config_base,
            "search_across_codebase": tool_activity_config_base,
            "upsert_framework_feature_validation_evidence": tool_activity_config_base,
            "set_framework_feature_validation_status": tool_activity_config_base,
        }
        if use_duckduckgo_search:
            call_expression_tool_activity_config["duckduckgo_search"] = (
                tool_activity_config_base
            )
        call_expression_toolset_activity_config: ToolsetActivityConfigMap = {
            default_toolset_id: toolset_activity_config
        }
        call_expression_toolset_tool_activity_config: ToolsetToolActivityConfigMap = {
            default_toolset_id: call_expression_tool_activity_config
        }
        if use_exa_tools:
            call_expression_toolset_activity_config[exa_toolset_id] = (
                toolset_activity_config
            )
            call_expression_toolset_tool_activity_config[exa_toolset_id] = {}

        agents[AgentType.CALL_EXPRESSION_VALIDATOR.value] = TemporalAgent(
            call_expression_validator_agent,
            activity_config=base_activity_config,
            model_activity_config=model_activity_config,
            toolset_activity_config=call_expression_toolset_activity_config,
            tool_activity_config=call_expression_toolset_tool_activity_config,
        )
        logger.info("Created call_expression_validator")

    if AgentType.BUSINESS_DOMAIN in ENABLED_AGENTS:
        domain_agent = create_business_logic_domain_agent(
            model,
            model_settings,
            builtin_tools=builtin_web_search_tools if use_builtin_web_search else None,
        )
        business_domain_tool_activity_config: ToolActivityConfigMap = {
            "get_data_model_files": tool_activity_config_base,
            "read_file_content": tool_activity_config_base,
        }
        agents[AgentType.BUSINESS_DOMAIN.value] = TemporalAgent(
            domain_agent,
            activity_config=base_activity_config,
            model_activity_config=model_activity_config,
            toolset_activity_config={default_toolset_id: toolset_activity_config},
            tool_activity_config={
                default_toolset_id: business_domain_tool_activity_config
            },
        )
        logger.info("Created business_domain_guide")

    if AgentType.AGENTS_MD_UPDATER in ENABLED_AGENTS:
        updater_agent = create_agents_md_updater_agent(model, model_settings)
        updater_tool_activity_config: ToolActivityConfigMap = {
            "updater_read_file": tool_activity_config_base,
            "updater_edit_file": tool_activity_config_base,
            "updater_apply_patch": tool_activity_config_base,
        }
        agents[AgentType.AGENTS_MD_UPDATER.value] = TemporalAgent(
            updater_agent,
            activity_config=base_activity_config,
            model_activity_config=model_activity_config,
            toolset_activity_config={default_toolset_id: toolset_activity_config},
            tool_activity_config={default_toolset_id: updater_tool_activity_config},
        )
        logger.info("Created agents_md_updater")

    logger.info("Enabled agents: {}", list(agents.keys()))
>>>>>>> origin/main
    return agents


# Default request_limit when user hasn't configured one explicitly.
# pydantic_ai's built-in default is 50, which is too low for larger codebases.
DEFAULT_REQUEST_LIMIT: int = 200

# Module-level cache for temporal agents singleton
_temporal_agents: TemporalAgentRegistry | None = None
_cached_model: Model | None = None
_cached_model_settings: ModelSettings | None = None
_cached_usage_limits: UsageLimits | None = None


def get_temporal_agents() -> TemporalAgentRegistry:
<<<<<<< HEAD
    """Get cached temporal agents singleton."""
=======
    """Get cached temporal agents singleton.

    Returns:
        Dictionary of temporal agent instances

    Raises:
        RuntimeError: If agents not initialized (call initialize_temporal_agents first)
    """
>>>>>>> origin/main
    global _temporal_agents
    if _temporal_agents is None:
        raise RuntimeError(
            "Temporal agents not initialized. Call initialize_temporal_agents() first."
        )
    return _temporal_agents


def initialize_temporal_agents(
    model: Model,
    settings: EnvironmentSettings,
    model_settings: ModelSettings | None = None,
    provider_key: str | None = None,
    exa_configured: bool = False,
    request_limit: int | None = None,
) -> TemporalAgentRegistry:
<<<<<<< HEAD
    """Initialize temporal agents with the given model."""
=======
    """Initialize temporal agents with the given model.

    This should be called once at worker startup after loading model from DB.

    Args:
        model: Configured Model instance from ModelFactory
        settings: Environment settings for retry configuration
        model_settings: Optional model settings (temperature, etc.)
        provider_key: Provider identifier for web search compatibility
        exa_configured: Whether Exa tool credentials are configured for this worker
        request_limit: Max LLM round-trips per Agent.run() call (None = DEFAULT_REQUEST_LIMIT)

    Returns:
        Dictionary of temporal agent instances
    """
>>>>>>> origin/main
    global _temporal_agents, _cached_model, _cached_model_settings, _cached_usage_limits

    retry_config = TemporalAgentRetryConfig(settings)

    effective_limit = (
        request_limit if request_limit is not None else DEFAULT_REQUEST_LIMIT
    )
    _cached_model = model
    _cached_model_settings = model_settings
    _cached_usage_limits = UsageLimits(request_limit=effective_limit)

    _temporal_agents = create_temporal_agents(
        model,
        retry_config,
        model_settings,
        provider_key=provider_key,
        exa_configured=exa_configured,
    )

    logger.info(
        "Temporal agents initialized with {} agents (request_limit={})",
<<<<<<< HEAD
        _temporal_agents.enabled_agent_count(),
=======
        len(_temporal_agents),
>>>>>>> origin/main
        effective_limit,
    )
    return _temporal_agents


def get_cached_model() -> Model:
<<<<<<< HEAD
    """Get the cached model instance used for agents."""
=======
    """Get the cached model instance used for agents.

    Returns:
        Cached Model instance

    Raises:
        RuntimeError: If agents not initialized
    """
>>>>>>> origin/main
    if _cached_model is None:
        raise RuntimeError(
            "Model not initialized. Call initialize_temporal_agents() first."
        )
    return _cached_model


def get_cached_model_settings() -> ModelSettings | None:
<<<<<<< HEAD
    """Get the cached model settings."""
=======
    """Get the cached model settings.

    Returns:
        Cached ModelSettings or None
    """
>>>>>>> origin/main
    return _cached_model_settings


def get_cached_usage_limits() -> UsageLimits | None:
<<<<<<< HEAD
    """Get the cached usage limits."""
=======
    """Get the cached usage limits.

    Returns:
        Cached UsageLimits (always set after initialization, defaults to 200)
    """
>>>>>>> origin/main
    return _cached_usage_limits
