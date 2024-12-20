from typing import List, Optional

import pytest
from unoplat_code_confluence.data_models.chapi.chapi_functioncall import ChapiFunctionCall
from unoplat_code_confluence.data_models.chapi_forge.unoplat_chapi_forge_function import UnoplatChapiForgeFunction
from unoplat_code_confluence.parser.python.in_class_dependency.sort_function_dependencies import SortFunctionDependencies


@pytest.fixture
def sort_dependencies() -> SortFunctionDependencies:
    """Fixture for SortFunctionDependencies."""
    return SortFunctionDependencies()

def create_function(
    name: str,
    calls: Optional[List[tuple[Optional[str], str]]] = None
) -> UnoplatChapiForgeFunction:
    """Helper to create test functions with dependencies.

    Args:
        name: Function name
        calls: List of tuples (node_name, function_name) representing function calls
    """
    function = UnoplatChapiForgeFunction(
        QualifiedName=f"test_module.{name}",
        Name=name
    )

    if calls:
        function.function_calls = [
            ChapiFunctionCall(
                NodeName=node_name,
                FunctionName=func_name
            ) for node_name, func_name in calls
        ]
    return function

class TestSortFunctionDependencies:
    
    def test_class_only_simple_chain(self, sort_dependencies: SortFunctionDependencies):
        """Test sorting class methods with a simple dependency chain."""
        functions = [
            create_function("method_c", [("self", "method_b")]),
            create_function("method_a"),
            create_function("method_b", [("self", "method_a")])
        ]
        
        result = sort_dependencies.sort_function_dependencies(
            functions=functions,
            node_type="CLASS"
        )
        
        # Expected order: method_a -> method_b -> method_c
        assert [f.name for f in result] == ["method_a", "method_b", "method_c"]

    def test_class_only_no_dependencies(self, sort_dependencies: SortFunctionDependencies):
        """Test sorting class methods with no dependencies."""
        functions = [
            create_function("method_a"),
            create_function("method_b"),
            create_function("method_c")
        ]
        
        result = sort_dependencies.sort_function_dependencies(
            functions=functions,
            node_type="CLASS"
        )
        
        # Order should be preserved when no dependencies exist
        assert [f.name for f in result] == ["method_a", "method_b", "method_c"]

    def test_class_only_with_cycle(self, sort_dependencies: SortFunctionDependencies):
        """Test handling of cyclic dependencies in class methods."""
        functions = [
            create_function("method_a", [("self", "method_b")]),
            create_function("method_b", [("self", "method_c")]),
            create_function("method_c", [("self", "method_a")])
        ]
        
        result = sort_dependencies.sort_function_dependencies(
            functions=functions,
            node_type="CLASS"
        )
        
        # Should return original order when cycle is detected
        assert result == functions

    def test_procedural_only_simple_chain(self, sort_dependencies: SortFunctionDependencies):
        """Test sorting procedural functions with a simple dependency chain."""
        functions = [
            create_function("func_c", [(None, "func_b")]),
            create_function("func_a"),
            create_function("func_b", [(None, "func_a")])
        ]
        
        result = sort_dependencies.sort_function_dependencies(
            functions=functions,
            node_type="PROCEDURAL"
        )
        
        # Expected order: func_a -> func_b -> func_c
        assert [f.name for f in result] == ["func_a", "func_b", "func_c"]

    def test_procedural_only_no_dependencies(self, sort_dependencies: SortFunctionDependencies):
        """Test sorting procedural functions with no dependencies."""
        functions = [
            create_function("func_a"),
            create_function("func_b"),
            create_function("func_c")
        ]
        
        result = sort_dependencies.sort_function_dependencies(
            functions=functions,
            node_type="PROCEDURAL"
        )
        
        # Order should be preserved when no dependencies exist
        assert [f.name for f in result] == ["func_a", "func_b", "func_c"]

    def test_procedural_only_with_cycle(self, sort_dependencies: SortFunctionDependencies):
        """Test sorting procedural functions with cyclic dependencies."""
        functions = [
            create_function("func_a", [(None, "func_b")]),
            create_function("func_b", [(None, "func_c")]),
            create_function("func_c", [(None, "func_a")])
        ]
        
        result = sort_dependencies.sort_function_dependencies(
            functions=functions,
            node_type="PROCEDURAL"
        )
        
        # Should return original order when cycle is detected
        assert result == functions

    def test_empty_functions_list(self, sort_dependencies: SortFunctionDependencies):
        """Test handling empty functions list."""
        result = sort_dependencies.sort_function_dependencies(
            functions=[],
            node_type="CLASS"
        )
        
        assert result == []