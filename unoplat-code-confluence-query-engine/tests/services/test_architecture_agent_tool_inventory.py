"""Deterministic tool-inventory smoke test for the Architecture agent.

Run with ``pytest -s`` to print the exact tools and JSON schemas supplied to a
model. ``TestModel(call_tools=[])`` intentionally requests no tool calls, so
this test cannot mutate the repository or run Mermaid.
"""

from __future__ import annotations

import json

from pydantic_ai.models.test import TestModel
import pytest

from unoplat_code_confluence_query_engine.config.settings import EnvironmentSettings
from unoplat_code_confluence_query_engine.models.runtime.architecture_agent_dependencies import (
    ArchitectureAgentDependencies,
)
from unoplat_code_confluence_query_engine.services.temporal.activity_retry_config import (
    TemporalAgentRetryConfig,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.agents.architecture import (
    build_architecture_agent,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.assembler import (
    create_assembly_context,
)


@pytest.mark.anyio
async def test_architecture_agent_prints_available_tool_schemas(tmp_path) -> None:
    """Print the exact function-tool contract exposed to the architecture model."""
    model = TestModel(call_tools=[])
    build_result = build_architecture_agent(
        create_assembly_context(
            model,
            TemporalAgentRetryConfig(EnvironmentSettings()),
        )
    )
    deps = ArchitectureAgentDependencies(
        repository_qualified_name="acme/repository",
        repository_root=str(tmp_path),
        repository_workflow_run_id="architecture-tool-inventory",
    )

    result = await build_result.agent.run(
        "Inspect the available tools only. Do not call any tools.",
        deps=deps,
    )

    request = model.last_model_request_parameters
    assert request is not None
    inventory = [
        {
            "name": tool.name,
            "parameters_json_schema": tool.parameters_json_schema,
        }
        for tool in request.function_tools
    ]
    print("\nArchitecture agent tool inventory:\n" + json.dumps(inventory, indent=2))

    assert result.output == "success (no tool calls)"
    assert [tool["name"] for tool in inventory] == [
        "validate_architecture",
        "load_skill",
        "ls",
        "read_file",
        "write_file",
        "edit_file",
        "glob",
        "grep",
        "execute",
    ]
    background_tools = {
        "run_in_background",
        "read_output",
        "kill_shell",
        "list_shells",
    }
    assert all(tool["name"] not in background_tools for tool in inventory)
