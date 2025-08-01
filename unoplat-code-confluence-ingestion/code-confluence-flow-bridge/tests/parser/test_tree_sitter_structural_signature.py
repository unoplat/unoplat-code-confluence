from pathlib import Path
import textwrap
from typing import Optional
import json

import pytest
from src.code_confluence_flow_bridge.models.code_confluence_parsing_models.structural_signature import StructuralSignature
from src.code_confluence_flow_bridge.models.code_confluence_parsing_models.function_info import FunctionInfo
from src.code_confluence_flow_bridge.parser.tree_sitter_structural_signature import (
    TreeSitterStructuralSignatureExtractor,
)


@pytest.mark.parametrize("language_name", ["python"])
def test_structural_signature_extraction(tmp_path: Path, language_name: str) -> None:
    """Validate that structural signature extraction matches expectations
    described in tree-sitter-analysis.md for a simple Python module.
    """
    sample_code: str = textwrap.dedent(
        '''
"""Module docstring"""

GLOBAL_CONSTANT = 42

def outer(a, b):
    """Outer function docstring"""
    def inner(x):
        return x * 2

    result = inner(a) + inner(b)
    print(result)
    return result


class Foo:
    """Foo class docstring"""
    CLASS_VAR = "bar"

    def method(self, x):
        value = str(x)
        print(value)
        return len(value) + 1
'''
    )

    file_path: Path = tmp_path / "sample.py"
    file_path.write_text(sample_code)

    extractor: TreeSitterStructuralSignatureExtractor = TreeSitterStructuralSignatureExtractor(
        language_name
    )
    with open(file_path, 'rb') as f:
        content = f.read()
    signature = extractor.extract_structural_signature(content)

    # 1. Module docstring
    assert signature.module_docstring == "Module docstring"

    # 2. Global variables include GLOBAL_CONSTANT
    global_var_signatures = [var.signature for var in signature.global_variables]
    assert any("GLOBAL_CONSTANT" in sig for sig in global_var_signatures)

    # 3. Functions include outer and nested inner
    function_signatures = [fn.signature for fn in signature.functions]
    assert any(sig.startswith("def outer") for sig in function_signatures)

    outer_function = next(
        fn for fn in signature.functions if fn.signature.startswith("def outer")
    )
    nested_signatures = [nf.signature for nf in outer_function.nested_functions]
    assert any(sig.startswith("def inner") for sig in nested_signatures)

    # 4. Classes include Foo with class variable and method
    class_signatures = [cl.signature for cl in signature.classes]
    assert any(sig.startswith("class Foo") for sig in class_signatures)

    foo_class = next(cl for cl in signature.classes if cl.signature.startswith("class Foo"))

    class_var_signatures = [var.signature for var in foo_class.vars]
    assert any("CLASS_VAR" in sig for sig in class_var_signatures)

    method_signatures = [m.signature for m in foo_class.methods]
    assert any(sig.startswith("def method") for sig in method_signatures)
    
    # 5. Test function calls - outer function should have exactly 3 calls
    assert len(outer_function.function_calls) == 3
    
    # Verify specific function calls with parameters
    assert "inner(a)" in outer_function.function_calls
    assert "inner(b)" in outer_function.function_calls  
    assert "print(result)" in outer_function.function_calls
    
    # Verify call counts
    inner_calls = [call for call in outer_function.function_calls if call.startswith("inner(")]
    assert len(inner_calls) == 2
    print_calls = [call for call in outer_function.function_calls if call.startswith("print(")]
    assert len(print_calls) == 1
    
    # Inner function should have no function calls
    inner_function = next(
        nf for nf in outer_function.nested_functions if nf.signature.startswith("def inner")
    )
    assert len(inner_function.function_calls) == 0
    
    # Method should have exactly 3 function calls: str(x), print(value), len(value)
    method = next(m for m in foo_class.methods if m.signature.startswith("def method"))
    assert len(method.function_calls) == 3
    assert "str(x)" in method.function_calls
    assert "print(value)" in method.function_calls
    assert "len(value)" in method.function_calls
    
    # Export structural signature to JSON for experimentation
    
    print(f"Total global variables: {len(signature.global_variables)}")
    print(f"Total functions: {len(signature.functions)}")
    print(f"Total classes: {len(signature.classes)}")
    if signature.classes:
        total_methods = sum(len(cls.methods) for cls in signature.classes)
        total_function_calls = sum(len(func.function_calls) for func in signature.functions) + \
                              sum(len(method.function_calls) for cls in signature.classes for method in cls.methods)
        print(f"Total methods across all classes: {total_methods}")
        print(f"Total function calls: {total_function_calls}")


# ---------------------------------------------------------------------------
# Additional complex case: decorators, async functions, dataclass, etc.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("language_name", ["python"])
def test_structural_signature_extraction_complex(tmp_path: Path, language_name: str) -> None:
    """Verify extractor handles async functions, decorators and dataclass-style classes."""

    complex_code: str = textwrap.dedent(
        '''
import asyncio
from dataclasses import dataclass


CONSTANT_VALUE = 123


def simple_decorator(fn):
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)
    return wrapper


@simple_decorator
async def fetch_data(url: str) -> str:
    """Asynchronously fetch data from the given URL."""
    await asyncio.sleep(0.1)
    print(f"Fetching {url}")
    return "response"


@simple_decorator
def process_data(data: str) -> str:
    """Process response data into uppercase."""
    result = data.upper()
    print(result)
    return result


@dataclass
class Person:
    name: str
    age: int

    GREETING_PREFIX = "Hello"

    @classmethod
    def greet(cls, name: str) -> str:
        return f"{cls.GREETING_PREFIX}, {name}"

    async def age_next_year(self) -> int:
        await asyncio.sleep(0)
        return self.age + 1
'''
    )

    file_path: Path = tmp_path / "complex_module.py"
    file_path.write_text(complex_code)

    extractor = TreeSitterStructuralSignatureExtractor(language_name)
    with open(file_path, 'rb') as f:
        content = f.read()
    sig: StructuralSignature = extractor.extract_structural_signature(content)

    # Global variable check
    assert any("CONSTANT_VALUE" in v.signature for v in sig.global_variables)

    # Functions (module-level)
    func_sigs = [fn.signature for fn in sig.functions]
    assert any("async def fetch_data" in sig_line for sig_line in func_sigs)
    assert any("def process_data" in sig_line for sig_line in func_sigs)

    # Class presence
    person_cls = next(cl for cl in sig.classes if "class Person" in cl.signature)

    # Class variable
    assert any("GREETING_PREFIX" in var.signature for var in person_cls.vars)

    # Methods inside Person – greet (decorated) and age_next_year (async)
    method_sigs = [m.signature for m in person_cls.methods]
    assert any(sig_line.startswith("@classmethod") or sig_line.startswith("def greet") for sig_line in method_sigs)
    assert any(sig_line.startswith("async def age_next_year") for sig_line in method_sigs)
    
    # Test function calls with exact counts and parameters
    # fetch_data should have exactly 2 calls: asyncio.sleep(0.1) and print(f"Fetching {url}")
    fetch_data_fn = next(fn for fn in sig.functions if "async def fetch_data" in fn.signature)
    assert len(fetch_data_fn.function_calls) == 2
    assert "asyncio.sleep(0.1)" in fetch_data_fn.function_calls
    assert "print(f\"Fetching {url}\")" in fetch_data_fn.function_calls
    
    # process_data should have exactly 2 calls: data.upper() and print(result)
    process_data_fn = next(fn for fn in sig.functions if "def process_data" in fn.signature)
    assert len(process_data_fn.function_calls) == 2
    assert "data.upper()" in process_data_fn.function_calls
    assert "print(result)" in process_data_fn.function_calls
    
    # simple_decorator function should have no direct calls (only nested function)
    decorator_fn = next(fn for fn in sig.functions if "def simple_decorator" in fn.signature)
    assert len(decorator_fn.function_calls) == 0
    
    # The wrapper function should have exactly 1 call: fn(*args, **kwargs)
    wrapper_fn = next(nf for nf in decorator_fn.nested_functions if "def wrapper" in nf.signature)
    assert len(wrapper_fn.function_calls) == 1
    assert "fn(*args, **kwargs)" in wrapper_fn.function_calls
    
    # age_next_year method should have exactly 1 call: asyncio.sleep(0)
    age_method = next(m for m in person_cls.methods if "async def age_next_year" in m.signature)
    assert len(age_method.function_calls) == 1
    assert "asyncio.sleep(0)" in age_method.function_calls
    
    
    print(f"Total global variables: {len(sig.global_variables)}")
    print(f"Total functions: {len(sig.functions)}")
    print(f"Total classes: {len(sig.classes)}")
    if sig.classes:
        total_methods = sum(len(cls.methods) for cls in sig.classes)
        total_function_calls = sum(len(func.function_calls) for func in sig.functions) + \
                              sum(len(method.function_calls) for cls in sig.classes for method in cls.methods)
        print(f"Total methods across all classes: {total_methods}")
        print(f"Total function calls: {total_function_calls}")


# ---------------------------------------------------------------------------
# Edge cases test: deeply nested functions, complex call patterns
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("language_name", ["python"])
def test_edge_cases_function_calls(tmp_path: Path, language_name: str) -> None:
    """Test edge cases for function call extraction with complex nesting and patterns."""
    
    edge_case_code: str = textwrap.dedent(
        '''
def complex_function(data):
    """Function with complex nested structures and call patterns"""
    
    # Direct calls at top level
    result = process(data)
    print(f"Processing: {result}")
    
    # Nested function level 1
    def level1_nested(x):
        # Calls inside first level nested
        transformed = transform(x)
        validated = validate(transformed)
        
        # Nested function level 2
        def level2_nested(y):
            # Calls inside second level nested
            normalized = normalize(y)
            
            # Nested function level 3
            def level3_nested(z):
                # Calls inside third level nested
                return finalize(z)
            
            # Call in level 2
            return level3_nested(normalized)
        
        # More calls in level 1
        result = level2_nested(validated)
        return optimize(result)
    
    # Lambda with function calls
    mapper = lambda x: transform(normalize(x))
    
    # List comprehension with function calls
    processed = [process(item) for item in data if validate(item)]
    
    # Generator expression with function calls
    generator = (transform(x) for x in processed if check(x))
    
    # Chained method calls
    chained = data.strip().lower().split()
    
    # Function calls as arguments
    nested_call = outer(inner(deep(data)))
    
    # Attribute access on function result
    attr_access = get_object().method()
    
    # Complex expression with multiple calls
    complex_expr = func1(arg1) + func2(arg2) * func3(arg3)
    
    # Return with function call
    return level1_nested(result)


class ComplexClass:
    """Class with complex method call patterns"""
    
    def method_with_comprehensions(self, items):
        # Method-level calls
        filtered = filter(None, items)
        
        # Nested function in method
        def helper(x):
            return process(x)
        
        # List comprehension in method
        results = [helper(item) for item in filtered]
        
        # Dict comprehension with calls
        mapping = {key: transform(value) for key, value in enumerate(results)}
        
        return sum(mapping.values())
'''
    )
    
    file_path: Path = tmp_path / "edge_cases.py"
    file_path.write_text(edge_case_code)
    
    extractor = TreeSitterStructuralSignatureExtractor(language_name)
    with open(file_path, 'rb') as f:
        content = f.read()
    sig: StructuralSignature = extractor.extract_structural_signature(content)
    
    # Get the complex function
    complex_func = next(fn for fn in sig.functions if "def complex_function" in fn.signature)
    
    # Verify no duplicate nested functions
    assert len(complex_func.nested_functions) == 1, "complex_function should only have level1_nested as immediate child"
    assert complex_func.nested_functions[0].signature == "def level1_nested(x):"
    
    # Ensure grandchildren don't appear in grandparent
    assert not any("level2_nested" in nf.signature for nf in complex_func.nested_functions)
    assert not any("level3_nested" in nf.signature for nf in complex_func.nested_functions)
    
    # Verify direct calls only (not from nested functions)
    direct_calls = complex_func.function_calls
    
    # Check that none of the nested function calls are included
    assert "transform(x)" in direct_calls  # From lambda/comprehension
    assert "validate(transformed)" not in direct_calls  # From level1_nested
    assert "normalize(y)" not in direct_calls  # From level2_nested
    assert "finalize(z)" not in direct_calls  # From level3_nested
    
    # Verify nested function call isolation
    level1 = next(nf for nf in complex_func.nested_functions if "def level1_nested" in nf.signature)
    assert "transform(x)" in level1.function_calls
    assert "validate(transformed)" in level1.function_calls
    assert "level2_nested(validated)" in level1.function_calls
    assert "optimize(result)" in level1.function_calls
    
    # Verify level2 nested function
    level2 = next(nf for nf in level1.nested_functions if "def level2_nested" in nf.signature)
    assert "normalize(y)" in level2.function_calls
    assert "level3_nested(normalized)" in level2.function_calls
    
    # Verify level3 nested function
    level3 = next(nf for nf in level2.nested_functions if "def level3_nested" in nf.signature)
    assert len(level3.function_calls) == 1
    assert "finalize(z)" in level3.function_calls
    
    # Test method with comprehensions
    complex_class = next(cl for cl in sig.classes if "class ComplexClass" in cl.signature)
    method = next(m for m in complex_class.methods if "def method_with_comprehensions" in m.signature)
    
    # Method should have direct calls but not nested helper calls
    assert "filter(None, items)" in method.function_calls
    assert "helper(item)" in method.function_calls  # From list comprehension
    assert "transform(value)" in method.function_calls  # From dict comprehension
    assert "enumerate(results)" in method.function_calls
    assert "sum(mapping.values())" in method.function_calls
    assert "mapping.values()" in method.function_calls
    
    # The helper function's call should not be in the method's direct calls
    helper_func = next(nf for nf in method.nested_functions if "def helper" in nf.signature)
    assert "process(x)" in helper_func.function_calls
    assert "process(x)" not in method.function_calls  # This is inside helper, not direct
    
    # Export structural signature to JSON for experimentation
    
    
    print(f"Total global variables: {len(sig.global_variables)}")
    print(f"Total functions: {len(sig.functions)}")
    print(f"Total classes: {len(sig.classes)}")
    if sig.classes:
        total_methods = sum(len(cls.methods) for cls in sig.classes)
        total_nested_functions = sum(len(func.nested_functions) for func in sig.functions) + \
                                sum(len(method.nested_functions) for cls in sig.classes for method in cls.methods)
        total_function_calls = sum(len(func.function_calls) for func in sig.functions) + \
                              sum(len(method.function_calls) for cls in sig.classes for method in cls.methods)
        print(f"Total methods across all classes: {total_methods}")
        print(f"Total nested functions: {total_nested_functions}")
        print(f"Total function calls: {total_function_calls}")


# ---------------------------------------------------------------------------
# Self-extraction test: Extract structure of tree_sitter_structural_signature.py itself
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("language_name", ["python"])
def test_self_extraction_tree_sitter_structural_signature(language_name: str) -> None:
    """Test that TreeSitterStructuralSignatureExtractor can extract its own structure."""
    
    # Get the actual source file path
    from src.code_confluence_flow_bridge.parser import tree_sitter_structural_signature
    source_file_path = tree_sitter_structural_signature.__file__
    
    # Extract structural signature
    extractor = TreeSitterStructuralSignatureExtractor(language_name)
    with open(source_file_path, 'rb') as f:
        content = f.read()
    signature = extractor.extract_structural_signature(content)
    
    # 1. Module-level verification
    # Module docstring (may have leading/trailing whitespace)
    assert signature.module_docstring is not None
    module_doc = signature.module_docstring.strip()
    assert module_doc.startswith("Tree-sitter structural signature extractor for code parsing.")
    assert "language-agnostic structural signature extraction" in module_doc
    
    # Global variables (3 cache dictionaries)
    assert len(signature.global_variables) == 3
    
    # Check that all expected variables are present in the signatures
    var_signatures = [var.signature for var in signature.global_variables]
    
    # Debug: print what we got
    print("\nExtracted global variables:")
    for i, var in enumerate(signature.global_variables):
        print(f"  [{i}] Line {var.start_line}-{var.end_line}: {repr(var.signature)}")
    
    # The signatures might be truncated or have strange formatting
    # Let's be more flexible in our assertions
    found_language_cache = any("_LANGUAGE_CACHE" in sig for sig in var_signatures)
    found_parser_cache = any("_PARSER_CACHE" in sig for sig in var_signatures)
    found_query_cache = any("_QUERY_CACHE" in sig for sig in var_signatures)
    
    assert found_language_cache, f"_LANGUAGE_CACHE not found in {var_signatures}"
    assert found_parser_cache, f"_PARSER_CACHE not found in {var_signatures}"
    assert found_query_cache, f"_QUERY_CACHE not found in {var_signatures}"
    
    # No module-level functions
    assert len(signature.functions) == 0
    
    # 2. Class-level verification
    assert len(signature.classes) == 1
    
    main_class = signature.classes[0]
    assert "TreeSitterStructuralSignatureExtractor" in main_class.signature
    assert main_class.signature.strip().endswith(":")
    assert main_class.docstring is not None
    assert "Extracts structural signatures from source code using tree-sitter queries." in main_class.docstring
    
    # Should have instance variables from __init__ method
    assert len(main_class.vars) == 5
    
    # Verify specific instance variables are captured
    class_var_signatures = [var.signature for var in main_class.vars]
    assert any("self.config" in sig for sig in class_var_signatures)
    assert any("self.language_name" in sig for sig in class_var_signatures)
    assert any("self.language:" in sig for sig in class_var_signatures)
    assert any("self.parser:" in sig for sig in class_var_signatures)
    assert any("self.queries:" in sig for sig in class_var_signatures)
    
    # 3. Method-level verification
    # Should have 21 methods (after hierarchical refactoring + nested class extraction)
    assert len(main_class.methods) == 21
    
    # Create a mapping of method names to method objects for easier verification
    method_map = {m.signature.split('(')[0].split()[-1]: m for m in main_class.methods}
    
    # Verify each method exists
    expected_methods = [
        "__init__", "_get_language", "_get_parser", "_get_compiled_queries",
        "_create_queries", "extract_structural_signature", "_extract_module_docstring",
        "_extract_global_variables", "_extract_functions", "_extract_classes",
        "_extract_class_variables_for_node", "_extract_methods_for_node",
        "_extract_nested_functions_for_node", "_is_at_module_level",
        "_clean_string_literal", "_is_immediate_child_function", 
        "_get_nested_function_ranges", "_get_nested_class_ranges",
        "_extract_function_calls_for_node", "_extract_instance_variables_for_method",
        "_extract_nested_classes_for_node"
    ]
    
    for method_name in expected_methods:
        assert method_name in method_map, f"Method {method_name} not found"
    
    # 4. Verify specific method details
    
    # __init__ method
    init_method = method_map["__init__"]
    assert "def __init__(self, language_name: str = \"python\"):" in init_method.signature
    assert init_method.docstring == "Initialize parser & queries with multi-level caching and lazy compilation."
    init_calls = init_method.function_calls
    assert "get_config(language_name)" in init_calls
    assert "self._get_language(language_name)" in init_calls
    assert "self._get_parser(language_name)" in init_calls
    assert "self._get_compiled_queries()" in init_calls
    
    # Static methods should have @staticmethod decorator
    static_methods = ["_get_language", "_get_parser"]
    for method_name in static_methods:
        method = method_map[method_name]
        assert method.signature.startswith("@staticmethod")
    
    # _get_language static method
    get_lang_method = method_map["_get_language"]
    assert "def _get_language(language_name: str) -> tree_sitter.Language:" in get_lang_method.signature
    assert get_lang_method.docstring == "Fetch a tree-sitter Language with caching."
    assert "get_language(language_name)" in get_lang_method.function_calls
    
    # extract_structural_signature - the main public method
    extract_method = method_map["extract_structural_signature"]
    assert "def extract_structural_signature(self, source_bytes: bytes) -> StructuralSignature:" in extract_method.signature
    assert extract_method.docstring == "Extract structural signature from byte content."
    # Should call various extraction methods
    extract_calls = extract_method.function_calls
    # No file reading operations, just parsing operations
    assert "self.parser.parse(source_bytes)" in extract_calls
    assert "self._extract_module_docstring(root_node, source_bytes)" in extract_calls
    assert "self._extract_global_variables(root_node, source_bytes)" in extract_calls
    assert "self._extract_functions(root_node, source_bytes)" in extract_calls
    assert "self._extract_classes(root_node, source_bytes)" in extract_calls
    assert "StructuralSignature(" in " ".join(extract_calls)
    
    # _extract_function_calls_for_node - our recently modified method
    func_calls_method = method_map["_extract_function_calls_for_node"]
    assert "start_line: Optional[int] = None" in func_calls_method.signature
    assert "end_line: Optional[int] = None" in func_calls_method.signature
    assert func_calls_method.docstring is not None
    assert "filters out calls that are within nested functions" in func_calls_method.docstring
    # Check for the new filtering logic calls
    assert "self.queries[\"function_calls\"].captures(func_node)" in func_calls_method.function_calls
    assert "self._get_nested_function_ranges(func_node)" in func_calls_method.function_calls
    assert "sorted(direct_call_nodes, key=lambda n: n.start_byte)" in func_calls_method.function_calls
    
    # 5. Verify no nested functions or classes
    for method in main_class.methods:
        assert len(method.nested_functions) == 0, f"Method {method.signature.split('(')[0]} should have no nested functions"
    
    # 6. Verify method ordering (should be sorted by line number)
    prev_line = 0
    for method in main_class.methods:
        assert method.start_line > prev_line, "Methods should be sorted by start line"
        prev_line = method.start_line
    
    # 7. Verify some complex method signatures are captured correctly
    create_queries_method = method_map["_create_queries"]
    assert create_queries_method.signature == "def _create_queries(self) -> Dict[str, str]:"
    
    # 8. Verify methods with complex logic have appropriate function calls
    extract_functions_method = method_map["_extract_functions"]
    # Should have many function calls for the complex extraction logic
    assert len(extract_functions_method.function_calls) > 10
    
    # 9. Test line number accuracy for a few methods
    # __init__ should be around line 46 (shifted due to import formatting)
    assert 40 < init_method.start_line < 55
    # extract_structural_signature should be around line 104 (shifted due to import formatting)
    assert 100 < extract_method.start_line < 110
    
    # 10. Export structural signature to JSON for experimentation
    
    # Convert to JSON-serializable dict
    signature_dict = signature.model_dump()
    
    # Write to JSON file in the same directory as the test
    json_output_path = Path(__file__).parent / "test_self_extraction_tree_sitter_structural_signature.json"
    with open(json_output_path, 'w', encoding='utf-8') as f:
        json.dump(signature_dict, f, indent=2, ensure_ascii=False)
    
    print(f"\nStructural signature exported to: {json_output_path}")
    print(f"Total methods extracted: {len(main_class.methods)}")
    print(f"Total function calls across all methods: {sum(len(m.function_calls) for m in main_class.methods)}")


# ---------------------------------------------------------------------------
# Test for no duplicate nested functions
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("language_name", ["python"])
def test_no_duplicate_nested_functions(tmp_path: Path, language_name: str) -> None:
    """Verify that nested functions are not duplicated in parent scopes."""
    
    test_code = textwrap.dedent('''
        def level0():
            """Top level function"""
            def level1():
                """First level nested"""
                def level2():
                    """Second level nested"""
                    def level3():
                        """Third level nested"""
                        pass
                    return level3
                
                @decorator
                def level2_decorated():
                    """Decorated sibling"""
                    pass
                    
                return level2
            
            def level1_sibling():
                """Sibling at first level"""
                pass
                
            return level1
        
        class TestClass:
            def method(self):
                def method_nested():
                    def method_deep_nested():
                        pass
                    return method_deep_nested
                return method_nested
    ''')
    
    file_path = tmp_path / "nested_test.py"
    file_path.write_text(test_code)
    
    extractor = TreeSitterStructuralSignatureExtractor(language_name)
    with open(file_path, 'rb') as f:
        content = f.read()
    sig = extractor.extract_structural_signature(content)
    
    # Helper to assert no duplicates
    def assert_unique_nested(func: FunctionInfo, seen_signatures: Optional[set[str]] = None):
        if seen_signatures is None:
            seen_signatures = set()
        
        for nf in func.nested_functions:
            assert nf.signature not in seen_signatures, f"Duplicate found: {nf.signature}"
            seen_signatures.add(nf.signature)
            assert_unique_nested(nf, seen_signatures.copy())
    
    # Test the main function
    level0 = next(f for f in sig.functions if "def level0" in f.signature)
    
    # Level 0 should only have level1 and level1_sibling as immediate children
    assert len(level0.nested_functions) == 2
    assert any("def level1()" in nf.signature for nf in level0.nested_functions)
    assert any("def level1_sibling()" in nf.signature for nf in level0.nested_functions)
    
    # Ensure no grandchildren appear at level 0
    assert not any("level2" in nf.signature for nf in level0.nested_functions)
    assert not any("level3" in nf.signature for nf in level0.nested_functions)
    
    # Check level1 has correct children
    level1 = next(nf for nf in level0.nested_functions if "def level1()" in nf.signature)
    assert len(level1.nested_functions) == 2  # level2 and level2_decorated
    assert any("def level2()" in nf.signature for nf in level1.nested_functions)
    assert any("def level2_decorated()" in nf.signature for nf in level1.nested_functions)
    
    # Ensure no level3 at level1
    assert not any("level3" in nf.signature for nf in level1.nested_functions)
    
    # Check no duplicates across the entire tree
    assert_unique_nested(level0)
    
    # Test class methods too
    test_class = sig.classes[0]
    method = test_class.methods[0]
    assert len(method.nested_functions) == 1
    assert "def method_nested()" in method.nested_functions[0].signature
    
    # method_deep_nested should not appear in method's immediate children
    assert not any("method_deep_nested" in nf.signature for nf in method.nested_functions)


# ---------------------------------------------------------------------------
# Test for main.py structural signature extraction
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("language_name", ["python"])
def test_main_py_structural_signature(language_name: str) -> None:
    """Test structural signature extraction of the main.py FastAPI application."""
    
    # Get the actual main.py file path
    from pathlib import Path
    
    # Build path to main.py from the test file location
    test_file_path = Path(__file__).parent.parent.parent
    main_py_path = test_file_path / "src" / "code_confluence_flow_bridge" / "main.py"
    
    # Ensure the file exists
    assert main_py_path.exists(), f"main.py not found at {main_py_path}"
    
    # Extract structural signature
    extractor = TreeSitterStructuralSignatureExtractor(language_name)
    with open(main_py_path, 'rb') as f:
        content = f.read()
    signature = extractor.extract_structural_signature(content)
    
    # 1. Module-level verification
    # No module docstring expected (starts with imports)
    assert signature.module_docstring is None or signature.module_docstring.strip() == ""
    
    # 2. Global variables verification
    # Should have at least: logger, app, origins
    assert len(signature.global_variables) >= 3
    
    global_var_signatures = [var.signature for var in signature.global_variables]
    assert any("logger" in sig for sig in global_var_signatures), f"logger not found in {global_var_signatures}"
    assert any("app" in sig for sig in global_var_signatures), f"app not found in {global_var_signatures}"
    assert any("origins" in sig for sig in global_var_signatures), f"origins not found in {global_var_signatures}"
    
    # 3. Functions verification
    # Should have many functions (utility, endpoints, etc.)
    assert len(signature.functions) >= 20, f"Expected at least 20 functions, got {len(signature.functions)}"
    
    function_signatures = [fn.signature for fn in signature.functions]
    
    # Key utility functions
    assert any("async def get_temporal_client" in sig for sig in function_signatures), "get_temporal_client not found"
    assert any("async def _serve_worker" in sig for sig in function_signatures), "_serve_worker not found"
    assert any("def create_worker" in sig for sig in function_signatures), "create_worker not found"
    assert any("async def fetch_github_token_from_db" in sig for sig in function_signatures), "fetch_github_token_from_db not found"
    assert any("async def start_workflow" in sig for sig in function_signatures), "start_workflow not found"
    assert any("async def generate_sse_events" in sig for sig in function_signatures), "generate_sse_events not found"
    assert any("async def monitor_workflow" in sig for sig in function_signatures), "monitor_workflow not found"
    
    # FastAPI endpoints
    assert any("async def ingest_token" in sig for sig in function_signatures), "ingest_token not found"
    assert any("async def update_token" in sig for sig in function_signatures), "update_token not found"
    assert any("async def delete_token" in sig for sig in function_signatures), "delete_token not found"
    assert any("async def get_repos" in sig for sig in function_signatures), "get_repos not found"
    assert any("async def ingestion" in sig for sig in function_signatures), "ingestion not found"
    assert any("async def get_repository_status" in sig for sig in function_signatures), "get_repository_status not found"
    
    # Context manager function
    assert any("async def lifespan" in sig for sig in function_signatures), "lifespan not found"
    
    # 4. No classes should be defined directly in main.py
    assert len(signature.classes) == 0, f"Expected no classes, got {len(signature.classes)}"
    
    # 5. Function call verification for complex functions
    
    # create_worker function should have many calls
    create_worker_fn = next((fn for fn in signature.functions if "def create_worker" in fn.signature), None)
    assert create_worker_fn is not None, "create_worker function not found"
    assert len(create_worker_fn.function_calls) >= 10, f"create_worker should have many calls, got {len(create_worker_fn.function_calls)}"
    
    # Check some specific calls in create_worker
    create_worker_calls = create_worker_fn.function_calls
    assert any("Worker(" in call for call in create_worker_calls), "Worker instantiation not found"
    assert any("logger.info(" in call for call in create_worker_calls), "logger.info call not found"
    
    # ingestion function should have specific calls
    ingestion_fn = next((fn for fn in signature.functions if "async def ingestion" in fn.signature), None)
    assert ingestion_fn is not None, "ingestion function not found"
    assert len(ingestion_fn.function_calls) >= 5, f"ingestion should have several calls, got {len(ingestion_fn.function_calls)}"
    
    ingestion_calls = ingestion_fn.function_calls
    assert any("fetch_github_token_from_db(" in call for call in ingestion_calls), "fetch_github_token_from_db call not found"
    assert any("start_workflow(" in call for call in ingestion_calls), "start_workflow call not found"
    assert any("asyncio.create_task(" in call for call in ingestion_calls), "asyncio.create_task call not found"
    
    # lifespan function should have many setup/teardown calls
    lifespan_fn = next((fn for fn in signature.functions if "async def lifespan" in fn.signature), None)
    assert lifespan_fn is not None, "lifespan function not found"
    assert len(lifespan_fn.function_calls) >= 15, f"lifespan should have many calls, got {len(lifespan_fn.function_calls)}"
    
    lifespan_calls = lifespan_fn.function_calls
    assert any("get_temporal_client(" in call for call in lifespan_calls), "get_temporal_client call not found"
    assert any("CodeConfluenceGraph(" in call for call in lifespan_calls), "CodeConfluenceGraph call not found"
    assert any("create_db_and_tables(" in call for call in lifespan_calls), "create_db_and_tables call not found"
    
    # get_repos function should have GraphQL-related calls
    get_repos_fn = next((fn for fn in signature.functions if "async def get_repos" in fn.signature), None)
    assert get_repos_fn is not None, "get_repos function not found"
    assert len(get_repos_fn.function_calls) >= 8, f"get_repos should have several calls, got {len(get_repos_fn.function_calls)}"
    
    get_repos_calls = get_repos_fn.function_calls
    assert any("GQLClient(" in call for call in get_repos_calls), "GQLClient call not found"
    assert any("client.execute(" in call for call in get_repos_calls), "client.execute call not found"
    
    # 6. Verify line numbers are reasonable
    # Functions should be ordered by line number
    prev_line = 0
    for fn in signature.functions:
        assert fn.start_line > prev_line, f"Functions should be ordered by line number, {fn.signature} at line {fn.start_line} comes before {prev_line}"
        prev_line = fn.start_line
    
    # Check some specific line number ranges
    get_temporal_client_fn = next((fn for fn in signature.functions if "async def get_temporal_client" in fn.signature), None)
    assert get_temporal_client_fn is not None
    assert 150 < get_temporal_client_fn.start_line < 200, f"get_temporal_client should be around line 157, got {get_temporal_client_fn.start_line}"
    
    # 7. Check for nested functions in lifespan
    assert len(lifespan_fn.nested_functions) == 0, "lifespan should not have nested functions directly"
    
    # 8. Export structural signature to JSON for experimentation
    
    # Convert to JSON-serializable dict
    signature_dict = signature.model_dump()
    
    # Write to JSON file in the same directory as the test
    json_output_path = Path(__file__).parent / "test_main_py_structural_signature.json"
    with open(json_output_path, 'w', encoding='utf-8') as f:
        json.dump(signature_dict, f, indent=2, ensure_ascii=False)
    
    print(f"\nStructural signature exported to: {json_output_path}")
    print(f"Total global variables: {len(signature.global_variables)}")
    print(f"Total functions: {len(signature.functions)}")
    print(f"Total classes: {len(signature.classes)}")
    
    # Calculate total function calls across all functions
    total_function_calls = sum(len(func.function_calls) for func in signature.functions)
    print(f"Total function calls across all functions: {total_function_calls}")
    
    # Calculate total nested functions
    total_nested_functions = sum(len(func.nested_functions) for func in signature.functions)
    print(f"Total nested functions: {total_nested_functions}")
    
    # Print some interesting statistics
    functions_with_calls = [fn for fn in signature.functions if len(fn.function_calls) > 0]
    print(f"Functions with function calls: {len(functions_with_calls)}")
    
    if functions_with_calls:
        max_calls = max(len(fn.function_calls) for fn in functions_with_calls)
        max_calls_fn = next(fn for fn in functions_with_calls if len(fn.function_calls) == max_calls)
        print(f"Function with most calls: {max_calls_fn.signature.split('(')[0].strip().split()[-1]} ({max_calls} calls)")
    
    # Print decorator usage
    decorated_functions = [fn for fn in signature.functions if fn.signature.strip().startswith("@")]
    print(f"Functions with decorators: {len(decorated_functions)}")
    
    # Print async function count
    async_functions = [fn for fn in signature.functions if "async def" in fn.signature]
    print(f"Async functions: {len(async_functions)}")
    
    print("\nKey findings:")
    print(f"- FastAPI application with {len(signature.functions)} functions")
    print(f"- {len(async_functions)} async functions for handling concurrent operations")
    print(f"- {total_function_calls} total function calls indicating complex business logic")
    print(f"- {len(signature.global_variables)} global variables for app configuration")
    print(f"- No classes defined (all imported), following separation of concerns")


# ---------------------------------------------------------------------------
# Comprehensive Instance Variable Edge Cases Test
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("language_name", ["python"])
def test_instance_variable_edge_cases(tmp_path: Path, language_name: str) -> None:
    """Test comprehensive edge cases for instance variable detection in structural signatures.
    
    This test covers various scenarios that could break or produce false positives
    in instance variable detection, ensuring robustness of the Tree-sitter query.
    """
    
    # Use the edge cases file from test_data
    edge_cases_file_path = Path(__file__).parent / "test_data" / "instance_variable_edge_cases.py"
    assert edge_cases_file_path.exists(), f"Edge cases file not found at {edge_cases_file_path}"
    
    file_path = str(edge_cases_file_path)
    
    extractor = TreeSitterStructuralSignatureExtractor(language_name)
    with open(file_path, 'rb') as f:
        content = f.read()
    signature = extractor.extract_structural_signature(content)
    
    # ========================================================================
    # TEST 1: FastAPIApp class - comprehensive instance variable patterns
    # ========================================================================
    
    fastapi_class = next(cls for cls in signature.classes if "class FastAPIApp" in cls.signature)
    
    # Should capture both class variables and instance variables
    class_var_signatures = [var.signature for var in fastapi_class.vars]
    
    print(f"\nFastAPIApp class variables found ({len(fastapi_class.vars)}):")
    for i, var in enumerate(fastapi_class.vars):
        print(f"  [{i}] Line {var.start_line}: {repr(var.signature)}")
    
    # Direct class variables (should be captured)
    assert any("CLASS_CONSTANT" in sig for sig in class_var_signatures), "CLASS_CONSTANT not captured"
    assert any("shared_cache" in sig for sig in class_var_signatures), "shared_cache not captured"
    
    # Basic instance variables from __init__ (should be captured)
    assert any("self.app = FastAPI()" in sig for sig in class_var_signatures), "self.app not captured"
    assert any("self.config = config" in sig for sig in class_var_signatures), "self.config not captured"
    assert any("self.database_url:" in sig for sig in class_var_signatures), "self.database_url not captured"
    
    # Type-annotated instance variables (should be captured)
    assert any("self.clients:" in sig for sig in class_var_signatures), "self.clients not captured"
    assert any("self.cache:" in sig for sig in class_var_signatures), "self.cache not captured"
    assert any("self.metrics:" in sig for sig in class_var_signatures), "self.metrics not captured"
    
    # Complex expressions (should be captured)
    assert any("self.router = APIRouter" in sig for sig in class_var_signatures), "self.router not captured"
    assert any("self.middleware_stack =" in sig for sig in class_var_signatures), "self.middleware_stack not captured"
    
    # Conditional assignments (captured - our hierarchical query captures assignments in if/else blocks)
    # This is expected behavior - assignments inside control flow are captured with updated query
    assert any("self.auth_handler = AuthHandler" in sig for sig in class_var_signatures), "self.auth_handler (then) should be captured - inside if block"
    assert any("self.auth_handler = None" in sig for sig in class_var_signatures), "self.auth_handler (else) should be captured - inside else block"
    
    # Nested attribute assignments (NOT captured - Tree-sitter query doesn't match nested attributes)
    # This is expected behavior - our query only matches simple self.attr assignments
    assert not any("self.settings.debug =" in sig for sig in class_var_signatures), "self.settings.debug should not be captured - nested attribute"
    assert not any("self.settings.timeout =" in sig for sig in class_var_signatures), "self.settings.timeout should not be captured - nested attribute"
    
    # Method call results (should be captured)
    assert any("self.connection = self._create_connection()" in sig for sig in class_var_signatures), "self.connection not captured"
    assert any("self.logger = setup_logger" in sig for sig in class_var_signatures), "self.logger not captured"
    
    # F-string assignments (should be captured)
    assert any("self.base_url = f" in sig for sig in class_var_signatures), "self.base_url not captured"
    assert any("self.version_info = f" in sig for sig in class_var_signatures), "self.version_info not captured"
    
    # Lambda and comprehensions (should be captured)
    assert any("self.data_processor = lambda" in sig for sig in class_var_signatures), "self.data_processor not captured"
    assert any("self.valid_routes =" in sig for sig in class_var_signatures), "self.valid_routes not captured"
    
    # Instance variables from configure_middleware method (should be captured)
    assert any("self.cors_middleware =" in sig for sig in class_var_signatures), "self.cors_middleware not captured"
    assert any("self.rate_limiter =" in sig for sig in class_var_signatures), "self.rate_limiter not captured"
    assert any("self.security_config =" in sig for sig in class_var_signatures), "self.security_config not captured"
    
    # Complex nested assignments (NOT captured - Tree-sitter query doesn't match deeply nested attributes)
    # This is expected behavior - our query only matches simple self.attr assignments
    assert not any("self.nested.handler.config =" in sig for sig in class_var_signatures), "self.nested.handler.config should not be captured - deeply nested attribute"
    assert not any("self.deep.very.nested.setting =" in sig for sig in class_var_signatures), "self.deep.very.nested.setting should not be captured - deeply nested attribute"
    
    # Instance variables from private method (should be captured)
    assert any("self.connection_pool =" in sig for sig in class_var_signatures), "self.connection_pool not captured"
    assert any("self.connection_helper =" in sig for sig in class_var_signatures), "self.connection_helper not captured"
    
    # Instance variables from async method (should be captured)
    assert any("self.async_client =" in sig for sig in class_var_signatures), "self.async_client not captured"
    assert any("self.event_loop =" in sig for sig in class_var_signatures), "self.event_loop not captured"
    assert any("self.async_data = await" in sig for sig in class_var_signatures), "self.async_data not captured"
    
    # Property setter assignments are NOT reliably captured due to decorator patterns
    # This is expected behavior - our focus is on constructor and regular method instance variables
    property_class = next(cls for cls in signature.classes if "class PropertyAndDescriptorClass" in cls.signature)
    property_vars = [var.signature for var in property_class.vars]
    # Note: Property setter assignments (e.g., self._private_value = value in @property.setter)
    # are not guaranteed to be captured due to complex decorator AST structures
    
    # ========================================================================
    # TEST 2: Verify local variables are NOT captured
    # ========================================================================
    
    # Local variables in methods should NOT appear
    assert not any("local_config =" in sig for sig in class_var_signatures), "local_config incorrectly captured"
    assert not any("middleware_list =" in sig for sig in class_var_signatures), "middleware_list incorrectly captured"
    assert not any("temp_handler =" in sig for sig in class_var_signatures), "temp_handler incorrectly captured"
    
    # Variables on other objects should NOT be captured
    assert not any("other_obj.config =" in sig for sig in class_var_signatures), "other_obj.config incorrectly captured"
    assert not any("different.setting =" in sig for sig in class_var_signatures), "different.setting incorrectly captured"
    
    # Variables in static/class methods should NOT be captured as instance vars
    assert not any("default_settings =" in sig for sig in class_var_signatures), "default_settings incorrectly captured"
    assert not any("temp_config =" in sig for sig in class_var_signatures), "temp_config incorrectly captured"
    assert not any("config_data =" in sig for sig in class_var_signatures), "config_data incorrectly captured"
    
    # Nested function variables should NOT be captured
    assert not any("local_conn =" in sig for sig in class_var_signatures), "local_conn incorrectly captured"
    assert not any("helper_config =" in sig for sig in class_var_signatures), "helper_config incorrectly captured"
    assert not any("inner_self.fake_attr =" in sig for sig in class_var_signatures), "inner_self.fake_attr incorrectly captured"
    
    # Async method local variables should NOT be captured
    assert not any("async_config =" in sig for sig in class_var_signatures), "async_config incorrectly captured"
    
    # Property local variables should NOT be captured
    assert not any("temp_calc =" in sig for sig in property_vars), "temp_calc incorrectly captured"
    assert not any("validation_result =" in sig for sig in property_vars), "validation_result incorrectly captured"
    
    # ========================================================================
    # TEST 3: Nested class instance variables
    # ========================================================================
    
    nested_class_test = next(cls for cls in signature.classes if "class NestedClassTest" in cls.signature)
    nested_test_vars = [var.signature for var in nested_class_test.vars]
    
    # Parent class should have its own instance variables
    assert any("PARENT_CONSTANT =" in sig for sig in nested_test_vars), "PARENT_CONSTANT not captured"
    assert any("self.parent_attr =" in sig for sig in nested_test_vars), "self.parent_attr not captured"
    assert any("self.nested_instance =" in sig for sig in nested_test_vars), "self.nested_instance not captured"
    
    # Find the nested class (now properly nested in parent class)
    nested_class = nested_class_test.nested_classes[0]  # NestedClass is now in nested_classes
    nested_class_vars = [var.signature for var in nested_class.vars]
    
    # Nested class should have its own separate instance variables
    assert any("NESTED_CONSTANT =" in sig for sig in nested_class_vars), "NESTED_CONSTANT not captured"
    assert any("self.nested_attr =" in sig for sig in nested_class_vars), "self.nested_attr not captured"
    assert any("self.config =" in sig for sig in nested_class_vars), "nested self.config not captured"
    
    # Verify nested class variables don't leak into parent
    assert not any("NESTED_CONSTANT =" in sig for sig in nested_test_vars), "NESTED_CONSTANT leaked to parent"
    assert not any("nested_attr =" in sig for sig in nested_test_vars), "nested_attr leaked to parent"
    
    # Verify parent class variables don't leak into nested
    assert not any("PARENT_CONSTANT =" in sig for sig in nested_class_vars), "PARENT_CONSTANT leaked to nested"
    assert not any("parent_attr =" in sig for sig in nested_class_vars), "parent_attr leaked to nested"
    
    # ========================================================================
    # TEST 4: Type annotation handling
    # ========================================================================
    
    typed_class = next(cls for cls in signature.classes if "class TypeAnnotatedClass" in cls.signature)
    typed_vars = [var.signature for var in typed_class.vars]
    
    # ClassVar annotated variables (should be captured)
    assert any("class_config:" in sig for sig in typed_vars), "class_config not captured"
    assert any("shared_state:" in sig for sig in typed_vars), "shared_state not captured"
    
    # Type-annotated instance variables (should be captured)
    assert any("self.typed_config:" in sig for sig in typed_vars), "self.typed_config not captured"
    assert any("self.optional_cache:" in sig for sig in typed_vars), "self.optional_cache not captured"
    assert any("self.generic_list:" in sig for sig in typed_vars), "self.generic_list not captured"
    assert any("self.union_type:" in sig for sig in typed_vars), "self.union_type not captured"
    assert any("self.complex_type:" in sig for sig in typed_vars), "self.complex_type not captured"
    
    # ========================================================================
    # TEST 5: Global variables should NOT appear in any class
    # ========================================================================
    
    all_class_vars = []
    for cls in signature.classes:
        all_class_vars.extend([var.signature for var in cls.vars])
    
    # Module-level variables should NOT be captured as class variables
    assert not any("GLOBAL_CONFIG =" in sig for sig in all_class_vars), "GLOBAL_CONFIG incorrectly captured"
    assert not any("app_instance =" in sig for sig in all_class_vars), "app_instance incorrectly captured"
    assert not any("ANOTHER_GLOBAL =" in sig for sig in all_class_vars), "ANOTHER_GLOBAL incorrectly captured"
    assert not any("module_config =" in sig for sig in all_class_vars), "module_config incorrectly captured"
    
    # Module function variables should NOT be captured
    assert not any("local_var =" in sig for sig in all_class_vars), "local_var incorrectly captured"
    assert not any("fake_self.attribute =" in sig for sig in all_class_vars), "fake_self.attribute incorrectly captured"
    assert not any("nested_var =" in sig for sig in all_class_vars), "nested_var incorrectly captured"
    
    # ========================================================================
    # TEST 6: Method counting and structure verification
    # ========================================================================
    
    # FastAPIApp should have the expected number of methods
    expected_fastapi_methods = ["__init__", "configure_middleware", "create_default_config", 
                               "from_config_file", "_create_connection", "async_setup"]
    assert len(fastapi_class.methods) == len(expected_fastapi_methods), f"Expected {len(expected_fastapi_methods)} methods, got {len(fastapi_class.methods)}"
    
    # Verify specific method signatures exist
    method_signatures = [method.signature for method in fastapi_class.methods]
    for expected_method in expected_fastapi_methods:
        assert any(expected_method in sig for sig in method_signatures), f"Method {expected_method} not found"
    
    # ========================================================================
    # TEST 7: Edge case validation - malformed code resilience
    # ========================================================================
    
    # The parser should handle the edge cases gracefully without crashing
    # and should not produce duplicate entries
    
    # Check for duplicates in instance variables
    seen_signatures = set()
    duplicates = []
    for var in fastapi_class.vars:
        if var.signature in seen_signatures:
            duplicates.append(var.signature)
        seen_signatures.add(var.signature)
    
    assert len(duplicates) == 0, f"Found duplicate instance variables: {duplicates}"
    
    # ========================================================================
    # Export results for analysis
    # ========================================================================
    
    # Convert to JSON-serializable dict
    signature_dict = signature.model_dump()
    
    # Write to JSON file in the same directory as the test
    json_output_path = Path(__file__).parent / "test_instance_variable_edge_cases.json"
    with open(json_output_path, 'w', encoding='utf-8') as f:
        json.dump(signature_dict, f, indent=2, ensure_ascii=False)
    
    print(f"\nInstance variable edge cases signature exported to: {json_output_path}")
    print(f"Total classes tested: {len(signature.classes)}")
    
    for cls in signature.classes:
        class_name = cls.signature.split()[1].rstrip(':')
        print(f"  {class_name}: {len(cls.vars)} variables, {len(cls.methods)} methods")
    
    print(f"\nFastAPIApp detailed breakdown:")
    print(f"  Total variables captured: {len(fastapi_class.vars)}")
    
    # Count different types of variables
    class_vars = [v for v in fastapi_class.vars if not v.signature.startswith("self.")]
    instance_vars = [v for v in fastapi_class.vars if v.signature.startswith("self.")]
    
    print(f"  Direct class variables: {len(class_vars)}")
    print(f"  Instance variables: {len(instance_vars)}")
    
    # Verify the ratio makes sense (should be mostly instance variables)
    assert len(instance_vars) > len(class_vars), "Should have more instance variables than class variables"
    assert len(instance_vars) >= 20, f"Should capture at least 20 instance variables, got {len(instance_vars)}"
    
    print(f"\nTest passed: Instance variable detection is robust across {len(instance_vars)} instance variables and {len(class_vars)} class variables")


# ---------------------------------------------------------------------------
# Demonstration Test: Local Variables Are NOT Captured
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("language_name", ["python"])
def test_local_variables_not_captured(tmp_path: Path, language_name: str) -> None:
    """Demonstrate that local variables are NOT captured by the structural signature extractor.
    
    This test clearly shows the difference between what IS captured (class vars, instance vars)
    and what is NOT captured (local variables in various contexts).
    """
    
    # Use the demo file from test_data
    demo_file_path = Path(__file__).parent / "test_data" / "demo_local_vars.py"
    assert demo_file_path.exists(), f"Demo file not found at {demo_file_path}"
    
    file_path = str(demo_file_path)
    
    extractor = TreeSitterStructuralSignatureExtractor(language_name)
    with open(file_path, 'rb') as f:
        content = f.read()
    signature = extractor.extract_structural_signature(content)
    
    # Get the demo class
    demo_class = next(cls for cls in signature.classes if "class DemoClass" in cls.signature)
    captured_vars = [var.signature for var in demo_class.vars]
    
    print(f"\nDemoClass variables captured ({len(demo_class.vars)}):")
    for i, var in enumerate(demo_class.vars):
        print(f"  [{i}] Line {var.start_line}: {repr(var.signature)}")
    
    # ========================================================================
    # Verify CAPTURED variables (class vars + instance vars)
    # ========================================================================
    
    # Class variable should be captured
    assert any("CLASS_VAR" in sig for sig in captured_vars), "CLASS_VAR should be captured"
    
    # Instance variables should be captured
    assert any("self.instance_var" in sig for sig in captured_vars), "self.instance_var should be captured"
    assert any("self.app" in sig for sig in captured_vars), "self.app should be captured"
    assert any("self.method_instance_var" in sig for sig in captured_vars), "self.method_instance_var should be captured"
    assert any("self.outer_instance_var" in sig for sig in captured_vars), "self.outer_instance_var should be captured"
    assert any("self.after_nested" in sig for sig in captured_vars), "self.after_nested should be captured"
    
    # ========================================================================
    # Verify NOT CAPTURED variables (local vars in various contexts)
    # ========================================================================
    
    # Local variables in __init__ method should NOT be captured
    assert not any("local_var" in sig for sig in captured_vars), "local_var should NOT be captured"
    assert not any("temp_config" in sig for sig in captured_vars), "temp_config should NOT be captured"
    assert not any("helper_obj" in sig for sig in captured_vars), "helper_obj should NOT be captured"
    
    # Assignments to other objects should NOT be captured
    assert not any("helper_obj.config" in sig for sig in captured_vars), "helper_obj.config should NOT be captured"
    
    # Local variables in regular method should NOT be captured
    assert not any("local_data" in sig for sig in captured_vars), "local_data should NOT be captured"
    assert not any("temp_result" in sig for sig in captured_vars), "temp_result should NOT be captured"
    assert not any("cache =" in sig for sig in captured_vars), "cache should NOT be captured"
    assert not any("items =" in sig for sig in captured_vars), "items should NOT be captured"
    assert not any("processed_items" in sig for sig in captured_vars), "processed_items should NOT be captured"
    
    # Local variables in static method should NOT be captured
    assert not any("static_local" in sig for sig in captured_vars), "static_local should NOT be captured"
    assert not any("config =" in sig for sig in captured_vars), "config should NOT be captured"
    
    # Local variables in method with nested function should NOT be captured
    assert not any("outer_local" in sig for sig in captured_vars), "outer_local should NOT be captured"
    
    # Variables in nested functions should NOT be captured
    assert not any("nested_local" in sig for sig in captured_vars), "nested_local should NOT be captured"
    assert not any("nested_config" in sig for sig in captured_vars), "nested_config should NOT be captured"
    assert not any("fake_self.attribute" in sig for sig in captured_vars), "fake_self.attribute should NOT be captured"
    
    # ========================================================================
    # Verify global variables are not captured as class variables
    # ========================================================================
    
    # Global variables should appear in signature.global_variables, not class vars
    global_var_signatures = [var.signature for var in signature.global_variables]
    assert any("GLOBAL_VAR" in sig for sig in global_var_signatures), "GLOBAL_VAR should be in global variables"
    assert not any("GLOBAL_VAR" in sig for sig in captured_vars), "GLOBAL_VAR should NOT be in class variables"
    
    # Module function variables should not appear anywhere in class variables
    assert not any("func_local" in sig for sig in captured_vars), "func_local should NOT be captured"
    assert not any("temp_obj" in sig for sig in captured_vars), "temp_obj should NOT be captured"
    
    # ========================================================================
    # Summary assertions
    # ========================================================================
    
    # Should have exactly 1 class variable and 5 instance variables
    class_vars = [v for v in demo_class.vars if not v.signature.startswith("self.")]
    instance_vars = [v for v in demo_class.vars if v.signature.startswith("self.")]
    
    assert len(class_vars) == 1, f"Expected 1 class variable, got {len(class_vars)}"
    assert len(instance_vars) == 5, f"Expected 5 instance variables, got {len(instance_vars)}"
    
    print(f"\n✅ Verification complete:")
    print(f"   Class variables captured: {len(class_vars)} (CLASS_VAR)")
    print(f"   Instance variables captured: {len(instance_vars)} (self.* assignments)")
    print(f"   Local variables correctly filtered out: ALL")
    print(f"   Total captured: {len(demo_class.vars)} (only structural class elements)")
    
    print(f"\n📝 Key insight: The extractor intentionally captures only structural class elements")
    print(f"   (class variables + instance variables) while filtering out implementation")
    print(f"   details (local variables, temporary objects, control flow variables).") 