from __future__ import annotations

from collections.abc import Awaitable, Callable

from unoplat_code_confluence_query_engine.agents.code_confluence_agents import (
    get_engineering_citation_instructions,
    per_language_development_workflow_prompt,
)


def build_development_workflow_instructions() -> str:
    return (
        "<role>Engineering Workflow Synthesizer</role>\n"
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


def build_per_language_development_workflow_instructions() -> Callable[..., Awaitable[str]]:
    return per_language_development_workflow_prompt
