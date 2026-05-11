from __future__ import annotations

import asyncio
from pathlib import Path
from typing import cast

from pydantic_ai import RunContext
from pydantic_ai.tools import ToolDefinition
from pydantic_ai_backends.backends.local import LocalBackend

from unoplat_code_confluence_query_engine.models.repository.repository_ruleset_metadata import (
    CodebaseMetadata,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.agents.user_prompts.build_user_prompt_development_workflow import (
    build_development_workflow_instructions,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.capabilities.readonly_console import (
    MARKDOWN_READ_WRITE_EXECUTE_RULESET,
    build_markdown_execute_console_capability,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.constants import (
    DEVELOPMENT_WORKFLOW_CONSOLE_TOOLSET_ID,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_backend_resolver import (
    resolve_agent_backend,
)


def _build_metadata(
    *,
    language: str = "python",
    package_manager: str = "uv",
    codebase_name: str = "apps/api",
    codebase_path: str = "/opt/unoplat/repositories/acme-repo/apps/api",
) -> CodebaseMetadata:
    return CodebaseMetadata(
        codebase_name=codebase_name,
        codebase_path=codebase_path,
        codebase_programming_language=language,
        codebase_package_manager=package_manager,
        codebase_package_manager_provenance="local",
        codebase_workspace_root=".",
        codebase_workspace_root_path=codebase_path,
    )


def test_development_workflow_backend_uses_local_backend_with_execute_enabled() -> None:
    metadata = _build_metadata()

    backend = resolve_agent_backend(
        agent_name="development_workflow_guide",
        metadata=metadata,
        workflow_run_id="run-123",
    )

    assert isinstance(backend, LocalBackend)
    assert backend.root_dir == Path("/opt/unoplat/repositories/acme-repo/apps/api")
    assert backend.execute_enabled is True
    assert backend.permissions == MARKDOWN_READ_WRITE_EXECUTE_RULESET
    assert backend.permission_checker is not None
    assert backend.permission_checker.check_sync("read", metadata.codebase_path) == "allow"
    assert backend.permission_checker.check_sync("execute", "uv run pytest") == "allow"
    assert backend.permission_checker.check_sync("write", "AGENTS.md") == "allow"
    assert backend.permission_checker.check_sync("edit", "AGENTS.md") == "allow"
    assert backend.permission_checker.check_sync("write", "src/app.py") == "deny"
    assert backend.permission_checker.check_sync("edit", "src/app.py") == "deny"


def test_development_workflow_console_capability_keeps_execute_and_markdown_editing() -> None:
    capability = build_markdown_execute_console_capability(DEVELOPMENT_WORKFLOW_CONSOLE_TOOLSET_ID)

    toolset = capability.get_toolset()
    assert toolset is not None
    assert toolset.id == DEVELOPMENT_WORKFLOW_CONSOLE_TOOLSET_ID

    tool_defs = [
        ToolDefinition(name="read_file"),
        ToolDefinition(name="write_file"),
        ToolDefinition(name="edit_file"),
        ToolDefinition(name="execute"),
    ]
    visible_tool_defs = asyncio.run(
        capability.prepare_tools(cast(RunContext[object], None), tool_defs)
    )

    assert [tool.name for tool in visible_tool_defs] == [
        "read_file",
        "write_file",
        "edit_file",
        "execute",
    ]


def test_development_workflow_instructions_describe_direct_agents_md_section_ownership() -> None:
    instructions = build_development_workflow_instructions()

    assert "Local repository inspection tools available in this run: ls, read_file, glob, grep." in instructions
    assert (
        "CLI help/version discovery tool available in this run: execute. Use it only for commands containing --help, -h, --version, -v, or an explicit help subcommand/token; never use it to run install, build, test, lint, type_check, dev, server, watch, or reload commands."
        in instructions
    )
    assert "Markdown editing tools available in this run: write_file and edit_file for Markdown files only." in instructions
    assert "AGENTS.md / ## Engineering Workflow" in instructions
    assert "dependencies_overview.md, business_domain_references.md, app_interfaces.md" in instructions
