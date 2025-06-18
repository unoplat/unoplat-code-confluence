from pathlib import Path
import textwrap

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
    signature = extractor.extract_structural_signature(str(file_path))

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

    class_var_signatures = [var.signature for var in foo_class.class_variables]
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
    import json
    from pathlib import Path
    
    # Convert to JSON-serializable dict
    signature_dict = signature.model_dump()
    
    # Write to JSON file in the same directory as the test
    json_output_path = Path(__file__).parent / "test_structural_signature_extraction.json"
    with open(json_output_path, 'w', encoding='utf-8') as f:
        json.dump(signature_dict, f, indent=2, ensure_ascii=False)
    
    print(f"\nStructural signature exported to: {json_output_path}")
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
    sig: StructuralSignature = extractor.extract_structural_signature(str(file_path))

    # Global variable check
    assert any("CONSTANT_VALUE" in v.signature for v in sig.global_variables)

    # Functions (module-level)
    func_sigs = [fn.signature for fn in sig.functions]
    assert any("async def fetch_data" in sig_line for sig_line in func_sigs)
    assert any("def process_data" in sig_line for sig_line in func_sigs)

    # Class presence
    person_cls = next(cl for cl in sig.classes if "class Person" in cl.signature)

    # Class variable
    assert any("GREETING_PREFIX" in var.signature for var in person_cls.class_variables)

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
    
    # Export structural signature to JSON for experimentation
    import json
    from pathlib import Path
    
    # Convert to JSON-serializable dict
    signature_dict = sig.model_dump()
    
    # Write to JSON file in the same directory as the test
    json_output_path = Path(__file__).parent / "test_structural_signature_extraction_complex.json"
    with open(json_output_path, 'w', encoding='utf-8') as f:
        json.dump(signature_dict, f, indent=2, ensure_ascii=False)
    
    print(f"\nStructural signature exported to: {json_output_path}")
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
    sig: StructuralSignature = extractor.extract_structural_signature(str(file_path))
    
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
    import json
    from pathlib import Path
    
    # Convert to JSON-serializable dict
    signature_dict = sig.model_dump()
    
    # Write to JSON file in the same directory as the test
    json_output_path = Path(__file__).parent / "test_edge_cases_function_calls.json"
    with open(json_output_path, 'w', encoding='utf-8') as f:
        json.dump(signature_dict, f, indent=2, ensure_ascii=False)
    
    print(f"\nStructural signature exported to: {json_output_path}")
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
    signature = extractor.extract_structural_signature(source_file_path)
    
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
    assert "Extracts structural signatures from source code using tree-sitter queries." in main_class.docstring
    
    # No class variables
    assert len(main_class.class_variables) == 0
    
    # 3. Method-level verification
    # Should have 19 methods (including the new _is_immediate_child_function)
    assert len(main_class.methods) == 19
    
    # Create a mapping of method names to method objects for easier verification
    method_map = {m.signature.split('(')[0].split()[-1]: m for m in main_class.methods}
    
    # Verify each method exists
    expected_methods = [
        "__init__", "_get_language", "_get_parser", "_get_compiled_queries",
        "_create_queries", "extract_structural_signature", "_extract_module_docstring",
        "_extract_global_variables", "_extract_functions", "_extract_classes",
        "_extract_class_variables_for_node", "_extract_methods_for_node",
        "_extract_nested_functions_for_node", "_is_at_module_level",
        "_is_class_level_variable", "_clean_string_literal", "_is_immediate_child_function",
        "_get_nested_function_ranges", "_extract_function_calls_for_node"
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
    assert "def extract_structural_signature(self, file_path: str) -> StructuralSignature:" in extract_method.signature
    assert extract_method.docstring == "Extract structural signature from a source code file."
    # Should call various extraction methods
    extract_calls = extract_method.function_calls
    assert "open(file_path, 'rb')" in extract_calls
    assert "f.read()" in extract_calls
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
    # __init__ should be around line 35
    assert 30 < init_method.start_line < 45
    # extract_structural_signature should be around line 93
    assert 90 < extract_method.start_line < 100
    
    # 10. Export structural signature to JSON for experimentation
    import json
    from pathlib import Path
    
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
    sig = extractor.extract_structural_signature(str(file_path))
    
    # Helper to assert no duplicates
    def assert_unique_nested(func: FunctionInfo, seen_signatures: set = None):
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