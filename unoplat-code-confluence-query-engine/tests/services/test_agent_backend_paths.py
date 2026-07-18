"""Unit tests for agent backend path resolution."""

from __future__ import annotations

import pytest

from unoplat_code_confluence_query_engine.models.repository.repository_ruleset_metadata import (
    CodebaseMetadata,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_backend_paths import (
    resolve_repository_root,
)


@pytest.mark.parametrize(
    ("codebase_name", "codebase_path"),
    [
        (
            "unoplat-code-confluence-query-engine",
            "/opt/unoplat/repositories/unoplat-code-confluence/"
            "unoplat-code-confluence-query-engine",
        ),
        (
            "unoplat-code-confluence-ingestion/code-confluence-flow-bridge",
            "/opt/unoplat/repositories/unoplat-code-confluence/"
            "unoplat-code-confluence-ingestion/code-confluence-flow-bridge",
        ),
    ],
    ids=["query-engine-one-level-deep", "flow-bridge-two-levels-deep"],
)
def test_resolve_repository_root_for_nested_codebase(
    codebase_name: str, codebase_path: str
) -> None:
    metadata = CodebaseMetadata(
        codebase_name=codebase_name,
        codebase_path=codebase_path,
        codebase_programming_language="python",
        codebase_package_manager="uv",
    )

    assert resolve_repository_root(metadata) == "/opt/unoplat/repositories/unoplat-code-confluence"
