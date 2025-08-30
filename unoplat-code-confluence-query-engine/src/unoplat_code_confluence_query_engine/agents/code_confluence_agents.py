from typing import Dict, List, Optional

from loguru import logger
from pydantic_ai import Agent, Tool
from pydantic_ai.models import Model
from pydantic_ai.settings import ModelSettings

from unoplat_code_confluence_query_engine.models.agent_dependencies import (
    AgentDependencies,
)
from unoplat_code_confluence_query_engine.models.agent_md_output import (
    DevelopmentWorkflow,
    FrameworkLibraryOutput,
    ProjectStructure,
)
from unoplat_code_confluence_query_engine.services.mcp.mcp_server_manager import (
    MCPServerManager,
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
from unoplat_code_confluence_query_engine.tools.get_framework_lib_feature_overview import (
    get_framework_lib_feature_overview,
)
from unoplat_code_confluence_query_engine.tools.get_lib_data import get_lib_data
from unoplat_code_confluence_query_engine.tools.get_structural_signature import (
    get_structural_signature,
)
from unoplat_code_confluence_query_engine.tools.search_across_codebase import (
    search_across_codebase,
)


def create_code_confluence_agents(mcp_server_manager: MCPServerManager, model: Model, model_settings: Optional[ModelSettings] = None) -> Dict[str, Agent]:
    """Create code confluence agents with provided model.
    
    Args:
        mcp_server_manager: MCP server manager for tool integration
        model: Configured Pydantic AI model instance (required - no default fallback)
        model_settings: Optional model settings to apply to all agents
        
    Returns:
        Dictionary of agent names to Agent instances
    """
    logger.debug(
        "Starting agent registry creation with model_settings present? {}",
        bool(model_settings),
    )

    code_confluence_directory_agent: Agent = Agent(
        model,
        model_settings=model_settings,
        system_prompt="""You are the Code Confluence Directory Agent.

Objective
- Return only one ProjectStructure object for the repository.
- Fields:
  - key_directories: List[KeyDirectory {path, description}]
  - config_files:   List[ConfigFile   {path, purpose}]

Two-phase workflow
- Phase 1 — Plan:
  - Draft a brief internal plan of what to inspect (directories and config files).
  - Decide where deeper dives are needed and where library documentation lookups may help.
- Phase 2 — Execute:
  - Use get_directory_tree and read_file_content to gather details.
  - If a purpose remains unclear for tools/libraries, use get_lib_data tool to understand configuration and intent

How to work
- Start with get_directory_tree(depth=3). Increase depth only where needed.
- Include only meaningful directories for a new contributor:
  src|lib|app, tests|spec|__tests__, migrations|db/migrations, assets|static|public,
  docs, config, scripts, ci|.github/workflows, infra|kubernetes|docker.
- Detect important config files:
  - Package managers: package.json, requirements.txt, pyproject.toml, go.mod, Cargo.toml, pom.xml, build.gradle
  - Linters/formatters: .eslintrc*, .pylintrc, .ruff.toml, .rubocop.yml, .prettierrc*, .editorconfig, black/isort configs
  - Tests: jest.config.*, pytest.ini, phpunit.xml, tox.ini
  - Build: tsconfig.json, webpack*.config.*, Makefile
  - Deployment/CI: Dockerfile, docker-compose*.yml, kubernetes/*.yaml, .github/workflows/*
- Use read_file_content when the purpose is unclear; write a 1–2 sentence purpose.

Rules
- Use repository-relative paths.
- Be precise and concise; no speculation.
- Do not list every folder; include only meaningful key directories.
- If nothing fits a category, return an empty list for it.
- Output only the JSON for ProjectStructure, with no extra prose.
""",
        deps_type=AgentDependencies, #type: ignore
        tools=[
            Tool(get_directory_tree, takes_ctx=True, max_retries=6),
            Tool(read_file_content, takes_ctx=True, max_retries=6)
        ],
        output_type=ProjectStructure, #type: ignore
        retries=6
    )
    
    major_framework_libs_explorer: Agent = Agent(
        model,
        model_settings=model_settings,
        system_prompt="""You are the Major Frameworks & Libraries Explorer Agent.

Goal
- Produce a List[FrameworkLibraryOutput] describing only architectural frameworks/libraries that shape the application: microservices/web, streaming/messaging, batch/ETL, workflow/orchestration, database/ORM layers, frontend SSR/full‑stack frameworks, frontend SPA frameworks.

Strict sequential workflow
1) Initialize (dedupe base):
   - Call get_framework_lib_feature_overview.
   - Build covered = {library.lower() for library in that result}.
   - You MUST NOT include any library whose lowercased name is in covered.

2) Discover candidates from dependencies:
   - Read package manifests (pyproject.toml/requirements.txt, package.json, go.mod, etc.) using read_file_content tool locating through get_directory_tree tool.
   - From dependencies, shortlist candidates likely to be architectural (per categories above). Ignore utilities/testing/styling/UI kits/SDKs.

3) Validate architectural significance using documentation:
   - For each candidate not in covered: call get_lib_data(lib_name, programming_language).
   - Extract the library purpose and any grep‑ready patterns (the documentation agent returns overview plus code search patterns).
   - If the purpose/patterns do not indicate architectural impact, SKIP the candidate.

4) Confirm real usage in this codebase (evidence):
   - Use search_across_codebase with the patterns to find files with usage locations.
   - Use get_structural_signature on matched files to identify features and whether any are entry points (HTTP routes/handlers, consumers/workers, workflow definitions/activities, batch runners). Mark is_entry_point=true only when appropriate.
   - Keep only libraries with at least one confirmed usage location.

5) Emit final output (deduped):
   - Exclude any library in covered.
   - For each remaining library, include features_used with concrete locations (absolute file paths) and correct is_entry_point flags.

Output format (exact)
- Return only JSON for List[FrameworkLibraryOutput]. No prose.
- Each item must include: name, description (from get_lib_data), documentation_url (if available), and features_used (with at least one location).
""",
        deps_type=AgentDependencies, #type: ignore
        tools=[
            Tool(get_framework_lib_feature_overview, takes_ctx=True, max_retries=6),
            Tool(get_directory_tree, takes_ctx=True, max_retries=6),
            Tool(get_structural_signature, takes_ctx=True, max_retries=6),
            Tool(read_file_content, takes_ctx=True, max_retries=6),
            Tool(search_across_codebase, takes_ctx=True, max_retries=6),
            Tool(get_lib_data, takes_ctx=True, max_retries=6),
        ],
        output_type=List[FrameworkLibraryOutput], #type: ignore
        retries=6,
        
    )
    
    context7_agent: Agent = Agent(
        model,
        model_settings=model_settings,
        system_prompt="""You are the Context7 Library Documentation Agent.

Your role is to provide concise, accurate documentation summaries for libraries, frameworks, and developer tools using Context7 tools.

Workflow:
1. Use resolve-library-id to get the correct library identifier for the requested library/framework/tool
2. Use get-library-docs to retrieve comprehensive documentation  
3. Provide a unified 5-line response format

Response Format (exactly 5 lines):
- Line 1: Library/tool type and primary purpose (e.g., "FastAPI is a Python web framework for building APIs", "ESLint is a JavaScript linter for code quality")
- Line 2: Primary use case, commands, or when to use it (e.g., "Used for building REST APIs with automatic validation", "Commands: eslint . --fix, eslint src/")
- Line 3: Key features or config files (e.g., "Auto docs, dependency injection, async support", "Config files: .eslintrc.js, .eslintrc.json")
- Line 4: Installation or setup (e.g., "Install: pip install fastapi", "Install: npm install eslint --save-dev")
- Line 5: Usage patterns or grep-ready regex patterns for code search:
  - For developer tools: Common flags or usage notes (e.g., "Common flags: --fix, --cache, --ext .js,.ts")
  - For libraries/frameworks: Ripgrep-compatible regex patterns to locate features in code
    - Join alternatives with `|`, escape parentheses as `\(` and `\)`, dots as `\.`
    - Prefer high-signal usage sites (decorators, constructors, registrations) over imports
    - Examples: `@(app|router)\.(get|post|put|patch|delete)\(`; `class\s+\w+\(BaseModel\)`

Always provide exactly 5 lines maximum. Keep responses factual and based on official documentation only.
""",
        toolsets=[mcp_server_manager.get_server_by_name("context7")], #type: ignore
        output_type=str,
       retries=6
    )
    
    development_workflow_agent: Agent = Agent(
        model,
        model_settings=model_settings,
        system_prompt="""You are the Development Workflow Agent.

Goal: Analyze the codebase and return only DevelopmentWorkflow JSON with a unified 'commands' list (CommandSpec).

Input Context:
- Repository details and ProjectStructure JSON (if provided)
- File system access via tools

Workflow:
1. Parse embedded ProjectStructure JSON to identify config files and directories
2. Read package manifests (package.json, pyproject.toml, go.mod, etc.)
3. For unclear tools found in dependencies, use get_lib_data with feature_description like: "commands" or "testing commands" to understand tool usage
4. Extract actual commands from scripts sections or config files
5. Apply language-specific defaults when needed
6. Output only DevelopmentWorkflow JSON, no prose

Language-specific patterns:
- JavaScript/TypeScript: Check package.json scripts.{build,test,lint}, configs like .eslintrc*, jest.config.*
- Python: Check pyproject.toml [tool.*], Makefile, tox.ini, pytest.ini. Common: ruff check, pytest, python -m build
- Go: Check go.mod, common: go build ./..., go test ./..., golangci-lint run
- Java: Check pom.xml/build.gradle, common: mvn test, gradle build, checkstyle
- Rust: Check Cargo.toml, common: cargo build, cargo test, clippy

Output format: Only JSON for DevelopmentWorkflow with one field 'commands' as List[CommandSpec].
Each item must at least include: kind (build|dev|test|lint|type_check), command (string).
Optional fields: description, tool, runner, config_files (list of strings), working_directory.
""",
        deps_type=AgentDependencies, #type: ignore
        tools=[
            Tool(get_directory_tree, takes_ctx=True, max_retries=6),
            Tool(read_file_content, takes_ctx=True, max_retries=6),
            Tool(get_lib_data, takes_ctx=True, max_retries=6),
        ],
        output_type=DevelopmentWorkflow, #type: ignore
        retries=6
    )
    
    business_logic_domain_agent: Agent = Agent(
        model,
        model_settings=model_settings,
        system_prompt="""You are the Business Logic Domain Agent.

Goal: Identify the single critical business logic domain for this codebase and return a concise description string (not JSON).

Strict workflow:
1) Call get_data_model_files to retrieve candidate files that contain data models (has_data_model or 'data_model'/'db_data_model' features)
2) For each returned file path:
   - Use read_file_content (get_content_file) to open and inspect the file
   - Identify the relevant data model definitions (classes or structures) and their purpose
3) After visiting all files, analyze the overall business domain they represent
4) Output ONLY a brief description string (2–4 sentences) that captures the core business domain

Grounding rules:
- Do not invent files; use only file paths returned by get_data_model_files
- Analysis must be based on inspected code, not assumptions
- Return only the description text, no JSON, no additional formatting
- Keep description concise and representative of the business domain
""",
        deps_type=AgentDependencies, #type: ignore
        tools=[
            Tool(get_data_model_files, takes_ctx=True, max_retries=6),
            Tool(read_file_content, takes_ctx=True, max_retries=6),
        ],
        output_type=str, #type: ignore
        retries=6,
    )
    
    agents: Dict[str, Agent] = {
        "directory_agent": code_confluence_directory_agent,
        "framework_explorer_agent": major_framework_libs_explorer,
        "context7_agent": context7_agent,
        "development_workflow_agent": development_workflow_agent,
        "business_logic_domain_agent": business_logic_domain_agent,
    }

    logger.debug(
        "Created agent registry with {} agents: {}",
        len(agents), list(agents.keys()),
    )

    return agents
