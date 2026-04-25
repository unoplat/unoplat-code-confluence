"""Shared local-console capability builders for repository agents.

Supports local-console profiles for:
- fully readonly inspection
- read plus execute without modification
- markdown-scoped editing
- markdown-scoped editing plus safe command execution
"""

from __future__ import annotations

from dataclasses import dataclass

from pydantic_ai_backends import OperationPermissions, PermissionRule, PermissionRuleset
from pydantic_ai_backends.capability import ConsoleCapability
from pydantic_ai_backends.permissions.checker import PermissionChecker
from pydantic_ai_backends.permissions.presets import (
    DANGEROUS_COMMANDS,
    SECRETS_PATTERNS,
)
from pydantic_ai_backends.toolsets.console import (
    EDIT_FILE_DESCRIPTION,
    GLOB_DESCRIPTION,
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


READ_AND_EXECUTE_RULESET = PermissionRuleset(
    default="deny",
    read=_read_permissions(),
    write=OperationPermissions(default="deny"),
    edit=OperationPermissions(default="deny"),
    execute=OperationPermissions(
        default="allow",
        rules=_deny_rules(DANGEROUS_COMMANDS, "Block dangerous commands"),
    ),
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
    execute=OperationPermissions(
        default="allow",
        rules=_deny_rules(DANGEROUS_COMMANDS, "Block dangerous commands"),
    ),
    glob=OperationPermissions(default="allow"),
    grep=OperationPermissions(default="allow"),
    ls=OperationPermissions(default="allow"),
)


GLOB_RELATIVE_DESCRIPTION = (
    f"{GLOB_DESCRIPTION}\n\n"
    "IMPORTANT: The `pattern` argument MUST be relative. Never start it with `/`. "
    "Absolute patterns (e.g., `/app/**/*.py`) are rejected by Python 3.13's pathlib "
    "with `NotImplementedError: Non-relative patterns are unsupported`. "
    "To search under a specific directory, set the `path` argument to that directory "
    "and keep the `pattern` relative (e.g., `path=\"/app/src\"`, `pattern=\"**/*.py\"`)."
)


COMMON_TOOL_DESCRIPTIONS: dict[str, str] = {
    "glob": GLOB_RELATIVE_DESCRIPTION,
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


@dataclass
class LocalConsoleCapability(ConsoleCapability):
    """Console capability with stable toolset IDs and explicit permissions."""

    toolset_id: str = ""
    descriptions: dict[str, str] | None = None

    def __post_init__(self) -> None:
        if not self.toolset_id:
            raise ValueError("toolset_id is required for LocalConsoleCapability")
        if self.permissions is None:
            raise ValueError("permissions are required for LocalConsoleCapability")

        self._toolset = create_console_toolset(
            id=self.toolset_id,
            include_execute=self.include_execute,
            edit_format=self.edit_format,
            descriptions=self.descriptions,
            permissions=self.permissions,
        )
        self._checker = PermissionChecker(
            ruleset=self.permissions,
            ask_fallback="deny",
        )


def build_local_console_capability(
    *,
    toolset_id: str,
    include_execute: bool,
    permissions: PermissionRuleset,
    descriptions: dict[str, str] | None = None,
) -> LocalConsoleCapability:
    """Create a local console capability with explicit permissions."""
    return LocalConsoleCapability(
        toolset_id=toolset_id,
        include_execute=include_execute,
        permissions=permissions,
        descriptions=descriptions,
    )


def build_readonly_console_capability(toolset_id: str) -> LocalConsoleCapability:
    """Create a read-only local console capability."""
    return build_local_console_capability(
        toolset_id=toolset_id,
        include_execute=False,
        permissions=READONLY_CONSOLE_RULESET,
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


def build_markdown_execute_console_capability(toolset_id: str) -> LocalConsoleCapability:
    """Create a console capability with safe execute and markdown-only writes."""
    return build_local_console_capability(
        toolset_id=toolset_id,
        include_execute=True,
        permissions=MARKDOWN_READ_WRITE_EXECUTE_RULESET,
        descriptions=MARKDOWN_ONLY_TOOL_DESCRIPTIONS,
    )
