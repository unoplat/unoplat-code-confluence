#!/usr/bin/env python3
"""
Tests for PythonLinkNestedFunction to verify it correctly identifies nested functions
and sets the parent_function_name field in UnoplatChapiForgeFunction objects.
"""

# Standard Library
from typing import Dict, List, Optional

# Third Party
import pytest

# First Party
from src.code_confluence_flow_bridge.parser.python.python_link_nested_function import PythonLinkNestedFunction
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_chapi_forge_function import UnoplatChapiForgeFunction
from src.code_confluence_flow_bridge.parser.tree_sitter.code_confluence_tree_sitter import CodeConfluenceTreeSitter
from src.code_confluence_flow_bridge.models.configuration.settings import ProgrammingLanguage


class TestPythonLinkNestedFunction:
    """Test suite for Python link nested function functionality."""

    @pytest.fixture
    def tree_sitter(self) -> CodeConfluenceTreeSitter:
        """Create CodeConfluenceTreeSitter instance for Python."""
        return CodeConfluenceTreeSitter(language=ProgrammingLanguage.PYTHON)

    @pytest.fixture
    def nested_linker(self, tree_sitter: CodeConfluenceTreeSitter) -> PythonLinkNestedFunction:
        """Create PythonLinkNestedFunction instance."""
        return PythonLinkNestedFunction(tree_sitter)

    def test_simple_nested_function(self, nested_linker: PythonLinkNestedFunction) -> None:
        """Test identification of a simple nested function."""
        # Full file content with a single nested function
        file_content = '''def outer_function(name):
    def inner_function():
        return "Hello"
    greeting = inner_function()
    return f"{greeting}, {name}!"
'''
        
        # Create UnoplatChapiForgeFunction objects with full content
        outer_func = UnoplatChapiForgeFunction(
            Name="outer_function",
            Content='''def outer_function(name):
    def inner_function():
        return "Hello"
    greeting = inner_function()
    return f"{greeting}, {name}!"''',
            QualifiedName="module.outer_function"
        )
        
        inner_func = UnoplatChapiForgeFunction(
            Name="inner_function",
            Content='''def inner_function():
    return "Hello"''',
            QualifiedName="module.inner_function"
        )
        
        functions = [outer_func, inner_func]
        
        # Process nested functions
        nested_linker.process_nested_functions(functions, file_content)
        
        # Assertions
        assert outer_func.parent_function_name is None
        assert inner_func.parent_function_name == "module.outer_function"

    def test_multiple_nested_functions(self, nested_linker: PythonLinkNestedFunction) -> None:
        """Test identification of multiple nested functions within the same parent."""
        # File content with multiple nested functions
        file_content = '''def parent_function(x, y):
    def nested_func1():
        return x + y
    
    def nested_func2():
        return x * y
    
    return nested_func1() + nested_func2()
'''
        
        # Create UnoplatChapiForgeFunction objects
        parent_func = UnoplatChapiForgeFunction(
            Name="parent_function",
            Content='''def parent_function(x, y):
    def nested_func1():
        return x + y
    
    def nested_func2():
        return x * y
    
    return nested_func1() + nested_func2()''',
            QualifiedName="module.parent_function"
        )
        
        nested_func1 = UnoplatChapiForgeFunction(
            Name="nested_func1",
            Content='''def nested_func1():
    return x + y''',
            QualifiedName="module.nested_func1"
        )
        
        nested_func2 = UnoplatChapiForgeFunction(
            Name="nested_func2",
            Content='''def nested_func2():
    return x * y''',
            QualifiedName="module.nested_func2"
        )
        
        functions = [parent_func, nested_func1, nested_func2]
        
        # Process nested functions
        nested_linker.process_nested_functions(functions, file_content)
        
        # Assertions
        assert parent_func.parent_function_name is None
        assert nested_func1.parent_function_name == "module.parent_function"
        assert nested_func2.parent_function_name == "module.parent_function"

    def test_nested_functions_with_decorators(self, nested_linker: PythonLinkNestedFunction) -> None:
        """Test identification of nested functions with decorators."""
        # File content with decorators
        file_content = '''def outer_function():
    @decorator
    def inner_function():
        return "Hello"
    
    return inner_function()
'''
        
        # Create UnoplatChapiForgeFunction objects
        outer_func = UnoplatChapiForgeFunction(
            Name="outer_function",
            Content='''def outer_function():
    @decorator
    def inner_function():
        return "Hello"
    
    return inner_function()''',
            QualifiedName="module.outer_function"
        )
        
        inner_func = UnoplatChapiForgeFunction(
            Name="inner_function",
            Content='''@decorator
def inner_function():
    return "Hello"''',
            QualifiedName="module.inner_function"
        )
        
        functions = [outer_func, inner_func]
        
        # Process nested functions
        nested_linker.process_nested_functions(functions, file_content)
        
        # Assertions
        assert outer_func.parent_function_name is None
        assert inner_func.parent_function_name == "module.outer_function"

    def test_multi_level_nested_functions(self, nested_linker: PythonLinkNestedFunction) -> None:
        """Test identification of multi-level nested functions."""
        # File content with multi-level nesting
        file_content = '''def level1():
    def level2():
        def level3():
            return "deeply nested"
        return level3()
    return level2()
'''
        
        # Create UnoplatChapiForgeFunction objects
        level1_func = UnoplatChapiForgeFunction(
            Name="level1",
            Content='''def level1():
    def level2():
        def level3():
            return "deeply nested"
        return level3()
    return level2()''',
            QualifiedName="module.level1"
        )
        
        level2_func = UnoplatChapiForgeFunction(
            Name="level2",
            Content='''def level2():
    def level3():
        return "deeply nested"
    return level3()''',
            QualifiedName="module.level2"
        )
        
        level3_func = UnoplatChapiForgeFunction(
            Name="level3",
            Content='''def level3():
    return "deeply nested"''',
            QualifiedName="module.level3"
        )
        
        functions = [level1_func, level2_func, level3_func]
        
        # Process nested functions
        nested_linker.process_nested_functions(functions, file_content)
        
        # Assertions
        assert level1_func.parent_function_name is None
        assert level2_func.parent_function_name == "module.level1"
        assert level3_func.parent_function_name == "module.level2"

    def test_conditional_nested_functions(self, nested_linker: PythonLinkNestedFunction) -> None:
        """Test identification of nested functions within conditional blocks."""
        # File content with conditional nested functions
        file_content = '''def outer(x):
    if x > 0:
        def inner():
            return x
    else:
        def inner():
            return -x
    return inner()
'''
        
        # Create UnoplatChapiForgeFunction objects
        outer_func = UnoplatChapiForgeFunction(
            Name="outer",
            Content='''def outer(x):
    if x > 0:
        def inner():
            return x
    else:
        def inner():
            return -x
    return inner()''',
            QualifiedName="module.outer"
        )
        
        inner_func = UnoplatChapiForgeFunction(
            Name="inner",
            Content='''def inner():
    return x''',
            QualifiedName="module.inner"
        )
        
        functions = [outer_func, inner_func]
        
        # Process nested functions
        nested_linker.process_nested_functions(functions, file_content)
        
        # Assertions
        assert outer_func.parent_function_name is None
        assert inner_func.parent_function_name == "module.outer"

    def test_nested_functions_in_class_methods(self, nested_linker: PythonLinkNestedFunction) -> None:
        """Test identification of nested functions within class methods."""
        # File content with nested functions in class methods
        file_content = '''class MyClass:
    def method(self):
        def inner_function():
            return "Inside method"
        return inner_function()
'''
        
        # Create UnoplatChapiForgeFunction objects
        method_func = UnoplatChapiForgeFunction(
            Name="method",
            Content='''def method(self):
    def inner_function():
        return "Inside method"
    return inner_function()''',
            QualifiedName="module.MyClass.method"
        )
        
        inner_func = UnoplatChapiForgeFunction(
            Name="inner_function",
            Content='''def inner_function():
    return "Inside method"''',
            QualifiedName="module.inner_function"
        )
        
        functions = [method_func, inner_func]
        
        # Process nested functions
        nested_linker.process_nested_functions(functions, file_content)
        
        # Assertions
        assert method_func.parent_function_name is None
        assert inner_func.parent_function_name == "module.MyClass.method"

    def test_no_nested_functions(self, nested_linker: PythonLinkNestedFunction) -> None:
        """Test behavior when there are no nested functions."""
        # File content with no nested functions
        file_content = '''def func1():
    return "Hello"

def func2():
    return "World"
'''
        
        # Create UnoplatChapiForgeFunction objects
        func1 = UnoplatChapiForgeFunction(
            Name="func1",
            Content='''def func1():
    return "Hello"''',
            QualifiedName="module.func1"
        )
        
        func2 = UnoplatChapiForgeFunction(
            Name="func2",
            Content='''def func2():
    return "World"''',
            QualifiedName="module.func2"
        )
        
        functions = [func1, func2]
        
        # Process nested functions
        nested_linker.process_nested_functions(functions, file_content)
        
        # Assertions
        assert func1.parent_function_name is None
        assert func2.parent_function_name is None

    def test_extract_function_signature(self, nested_linker: PythonLinkNestedFunction) -> None:
        """Test the _extract_function_signature method directly."""
        # Test with a simple function
        simple_content = '''def simple_function():
    return "Hello"'''
        assert (
            nested_linker._extract_function_signature(simple_content) ==
            'def simple_function():'
        )
        
        # Test with a decorated function
        decorated_content = '''@decorator
@another_decorator
def decorated_function():
    return "Hello"'''
        assert (
            nested_linker._extract_function_signature(decorated_content) ==
            'def decorated_function():'
        )
        
        # Test with empty content
        assert nested_linker._extract_function_signature('') is None

    def test_edge_cases(self, nested_linker: PythonLinkNestedFunction) -> None:
        """Test edge cases and potential error conditions."""
        # Empty input
        functions: List[UnoplatChapiForgeFunction] = []
        nested_linker.process_nested_functions(functions, '')
        assert functions == []
        
        # Functions with no content
        func_no_content = UnoplatChapiForgeFunction(
            Name="func_no_content",
            Content="",
            QualifiedName="module.func_no_content"
        )
        functions_list = [func_no_content]
        nested_linker.process_nested_functions(functions_list, 'def func_no_content(): pass')
        assert func_no_content.parent_function_name is None
