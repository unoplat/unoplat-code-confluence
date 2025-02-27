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
    def import_prefix(self) -> str:
        """Create a mock import prefix."""
        return "src/code_confluence_flow_bridge"

    def test_class_qualified_name_simple(self, strategy: PythonQualifiedNameStrategy, import_prefix: str) -> None:
        """Test qualified name generation for a simple class path."""
        node_name = "GithubHelper"
        file_path = "/Users/jayghiya/.unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/confluence_git/github_helper.py"
        node_type = "CLASS"

        qualified_name = strategy.get_qualified_name(
            node_name=node_name,
            node_file_path=file_path,
            node_type=node_type,
            import_prefix=import_prefix
        )

        assert qualified_name == "src.code_confluence_flow_bridge.confluence_git.github_helper.GithubHelper"

    def test_python_node_dependency_processor(self, strategy: PythonQualifiedNameStrategy, import_prefix: str) -> None:
        """Test qualified name generation for PythonNodeDependencyProcessor."""
        node_name = "PythonNodeDependencyProcessor"
        file_path = "/Users/jayghiya/.unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/parser/python/python_node_dependency_processor.py"
        node_type = "CLASS"

        qualified_name = strategy.get_qualified_name(
            node_name=node_name,
            node_file_path=file_path,
            node_type=node_type,
            import_prefix=import_prefix
        )

        assert qualified_name == "src.code_confluence_flow_bridge.parser.python.python_node_dependency_processor.PythonNodeDependencyProcessor"

    