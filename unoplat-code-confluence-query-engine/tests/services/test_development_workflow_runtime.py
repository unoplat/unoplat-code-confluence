from __future__ import annotations

import asyncio
from pathlib import Path
from typing import cast

from pydantic_ai import Agent, PromptedOutput, RunContext, capture_run_messages, models
from pydantic_ai.exceptions import UnexpectedModelBehavior
from pydantic_ai.models.test import TestModel
from pydantic_ai.tools import ToolDefinition
from pydantic_ai_backends.backends.local import LocalBackend
import pytest

from unoplat_code_confluence_query_engine.models.output.engineering_workflow_output import (
    ENGINEERING_WORKFLOW_FULL_OUTPUT,
    ENGINEERING_WORKFLOW_NO_CHANGE,
    EngineeringWorkflowAgentOutput,
)
from unoplat_code_confluence_query_engine.models.repository.repository_ruleset_metadata import (
    CodebaseMetadata,
)
from unoplat_code_confluence_query_engine.models.runtime.agent_dependencies import (
    AgentDependencies,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.agents.user_prompts.build_user_prompt_development_workflow import (
    build_development_workflow_prompt,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.agents.validators.development_workflow_validator import (
    validate_engineering_development_workflow_output,
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

setattr(models, "ALLOW_MODEL_REQUESTS", False)


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
    assert (
        backend.permission_checker.check_sync("read", metadata.codebase_path) == "allow"
    )
    assert backend.permission_checker.check_sync("execute", "uv run pytest") == "allow"
    assert backend.permission_checker.check_sync("write", "AGENTS.md") == "allow"
    assert backend.permission_checker.check_sync("edit", "AGENTS.md") == "allow"
    assert backend.permission_checker.check_sync("write", "src/app.py") == "deny"
    assert backend.permission_checker.check_sync("edit", "src/app.py") == "deny"


def test_development_workflow_console_capability_keeps_execute_and_markdown_editing() -> (
    None
):
    capability = build_markdown_execute_console_capability(
        DEVELOPMENT_WORKFLOW_CONSOLE_TOOLSET_ID
    )

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


def _valid_managed_agents_md() -> str:
    return """<!-- UNOPLAT_CODE_CONFLUENCE_CONTEXT:BEGIN -->
<CRITICAL_INSTRUCTION>

</CRITICAL_INSTRUCTION>

## Engineering Workflow
### Install
- `uv sync` (repo root; `pyproject.toml`)
### Build
- Not detected
### Dev
- Not detected
### Test
- `uv run pytest` (repo root; `pyproject.toml`)
### Lint
- Not detected
### Type Check
- Not detected

## Dependency Guide
See [`dependencies_overview.md`](./dependencies_overview.md) for the full dependency catalog and usage notes.

## Business Domain
### Description

### References

See [`business_domain_references.md`](./business_domain_references.md) for the supporting source references used to derive this domain summary.

## App Interfaces
See [`app_interfaces.md`](./app_interfaces.md) for the canonical interface and endpoint reference.

<!-- UNOPLAT_CODE_CONFLUENCE_CONTEXT:END -->
"""


def _build_development_workflow_deps(
    tmp_path: Path, *, allow_no_change_output: bool
) -> AgentDependencies:
    (tmp_path / "AGENTS.md").write_text(_valid_managed_agents_md(), encoding="utf-8")
    return AgentDependencies(
        repository_qualified_name="acme/repo",
        codebase_metadata=_build_metadata(codebase_path=str(tmp_path)),
        repository_workflow_run_id="repo-run-1",
        codebase_workflow_run_id="codebase-run-1",
        agent_name="development_workflow_guide",
        allow_no_change_output=allow_no_change_output,
    )


def _build_development_workflow_test_agent(
    model: TestModel,
) -> Agent[AgentDependencies, EngineeringWorkflowAgentOutput]:
    agent = Agent(
        model,
        deps_type=AgentDependencies,
        output_type=EngineeringWorkflowAgentOutput,
        retries={"output": 1},
    )
    agent.output_validator(validate_engineering_development_workflow_output)
    return agent


@pytest.mark.anyio
async def test_development_workflow_agent_accepts_full_output_without_previous_snapshot(
    tmp_path: Path,
) -> None:
    deps = _build_development_workflow_deps(tmp_path, allow_no_change_output=False)
    model = TestModel(
        custom_output_args={
            "status": ENGINEERING_WORKFLOW_FULL_OUTPUT,
            "commands": [
                {
                    "command": "uv run pytest",
                    "stage": "test",
                    "config_file": "pyproject.toml",
                }
            ],
        },
        seed=0,
    )
    agent = _build_development_workflow_test_agent(model)

    result = await agent.run(
        build_development_workflow_prompt(
            codebase_path=str(tmp_path),
            programming_language="python",
            package_manager="uv",
            allow_no_change_output=False,
        ),
        deps=deps,
    )

    assert result.output.status == ENGINEERING_WORKFLOW_FULL_OUTPUT
    assert result.output.commands is not None
    assert [command.command for command in result.output.commands] == ["uv run pytest"]


@pytest.mark.anyio
async def test_development_workflow_agent_accepts_no_change_when_previous_snapshot_exists(
    tmp_path: Path,
) -> None:
    deps = _build_development_workflow_deps(tmp_path, allow_no_change_output=True)
    model = TestModel(
        custom_output_args={"status": ENGINEERING_WORKFLOW_NO_CHANGE},
        seed=1,
    )
    agent = _build_development_workflow_test_agent(model)

    result = await agent.run(
        build_development_workflow_prompt(
            codebase_path=str(tmp_path),
            programming_language="python",
            package_manager="uv",
            allow_no_change_output=True,
        ),
        deps=deps,
    )

    assert result.output.status == ENGINEERING_WORKFLOW_NO_CHANGE
    assert result.output.commands is None


@pytest.mark.anyio
async def test_development_workflow_agent_accepts_bare_text_full_output_without_union_wrapper(
    tmp_path: Path,
) -> None:
    deps = _build_development_workflow_deps(tmp_path, allow_no_change_output=False)
    model = TestModel(
        custom_output_text=(
            '{"status":"full_output","commands":[{"command":"uv run pytest",'
            '"stage":"test","config_file":"pyproject.toml"}]}'
        ),
        seed=0,
    )
    agent = Agent(
        model,
        deps_type=AgentDependencies,
        output_type=PromptedOutput(EngineeringWorkflowAgentOutput),
        retries={"output": 1},
    )
    agent.output_validator(validate_engineering_development_workflow_output)

    result = await agent.run(
        build_development_workflow_prompt(
            codebase_path=str(tmp_path),
            programming_language="python",
            package_manager="uv",
            allow_no_change_output=False,
        ),
        deps=deps,
    )

    assert result.output.status == ENGINEERING_WORKFLOW_FULL_OUTPUT
    assert result.output.commands is not None
    assert [command.command for command in result.output.commands] == ["uv run pytest"]


@pytest.mark.anyio
async def test_development_workflow_agent_retries_no_change_with_commands(
    tmp_path: Path,
) -> None:
    deps = _build_development_workflow_deps(tmp_path, allow_no_change_output=True)
    model = TestModel(
        custom_output_args={
            "status": ENGINEERING_WORKFLOW_NO_CHANGE,
            "commands": [
                {
                    "command": "uv run pytest",
                    "stage": "test",
                    "config_file": "pyproject.toml",
                }
            ],
        },
        seed=1,
    )
    agent = _build_development_workflow_test_agent(model)

    with capture_run_messages() as messages:
        with pytest.raises(UnexpectedModelBehavior, match="Exceeded maximum retries"):
            await agent.run(
                build_development_workflow_prompt(
                    codebase_path=str(tmp_path),
                    programming_language="python",
                    package_manager="uv",
                    allow_no_change_output=True,
                ),
                deps=deps,
            )

    assert any(
        "omit the commands field" in str(part)
        for message in messages
        for part in message.parts
    )


@pytest.mark.anyio
async def test_development_workflow_agent_retries_no_change_without_previous_snapshot(
    tmp_path: Path,
) -> None:
    deps = _build_development_workflow_deps(tmp_path, allow_no_change_output=False)
    model = TestModel(
        custom_output_args={"status": ENGINEERING_WORKFLOW_NO_CHANGE},
        seed=1,
    )
    agent = _build_development_workflow_test_agent(model)

    with capture_run_messages() as messages:
        with pytest.raises(UnexpectedModelBehavior, match="Exceeded maximum retries"):
            await agent.run(
                build_development_workflow_prompt(
                    codebase_path=str(tmp_path),
                    programming_language="python",
                    package_manager="uv",
                    allow_no_change_output=False,
                ),
                deps=deps,
            )

    assert any(
        "previous structured engineering_workflow data is unavailable" in str(part)
        for message in messages
        for part in message.parts
    )
