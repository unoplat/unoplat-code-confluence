"""Dynamic system prompts for code confluence agents."""

from pydantic_ai import RunContext

from unoplat_code_confluence_query_engine.models.runtime.agent_dependencies import (
    AgentDependencies,
)

<<<<<<< HEAD

def get_engineering_citation_instructions() -> str:
    """Return stable citation-validation instructions for the engineering workflow agent."""
    return (
        "<citation_validation>\n"
        "For EVERY command you emit, verify it against official documentation using the available documentation/search capability together with repository evidence.\n"
        "Prefer official or vendor-authored documentation for the tool or framework behind each command.\n"
        "Confirm the command syntax, flags, scope, and usage before emitting it.\n\n"
        "Confidence scoring guidance:\n"
        "- 0.90-1.00: exact match with official documentation or strong repository/config evidence\n"
        "- 0.71-0.89: strong evidence and acceptable to emit\n"
        "- 0.50-0.70: partially supported or inferred; do NOT emit\n"
        "- Below 0.50: speculative; do NOT emit\n\n"
        "Only emit commands when confidence is > 0.70.\n"
        "If official documentation cannot be verified, rely on repository evidence only and remain conservative.\n"
=======
SEARCH_MODE_EXA = "exa"
SEARCH_MODE_BUILTIN_WEB_SEARCH = "builtin_web_search"
SEARCH_MODE_DUCKDUCKGO = "duckduckgo"
SEARCH_MODE_NONE = "none"


def get_official_docs_search_instruction(
    search_mode: str,
    *,
    target: str,
) -> str:
    """Return search-mode-specific instruction for official documentation lookup.

    Args:
        search_mode: Resolved search mode (`exa`, `builtin_web_search`, `duckduckgo`, or `none`).
        target: Subject to validate against official docs (for example "framework API usage").

    Returns:
        Instruction sentence describing required documentation lookup behavior.
    """
    if search_mode == SEARCH_MODE_EXA:
        return f"Use Exa MCP tools (web_search_exa/get_code_context_exa) to verify {target} against official documentation."
    if search_mode == SEARCH_MODE_BUILTIN_WEB_SEARCH:
        return f"Use built-in web_search to verify {target} against official documentation."
    if search_mode == SEARCH_MODE_DUCKDUCKGO:
        return f"Use the DuckDuckGo search tool to verify {target} against official documentation."
    return f"No external search tools are available; if official documentation cannot be verified for {target}, choose a conservative unresolved path."


def get_official_docs_workflow_steps(
    search_mode: str,
    *,
    target: str,
    unresolved_outcome: str,
) -> str:
    """Return numbered workflow steps for official docs verification by search mode.

    Args:
        search_mode: Resolved search mode (`exa`, `builtin_web_search`, `duckduckgo`, or `none`).
        target: Subject to verify against official documentation.
        unresolved_outcome: Required fallback behavior when docs cannot be verified.

    Returns:
        Multi-line numbered steps string.
    """
    if search_mode == SEARCH_MODE_EXA:
        return (
            f"1. Use Exa MCP tools (web_search_exa/get_code_context_exa) to locate official documentation for {target}.\n"
            "2. Evaluate results:\n"
            "   - If official documentation is found: continue with evidence-backed synthesis\n"
            f"   - If docs are missing/ambiguous: {unresolved_outcome}\n"
            "3. Return structured output."
        )
    if search_mode == SEARCH_MODE_BUILTIN_WEB_SEARCH:
        return (
            f"1. Use built-in web_search to locate official documentation for {target}.\n"
            "2. Evaluate results:\n"
            "   - If official documentation is found: continue with evidence-backed synthesis\n"
            f"   - If docs are missing/ambiguous: {unresolved_outcome}\n"
            "3. Return structured output."
        )
    if search_mode == SEARCH_MODE_DUCKDUCKGO:
        return (
            f"1. Use the DuckDuckGo search tool to locate official documentation for {target}.\n"
            "2. Evaluate results:\n"
            "   - If official documentation is found: continue with evidence-backed synthesis\n"
            f"   - If docs are missing/ambiguous: {unresolved_outcome}\n"
            "3. Return structured output."
        )
    return (
        "1. Use available repository context only.\n"
        f"2. Since official documentation lookup is unavailable: {unresolved_outcome}\n"
        "3. Return structured output."
    )


def get_engineering_citation_instructions(search_mode: str) -> str:
    """Return mode-specific citation validation instructions for the engineering workflow agent."""
    if search_mode == SEARCH_MODE_EXA:
        return (
            "<citation_validation>\n"
            "For EVERY command you emit, you MUST verify it against official documentation "
            "using the Exa MCP tools (web_search_exa / get_code_context_exa).\n"
            "Search for the official docs of the tool or framework behind each command and confirm "
            "the command syntax, flags, and usage are correct before emitting it.\n\n"
            "Confidence scoring guidance:\n"
            "- 0.8-1.0: Exact match with official documentation or config file evidence\n"
            "- 0.5-0.79: Reasonable variant confirmed by documentation patterns\n"
            "- 0.35-0.49: Inferred from file structure and common conventions\n"
            "- Below 0.35: Speculative — do NOT emit these commands\n"
            "Only emit commands with confidence >= 0.35.\n"
            "</citation_validation>\n"
        )
    if search_mode == SEARCH_MODE_BUILTIN_WEB_SEARCH:
        return (
            "<citation_validation>\n"
            "For EVERY command you emit, you MUST verify it against official documentation "
            "using the built-in web_search tool.\n"
            "Search for the official docs of the tool or framework behind each command and confirm "
            "the command syntax, flags, and usage are correct before emitting it.\n\n"
            "Confidence scoring guidance:\n"
            "- 0.8-1.0: Exact match with official documentation or config file evidence\n"
            "- 0.5-0.79: Reasonable variant confirmed by documentation patterns\n"
            "- 0.35-0.49: Inferred from file structure and common conventions\n"
            "- Below 0.35: Speculative — do NOT emit these commands\n"
            "Only emit commands with confidence >= 0.35.\n"
            "</citation_validation>\n"
        )
    if search_mode == SEARCH_MODE_DUCKDUCKGO:
        return (
            "<citation_validation>\n"
            "For EVERY command you emit, you MUST verify it against official documentation "
            "using the DuckDuckGo search tool.\n"
            "Search for the official docs of the tool or framework behind each command and confirm "
            "the command syntax, flags, and usage are correct before emitting it.\n\n"
            "Confidence scoring guidance:\n"
            "- 0.8-1.0: Exact match with official documentation or config file evidence\n"
            "- 0.5-0.79: Reasonable variant confirmed by documentation patterns\n"
            "- 0.35-0.49: Inferred from file structure and common conventions\n"
            "- Below 0.35: Speculative — do NOT emit these commands\n"
            "Only emit commands with confidence >= 0.35.\n"
            "</citation_validation>\n"
        )
    return (
        "<citation_validation>\n"
        "External search is unavailable. Verify commands only from repository evidence "
        "(Taskfile/Makefile/configs/scripts) and avoid speculative assumptions.\n"
        "If official documentation cannot be verified, keep outputs conservative and avoid "
        "high-confidence claims.\n\n"
        "Confidence scoring guidance:\n"
        "- 0.6-1.0: Strong repository-local evidence for exact command syntax\n"
        "- 0.35-0.59: Plausible command inferred from repository conventions\n"
        "- Below 0.35: Speculative — do NOT emit these commands\n"
        "Only emit commands with confidence >= 0.35.\n"
>>>>>>> origin/main
        "</citation_validation>\n"
    )


async def per_language_development_workflow_prompt(
    ctx: RunContext[AgentDependencies],
) -> str:
    """Generate single-agent prompt for canonical engineering workflow extraction."""
    lang = ctx.deps.codebase_metadata.codebase_programming_language
    package_manager = ctx.deps.codebase_metadata.codebase_package_manager
    codebase_path = ctx.deps.codebase_metadata.codebase_path

    provenance = ctx.deps.codebase_metadata.codebase_package_manager_provenance
    workspace_root = ctx.deps.codebase_metadata.codebase_workspace_root
    workspace_root_path = ctx.deps.codebase_metadata.codebase_workspace_root_path
    package_manager_provenance_line = ""
    if provenance is not None:
        package_manager_provenance_line = f"Package manager provenance: {provenance}\n"

    monorepo_context = ""
<<<<<<< HEAD
    is_typescript = lang.lower() == "typescript"
    if provenance == "inherited" and is_typescript:
=======
    if provenance == "inherited":
>>>>>>> origin/main
        monorepo_context = (
            "<monorepo_context>\nThis codebase is a workspace member in a monorepo.\n"
        )
        if workspace_root is not None:
            monorepo_context += f"Workspace root (repo-relative): {workspace_root}\n"
        if workspace_root_path:
            monorepo_context += f"Workspace root (absolute): {workspace_root_path}\n"
        if workspace_root is not None:
            monorepo_context += (
                "Use the typescript-monorepo skill for workspace-aware command guidance.\n"
                "Inspect workspace-owned configuration from the workspace root path when command scope differs from the leaf root.\n"
            )
        else:
            monorepo_context += (
                "Use the typescript-monorepo skill for workspace-aware command guidance.\n"
                "Because workspace_root is missing, derive parent absolute paths from codebase_path and walk upward until the nearest owning workspace root is found.\n"
            )
        monorepo_context += "</monorepo_context>\n\n"

    return (
        f"You are the Development Workflow Guide for {lang} projects.\n"
        f"Package manager: {package_manager}\n"
        f"{package_manager_provenance_line}\n" + monorepo_context + "<task>\n"
<<<<<<< HEAD
        "Analyze the codebase and return an  engineering_workflow JSON object only.\n"
=======
        "Analyze the codebase and return a canonical engineering_workflow JSON object only.\n"
>>>>>>> origin/main
        "commands MUST NOT be empty.\n"
        "</task>\n\n"
        "<file_path_requirements>\n"
        "When using tools, pass ABSOLUTE filesystem paths only.\n"
        f"The codebase root path is: {codebase_path}\n"
        "If monorepo context indicates inherited ownership, you may inspect absolute parent directories above the codebase root to locate the owning workspace root.\n"
<<<<<<< HEAD
        "In FINAL OUTPUT, every config_file path MUST be repository-root-relative (never absolute).\n"
        "Never use codebase-relative '..' segments in config_file paths.\n"
=======
        "In FINAL OUTPUT, every config_file path MUST be repo-relative (never absolute).\n"
>>>>>>> origin/main
        "</file_path_requirements>\n\n"
        "<output_contract>\n"
        "Return ONLY JSON with this exact top-level shape:\n"
        '{"commands":[{"command":"<runnable command>","stage":"install|build|dev|test|lint|type_check",'
<<<<<<< HEAD
        '"config_file":"<repository-root-relative path or unknown>","confidence":0.0,'
=======
        '"config_file":"<repo-relative path or unknown>","confidence":0.0,'
>>>>>>> origin/main
        '"working_directory":"<repo-relative dir: omit/null=codebase root, .=repo root, path=workspace root>"}]}\n'
        "Do not include markdown, prose, or extra keys.\n"
        "</output_contract>\n\n"
        "<command_discovery_requirements>\n"
        "You MUST inspect likely command sources before final output:\n"
        "- Python: pyproject.toml, Taskfile.yml, Makefile, tox.ini, noxfile.py, pytest.ini, ruff.toml, mypy.ini\n"
        "- TypeScript/JavaScript: package.json scripts, Taskfile.yml, Makefile, turbo/nx configs\n"
        "- Rust: Cargo.toml / cargo aliases\n"
        "- Go: Makefile/taskfile/go toolchain conventions\n"
        "If install/bootstrap/setup commands exist, include them with stage=install.\n"
        "If build/test/lint/type_check commands exist, include them too.\n"
        "</command_discovery_requirements>\n\n"
        "<rules>\n"
        "- Include install commands whenever install/bootstrap/setup evidence exists.\n"
        "- stage must be one of: install, build, dev, test, lint, type_check.\n"
        "- Emit only the keys defined in output_contract and nothing else.\n"
<<<<<<< HEAD
        "- config_file is the single most relevant configuration file for this command (repository-root-relative path or 'unknown').\n"
        "- confidence is a float between 0.0 and 1.0.\n"
        "- Commands with confidence <= 0.70 will be filtered out.\n"
=======
        "- config_file is the single most relevant configuration file for this command (repo-relative path or 'unknown').\n"
        "- confidence is a float between 0.0 and 1.0.\n"
        "- Commands below 0.35 confidence will be filtered out.\n"
>>>>>>> origin/main
        "- working_directory: omit or null to run from codebase root, '.' to run from repo root, or a repo-relative path for a specific workspace root.\n"
        "</rules>\n"
        "<examples>\n"
        "Example (Python + uv):\n"
        '{"commands":['
        '{"command":"uv sync --group dev --group test","stage":"install","config_file":"pyproject.toml","confidence":0.95},'
<<<<<<< HEAD
        "Example (TypeScript):\n"
        '{"commands":['
        '{"command":"npm ci","stage":"install","config_file":"package.json","confidence":0.95},'
        "Example (TypeScript monorepo workspace member):\n"
        '{"commands":['
        '{"command":"pnpm install","stage":"install","config_file":"infra/services/pnpm-workspace.yaml","confidence":0.95,"working_directory":"infra/services"},'
=======
        '{"command":"uv run fastapi dev --port 8001","stage":"dev","config_file":"pyproject.toml","confidence":0.85},'
        '{"command":"uv run --group test pytest -v","stage":"test","config_file":"pyproject.toml","confidence":0.90},'
        '{"command":"uv run --group dev ruff check src/","stage":"lint","config_file":"ruff.toml","confidence":0.90},'
        '{"command":"uv run --group dev basedpyright src/","stage":"type_check","config_file":"pyproject.toml","confidence":0.85}]}\n'
        "Example (TypeScript):\n"
        '{"commands":['
        '{"command":"npm ci","stage":"install","config_file":"package.json","confidence":0.95},'
        '{"command":"npm run dev","stage":"dev","config_file":"package.json","confidence":0.90},'
        '{"command":"npm run build","stage":"build","config_file":"package.json","confidence":0.90},'
        '{"command":"npm run test","stage":"test","config_file":"package.json","confidence":0.85},'
        '{"command":"npm run lint","stage":"lint","config_file":"package.json","confidence":0.85}]}\n'
        "Example (TypeScript monorepo workspace member):\n"
        '{"commands":['
        '{"command":"pnpm install","stage":"install","config_file":"infra/services/pnpm-workspace.yaml","confidence":0.95,"working_directory":"infra/services"},'
        '{"command":"pnpm run build --filter api","stage":"build","config_file":"infra/services/package.json","confidence":0.85,"working_directory":"infra/services"},'
        '{"command":"pnpm run test","stage":"test","config_file":"infra/services/apps/api/package.json","confidence":0.85},'
        '{"command":"pnpm run lint","stage":"lint","config_file":"infra/services/apps/api/package.json","confidence":0.85}]}\n'
>>>>>>> origin/main
        "</examples>\n"
    )
