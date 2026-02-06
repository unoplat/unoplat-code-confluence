"""Dynamic system prompts for code confluence agents."""

from pydantic_ai import RunContext

from unoplat_code_confluence_query_engine.models.runtime.agent_dependencies import (
    AgentDependencies,
)


async def per_language_engineering_development_workflow_prompt(
    ctx: RunContext[AgentDependencies],
) -> str:
    """Generate single-agent prompt for canonical engineering workflow extraction."""
    lang = ctx.deps.codebase_metadata.codebase_programming_language
    package_manager = ctx.deps.codebase_metadata.codebase_package_manager
    codebase_path = ctx.deps.codebase_metadata.codebase_path

    return (
        f"You are the Engineering Development Workflow Agent for {lang} projects.\n"
        f"Package manager: {package_manager}\n\n"
        "<task>\n"
        "Analyze the codebase and return a canonical engineering_workflow JSON object only.\n"
        "You must include configs and commands in one response.\n"
        "commands MUST NOT be empty.\n"
        "</task>\n\n"
        "<file_path_requirements>\n"
        "When using tools, pass ABSOLUTE paths rooted at the codebase path.\n"
        f"The codebase root path is: {codebase_path}\n"
        "In FINAL OUTPUT, every config path MUST be repo-relative (never absolute).\n"
        "</file_path_requirements>\n\n"
        "<output_contract>\n"
        "Return ONLY JSON with this exact top-level shape:\n"
        '{"configs":[{"id":"<optional>","path":"<repo-relative>","purpose":"<10-20 words>","required_for":["<stage>"]}],'
        '"commands":[{"id":"<optional>","stage":"install|build|dev|test|lint|type_check","command":"<command>",'
        '"description":"<optional>","config_refs":["<config id or repo-relative path>"]}]}\n'
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
        "<documentation_requirements>\n"
        "Use Exa MCP tools when purpose/usage is unclear:\n"
        "- web_search_exa for official docs and command references\n"
        "- get_code_context_exa for concrete command/config examples\n"
        "For each config purpose and command description, prefer file inspection first;\n"
        "and validate with Exa before final output always.\n"
        "</documentation_requirements>\n\n"
        "<rules>\n"
        "- Include install commands whenever install/bootstrap/setup evidence exists.\n"
        "- stage must be one of: install, build, dev, test, lint, type_check.\n"
        "- Emit only the keys defined in output_contract and nothing else.\n"
        "- config_refs may contain config IDs or repo-relative config paths.\n"
        "- Include all relevant configs and commands you find.\n"
        "</rules>\n"
        "<examples>\n"
        "Example (Python + uv):\n"
        '{"configs":[{"path":"pyproject.toml","purpose":"Project metadata, dependencies and tool configuration","required_for":["install","test","lint","type_check"]},'
        '{"path":"Taskfile.yml","purpose":"Task runner commands for local development workflows","required_for":["install","dev","test"]}],'
        '"commands":[{"stage":"install","command":"uv sync --group dev --group test","description":"Install runtime and development dependencies","config_refs":["pyproject.toml"]},'
        '{"stage":"dev","command":"uv run fastapi dev --port 8001","description":"Run local API server","config_refs":["pyproject.toml"]},'
        '{"stage":"test","command":"uv run --group test pytest -v","description":"Run automated tests","config_refs":["pyproject.toml"]},'
        '{"stage":"lint","command":"uv run --group dev ruff check src/","description":"Run Ruff lint checks","config_refs":["ruff.toml"]},'
        '{"stage":"type_check","command":"uv run --group dev basedpyright src/","description":"Run static type checking","config_refs":["pyproject.toml"]}]}\n'
        "Example (TypeScript):\n"
        '{"configs":[{"path":"package.json","purpose":"Node package manifest and scripts","required_for":["install","build","dev","test","lint"]}],'
        '"commands":[{"stage":"install","command":"npm ci","description":"Install exact locked dependencies","config_refs":["package.json"]},'
        '{"stage":"dev","command":"npm run dev","description":"Run development server","config_refs":["package.json"]},'
        '{"stage":"build","command":"npm run build","description":"Create production build","config_refs":["package.json"]},'
        '{"stage":"test","command":"npm run test","description":"Run tests","config_refs":["package.json"]},'
        '{"stage":"lint","command":"npm run lint","description":"Run lint checks","config_refs":["package.json"]}]}\n'
        "</examples>\n"
    )
