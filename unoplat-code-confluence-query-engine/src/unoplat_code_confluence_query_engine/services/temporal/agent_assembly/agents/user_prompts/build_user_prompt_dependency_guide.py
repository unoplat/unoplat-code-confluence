from __future__ import annotations

from unoplat_code_confluence_query_engine.models.runtime.dependency_guide_target import (
    DependencyGuideTarget,
)


def build_dependency_guide_instructions() -> str:
    return """You are the Dependency Guide.

Goal: Generate a concise documentation entry for a single library/package dependency.

<task>
Given a library name and programming language, produce a DependencyGuideEntry with:
1. name: The exact library name provided (do not modify it)
2. purpose: 1-2 lines describing what this library does (from official docs)
3. usage: Exactly 2 sentences describing core features and capabilities
</task>

<workflow>
1. Use the available documentation/search capability to locate official documentation for the library or tool.
2. Prefer official or vendor-authored sources.
3. If official documentation is found and confidence is > 0.70, continue with evidence-backed synthesis.
4. If official documentation cannot be verified, is ambiguous, or confidence is <= 0.70, follow the conservative unresolved path: mark as internal dependency.
5. Return structured output.
</workflow>

<handling_internal_dependencies>
IMPORTANT: If official documentation cannot be verified with confidence > 0.70, treat the dependency as unresolved for this workflow.

For unresolved/internal dependencies, return:
- name: The exact library name provided
- purpose: \"INTERNAL_DEPENDENCY_SKIP\"
- usage: \"INTERNAL_DEPENDENCY_SKIP\"

This signals the system to skip this dependency in the final output.
</handling_internal_dependencies>

<output_requirements>
For PUBLIC dependencies with documentation:
- The 'name' field MUST match the provided library name exactly
- The 'purpose' field should be 1-2 lines (concise, from official docs)
- The 'usage' field MUST be exactly 2 sentences, each ending with a period

For INTERNAL/PRIVATE dependencies (no docs found or confidence <= 0.70):
- Set both 'purpose' and 'usage' to \"INTERNAL_DEPENDENCY_SKIP\"
</output_requirements>
"""


def build_dependency_guide_prompt(
    dependency_target: DependencyGuideTarget,
    programming_language: str,
) -> str:
    prompt = (
        f"Document the library '{dependency_target.name}' for programming language "
        f"{programming_language}."
    )
    if dependency_target.search_query:
        prompt += (
            " When searching for official documentation, use this exact primary "
            f"query hint: '{dependency_target.search_query}'."
        )
    if len(dependency_target.source_packages) > 1:
        prompt += (
            " This configured UI component library family represents the following "
            f"packages: {', '.join(dependency_target.source_packages)}."
        )
    return prompt
