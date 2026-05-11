"""Validation tests for TypeScript framework query dedup assumptions.

These tests execute the call-expression query sourced from
``src/.../typescript/queries`` against repository TypeScript source and
verify whether query output itself contains duplicate AST-node captures.
"""

from collections import Counter
from pathlib import Path

import pytest
from src.code_confluence_flow_bridge.engine.programming_language.typescript.typescript_framework_query_builder import (
    TypeScriptFrameworkQueryBuilder,
)
from src.code_confluence_flow_bridge.engine.programming_language.typescript.typescript_source_context import (
    TypeScriptSourceContext,
)
import tree_sitter
from unoplat_code_confluence_commons.base_models import (
    Concept,
    FeatureSpec,
    LocatorStrategy,
    TargetLevel,
)


def _build_call_expression_spec() -> FeatureSpec:
    """Build a permissive call-expression feature spec for query execution."""
    return FeatureSpec(
        capability_key="test",
        operation_key="call_expression",
        library="query_validation",
        description="Call-expression query validation",
        absolute_paths=["zustand.create"],
        target_level=TargetLevel.FUNCTION,
        concept=Concept.CALL_EXPRESSION,
        locator_strategy=LocatorStrategy.VARIABLE_BOUND,
        base_confidence=0.9,
    )


@pytest.fixture(scope="module")
def typescript_ast_sample_path() -> Path:
    """Path to repository TypeScript source sample used for parser/query tests."""
    test_file = Path(__file__)
    sample_path = (
        test_file.parent.parent.parent
        / "test_data"
        / "typescript_files"
        / "typescript_ast_sample.ts"
    )
    assert sample_path.exists(), f"TypeScript AST sample not found at {sample_path}"
    return sample_path


@pytest.fixture(scope="module")
def typescript_source_context(
    typescript_ast_sample_path: Path,
) -> TypeScriptSourceContext:
    """Parsed TypeScript source context for query execution."""
    return TypeScriptSourceContext.from_bytes(
        typescript_ast_sample_path.read_bytes()
    )


def _collect_call_expression_nodes(
    context: TypeScriptSourceContext,
) -> list[tree_sitter.Node]:
    """Run the framework call-expression query and return captured nodes."""
    query = TypeScriptFrameworkQueryBuilder().build_query(_build_call_expression_spec())
    matches = tree_sitter.QueryCursor(query).matches(context.root_node)

    return [
        captures["call_expression"][0]
        for _pattern_index, captures in matches
        if captures.get("call_expression")
    ]


def test_call_expression_query_captures_are_unique_by_byte_range(
    typescript_source_context: TypeScriptSourceContext,
) -> None:
    """Assert query output does not duplicate AST nodes by byte range."""
    call_nodes = _collect_call_expression_nodes(typescript_source_context)

    assert call_nodes, "Expected call_expression query to capture at least one node"

    byte_ranges = [(node.start_byte, node.end_byte) for node in call_nodes]
    assert len(byte_ranges) == len(set(byte_ranges))


def test_call_expression_query_has_line_range_collisions(
    typescript_source_context: TypeScriptSourceContext,
) -> None:
    """Demonstrate that line-range-only dedup keys can merge distinct matches."""
    call_nodes = _collect_call_expression_nodes(typescript_source_context)

    line_ranges = [
        (node.start_point[0] + 1, node.end_point[0] + 1) for node in call_nodes
    ]
    line_range_counts = Counter(line_ranges)

    collision_ranges = [
        line_range for line_range, count in line_range_counts.items() if count > 1
    ]

    assert collision_ranges, (
        "Expected at least one shared line range among call_expression matches "
        "in repository TypeScript sample"
    )
