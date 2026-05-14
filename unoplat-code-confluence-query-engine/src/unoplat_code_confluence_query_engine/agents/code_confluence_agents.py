"""Dynamic system prompts for code confluence agents."""

from pydantic_ai import RunContext

from unoplat_code_confluence_query_engine.models.output.engineering_workflow_output import (
    ENGINEERING_WORKFLOW_NO_CHANGE,
)
from unoplat_code_confluence_query_engine.models.runtime.agent_dependencies import (
    AgentDependencies,
)


def get_engineering_citation_instructions() -> str:
    """Return command-verification policy for the engineering workflow agent."""
    return (
        "<verification_strategy>\n"
        "Use console capability tools to inspect the codebase before emitting commands.\n"
        "Prefer `glob`, `grep`, and `read_file` for discovering configuration files and scripts.\n\n"
        "Execute policy (CLI help/version discovery only):\n"
        "- Use `execute` only for CLI help/version discovery: allowed commands must contain `--help`, `-h`, `--version`, `-v`, or an explicit `help` subcommand/token (for example `uv help run`, `npm help run`, `npm run --help`, `python -m fastapi --help`, `npx vite --help`).\n"
        "- Do NOT execute install, build, test, lint, type_check, dev, server, watch, reload, or package-install/sync commands. Examples of prohibited commands include `uv sync`, `npm install`, `pnpm install`, `bun install`, `pytest`, `ruff check`, `mypy`, `basedpyright`, `tsc`, `npm run build`, `npm test`, `npm run lint`, `npm run dev`, `vite`, `next dev`, `fastapi dev`, `uvicorn --reload`, and any watch/reload/server command.\n"
        "- Any command without `--help`, `-h`, `--version`, `-v`, or an explicit `help` token is a wrong command for `execute`.\n\n"
        "Evidence sources (in priority order):\n"
        "- Prefer codebase package/config files (e.g. `package.json`, `pyproject.toml`, Makefiles, framework configs) and CLI command/subcommand help output as primary evidence.\n"
        "- Consult official documentation via web search/fetch only when repository evidence plus CLI help is insufficient to resolve command syntax, flags, or framework conventions.\n\n"
        "Command selection criteria:\n"
        "- Final emitted commands may be unexecuted, but every emitted command must be directly supported by codebase package/config evidence, CLI help output, or official documentation evidence.\n"
        "- If a command cannot be grounded in any of those evidence sources, do NOT emit it.\n"
        "</verification_strategy>\n"
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
    is_typescript = lang.lower() == "typescript"
    if provenance == "inherited" and is_typescript:
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
        "Analyze the codebase and maintain AGENTS.md / ## Engineering Workflow.\n"
        f"If the existing section is complete and still correct after verifying package-manager, lint, and type-check evidence, return exactly {ENGINEERING_WORKFLOW_NO_CHANGE}.\n"
        "If the section is missing, incomplete, stale, or edited, return an engineering_workflow JSON object.\n"
        "</task>\n\n"
        "<file_path_requirements>\n"
        "When using file-related tools, pass ABSOLUTE filesystem paths only.\n"
        f"The codebase root path is: {codebase_path}\n"
        "If monorepo context indicates inherited ownership, you may inspect absolute parent directories above the codebase root to locate the owning workspace root.\n"
        "In FINAL OUTPUT, every config_file path MUST be repository-root-relative (never absolute).\n"
        "Never use codebase-relative '..' segments in config_file paths.\n"
        "</file_path_requirements>\n\n"
        "<output_contract>\n"
        "Return ONLY one of these outputs:\n"
        f"1. The exact string {ENGINEERING_WORKFLOW_NO_CHANGE} when no markdown update is required.\n"
        "2. JSON with this exact top-level shape when an update is required:\n"
        '{"commands":[{"command":"<runnable command>","stage":"install|build|dev|test|lint|type_check",'
        '"config_file":"<repository-root-relative path or unknown>",'
        '"working_directory":"<repo-relative dir: omit/null=codebase root, .=repo root, path=workspace root>"}]}\n'
        "</output_contract>\n\n"
        "<rules>\n"
        "- Use console tools (`glob`, `grep`, `read_file`) to discover configuration files, scripts, and project structure before emitting commands.\n"
        "- When ## Engineering Workflow already exists, first inspect current package-manager config/scripts plus lint and type-check config/script sources to decide whether the section needs changes.\n"
        f"- Return {ENGINEERING_WORKFLOW_NO_CHANGE} only when the existing section is complete, still correct, and you made no AGENTS.md edit.\n"
        "- Follow the shared verification strategy when deciding whether a command is verified enough to include.\n"
        "- Include install commands whenever install/bootstrap/setup evidence exists.\n"
        "- stage must be one of: install, build, dev, test, lint, type_check.\n"
        "- Emit only the keys defined in output_contract and nothing else.\n"
        "- config_file is the single most relevant configuration file for this command (repository-root-relative path or 'unknown').\n"
        "- working_directory: omit or null to run from codebase root, '.' to run from repo root, or a repo-relative path for a specific workspace root.\n"
        "</rules>\n"
    )
