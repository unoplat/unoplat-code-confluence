from __future__ import annotations

from collections.abc import Awaitable, Callable

from unoplat_code_confluence_query_engine.agents.code_confluence_agents import (
    get_engineering_citation_instructions,
    per_language_development_workflow_prompt,
)


def build_development_workflow_instructions() -> str:
    return (
        "<role>Engineering Workflow Synthesizer</role>\n"
        "<available_tools>\n"
        "Local repository inspection tools available in this run: ls, read_file, glob, grep.\n"
        "Local command verification tool available in this run: execute.\n"
        "Markdown editing tools available in this run: write_file and edit_file for Markdown files only.\n"
        "External documentation tools available in this run: Exa search toolsets when configured, plus shared web_search and web_fetch capabilities.\n"
        "Use ls/glob/grep to discover workflow files and commands, and read_file to inspect them.\n"
        "When external documentation is needed, prefer Exa for broad discovery if it is available in this run. Still use web_search and web_fetch for targeted lookup and page retrieval even when Exa is present.\n"
        "For discovery tools, use arguments that match the tool contract.\n"
        "</available_tools>\n"
        "<markdown_ownership>\n"
        "You directly own exactly one markdown location: AGENTS.md / ## Engineering Workflow.\n"
        "Before returning your final structured EngineeringWorkflow output, create or update only that section inside the existing managed block.\n"
        "Assume AGENTS.md already contains the managed block skeleton from bootstrap; preserve the begin/end markers, CRITICAL_INSTRUCTION block, and all other H2 sections exactly as they are.\n"
        "Allowed edits:\n"
        "- AGENTS.md content under ## Engineering Workflow only.\n"
        "Forbidden edits:\n"
        "- any other AGENTS.md heading or section content\n"
        "- any non-markdown file\n"
        "- dependencies_overview.md, business_domain_references.md, app_interfaces.md, or any source/config file\n"
        "If ## Engineering Workflow is already correct, do not rewrite it.\n"
        "Use this exact section shape:\n"
        "## Engineering Workflow\n"
        "### Install\n"
        "### Build\n"
        "### Dev\n"
        "### Test\n"
        "### Lint\n"
        "### Type Check\n"
        "Put runnable commands from your structured output under the matching stage as bullets, including working directory/config-file notes when known. Use an explicit 'Not detected' bullet for stages with no discovered command.\n"
        "</markdown_ownership>\n"
        f"{get_engineering_citation_instructions()}"
    )


def build_development_workflow_prompt(
    codebase_path: str,
    programming_language: str,
    package_manager: str,
) -> str:
    return (
        f"Analyze engineering workflow for {codebase_path} "
        f"using language {programming_language} "
        f"and package manager {package_manager}"
    )


def build_per_language_development_workflow_instructions() -> Callable[
    ..., Awaitable[str]
]:
    return per_language_development_workflow_prompt
