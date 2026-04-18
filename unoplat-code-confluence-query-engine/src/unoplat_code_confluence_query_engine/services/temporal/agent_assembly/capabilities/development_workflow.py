"""Audited console capability for the development workflow agent.

Wraps upstream ``ConsoleCapability`` with ``STRICT_RULESET`` and an
auto-approve callback that logs every permission decision via loguru.
"""

from __future__ import annotations

from dataclasses import dataclass

from loguru import logger
from pydantic_ai_backends.capability import ConsoleCapability
from pydantic_ai_backends.permissions.checker import PermissionChecker
from pydantic_ai_backends.permissions.presets import STRICT_RULESET
from pydantic_ai_backends.toolsets.console import EditFormat, create_console_toolset

from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.constants import (
    DEVELOPMENT_WORKFLOW_CONSOLE_TOOLSET_ID,
)


async def auto_approve_with_logging(operation: str, target: str, reason: str) -> bool:
    """Auto-approve a permission request and log the decision.

    This callback is invoked by :class:`PermissionChecker` whenever the
    ruleset action for an operation is ``"ask"``.  It always returns
    ``True`` (approve) but records the operation, target, and reason so
    that every sandbox interaction is auditable.
    """
    logger.info(
        "Auto-approved console operation: {} on '{}' (reason: {})",
        operation,
        target,
        reason if reason else "none",
    )
    return True


@dataclass
class AuditedConsoleCapability(ConsoleCapability):
    """Console capability with strict permissions and audit logging.

    Subclasses :class:`ConsoleCapability` to override the permission
    checker with ``STRICT_RULESET`` + :func:`auto_approve_with_logging`.
    All console tool invocations pass through the checker, ensuring every
    operation is logged regardless of whether the ruleset would normally
    allow it silently.
    """

    def __post_init__(self) -> None:
        """Build a Temporal-safe console toolset and audited permission checker.

        Tool-level deferred approvals are intentionally disabled here. The
        development workflow agent must complete in a single run with a final
        ``EngineeringWorkflow`` output, while sandbox permission decisions are
        still enforced and logged by ``PermissionChecker`` below.
        """
        self._toolset = create_console_toolset(
            id=DEVELOPMENT_WORKFLOW_CONSOLE_TOOLSET_ID,
            include_execute=self.include_execute,
            require_execute_approval=False,
            edit_format=self.edit_format,
        )
        self._checker = PermissionChecker(
            ruleset=STRICT_RULESET,
            ask_callback=auto_approve_with_logging,
            ask_fallback="error",
        )


def build_audited_console_capability(
    *,
    include_execute: bool = True,
    edit_format: EditFormat = "str_replace",
) -> AuditedConsoleCapability:
    """Create an :class:`AuditedConsoleCapability` for agent assembly.

    This factory is the public entry-point that step-5 agent wiring will
    call.  Keeping it separate from the class allows callers to stay
    decoupled from the dataclass constructor.

    Args:
        include_execute: Whether the ``execute`` tool is available.
        edit_format: Edit format passed through to the console toolset.

    Returns:
        A fully-configured capability ready to attach to an agent.
    """
    return AuditedConsoleCapability(
        include_execute=include_execute,
        edit_format=edit_format,
    )
