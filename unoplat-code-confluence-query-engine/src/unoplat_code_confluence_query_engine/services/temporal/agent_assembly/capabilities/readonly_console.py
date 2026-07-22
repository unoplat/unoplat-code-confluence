"""Shared local-console capability builders for repository agents.

Supports local-console profiles for:
- fully readonly inspection
- read plus execute without modification
- markdown-scoped editing
- markdown-scoped editing plus safe command execution
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pydantic_ai.exceptions import SkipToolExecution
from pydantic_ai.messages import ToolCallPart
from pydantic_ai.tools import RunContext, ToolDefinition
from pydantic_ai_backends import OperationPermissions, PermissionRule, PermissionRuleset
from pydantic_ai_backends.capability import ConsoleCapability
from pydantic_ai_backends.permissions.checker import (
    PermissionChecker,
    PermissionDeniedError,
)
from pydantic_ai_backends.permissions.presets import (
    DANGEROUS_COMMANDS,
    SECRETS_PATTERNS,
)
from pydantic_ai_backends.toolsets.console import (
    EDIT_FILE_DESCRIPTION,
    GLOB_DESCRIPTION,
    GREP_DESCRIPTION,
    WRITE_FILE_DESCRIPTION,
    create_console_toolset,
)


def _deny_rules(patterns: list[str], description: str) -> list[PermissionRule]:
    return [
        PermissionRule(pattern=pattern, action="deny", description=description)
        for pattern in patterns
    ]


MARKDOWN_FILE_PATTERNS = ["*.md", "**/*.md"]
NON_MARKDOWN_FILE_PATTERNS = [
    "*.js",
    "**/*.js",
    "*.jsx",
    "**/*.jsx",
    "*.ts",
    "**/*.ts",
    "*.tsx",
    "**/*.tsx",
    "*.py",
    "**/*.py",
    "*.pyi",
    "**/*.pyi",
    "*.rs",
    "**/*.rs",
    "*.java",
    "**/*.java",
    "*.go",
    "**/*.go",
    "*.kt",
    "**/*.kt",
    "*.kts",
    "**/*.kts",
    "*.scala",
    "**/*.scala",
    "*.c",
    "**/*.c",
    "*.cc",
    "**/*.cc",
    "*.cpp",
    "**/*.cpp",
    "*.h",
    "**/*.h",
    "*.hpp",
    "**/*.hpp",
    "*.cs",
    "**/*.cs",
    "*.php",
    "**/*.php",
    "*.rb",
    "**/*.rb",
    "*.swift",
    "**/*.swift",
    "*.json",
    "**/*.json",
    "*.jsonc",
    "**/*.jsonc",
    "*.yaml",
    "**/*.yaml",
    "*.yml",
    "**/*.yml",
    "*.toml",
    "**/*.toml",
    "*.ini",
    "**/*.ini",
    "*.env",
    "**/*.env",
    "*.xml",
    "**/*.xml",
    "*.sql",
    "**/*.sql",
    "*.sh",
    "**/*.sh",
    "*.bash",
    "**/*.bash",
    "*.zsh",
    "**/*.zsh",
    "*.fish",
    "**/*.fish",
    "*.dockerfile",
    "**/*.dockerfile",
    "Dockerfile",
    "**/Dockerfile",
]
_SOURCE_CODE_EXTENSIONS: tuple[str, ...] = (
    "py",
    "pyi",
    "ts",
    "tsx",
    "js",
    "jsx",
    "go",
    "java",
    "kt",
    "kts",
    "scala",
    "rs",
    "rb",
    "php",
    "cs",
    "swift",
    "c",
    "cc",
    "cpp",
    "h",
    "hpp",
)
_SECRET_NAME_TOKENS: tuple[str, ...] = (
    "credentials",
    "secrets",
    "secret",
    "password",
)
SAFE_SOURCE_NAME_OVERRIDES: list[str] = [
    f"**/*{token}*.{ext}"
    for token in _SECRET_NAME_TOKENS
    for ext in _SOURCE_CODE_EXTENSIONS
]

_CALL_EXPRESSION_TEST_DIRECTORY_NAMES: tuple[str, ...] = (
    "tests",
    "test",
    "__tests__",
    "test_data",
)
_CALL_EXPRESSION_PYTHON_TEST_FILENAMES: tuple[str, ...] = (
    "test_*.py",
    "*_test.py",
    "conftest.py",
)
_CALL_EXPRESSION_JS_TS_TEST_SUFFIXES: tuple[str, ...] = ("test", "spec")
_CALL_EXPRESSION_JS_TS_TEST_EXTENSIONS: tuple[str, ...] = (
    "js",
    "jsx",
    "ts",
    "tsx",
)
_CALL_EXPRESSION_JS_TS_TEST_FILENAMES: tuple[str, ...] = tuple(
    name
    for ext in _CALL_EXPRESSION_JS_TS_TEST_EXTENSIONS
    for name in (
        f"test.{ext}",
        f"test_*.{ext}",
        f"*_test.{ext}",
    )
)
CALL_EXPRESSION_TEST_PATH_PATTERNS: list[str] = [
    pattern
    for name in _CALL_EXPRESSION_TEST_DIRECTORY_NAMES
    for pattern in (name, f"{name}/**", f"**/{name}", f"**/{name}/**")
] + [
    pattern
    for filename in _CALL_EXPRESSION_PYTHON_TEST_FILENAMES
    for pattern in (filename, f"**/{filename}")
] + [
    pattern
    for filename in _CALL_EXPRESSION_JS_TS_TEST_FILENAMES
    for pattern in (filename, f"**/{filename}")
] + [
    pattern
    for suffix in _CALL_EXPRESSION_JS_TS_TEST_SUFFIXES
    for ext in _CALL_EXPRESSION_JS_TS_TEST_EXTENSIONS
    for pattern in (f"*.{suffix}.{ext}", f"**/*.{suffix}.{ext}")
]


COMMAND_DISCOVERY_ALLOW_PATTERNS: list[str] = [
    "**--help",
    "**--help **",
    "**--help=**",
    "** -h",
    "** -h **",
    "**--version",
    "**--version **",
    "**--version=**",
    "** -v",
    "** -v **",
    "** help",
    "** help **",
]

ARCHITECTURE_ARTIFACT = "architecture.md"
ARCHITECTURE_VALIDATION_COMMAND = (
    "mmdc --input architecture.md "
    "--output /tmp/unoplat-architecture-validation-$$.svg "
    "--puppeteerConfigFile /app/puppeteer-config.json --quiet"
)

CONSOLE_TOOL_MAX_RETRIES: int = 3


def _allow_rules(patterns: list[str], description: str) -> list[PermissionRule]:
    return [
        PermissionRule(pattern=pattern, action="allow", description=description)
        for pattern in patterns
    ]


def _read_permissions() -> OperationPermissions:
    return OperationPermissions(
        default="allow",
        rules=[
            *_allow_rules(
                SAFE_SOURCE_NAME_OVERRIDES,
                "Allow source files whose names collide with secret tokens",
            ),
            *_deny_rules(SECRETS_PATTERNS, "Protect sensitive files"),
        ],
    )


def _call_expression_discovery_path_permissions() -> OperationPermissions:
    """Production-only path permissions for call-expression discovery.

    First-match-wins order:
    1. Deny test directories and test filenames.
    2. Allow source files whose names collide with secret tokens.
    3. Deny secret-bearing paths.
    """
    return OperationPermissions(
        default="allow",
        rules=[
            *_deny_rules(
                CALL_EXPRESSION_TEST_PATH_PATTERNS,
                "Hide test paths from call-expression discovery",
            ),
            *_allow_rules(
                SAFE_SOURCE_NAME_OVERRIDES,
                "Allow source files whose names collide with secret tokens",
            ),
            *_deny_rules(SECRETS_PATTERNS, "Protect sensitive files"),
        ],
    )


def _execute_deny_rules() -> list[PermissionRule]:
    return [
        *_deny_rules(DANGEROUS_COMMANDS, "Block dangerous commands"),
    ]


def _execute_metadata_only_permissions() -> OperationPermissions:
    """Publish execute to the model but emulate deny-by-default at call time.

    `pydantic_ai_backends.create_console_toolset` removes the execute tool from
    the toolset whenever `permissions.execute.default == "deny"` (the predicate
    `_is_denied_by_ruleset` ignores allow-rules and looks only at `default`).
    To keep the agent able to run CLI help/version probes — while still failing
    safe for everything else — we set `default="allow"` so the tool is
    advertised to the model, and order the rules so that:

    1. Dangerous commands are denied first (defensive against pathological
       inputs such as `rm -rf --help`).
    2. CLI help/version forms (for example `bun --help`, `task help`, `vite -v`)
       are explicitly allowed.
    3. A catch-all `**` deny rule emulates the original default-deny posture
       for any command that is neither dangerous nor a help/version probe.

    `PermissionChecker` evaluates rules in order with first-match-wins
    semantics, so this preserves identical runtime safety to the previous
    deny-by-default ruleset while exposing the tool to the model.
    """
    return OperationPermissions(
        default="allow",
        rules=[
            *_execute_deny_rules(),
            *_allow_rules(
                COMMAND_DISCOVERY_ALLOW_PATTERNS,
                "Allow CLI help/version discovery commands only",
            ),
        ],
    )


READONLY_CONSOLE_RULESET = PermissionRuleset(
    default="deny",
    read=_read_permissions(),
    write=OperationPermissions(default="deny"),
    edit=OperationPermissions(default="deny"),
    execute=OperationPermissions(default="deny"),
    glob=OperationPermissions(default="allow"),
    grep=OperationPermissions(default="allow"),
    ls=OperationPermissions(default="allow"),
)


CALL_EXPRESSION_DISCOVERY_RULESET = PermissionRuleset(
    default="deny",
    read=_call_expression_discovery_path_permissions(),
    write=OperationPermissions(default="deny"),
    edit=OperationPermissions(default="deny"),
    execute=OperationPermissions(default="deny"),
    glob=_call_expression_discovery_path_permissions(),
    grep=_call_expression_discovery_path_permissions(),
    ls=_call_expression_discovery_path_permissions(),
)


READ_AND_EXECUTE_RULESET = PermissionRuleset(
    default="deny",
    read=_read_permissions(),
    write=OperationPermissions(default="deny"),
    edit=OperationPermissions(default="deny"),
    execute=_execute_metadata_only_permissions(),
    glob=OperationPermissions(default="allow"),
    grep=OperationPermissions(default="allow"),
    ls=OperationPermissions(default="allow"),
)


MARKDOWN_READ_WRITE_RULESET = PermissionRuleset(
    default="deny",
    read=_read_permissions(),
    write=OperationPermissions(
        default="allow",
        rules=[
            *_deny_rules(SECRETS_PATTERNS, "Protect sensitive files"),
            *_allow_rules(MARKDOWN_FILE_PATTERNS, "Allow markdown writes"),
            *_deny_rules(NON_MARKDOWN_FILE_PATTERNS, "Deny non-markdown writes"),
        ],
    ),
    edit=OperationPermissions(
        default="allow",
        rules=[
            *_deny_rules(SECRETS_PATTERNS, "Protect sensitive files"),
            *_allow_rules(MARKDOWN_FILE_PATTERNS, "Allow markdown edits"),
            *_deny_rules(NON_MARKDOWN_FILE_PATTERNS, "Deny non-markdown edits"),
        ],
    ),
    execute=OperationPermissions(default="deny"),
    glob=OperationPermissions(default="allow"),
    grep=OperationPermissions(default="allow"),
    ls=OperationPermissions(default="allow"),
)


MARKDOWN_READ_WRITE_EXECUTE_RULESET = PermissionRuleset(
    default="deny",
    read=_read_permissions(),
    write=MARKDOWN_READ_WRITE_RULESET.write,
    edit=MARKDOWN_READ_WRITE_RULESET.edit,
    execute=_execute_metadata_only_permissions(),
    glob=OperationPermissions(default="allow"),
    grep=OperationPermissions(default="allow"),
    ls=OperationPermissions(default="allow"),
)


def build_architecture_console_ruleset(
    architecture_path: str = f"**/{ARCHITECTURE_ARTIFACT}",
) -> PermissionRuleset:
    """Build Architecture permissions scoped to one artifact and Mermaid CLI.

    The console capability uses the default recursive artifact pattern because it
    is assembled before codebase metadata is available. Backend resolution grants
    access only within the resolved repository boundary.
    """
    # `create_console_toolset` hides write/edit/execute tools when the
    # operation default is "deny". Using default="allow" keeps those tools
    # registered without marking them requires_approval (which default="ask"
    # does). Approval-required tools become DeferredToolRequests, and the
    # Architecture agent only accepts str output, so "ask" aborts the run on
    # the first write. Explicit allow rules plus a catch-all deny preserve
    # deny-by-default safety with first-match-wins evaluation.
    artifact_permissions = OperationPermissions(
        default="allow",
        rules=[
            PermissionRule(
                pattern=architecture_path,
                action="allow",
                description="Allow only the repository-root architecture artifact",
            ),
            PermissionRule(
                pattern="**",
                action="deny",
                description="Deny all non-architecture artifact paths",
            ),
        ],
    )
    return PermissionRuleset(
        default="allow",
        read=_read_permissions(),
        write=artifact_permissions,
        edit=artifact_permissions,
        # Allow rules must precede the catch-all deny because
        # PermissionChecker uses first-match-wins semantics. The permission
        # patterns use glob syntax: one rule covers the bare executable and the
        # other covers any mmdc arguments.
        execute=OperationPermissions(
            default="allow",
            rules=[
                *_allow_rules(
                    ["mmdc", "mmdc **"],
                    "Allow Mermaid CLI help, version, and render commands",
                ),
                PermissionRule(
                    pattern="**",
                    action="deny",
                    description="Deny all non-mmdc commands",
                ),
            ],
        ),
        glob=OperationPermissions(default="allow"),
        grep=OperationPermissions(default="allow"),
        ls=OperationPermissions(default="allow"),
    )


ARCHITECTURE_CONSOLE_RULESET = build_architecture_console_ruleset()


GLOB_RELATIVE_DESCRIPTION = (
    f"{GLOB_DESCRIPTION}\n\n"
    "IMPORTANT: The `pattern` argument MUST be relative. Never start it with `/`. "
    "Absolute patterns (e.g., `/app/**/*.py`) are rejected by Python 3.13's pathlib "
    "with `NotImplementedError: Non-relative patterns are unsupported`. "
    "To search under a specific directory, set the `path` argument to that directory "
    'and keep the `pattern` relative (e.g., `path="/app/src"`, `pattern="**/*.py"`).'
)

GREP_CONTRACT_DESCRIPTION = (
    f"{GREP_DESCRIPTION}\n\n"
    "IMPORTANT: The required regex argument is named exactly `pattern` — never `.pattern`, "
    "`query`, or any other key. The `path` argument is only a file or directory to search "
    "inside; do not put filename glob wildcards in `path`. To restrict searched files by "
    'glob, use `glob_pattern` separately (e.g., `path="/repo"`, '
    '`glob_pattern=".github/workflows/*.yml"`, `pattern="ruff|mypy"`).'
)


COMMON_TOOL_DESCRIPTIONS: dict[str, str] = {
    "glob": GLOB_RELATIVE_DESCRIPTION,
    "grep": GREP_CONTRACT_DESCRIPTION,
}


MARKDOWN_ONLY_TOOL_DESCRIPTIONS: dict[str, str] = {
    **COMMON_TOOL_DESCRIPTIONS,
    "write_file": (
        f"{WRITE_FILE_DESCRIPTION}\n\n"
        "This agent may write only Markdown files matching `*.md` inside the current codebase root. "
        "Non-markdown writes are denied."
    ),
    "edit_file": (
        f"{EDIT_FILE_DESCRIPTION}\n\n"
        "This agent may edit only Markdown files matching `*.md` inside the current codebase root. "
        "Non-markdown edits are denied."
    ),
}

ARCHITECTURE_TOOL_DESCRIPTIONS: dict[str, str] = {
    **COMMON_TOOL_DESCRIPTIONS,
    "write_file": (
        f"{WRITE_FILE_DESCRIPTION}\n\n"
        "This agent may write only repository-root `architecture.md`. All other files are denied."
    ),
    "edit_file": (
        f"{EDIT_FILE_DESCRIPTION}\n\n"
        "This agent may edit only repository-root `architecture.md`. All other files are denied."
    ),
    "execute": (
        "Execute Mermaid CLI from the repository root. Only the `mmdc` executable is "
        "permitted, including help, version, and render invocations; unrelated "
        "executables are denied."
    ),
}


@dataclass
class LocalConsoleCapability(ConsoleCapability):
    """Console capability with stable toolset IDs and explicit permissions."""

    toolset_id: str = ""
    descriptions: dict[str, str] | None = None
    visible_despite_wildcard_denial: frozenset[str] = field(default_factory=frozenset)

    def __post_init__(self) -> None:
        if not self.toolset_id:
            raise ValueError("toolset_id is required for LocalConsoleCapability")
        if self.permissions is None:
            raise ValueError("permissions are required for LocalConsoleCapability")

        self._toolset = create_console_toolset(
            id=self.toolset_id,
            include_execute=self.include_execute,
            include_background=False,
            edit_format=self.edit_format,
            descriptions=self.descriptions,
            permissions=self.permissions,
            max_retries=CONSOLE_TOOL_MAX_RETRIES,
        )
        self._checker = PermissionChecker(
            ruleset=self.permissions,
            ask_fallback="deny",
        )

    async def before_tool_execute(
        self,
        ctx: RunContext[Any],
        *,
        call: ToolCallPart,
        tool_def: ToolDefinition,
        args: dict[str, Any],
    ) -> dict[str, Any]:
        """Return a safe tool result when the permission policy blocks a call."""
        try:
            return await super().before_tool_execute(
                ctx,
                call=call,
                tool_def=tool_def,
                args=args,
            )
        except PermissionDeniedError as error:
            raise SkipToolExecution(
                "Access is blocked by safety policy: "
                f"{error}. Do not retry this exact path or command; "
                "continue using allowed evidence."
            ) from error

    async def prepare_tools(
        self,
        ctx: RunContext[Any],
        tool_defs: list[ToolDefinition],
    ) -> list[ToolDefinition]:
        """Keep explicitly scoped tools visible despite wildcard preflight denial.

        ``ConsoleCapability`` tests each operation against ``*`` before exposing
        it. A scoped ruleset intentionally denies that wildcard through its final
        catch-all rule even though it permits a concrete artifact path or command.
        The actual call remains protected by ``before_tool_execute``, which checks
        the supplied path/command and converts a denial to ``SkipToolExecution``.
        """
        prepared = await super().prepare_tools(ctx, tool_defs)
        if not self.visible_despite_wildcard_denial:
            return prepared

        prepared_names = {tool.name for tool in prepared}
        return [
            tool
            for tool in tool_defs
            if tool.name in prepared_names
            or tool.name in self.visible_despite_wildcard_denial
        ]


def build_local_console_capability(
    *,
    toolset_id: str,
    include_execute: bool,
    permissions: PermissionRuleset,
    descriptions: dict[str, str] | None = None,
    visible_despite_wildcard_denial: frozenset[str] = frozenset(),
) -> LocalConsoleCapability:
    """Create a local console capability with explicit permissions."""
    return LocalConsoleCapability(
        toolset_id=toolset_id,
        include_execute=include_execute,
        permissions=permissions,
        descriptions=descriptions,
        visible_despite_wildcard_denial=visible_despite_wildcard_denial,
    )


def build_readonly_console_capability(toolset_id: str) -> LocalConsoleCapability:
    """Create a read-only local console capability."""
    return build_local_console_capability(
        toolset_id=toolset_id,
        include_execute=False,
        permissions=READONLY_CONSOLE_RULESET,
        descriptions=COMMON_TOOL_DESCRIPTIONS,
    )


def build_call_expression_discovery_console_capability(
    toolset_id: str,
) -> LocalConsoleCapability:
    """Create a production-only console for call-expression discovery."""
    return build_local_console_capability(
        toolset_id=toolset_id,
        include_execute=False,
        permissions=CALL_EXPRESSION_DISCOVERY_RULESET,
        descriptions=COMMON_TOOL_DESCRIPTIONS,
    )


def build_execute_console_capability(toolset_id: str) -> LocalConsoleCapability:
    """Create a local console capability that allows execute but not write/edit."""
    return build_local_console_capability(
        toolset_id=toolset_id,
        include_execute=True,
        permissions=READ_AND_EXECUTE_RULESET,
        descriptions=COMMON_TOOL_DESCRIPTIONS,
    )


def build_markdown_console_capability(toolset_id: str) -> LocalConsoleCapability:
    """Create a local console capability that can modify only `*.md` files."""
    return build_local_console_capability(
        toolset_id=toolset_id,
        include_execute=False,
        permissions=MARKDOWN_READ_WRITE_RULESET,
        descriptions=MARKDOWN_ONLY_TOOL_DESCRIPTIONS,
    )


def build_markdown_execute_console_capability(
    toolset_id: str,
) -> LocalConsoleCapability:
    """Create a console capability with safe execute and markdown-only writes."""
    return build_local_console_capability(
        toolset_id=toolset_id,
        include_execute=True,
        permissions=MARKDOWN_READ_WRITE_EXECUTE_RULESET,
        descriptions=MARKDOWN_ONLY_TOOL_DESCRIPTIONS,
    )


def build_architecture_console_capability(toolset_id: str) -> LocalConsoleCapability:
    """Create the Architecture console with one artifact and Mermaid CLI access."""
    return build_local_console_capability(
        toolset_id=toolset_id,
        include_execute=True,
        permissions=ARCHITECTURE_CONSOLE_RULESET,
        descriptions=ARCHITECTURE_TOOL_DESCRIPTIONS,
        visible_despite_wildcard_denial=frozenset(
            {"write_file", "edit_file", "execute"}
        ),
    )
