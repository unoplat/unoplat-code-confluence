"""Dynamic system prompts for code confluence agents.

This module provides per-language system prompts that are attached to agents
at runtime based on the codebase's programming language.
"""

from pydantic_ai import RunContext

from unoplat_code_confluence_query_engine.models.runtime.agent_dependencies import (
    AgentDependencies,
)


async def per_programming_language_configuration_prompt(
    ctx: RunContext[AgentDependencies],
) -> str:
    """Generate per-language configuration prompt for project configuration agent.

    Args:
        ctx: Run context containing codebase metadata with programming language.

    Returns:
        Language-specific configuration prompt string.
    """
    common_prompt = (
        f"<task>Given a codebase path for {ctx.deps.codebase_metadata.codebase_programming_language} programming language scan the directory tree for the current codebase and identify important configuration files for development, testing, linting, formatting, packaging, CI/CD, containers, and infrastructure </task>"
        f"<file_path_requirements>"
        f"CRITICAL: When calling read_file_content, get_directory_tree, or any tool that accepts file paths:"
        f"- ALWAYS use ABSOLUTE paths starting with / (e.g., /opt/unoplat/repositories/my-repo/src/config.json)"
        f"- NEVER use relative paths (e.g., config.json, src/file.py, ./package.json)"
        f"- When you find files via search_across_codebase or get_directory_tree, construct absolute paths by combining the codebase root path with relative paths"
        f"- The codebase root path is: {ctx.deps.codebase_metadata.codebase_path}"
        f"</file_path_requirements>"
        f"<output_contract>"
        f"Return ONLY JSON with this exact shape:"
        f'{{"config_files":[{{"path":"<ABSOLUTE_PATH>","purpose":"<10-20 words>"}}]}}'
        f"Rules:"
        f"- Use key 'path' ONLY (never use file_path, absolute_path, or name)"
        f"- Do NOT include extra keys or prose"
        f"- Always include config_files with all relevant entries"
        f"</output_contract>"
        f"<context>"
        f" <categories>"
        f"   <list>dev,test,lint,format,type_checking,styling,ui_components,routing,bundler,package,build,deploy,infrastructure</list>"
        f"   <note>These categories are for your reference only. DO NOT use category labels as the 'purpose' field value.</note>"
        f" </categories>"
        f" <purpose_field_instructions>"
        f"   <rule>The 'purpose' field MUST be a descriptive explanation (10-20 words) of what the configuration file does and its role in the project.</rule>"
        f"   <rule>Base your descriptions ONLY on official documentation obtained via Exa MCP tools (web_search_exa, get_code_context_exa) or actual file inspection via read_file_content.</rule>"
        f"   <rule>NEVER use generic category labels like 'dev', 'test', 'lint', 'packaging' as the purpose value.</rule>"
        f"   <good_example>TypeScript compiler configuration defining build options, module resolution, and type checking rules</good_example>"
        f"   <bad_example>dev</bad_example>"
        f"   <good_example>ESLint configuration for JavaScript/TypeScript linting with rules for code quality and style enforcement</good_example>"
        f"   <bad_example>lint</bad_example>"
        f" </purpose_field_instructions>"
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
        f'<lang name="typescript"><![CDATA['
        f"package.json|package-lock.json|yarn.lock|pnpm-lock.yaml|bun.lockb|"
        f"tsconfig*.json|"
        f".eslintrc*|eslint.config.(js|mjs|cjs|ts)|"
        f".prettier*|prettier.config.*|"
        f"jest.config.*|vitest.config.*|playwright.config.*|cypress.config.*|"
        f"vite.config.*|webpack*.config.*|rollup.config.*|esbuild.config.*|"
        f"tailwind.config.*|postcss.config.*|"
        f"components.json|"
        f"tsr.config.json|"
        f".nvmrc|.node-version|"
        f"nodemon.json|pm2.config.*|ecosystem.config.*|"
        f".husky/**|lint-staged.config.*|"
        f"turbo.json|nx.json|"
        f".storybook/**|storybook.config.*"
        f"]]></lang>"
        f"</context>"
    )

    python_config_prompt = (
        f'<lang name="python"><![CDATA['
        f"pyproject.toml|setup.cfg|setup.py|requirements*.{{txt,in}}|Pipfile|"
        f"tox.ini|pytest.ini|.coveragerc|"
        f".flake8|.pylintrc|mypy.ini|.mypy.ini|pyrightconfig.json|ruff.toml|.ruff.toml|"
        f"noxfile.py"
        f"]]></lang>"
        f"</context>"
    )

    java_config_prompt = (
        f'<lang name="java"><![CDATA['
        f"pom.xml|settings.xml|build.gradle|build.gradle.kts|settings.gradle|gradle.properties|"
        f"checkstyle.xml|pmd.xml|spotbugs*.xml"
        f"]]></lang>"
        f"</context>"
    )

    rust_config_prompt = (
        f'<lang name="rust"><![CDATA['
        f"Cargo.toml|Cargo.lock|"
        f"clippy.toml|rustfmt.toml|.rustfmt.toml|"
        f"]]></lang>"
        f"</context>"
    )

    step_common_prompt = (
        f"<steps>"
        f"<step>Understand directory structure of the codebase based on path provided and get_directory_tree tool.</step>"
        f"<step>Match paths inside the codebase path provided against language_config_globs for provided languages and general_config_globs using search_across_codebase tool and/or get_directory_tree.</step>"
        f"<step>For each matched configuration file, inspect it using read_file_content tool if needed to understand its contents.</step>"
        f"<step>For any configuration file whose purpose is unclear or unfamiliar, MUST use Exa MCP tools (web_search_exa, get_code_context_exa) with the tool/library name and programming language to retrieve official documentation. This ensures accurate descriptions and prevents hallucination.</step>"
        f"<step>Write a descriptive 'purpose' field (10-20 words) for each config file based on official documentation from Exa MCP tools or actual file inspection, following the examples in purpose_field_instructions.</step>"
        f"<step>Produce output JSON exactly as requested; include every relevant config file and never omit the config_files key.</step>"
        f"</steps>"
    )
    if ctx.deps.codebase_metadata.codebase_programming_language == "typescript":
        return (
            common_prompt + "\n" + typescript_config_prompt + "\n" + step_common_prompt
        )
    elif ctx.deps.codebase_metadata.codebase_programming_language == "python":
        return common_prompt + "\n" + python_config_prompt + "\n" + step_common_prompt
    elif ctx.deps.codebase_metadata.codebase_programming_language == "java":
        return common_prompt + "\n" + java_config_prompt + "\n" + step_common_prompt
    elif ctx.deps.codebase_metadata.codebase_programming_language == "rust":
        return common_prompt + "\n" + rust_config_prompt + "\n" + step_common_prompt
    else:
        return common_prompt


async def per_language_development_workflow_prompt(
    ctx: RunContext[AgentDependencies],
) -> str:
    """Generate per-language development workflow prompt.

    Args:
        ctx: Run context containing codebase metadata with programming language.

    Returns:
        Language-specific development workflow prompt string.
    """
    lang = ctx.deps.codebase_metadata.codebase_programming_language

    header = (
        f"You are the Development Workflow Agent for {lang} programming language with package manager {ctx.deps.codebase_metadata.codebase_package_manager}.\n\n"
        "Goal: Analyze the important config files provided by the user and return only DevelopmentWorkflow JSON with a unified 'commands' list.\n\n"
        "Strictly output only JSON, no prose.\n"
    )

    file_path_requirements = (
        "<file_path_requirements>\n"
        "CRITICAL: When calling read_file_content, get_directory_tree, or any tool that accepts file paths:\n"
        "- ALWAYS use ABSOLUTE paths starting with / (e.g., /opt/unoplat/repositories/my-repo/package.json)\n"
        "- NEVER use relative paths (e.g., package.json, src/file.py, ./config.json)\n"
        f"- The codebase root path is: {ctx.deps.codebase_metadata.codebase_path}\n"
        "</file_path_requirements>\n\n"
    )

    steps = (
        "Workflow:\n"
        "1. Extract runnable commands for build/dev/test/lint/type_check from scripts or config based on package manager and user provided config files related to development workflow.\n"
        "2. If a config or the tool be it package manager, linter etc is unclear, use Exa MCP tools (web_search_exa, get_code_context_exa) with feature_description like 'build command' 'dev command' 'testing commands' or 'lint commands' to extract precise commands for that particular tool.\n"
    )

    output_contract = (
        "Output format: DevelopmentWorkflow JSON with a single field 'commands' as a list of CommandSpec.\n"
        "Include all applicable commands; never omit the commands key.\n"
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

    return header + file_path_requirements + steps + output_contract + lang_hints
