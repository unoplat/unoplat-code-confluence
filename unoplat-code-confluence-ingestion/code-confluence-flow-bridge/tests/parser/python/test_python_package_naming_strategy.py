# Standard Library
from pathlib import Path

# Third Party
import pytest

# First Party
from src.code_confluence_flow_bridge.parser.python.python_package_naming_strategy import PythonPackageNamingStrategy


class TestPythonPackageNamingStrategy:
    @pytest.fixture
    def strategy(self) -> PythonPackageNamingStrategy:
        """Create a PythonPackageNamingStrategy instance."""
        return PythonPackageNamingStrategy()

    def test_get_package_name(self, strategy: PythonPackageNamingStrategy) -> None:
        """Test package name generation from file path."""
        # Given
        file_path = "/Users/jayghiya/.unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src/code_confluence_flow_bridge/confluence_git/github_helper.py"
        import_prefix = "src/code_confluence_flow_bridge"

        # When
        package_name = strategy.get_package_name(file_path, import_prefix)

        # Then
        assert package_name == "src.code_confluence_flow_bridge.confluence_git" 