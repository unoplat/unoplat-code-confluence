# Standard Library
import os
from pathlib import Path
from typing import Dict

# Third Party
import pytest

# First Party
from src.code_confluence_flow_bridge.parser.python.python_qualified_name_strategy import PythonQualifiedNameStrategy

class TestPythonQualifiedNameStrategy:
    @pytest.fixture
    def strategy(self) -> PythonQualifiedNameStrategy:
        """Create a PythonQualifiedNameStrategy instance."""
        return PythonQualifiedNameStrategy()

    @pytest.fixture
    def workspace_path(self) -> str:
        """Create a mock workspace path."""
        return "/workspace/project"

    def test_class_qualified_name_simple(self, strategy: PythonQualifiedNameStrategy, workspace_path: str) -> None:
        """Test qualified name generation for a simple class path."""
        node_name = "MyClass"
        file_path = "/workspace/project/module/file.py"
        node_type = "CLASS"

        qualified_name = strategy.get_qualified_name(
            node_name=node_name,
            node_file_path=file_path,
            local_workspace_path=workspace_path,
            node_type=node_type
        )

        assert qualified_name == "module.file.MyClass"

    def test_class_qualified_name_nested_packages(self, strategy: PythonQualifiedNameStrategy, workspace_path: str) -> None:
        """Test qualified name generation for a class in nested packages."""
        node_name = "MyClass"
        file_path = "/workspace/project/package/subpackage/module/file.py"
        node_type = "CLASS"

        qualified_name = strategy.get_qualified_name(
            node_name=node_name,
            node_file_path=file_path,
            local_workspace_path=workspace_path,
            node_type=node_type
        )

        assert qualified_name == "package.subpackage.module.file.MyClass"

    def test_function_qualified_name(self, strategy: PythonQualifiedNameStrategy, workspace_path: str) -> None:
        """Test qualified name generation for a function."""
        node_name = "my_function"
        file_path = "/workspace/project/module/file.py"
        node_type = "FUNCTION"

        qualified_name = strategy.get_qualified_name(
            node_name=node_name,
            node_file_path=file_path,
            local_workspace_path=workspace_path,
            node_type=node_type
        )

        assert qualified_name == "module.file"

    
    def test_same_directory_level(self, strategy: PythonQualifiedNameStrategy) -> None:
        """Test qualified name generation when file is at workspace root."""
        node_name = "MyClass"
        file_path = "/workspace/project/file.py"
        workspace_path = "/workspace/project"
        node_type = "CLASS"

        qualified_name = strategy.get_qualified_name(
            node_name=node_name,
            node_file_path=file_path,
            local_workspace_path=workspace_path,
            node_type=node_type
        )

        assert qualified_name == "file.MyClass"
