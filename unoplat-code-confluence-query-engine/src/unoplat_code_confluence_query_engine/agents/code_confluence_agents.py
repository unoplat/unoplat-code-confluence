"""Dynamic system prompts for code confluence agents."""

from pydantic_ai import RunContext

from unoplat_code_confluence_query_engine.models.runtime.agent_dependencies import (
    AgentDependencies,
)

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
    if provenance == "inherited":
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
        f"{package_manager_provenance_line}\n"
        + monorepo_context
        + "<task>\n"
        "Analyze the codebase and return a canonical engineering_workflow JSON object only.\n"
        "commands MUST NOT be empty.\n"
        "</task>\n\n"
        "<file_path_requirements>\n"
        "When using tools, pass ABSOLUTE filesystem paths only.\n"
        f"The codebase root path is: {codebase_path}\n"
        "If monorepo context indicates inherited ownership, you may inspect absolute parent directories above the codebase root to locate the owning workspace root.\n"
        "In FINAL OUTPUT, every config_file path MUST be repo-relative (never absolute).\n"
        "</file_path_requirements>\n\n"
        "<output_contract>\n"
        "Return ONLY JSON with this exact top-level shape:\n"
        '{"commands":[{"command":"<runnable command>","stage":"install|build|dev|test|lint|type_check",'
        '"config_file":"<repo-relative path or unknown>","confidence":0.0,'
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
        "- config_file is the single most relevant configuration file for this command (repo-relative path or 'unknown').\n"
        "- confidence is a float between 0.0 and 1.0.\n"
        "- Commands with confidence <= 0.70 will be filtered out.\n"
        "- working_directory: omit or null to run from codebase root, '.' to run from repo root, or a repo-relative path for a specific workspace root.\n"
        "</rules>\n"
        "<examples>\n"
        "Example (Python + uv):\n"
        '{"commands":['
        '{"command":"uv sync --group dev --group test","stage":"install","config_file":"pyproject.toml","confidence":0.95},'
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
        "</examples>\n"
    )
