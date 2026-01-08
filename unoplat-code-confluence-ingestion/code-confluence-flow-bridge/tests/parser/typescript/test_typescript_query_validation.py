"""Test validation for TypeScript Tree-sitter types.scm query file.

This module verifies that the types.scm query file compiles successfully
and correctly captures interfaces and type aliases from TypeScript source.
"""

from pathlib import Path

import pytest
import tree_sitter
from tree_sitter_language_pack import get_language


@pytest.fixture(scope="module")
def typescript_language() -> tree_sitter.Language:
    """Fixture providing TypeScript language for tree-sitter."""
    return get_language("typescript")  # type: ignore[arg-type]


@pytest.fixture(scope="module")
def typescript_query_dir() -> Path:
    """Fixture providing path to TypeScript query directory."""
    test_file = Path(__file__)
    query_dir = (
        test_file.parent.parent.parent.parent
        / "src"
        / "code_confluence_flow_bridge"
        / "engine"
        / "programming_language"
        / "typescript"
        / "queries"
    )
    assert query_dir.exists(), f"TypeScript query directory not found at {query_dir}"
    return query_dir


@pytest.fixture(scope="module")
def typescript_ast_sample_path() -> Path:
    """Fixture providing path to TypeScript AST sample file."""
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
def typescript_source_bytes(typescript_ast_sample_path: Path) -> bytes:
    """Fixture returning raw TypeScript source bytes for the AST sample."""
    return typescript_ast_sample_path.read_bytes()


@pytest.fixture(scope="module")
def typescript_source_lines(typescript_source_bytes: bytes) -> list[str]:
    """Fixture returning decoded TypeScript source lines for signature checks."""
    return typescript_source_bytes.decode("utf-8").splitlines()


@pytest.fixture(scope="module")
def typescript_ast_tree(
    typescript_language: tree_sitter.Language,
    typescript_source_bytes: bytes,
) -> tree_sitter.Tree:
    """Fixture providing parsed tree of TypeScript AST sample file."""
    parser = tree_sitter.Parser(typescript_language)
    tree = parser.parse(typescript_source_bytes)
    return tree


def _extract_interface_name(signature_line: str) -> str:
    """Extract interface identifier from the signature line."""
    line = signature_line.strip()
    if line.startswith("export "):
        line = line[len("export ") :].lstrip()
    if line.startswith("declare "):
        line = line[len("declare ") :].lstrip()
    if not line.startswith("interface "):
        return ""

    remainder = line[len("interface ") :]
    remainder = remainder.replace("{", " ").strip()
    if not remainder:
        return ""

    candidate = remainder.split()[0]
    if "<" in candidate:
        candidate = candidate.split("<", 1)[0]
    return candidate


def _extract_type_alias_name(signature_line: str) -> str:
    """Extract type alias identifier from the signature line."""
    line = signature_line.strip()
    if line.startswith("export "):
        line = line[len("export ") :].lstrip()
    if line.startswith("declare "):
        line = line[len("declare ") :].lstrip()
    if not line.startswith("type "):
        return ""

    remainder = line[len("type ") :]
    remainder = remainder.replace("=", " ").strip()
    if not remainder:
        return ""

    candidate = remainder.split()[0]
    if "<" in candidate:
        candidate = candidate.split("<", 1)[0]
    return candidate


def test_types_query_file_exists(typescript_query_dir: Path) -> None:
    """Verify types.scm query file exists."""
    query_path = typescript_query_dir / "types.scm"
    assert query_path.exists(), f"types.scm not found at {query_path}"


def test_types_query_compiles(
    typescript_language: tree_sitter.Language,
    typescript_query_dir: Path,
) -> None:
    """Test that types.scm compiles successfully."""
    query_path = typescript_query_dir / "types.scm"
    query_content = query_path.read_text(encoding="utf-8")
    assert len(query_content) > 0, "types.scm is empty"

    compiled_query = tree_sitter.Query(typescript_language, query_content)
    assert compiled_query is not None, "Query compilation returned None"


def test_types_query_basic_functionality(
    typescript_language: tree_sitter.Language,
    typescript_query_dir: Path,
    typescript_ast_tree: tree_sitter.Tree,
) -> None:
    """Test types query against TypeScript interfaces and type aliases from AST sample."""
    query_path = typescript_query_dir / "types.scm"
    tree = typescript_ast_tree

    query_content = query_path.read_text(encoding="utf-8")
    query = tree_sitter.Query(typescript_language, query_content)
    cursor = tree_sitter.QueryCursor(query)

    matches = cursor.matches(tree.root_node)

    assert len(matches) > 0, "types.scm should capture interfaces and type aliases"


def test_types_query_interface_ranges(
    typescript_language: tree_sitter.Language,
    typescript_query_dir: Path,
    typescript_ast_tree: tree_sitter.Tree,
    typescript_source_lines: list[str],
) -> None:
    """Ensure interface captures expose start/end lines and first-line signatures."""
    query_path = typescript_query_dir / "types.scm"

    query_content = query_path.read_text(encoding="utf-8")
    query = tree_sitter.Query(typescript_language, query_content)
    cursor = tree_sitter.QueryCursor(query)
    matches = cursor.matches(typescript_ast_tree.root_node)

    interface_ranges: dict[str, tuple[int, int, str]] = {}

    for _match_id, captures in matches:
        node_list = captures.get("interface")
        if not node_list:
            continue

        for node in node_list:
            start_line = node.start_point[0] + 1
            end_line = node.end_point[0] + 1
            signature_line = typescript_source_lines[start_line - 1].strip()
            name = _extract_interface_name(signature_line)
            if not name:
                continue

            interface_ranges[name] = (start_line, end_line, signature_line)

    expected_interfaces = {
        "ApiResponse": (70, 73, "export interface ApiResponse {"),
        "ApiError": (75, 80, "export interface ApiError {"),
        "ProviderFieldState": (333, 336, "export interface ProviderFieldState {"),
    }

    for name, (
        expected_start,
        expected_end,
        expected_signature,
    ) in expected_interfaces.items():
        assert name in interface_ranges, f"Missing interface capture for {name}"
        start_line, end_line, signature = interface_ranges[name]
        assert start_line == expected_start, (
            f"{name} start line mismatch (expected {expected_start}, got {start_line})"
        )
        assert end_line == expected_end, (
            f"{name} end line mismatch (expected {expected_end}, got {end_line})"
        )
        assert signature == expected_signature, (
            f"{name} signature mismatch (expected '{expected_signature}', got '{signature}')"
        )


def test_types_query_type_alias_ranges(
    typescript_language: tree_sitter.Language,
    typescript_query_dir: Path,
    typescript_ast_tree: tree_sitter.Tree,
    typescript_source_lines: list[str],
) -> None:
    """Ensure type alias captures expose start/end lines and first-line signatures."""
    query_path = typescript_query_dir / "types.scm"

    query_content = query_path.read_text(encoding="utf-8")
    query = tree_sitter.Query(typescript_language, query_content)
    cursor = tree_sitter.QueryCursor(query)
    matches = cursor.matches(typescript_ast_tree.root_node)

    alias_ranges: dict[str, tuple[int, int, str]] = {}

    for _match_id, captures in matches:
        node_list = captures.get("type_alias")
        if not node_list:
            continue

        for node in node_list:
            start_line = node.start_point[0] + 1
            end_line = node.end_point[0] + 1
            signature_line = typescript_source_lines[start_line - 1].strip()
            name = _extract_type_alias_name(signature_line)
            if not name:
                continue

            alias_ranges[name] = (start_line, end_line, signature_line)

    expected_aliases = {
        "FilterItemSchema": (
            320,
            320,
            "export type FilterItemSchema = z.infer<typeof filterItemSchema>;",
        ),
        "ExtendedColumnSort": (322, 326, "export type ExtendedColumnSort<TData> = {"),
        "ModelProviderDefinitions": (
            338,
            340,
            "export type ModelProviderDefinitions = ReadonlyArray<",
        ),
    }

    for name, (
        expected_start,
        expected_end,
        expected_signature,
    ) in expected_aliases.items():
        assert name in alias_ranges, f"Missing type alias capture for {name}"
        start_line, end_line, signature = alias_ranges[name]
        assert start_line == expected_start, (
            f"{name} start line mismatch (expected {expected_start}, got {start_line})"
        )
        assert end_line == expected_end, (
            f"{name} end line mismatch (expected {expected_end}, got {end_line})"
        )
        assert signature == expected_signature, (
            f"{name} signature mismatch (expected '{expected_signature}', got '{signature}')"
        )
