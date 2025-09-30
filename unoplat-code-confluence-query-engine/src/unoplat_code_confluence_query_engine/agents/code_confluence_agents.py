from typing import Any, Dict, Optional

from loguru import logger
from pydantic_ai import Agent, RunContext, Tool
from pydantic_ai.models import Model
from pydantic_ai.settings import ModelSettings

from unoplat_code_confluence_query_engine.models.agent_dependencies import (
    AgentDependencies,
)
from unoplat_code_confluence_query_engine.models.agent_md_output import (
    BusinessLogicDomain,
    DevelopmentWorkflow,
    ProjectConfiguration,
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
from unoplat_code_confluence_query_engine.tools.get_lib_data import get_lib_data
from unoplat_code_confluence_query_engine.tools.search_across_codebase import (
    search_across_codebase,
)

    # pyright: ignore[reportUndefinedVariable]
    

def create_code_confluence_agents(mcp_server_manager: MCPServerManager, model: Model, model_settings: Optional[ModelSettings] = None) -> Dict[str, Agent[Any]]:
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
    

    
    code_confluence_project_configuration_agent: Agent[AgentDependencies] = Agent(
        model,
        model_settings=model_settings,
        system_prompt="<role> Build/CI/Test/Lint/Type Configuration Locator</role>",
        deps_type=AgentDependencies, #type: ignore
        tools=[
            Tool(get_directory_tree, takes_ctx=True, max_retries=6),
            Tool(read_file_content, takes_ctx=True, max_retries=6),
            Tool(search_across_codebase, takes_ctx=True, max_retries=6)
        ],
        output_type=ProjectConfiguration, 
        retries=6
    )

    # Attach dynamic per-language system prompt for configuration
    try:
        code_confluence_project_configuration_agent.system_prompt(
            per_programming_language_configuration_prompt
        )
    except NameError:
        # Function is defined later in the module; safe to ignore if not yet bound at import time
        pass
    
      
    context7_agent: Agent[None] = Agent(
        model,
        model_settings=model_settings,
        system_prompt=r"""You are the Context7 Library Documentation Agent.

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
    
    development_workflow_agent: Agent[AgentDependencies] = Agent(
        model,
        model_settings=model_settings,
        system_prompt="<role> Development Workflow Synthesizer</role>",
        deps_type=AgentDependencies, #type: ignore
        tools=[
            Tool(get_directory_tree, takes_ctx=True, max_retries=6),
            Tool(read_file_content, takes_ctx=True, max_retries=6),
            Tool(get_lib_data, takes_ctx=True, max_retries=6),
        ],
        output_type=DevelopmentWorkflow, #type: ignore
        retries=6
    )

    # Attach dynamic per-language system prompt for development workflow
    try:
        development_workflow_agent.system_prompt(
            per_language_development_workflow_prompt
        )
    except NameError:
        pass
    
    business_logic_domain_agent: Agent[AgentDependencies] = Agent(
        model,
        model_settings=model_settings,
        system_prompt=r"""You are the Business Logic Domain Agent.

Goal: Identify the single critical business logic domain for this codebase and return strictly BusinessLogicDomain JSON.

Strict workflow:
1) Call get_data_model_files to retrieve candidate files that contain data models (both application and database data models)
2) Create a coverage checklist from ALL returned file paths and process UNTIL NONE REMAIN:
   - Maintain two lists: remaining_files (to do) and processed_files (done). Do not produce final output until remaining_files is empty.
   - For each file in remaining_files, do:
   - Use read_file_content (get_content_file) to open and inspect the file
   - Identify the relevant data model definitions (classes or structures) and their purpose
   - Record a short responsibility per file when clear; if uncertain after inspection, set responsibility to null (but still include the file)
   - Move the file from remaining_files to processed_files and continue
   - If the file is very large, read only the portions with definitions (e.g., class, dataclass, BaseModel, @Entity, schema) and proceed
   - If a tool call fails, retry up to 2 times; on persistent failure, include the file with responsibility=null
3) After visiting ALL files (remaining_files must be empty), analyze the overall business domain they represent
4) Output ONLY valid BusinessLogicDomain JSON with fields:
   - description: 2–4 sentences summarizing the domain nouns, core processes, and primary purpose
   - data_models: list of { path, responsibility } that includes EVERY path returned by get_data_model_files (responsibility may be null if uncertain)
   - Sort data_models by path ascending for determinism

Grounding rules:
- Do not invent files; use only file paths returned by get_data_model_files
- Analysis must be based on inspected code, not assumptions
- Output must be valid JSON with exactly the required fields. No extra fields or prose.
""",
        deps_type=AgentDependencies, #type: ignore
        tools=[
            Tool(get_data_model_files, takes_ctx=True, max_retries=6),
            Tool(read_file_content, takes_ctx=True, max_retries=6),
        ],
        output_type=BusinessLogicDomain,
        retries=6,
    )
    
    agents: Dict[str, Agent[Any]] = {
        "project_configuration_agent": code_confluence_project_configuration_agent,
        "development_workflow_agent": development_workflow_agent,
        "context7_agent": context7_agent,
        "business_logic_domain_agent": business_logic_domain_agent,
    }

    logger.debug(
        "Created agent registry with {} agents: {}",
        len(agents), list(agents.keys()),
    )

    return agents

def per_programming_language_configuration_prompt(ctx: RunContext[AgentDependencies]) -> str:
    
    common_prompt = (
        f"<task>Given a codebase path for {ctx.deps.codebase_metadata.codebase_programming_language} programming language scan the directory tree for the current codebase and identify important configuration files for development, testing, linting, formatting, packaging, CI/CD, containers, and infrastructure </task>"
        f"<context>"
        f" <categories>"
        f"   <list>dev,test,lint,format,package,build,deploy,infrastructure</list>"
        f" </categories>"
        f"  <general_config_globs><![CDATA["
        f".editorconfig|.gitignore|.gitattributes|.pre-commit-config.y*|Makefile|Justfile|Taskfile.y*ml|"
        f"Dockerfile*|.dockerignore|docker-compose.y*ml|"
        f".github/workflows/*.y*ml|.gitlab-ci.y*ml|.circleci/config.y*ml|azure-pipelines.y*ml|"
        f"renovate*.json|.renovaterc.*|.dependabot/config.y*ml|.github/dependabot.y*ml|"
        f"sonar-project.properties|.snyk|.license*|LICENSE|"
        f"k8s/**.y*ml|kubernetes/**.y*ml|charts/**|Chart.yaml|values*.y*ml|"
        f"terraform/*.tf|**/.terraform.lock.hcl|ansible.cfg|**/playbooks/**.y*ml|"
        f"serverless.(y*ml|ts)|template.y*ml|samconfig.toml"
        f"]]></general_config_globs>"
    )
    
    typescript_config_prompt = (
        f"<lang name=\"javascript typescript\"><![CDATA["
        f"package.json|package-lock.json|yarn.lock|pnpm-lock.yaml|bun.lockb|"
        f"tsconfig*.json|jsconfig.json|"
        f".eslintrc*|eslint.config.(js|mjs|cjs|ts)|"
        f".prettier*|prettier.config.*|"
        f"jest.config.*|vitest.config.*|karma.conf.*|.mocharc.*|nyc.config.*|.nycrc*|"
        f"babel.config.*|.babelrc*|"
        f"webpack*.config.*|rollup.config.*|vite.config.*|"
        f"cypress.config.*|cypress.json|playwright.config.*|"
        f"nodemon.json|ecosystem.config.*|.nvmrc|.husky/**"
        f"]]></lang>"
        f"</context>"
    )
    
    python_config_prompt = (
        f"<lang name=\"python\"><![CDATA["
        f"pyproject.toml|setup.cfg|setup.py|requirements*.{{txt,in}}|Pipfile|"
        f"tox.ini|pytest.ini|.coveragerc|"
        f".flake8|.pylintrc|mypy.ini|.mypy.ini|pyrightconfig.json|ruff.toml|.ruff.toml|"
        f"noxfile.py"
        f"]]></lang>"
        f"</context>"
    )
    
    java_config_prompt = (
        f"<lang name=\"java\"><![CDATA["
        f"pom.xml|settings.xml|build.gradle|build.gradle.kts|settings.gradle|gradle.properties|"
        f"checkstyle.xml|pmd.xml|spotbugs*.xml"
        f"]]></lang>"
        f"</context>"
    )
    
    rust_config_prompt = (
        f"<lang name=\"rust\"><![CDATA["
        f"Cargo.toml|Cargo.lock|"
        f"clippy.toml|rustfmt.toml|.rustfmt.toml|"
        f"]]></lang>"
        f"</context>"
    )
    
    step_common_prompt = (
        f"<steps>"
        f"<step>Understand directory structure of the codebase based on path provided and get_directory_Tree tool.</step>"
        f"<step>Match paths inside the codebase path provided against language_config_globs for provided languages and general_config_globs using search_across_codebase tool and/or get_directory_tree </step>"
        f"<step>Be very certain post matches found read the files using read_file_content tool if required."
        f"<step>Produce output JSON exactly as requested.</step>"
        f"</steps>"
    )
    if ctx.deps.codebase_metadata.codebase_programming_language == "javascript" or ctx.deps.codebase_metadata.codebase_programming_language == "typescript":
        return common_prompt + "\n" + typescript_config_prompt + "\n" + step_common_prompt
    elif ctx.deps.codebase_metadata.codebase_programming_language == "python":
        return common_prompt + "\n" + python_config_prompt + "\n" + step_common_prompt
    elif ctx.deps.codebase_metadata.codebase_programming_language == "java":
        return common_prompt + "\n" + java_config_prompt + "\n" + step_common_prompt
    elif ctx.deps.codebase_metadata.codebase_programming_language == "rust":
        return common_prompt + "\n" + rust_config_prompt + "\n" + step_common_prompt
    else:
        return common_prompt


def per_language_development_workflow_prompt(ctx: RunContext[AgentDependencies]) -> str:
    lang = ctx.deps.codebase_metadata.codebase_programming_language

    header = (
        f"You are the Development Workflow Agent for {lang} programming language with package manager {ctx.deps.codebase_metadata.codebase_package_manager}.\n\n"
        "Goal: Analyze the important config files provided by the user and return only DevelopmentWorkflow JSON with a unified 'commands' list.\n\n"
        "Strictly output only JSON, no prose.\n"
    )

    steps = (
        "Workflow:\n"
        "1. Extract runnable commands for build/dev/test/lint/type_check from scripts or config based on package manager and user provided config files related to development workflow.\n"
        "2. If a config or the tool be it package manager, linter etc is unclear, call get_lib_data with feature_description like 'build command' 'dev command' 'testing commands' or 'lint commands' to extract precise commands for that particular tool.\n"
    )

    output_contract = (
        "Output format: DevelopmentWorkflow JSON with a single field 'commands' as a list of CommandSpec.\n"
        "Each CommandSpec must include: kind (build|dev|test|lint|type_check), command (string). Optional: description, config_files[].\n\n"
    )

    if lang in ("javascript", "typescript"):
        lang_hints = (
            "JavaScript/TypeScript hints:\n"
            "- Primary: package.json scripts.{build,dev,start,test,lint,typecheck}.\n"
            "- Configs: tsconfig*.json, eslint.config.*|.eslintrc*, prettier*, jest|vitest|playwright|cypress configs, vite|webpack|rollup configs.\n"
            "- Common commands: vite build, next build, tsc -b, eslint . --max-warnings 0, vitest run, jest --ci.\n"
        )
    elif lang == "python":
        lang_hints = (
            "Python hints:\n"
            "- Manifests/configs: pyproject.toml [tool.pytest, tool.ruff, tool.mypy], tox.ini, pytest.ini, ruff.toml, mypy.ini, Makefile.\n"
            "- Common commands: python -m build, pytest -q, ruff check ., mypy .\n"
        )
    elif lang == "go":
        lang_hints = (
            "Go hints:\n"
            "- Manifests: go.mod; Common: go build ./..., go test ./..., golangci-lint run.\n"
        )
    elif lang == "java":
        lang_hints = (
            "Java hints:\n"
            "- Maven/Gradle: pom.xml or build.gradle(.kts); Common: mvn -q -DskipTests=false test, mvn -q package, gradle build, gradle test, checkstyle/spotbugs tasks.\n"
        )
    elif lang == "rust":
        lang_hints = (
            "Rust hints:\n"
            "- Cargo.toml; Common: cargo build, cargo test, cargo clippy -- -D warnings.\n"
        )
    else:
        lang_hints = ""

    return header + steps + output_contract + lang_hints
