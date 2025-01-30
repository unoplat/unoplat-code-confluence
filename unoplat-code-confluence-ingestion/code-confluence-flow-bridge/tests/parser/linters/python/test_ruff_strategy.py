# Standard Library
import os
import shutil
from pathlib import Path
from typing import Dict, List

# Third Party
import pytest
import tomlkit
from tomlkit.items import Comment, Table

# First Party
from src.code_confluence_flow_bridge.models.configuration.settings import ProgrammingLanguage
from src.code_confluence_flow_bridge.models.workflow.code_confluence_linter import LinterType
from src.code_confluence_flow_bridge.parser.linters.linter_factory import LinterStrategyFactory
from src.code_confluence_flow_bridge.parser.linters.linter_strategy import LinterStrategy


class TestRuffStrategy:
    @pytest.fixture
    def sample_project_path(self) -> str:
        """Get path to sample project for testing.
        
        Returns:
            str: Absolute path to sample project directory
        """
        return str(Path(__file__).parent.parent.parent.parent / "test_data" / "linter_python" / "sample_project")
    
    @pytest.fixture(autouse=True)
    def cleanup_after_test(self, sample_project_path: str) -> None:
        """Cleanup fixture to restore files after test.
        
        This fixture:
        1. Stores original file contents
        2. Runs the test
        3. Restores original files and removes generated files
        """
        # Store original contents
        pyproject_path = os.path.join(sample_project_path, "pyproject.toml")
        main_py_path = os.path.join(sample_project_path, "main.py")
        
        with open(pyproject_path, 'r', encoding='utf-8') as f:
            original_pyproject = f.read()
        with open(main_py_path, 'r', encoding='utf-8') as f:
            original_main = f.read()
            
        # Let test run
        yield
        
        # Cleanup: Restore original files
        with open(pyproject_path, 'w', encoding='utf-8') as f:
            f.write(original_pyproject)
        with open(main_py_path, 'w', encoding='utf-8') as f:
            f.write(original_main)
            
        # Remove generated files
        ruff_config = os.path.join(sample_project_path, "ruff.toml")
        if os.path.exists(ruff_config):
            os.remove(ruff_config)
            
        ruff_cache = os.path.join(sample_project_path, ".ruff_cache")
        if os.path.exists(ruff_cache):
            shutil.rmtree(ruff_cache)
    
    def test_ruff_linting(self, sample_project_path: str) -> None:
        """Test Ruff linting functionality.
        
        Args:
            sample_project_path: Path to test project
            
        Tests:
            1. Linter detects violations
            2. Existing Ruff config is commented out
            3. New config is created with correct settings
        """
        # Get Ruff strategy
        strategy: LinterStrategy = LinterStrategyFactory.get_strategy(
            programming_language=ProgrammingLanguage.PYTHON,
            linter_type=LinterType.RUFF
        )
        
        # Run linting
        result: bool = strategy.lint_codebase(
            local_workspace_path=sample_project_path,
            dependencies=[],  # type: ignore  # No dependencies needed for this test
            programming_language_version=">=3.11"
        )
        
        # Should return True because there are linting violations
        assert result is True
        
        # Verify pyproject.toml was modified
        pyproject_path: str = os.path.join(sample_project_path, "pyproject.toml")
        with open(pyproject_path, "r", encoding="utf-8") as f:
            content: Dict[str, Table] = tomlkit.parse(f.read())  # type: ignore
        
        # Check that Ruff sections were removed
        assert 'tool' not in content or 'ruff' not in content['tool']
        
        # Also verify no Ruff-related sections exist
        if 'tool' in content:
            tool_section = content['tool']
            assert all(not key.startswith('ruff') for key in tool_section.keys())
        
        # Verify new ruff.toml was created
        ruff_config_path: str = os.path.join(sample_project_path, "ruff.toml")
        assert os.path.exists(ruff_config_path)
        
        # Verify content of ruff.toml
        with open(ruff_config_path, "r", encoding="utf-8") as f:
            ruff_config: Dict[str, Any] = tomlkit.parse(f.read())  # type: ignore
            
        assert ruff_config["target-version"] == "py311"
        assert sample_project_path in ruff_config["src"]
        assert "I" in ruff_config["lint"]["select"]
        assert "E402" in ruff_config["lint"]["select"] 