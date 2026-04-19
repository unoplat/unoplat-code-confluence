"""Readonly local-console capability for the business domain agent.

Provides filesystem browsing (ls, read_file, glob, grep) with
``READONLY_RULESET`` permissions.  Write, edit, and execute operations
are denied and their tools are hidden from the model.
"""

from __future__ import annotations

from dataclasses import dataclass

from pydantic_ai_backends.capability import ConsoleCapability
from pydantic_ai_backends.permissions.checker import PermissionChecker
from pydantic_ai_backends.permissions.presets import READONLY_RULESET
from pydantic_ai_backends.toolsets.console import create_console_toolset

from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.constants import (
    BUSINESS_DOMAIN_CONSOLE_TOOLSET_ID,
)


@dataclass
class ReadonlyConsoleCapability(ConsoleCapability):
    """Console capability restricted to read-only filesystem operations.

    Overrides ``__post_init__`` to assign a stable Temporal-safe toolset
    ID and enforce ``READONLY_RULESET`` via ``PermissionChecker``.
    """

    def __post_init__(self) -> None:
        self._toolset = create_console_toolset(
            id=BUSINESS_DOMAIN_CONSOLE_TOOLSET_ID,
            include_execute=False,
        )
        self._checker = PermissionChecker(
            ruleset=READONLY_RULESET,
            ask_fallback="deny",
        )


def build_readonly_console_capability() -> ReadonlyConsoleCapability:
    """Create a :class:`ReadonlyConsoleCapability` for the business domain agent."""
    return ReadonlyConsoleCapability(
        include_execute=False,
        permissions=READONLY_RULESET,
    )
