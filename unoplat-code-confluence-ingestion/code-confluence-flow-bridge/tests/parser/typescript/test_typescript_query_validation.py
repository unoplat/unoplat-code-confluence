"""Test validation for TypeScript Tree-sitter query files.

This module verifies that all TypeScript `.scm` query files compile successfully
and can be used with the tree-sitter TypeScript grammar.
"""

from pathlib import Path

import pytest
import tree_sitter
from tree_sitter_language_pack import get_language


# TypeScript query files to validate
TYPESCRIPT_QUERY_FILES = {
    "imports": "imports.scm",
    "exports": "exports.scm",
    "functions": "functions.scm",
    "classes": "classes.scm",
    "methods": "methods.scm",
    "variables": "variables.scm",
    "types": "types.scm",
    "enums": "enums.scm",
    "namespaces": "namespaces.scm",
    "decorators": "decorators.scm",
    "jsx": "jsx.scm",
    "assertions": "assertions.scm",
}

# Queries that are optional (may not be fully implemented yet)
OPTIONAL_QUERIES = {"decorators", "jsx", "assertions"}


@pytest.fixture(scope="module")
def typescript_language() -> tree_sitter.Language:
    """Fixture providing TypeScript language for tree-sitter."""
    return get_language("typescript")  # type: ignore[arg-type]


@pytest.fixture(scope="module")
def typescript_query_dir() -> Path:
    """Fixture providing path to TypeScript query directory."""
    test_file = Path(__file__)
    query_dir = test_file.parent.parent.parent.parent / "src" / "code_confluence_flow_bridge" / "parser" / "queries" / "typescript"
    assert query_dir.exists(), f"TypeScript query directory not found at {query_dir}"
    return query_dir


@pytest.fixture(scope="module")
def typescript_ast_sample_path() -> Path:
    """Fixture providing path to TypeScript AST sample file."""
    test_file = Path(__file__)
    sample_path = test_file.parent.parent.parent.parent / "experiments" / "typescript_ast_sample.ts"
    assert sample_path.exists(), f"TypeScript AST sample not found at {sample_path}"
    return sample_path


@pytest.fixture(scope="module")
def typescript_ast_tree(typescript_language: tree_sitter.Language, typescript_ast_sample_path: Path) -> tree_sitter.Tree:
    """Fixture providing parsed tree of TypeScript AST sample file."""
    parser = tree_sitter.Parser(typescript_language)
    source_code = typescript_ast_sample_path.read_bytes()
    tree = parser.parse(source_code)
    return tree


def test_all_query_files_exist(typescript_query_dir: Path) -> None:
    """Verify all expected TypeScript query files exist."""
    for query_name, filename in TYPESCRIPT_QUERY_FILES.items():
        query_path = typescript_query_dir / filename
        if query_name in OPTIONAL_QUERIES:
            # Optional queries may not exist yet
            if not query_path.exists():
                pytest.skip(f"Optional query file {filename} not yet implemented")
        else:
            assert query_path.exists(), f"Required query file {filename} not found at {query_path}"


@pytest.mark.parametrize("query_name,filename", TYPESCRIPT_QUERY_FILES.items())
def test_query_file_compiles(
    query_name: str,
    filename: str,
    typescript_language: tree_sitter.Language,
    typescript_query_dir: Path
) -> None:
    """Test that each TypeScript query file compiles successfully."""
    # Skip jsx and assertions queries - to be tackled later
    if query_name in {"jsx", "assertions"}:
        pytest.skip(f"Query {query_name} temporarily skipped - will be tackled later")

    query_path = typescript_query_dir / filename

    # Skip optional queries if not implemented
    if query_name in OPTIONAL_QUERIES and not query_path.exists():
        pytest.skip(f"Optional query {query_name} not yet implemented")

    assert query_path.exists(), f"Query file {filename} not found"

    # Read query content
    query_content = query_path.read_text(encoding="utf-8")
    assert len(query_content) > 0, f"Query file {filename} is empty"

    # Attempt to compile the query
    try:
        compiled_query = tree_sitter.Query(typescript_language, query_content)
        assert compiled_query is not None, f"Query compilation returned None for {filename}"
        print(f"✓ {filename} compiled successfully")
    except Exception as e:
        pytest.fail(f"Failed to compile {filename}: {e}")


def test_imports_query_basic_functionality(
    typescript_language: tree_sitter.Language,
    typescript_query_dir: Path,
    typescript_ast_tree: tree_sitter.Tree
) -> None:
    """Test imports query against TypeScript import statements from AST sample."""
    query_path = typescript_query_dir / "imports.scm"
    if not query_path.exists():
        pytest.skip("imports.scm not found")

    # Use parsed AST sample tree
    tree = typescript_ast_tree

    # Load and execute query
    query_content = query_path.read_text(encoding="utf-8")
    query = tree_sitter.Query(typescript_language, query_content)
    cursor = tree_sitter.QueryCursor(query)

    # Execute query
    matches: list[tuple[int, dict[str, list[tree_sitter.Node]]]] = cursor.matches(tree.root_node)

    # Should capture import statements from AST sample
    assert len(matches) > 0, "imports.scm should capture import statements"
    print(f"✓ imports.scm captured {len(matches)} matches from AST sample")


def test_functions_query_basic_functionality(
    typescript_language: tree_sitter.Language,
    typescript_query_dir: Path,
    typescript_ast_tree: tree_sitter.Tree
) -> None:
    """Test functions query captures component-based signatures (not whole nodes).

    This test validates that the refactored query extracts individual function
    signature components: async keyword, name, type parameters, parameters,
    and return type - rather than capturing entire function nodes.
    """
    query_path = typescript_query_dir / "functions.scm"
    if not query_path.exists():
        pytest.skip("functions.scm not found")

    # Use parsed AST sample tree
    tree = typescript_ast_tree

    # Load and execute query
    query_content = query_path.read_text(encoding="utf-8")
    query = tree_sitter.Query(typescript_language, query_content)
    cursor = tree_sitter.QueryCursor(query)

    # Execute query
    matches = cursor.matches(tree.root_node)

    # Basic validation: should capture functions from AST sample
    assert len(matches) > 0, "functions.scm should capture function declarations"

    # Collect all capture names across all matches
    all_capture_names: set[str] = set()
    component_counts: dict[str, int] = {}

    for _match_id, captures_dict in matches:
        for capture_name, nodes in captures_dict.items():
            all_capture_names.add(capture_name)
            component_counts[capture_name] = component_counts.get(capture_name, 0) + len(nodes)

    # Validate component-based captures exist
    # Essential captures that should be present across function types
    assert "params" in all_capture_names, \
        "Query should capture @params for function signatures"

    # At least one type of function name should be captured
    name_captures = {"function_name", "arrow_name", "func_expr_name", "generator_name"}
    captured_names = name_captures & all_capture_names
    assert len(captured_names) > 0, \
        f"Query should capture at least one function name type: {name_captures}"

    # Optional but expected signature components
    expected_optional = {"async", "return_type", "type_params", "binding_keyword"}
    captured_optional = expected_optional & all_capture_names

    # Validate every match has @params (essential component)
    matches_without_params = 0
    for _match_id, captures_dict in matches:
        if "params" not in captures_dict:
            matches_without_params += 1

    assert matches_without_params == 0, \
        f"{matches_without_params} matches missing @params capture"

    # Print detailed summary
    print(f"✓ functions.scm captured {len(matches)} matches from AST sample")
    print(f"  Component captures found: {sorted(all_capture_names)}")
    print(f"  Function name types: {sorted(captured_names)}")
    print(f"  Optional components: {sorted(captured_optional)}")
    print(f"  Component counts: {component_counts}")

    # Additional validations for component counts
    total_components = sum(component_counts.values())
    assert total_components > len(matches), \
        f"Should have multiple components per match (got {total_components} components for {len(matches)} matches)"

    # Validate we're not capturing whole function bodies
    # Component captures should be small nodes (identifiers, type annotations, parameter lists)
    # If we were capturing whole nodes, we'd see very few total captures
    assert len(all_capture_names) >= 3, \
        f"Should capture at least 3 different component types (got {len(all_capture_names)})"


def test_classes_query_component_captures(
    typescript_language: tree_sitter.Language,
    typescript_query_dir: Path,
    typescript_ast_tree: tree_sitter.Tree
) -> None:
    """Validate classes.scm captures component-level signature elements.

    This test ensures the refactored query extracts individual class signature
    components (decorators, export keywords, heritage clauses) rather than
    capturing entire class nodes.
    """
    query_path = typescript_query_dir / "classes.scm"
    if not query_path.exists():
        pytest.skip("classes.scm not found")

    query_content = query_path.read_text(encoding="utf-8")
    query = tree_sitter.Query(typescript_language, query_content)
    cursor = tree_sitter.QueryCursor(query)
    matches = cursor.matches(typescript_ast_tree.root_node)

    # Collect component counts
    component_counts: dict[str, int] = {}
    for _match_id, captures_dict in matches:
        for capture_name, nodes in captures_dict.items():
            component_counts[capture_name] = component_counts.get(capture_name, 0) + len(nodes)

    # Assert at least some matches
    assert len(matches) > 0, "classes.scm should capture class declarations"

    # Assert class name captures exist (at least one type)
    name_captures = {"class_name", "exported_class_name", "default_class_name", "abstract_class_name"}
    captured_names = name_captures & set(component_counts.keys())
    assert len(captured_names) > 0, \
        f"Should capture at least one class name type from: {name_captures}"

    # Assert NO whole-node captures
    forbidden = {"class", "exported_class", "abstract_class", "class_body"}
    found_forbidden = forbidden & set(component_counts.keys())
    assert len(found_forbidden) == 0, \
        f"Should not capture whole nodes: {found_forbidden}"

    # Specific pattern checks based on typescript_ast_sample.ts

    # BaseRepository: @sealed decorator + abstract
    assert "class_decorator" in component_counts, \
        "Should capture @sealed decorator on BaseRepository"
    assert "abstract_keyword" in component_counts, \
        "Should capture 'abstract' keyword for BaseRepository"

    # ApiResource: export + generic + multiple implements
    assert "export_keyword" in component_counts, \
        "Should capture 'export' keyword for ApiResource"
    assert "type_params" in component_counts, \
        "Should capture type parameters for ApiResource<T extends Base>"

    # DefaultWorker: export default
    assert "default_keyword" in component_counts, \
        "Should capture 'default' keyword for DefaultWorker"

    # Heritage clauses (multiple classes have extends/implements)
    assert "extends_target" in component_counts, \
        "Should capture extends targets (InstrumentedFetcher, BaseRepository, etc.)"
    assert "implements_interface" in component_counts, \
        "Should capture implements interfaces (Auditable, Serializable, Loggable)"
    assert "implements_keyword" in component_counts, \
        "Should capture 'implements' keyword"

    # Ensure multiple components per class on average
    total_components = sum(component_counts.values())
    num_classes = sum(component_counts.get(name, 0) for name in name_captures)
    avg_components = total_components / num_classes if num_classes > 0 else 0
    assert avg_components >= 2, \
        f"Should have multiple components per class (got {avg_components:.1f})"

    print(f"✓ classes.scm captured {total_components} component captures across {num_classes} classes")
    print(f"  Average {avg_components:.1f} components per class")
    print(f"  Component types: {sorted(component_counts.keys())}")


def test_methods_query_component_captures(
    typescript_language: tree_sitter.Language,
    typescript_query_dir: Path,
    typescript_ast_tree: tree_sitter.Tree
) -> None:
    """Validate methods.scm captures method signature components including decorators.

    This test ensures the refactored query extracts individual method signature
    components (decorators, modifiers, parameters, return types) rather than
    capturing entire method bodies.
    """
    query_path = typescript_query_dir / "methods.scm"
    if not query_path.exists():
        pytest.skip("methods.scm not found")

    query_content = query_path.read_text(encoding="utf-8")
    query = tree_sitter.Query(typescript_language, query_content)
    cursor = tree_sitter.QueryCursor(query)
    matches = cursor.matches(typescript_ast_tree.root_node)

    component_counts: dict[str, int] = {}
    for _match_id, captures_dict in matches:
        for capture_name, nodes in captures_dict.items():
            component_counts[capture_name] = component_counts.get(capture_name, 0) + len(nodes)

    assert len(matches) > 0, "methods.scm should capture method definitions"

    # Assert method name captures
    assert "method_name" in component_counts, "Should capture method names"
    assert "getter_name" in component_counts or "setter_name" in component_counts, \
        "Should capture getter or setter names (ApiResource has both)"

    # Assert params captured for methods
    assert "params" in component_counts, "Should capture parameters"

    # InstrumentedFetcher.fetchJob has @logInvocation decorator
    assert "method_decorator" in component_counts, \
        "Should capture @logInvocation on InstrumentedFetcher.fetchJob"

    # ComprehensiveModifiers has public/private/protected methods
    assert "accessibility" in component_counts, \
        "Should capture public/private/protected modifiers"

    # ApiResource has getter/setter with literal "get"/"set" tokens
    assert "method_kind" in component_counts, \
        "Should capture 'get'/'set' keywords as method_kind for ApiResource accessors"

    # ApiResource has static async method
    assert "static" in component_counts, \
        "Should capture 'static' keyword on ApiResource.refreshAll and others"
    assert "async" in component_counts, \
        "Should capture 'async' keyword on async methods"

    # Assert NO whole-body captures
    forbidden = {"method", "method_body", "getter_body", "setter_body",
                 "constructor_body", "getter_method", "setter_method", "getter", "setter"}
    found_forbidden = forbidden & set(component_counts.keys())
    assert len(found_forbidden) == 0, \
        f"Should not capture whole bodies: {found_forbidden}"

    # Ensure multiple components per method on average
    total_components = sum(component_counts.values())
    method_count = component_counts.get("method_name", 0) + \
                   component_counts.get("getter_name", 0) + \
                   component_counts.get("setter_name", 0) + \
                   component_counts.get("constructor_name", 0)
    avg_components = total_components / method_count if method_count > 0 else 0
    assert avg_components >= 2, \
        f"Should have multiple components per method (got {avg_components:.1f})"

    print(f"✓ methods.scm captured {total_components} component captures across {method_count} methods")
    print(f"  Average {avg_components:.1f} components per method")
    print(f"  Component types: {sorted(component_counts.keys())}")


def test_types_query_basic_functionality(
    typescript_language: tree_sitter.Language,
    typescript_query_dir: Path,
    typescript_ast_tree: tree_sitter.Tree
) -> None:
    """Test types query against TypeScript interfaces and type aliases from AST sample."""
    query_path = typescript_query_dir / "types.scm"
    if not query_path.exists():
        pytest.skip("types.scm not found")

    # Use parsed AST sample tree
    tree = typescript_ast_tree

    # Load and execute query
    query_content = query_path.read_text(encoding="utf-8")
    query = tree_sitter.Query(typescript_language, query_content)
    cursor = tree_sitter.QueryCursor(query)

    # Execute query
    matches = cursor.matches(tree.root_node)

    # Should capture interfaces and type aliases from AST sample
    assert len(matches) > 0, "types.scm should capture interfaces and type aliases"
    print(f"✓ types.scm captured {len(matches)} matches from AST sample")


def test_exports_query_functionality(
    typescript_language: tree_sitter.Language,
    typescript_query_dir: Path,
    typescript_ast_tree: tree_sitter.Tree
) -> None:
    """Test exports query against various export patterns from AST sample."""
    query_path = typescript_query_dir / "exports.scm"
    if not query_path.exists():
        pytest.skip("exports.scm not found")

    # Use parsed AST sample tree
    tree = typescript_ast_tree
    query_content = query_path.read_text(encoding="utf-8")
    query = tree_sitter.Query(typescript_language, query_content)

    # Execute query once on entire AST sample
    cursor = tree_sitter.QueryCursor(query)
    matches = cursor.matches(tree.root_node)
    capture_names = {k for _, d in matches for k in d.keys()}

    # AST sample should contain various export patterns
    # The exact captures depend on what's in typescript_ast_sample.ts
    assert len(matches) > 0, "exports.scm should capture export statements"

    print(f"✓ exports.scm validated against AST sample export patterns ({len(matches)} matches)")


def test_methods_query_functionality(
    typescript_language: tree_sitter.Language,
    typescript_query_dir: Path,
    typescript_ast_tree: tree_sitter.Tree
) -> None:
    """Test methods query against class methods from AST sample."""
    query_path = typescript_query_dir / "methods.scm"
    if not query_path.exists():
        pytest.skip("methods.scm not found")

    # Use parsed AST sample tree
    tree = typescript_ast_tree
    query_content = query_path.read_text(encoding="utf-8")
    query = tree_sitter.Query(typescript_language, query_content)

    # Execute query once on entire AST sample
    cursor = tree_sitter.QueryCursor(query)
    matches = cursor.matches(tree.root_node)
    capture_names = {k for _, d in matches for k in d.keys()}

    # AST sample should contain class methods with various modifiers
    assert len(matches) > 0, "methods.scm should capture class methods"
    assert 'method_name' in capture_names or 'constructor_name' in capture_names, \
        "Should capture method or constructor names"

    print(f"✓ methods.scm validated against AST sample method patterns ({len(matches)} matches)")


def test_variables_query_functionality(
    typescript_language: tree_sitter.Language,
    typescript_query_dir: Path,
    typescript_ast_tree: tree_sitter.Tree
) -> None:
    """Test variables query against const/let/var declarations from AST sample."""
    query_path = typescript_query_dir / "variables.scm"
    if not query_path.exists():
        pytest.skip("variables.scm not found")

    # Use parsed AST sample tree
    tree = typescript_ast_tree
    query_content = query_path.read_text(encoding="utf-8")
    query = tree_sitter.Query(typescript_language, query_content)

    # Execute query once on entire AST sample
    cursor = tree_sitter.QueryCursor(query)
    matches = cursor.matches(tree.root_node)
    capture_names = {k for _, d in matches for k in d.keys()}

    # AST sample should contain various variable declarations
    assert len(matches) > 0, "variables.scm should capture variable declarations"
    assert 'const_let_variable_name' in capture_names or 'var_variable_name' in capture_names or 'property_name' in capture_names, \
        "Should capture variable names"

    print(f"✓ variables.scm validated against AST sample variable patterns ({len(matches)} matches)")


def test_enums_query_functionality(
    typescript_language: tree_sitter.Language,
    typescript_query_dir: Path,
    typescript_ast_tree: tree_sitter.Tree
) -> None:
    """Test enums query against various enum patterns from AST sample."""
    query_path = typescript_query_dir / "enums.scm"
    if not query_path.exists():
        pytest.skip("enums.scm not found")

    # Use parsed AST sample tree
    tree = typescript_ast_tree
    query_content = query_path.read_text(encoding="utf-8")
    query = tree_sitter.Query(typescript_language, query_content)

    # Execute query once on entire AST sample
    cursor = tree_sitter.QueryCursor(query)
    matches = cursor.matches(tree.root_node)
    capture_names = {k for _, d in matches for k in d.keys()}

    # AST sample should contain enum declarations
    assert len(matches) > 0, "enums.scm should capture enum declarations"
    assert 'enum_name' in capture_names, "Should capture enum names"

    print(f"✓ enums.scm validated against AST sample enum patterns ({len(matches)} matches)")


def test_namespaces_query_functionality(
    typescript_language: tree_sitter.Language,
    typescript_query_dir: Path,
    typescript_ast_tree: tree_sitter.Tree
) -> None:
    """Test namespaces query against namespace declarations from AST sample."""
    query_path = typescript_query_dir / "namespaces.scm"
    if not query_path.exists():
        pytest.skip("namespaces.scm not found")

    # Use parsed AST sample tree
    tree = typescript_ast_tree
    query_content = query_path.read_text(encoding="utf-8")
    query = tree_sitter.Query(typescript_language, query_content)

    # Execute query once on entire AST sample
    cursor = tree_sitter.QueryCursor(query)
    matches = cursor.matches(tree.root_node)
    capture_names = {k for _, d in matches for k in d.keys()}

    # AST sample should contain namespace/module declarations
    assert len(matches) > 0, "namespaces.scm should capture namespace/module declarations"
    assert 'namespace_name' in capture_names or 'module_name' in capture_names or 'module_declaration' in capture_names, \
        "Should capture namespace or module names"

    print(f"✓ namespaces.scm validated against AST sample namespace patterns ({len(matches)} matches)")


def test_query_capture_names_documented(typescript_query_dir: Path) -> None:
    """Verify query files have comments documenting their capture names."""
    for query_name, filename in TYPESCRIPT_QUERY_FILES.items():
        if query_name in OPTIONAL_QUERIES:
            continue

        query_path = typescript_query_dir / filename
        if not query_path.exists():
            continue

        content = query_path.read_text(encoding="utf-8")

        # Check for at least one comment or capture
        has_comment = ";" in content
        has_capture = "@" in content

        assert has_comment or has_capture, f"{filename} should have comments or captures documented"


def test_all_queries_summary(
    typescript_language: tree_sitter.Language,
    typescript_query_dir: Path
) -> None:
    """Summary test showing all query compilation results."""
    results = {}

    for query_name, filename in TYPESCRIPT_QUERY_FILES.items():
        query_path = typescript_query_dir / filename

        if not query_path.exists():
            results[query_name] = "NOT_FOUND"
            continue

        try:
            query_content = query_path.read_text(encoding="utf-8")
            tree_sitter.Query(typescript_language, query_content)
            results[query_name] = "COMPILED"
        except Exception as e:
            results[query_name] = f"FAILED: {str(e)[:50]}"

    # Print summary
    print("\n" + "="*60)
    print("TypeScript Query Validation Summary")
    print("="*60)
    for query_name, status in sorted(results.items()):
        optional_marker = " (optional)" if query_name in OPTIONAL_QUERIES else ""
        status_marker = "✓" if status == "COMPILED" else "✗"
        print(f"{status_marker} {query_name:15} {status:30} {optional_marker}")
    print("="*60)

    # Count results
    compiled = sum(1 for s in results.values() if s == "COMPILED")
    total_required = len([q for q in TYPESCRIPT_QUERY_FILES.keys() if q not in OPTIONAL_QUERIES])

    print(f"\nResults: {compiled}/{len(results)} queries compiled successfully")
    print(f"Required queries: {compiled}/{total_required} compiled")

    # Fail if any required query failed
    failed_required = [
        name for name, status in results.items()
        if status not in ("COMPILED", "NOT_FOUND") and name not in OPTIONAL_QUERIES
    ]

    if failed_required:
        pytest.fail(f"Required queries failed to compile: {', '.join(failed_required)}")
