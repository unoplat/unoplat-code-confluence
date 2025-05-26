# Standard Library
import os
import tempfile
from pathlib import Path
from unittest import mock

# Third Party
import pytest

# First Party
from src.code_confluence_flow_bridge.parser.package_manager.detectors.registry import _matches, detect_manager


@pytest.fixture
def temp_repo():
    """Create a temporary directory to simulate a repository"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


class TestDetectorRegistry:
    def test_matches_simple_file(self, temp_repo):
        # Create a test file
        test_file = temp_repo / "requirements.txt"
        test_file.touch()
        
        # Test simple string signature
        assert _matches(temp_repo, "requirements.txt")
        
        # Test file dict signature
        assert _matches(temp_repo, {"file": "requirements.txt"})
        
        # Test non-existent file
        assert not _matches(temp_repo, "nonexistent.txt")
    
    def test_matches_with_content(self, temp_repo):
        # Create a test file with content
        test_file = temp_repo / "pyproject.toml"
        test_file.write_text("[tool.poetry]\nname = \"test\"\n")
        
        # Test with content match
        assert _matches(temp_repo, {
            "file": "pyproject.toml",
            "contains": "[tool.poetry]"
        })
        
        # Test with content mismatch
        assert not _matches(temp_repo, {
            "file": "pyproject.toml",
            "contains": "[tool.uv]"
        })
    
    def test_matches_with_glob(self, temp_repo):
        # Create test files
        (temp_repo / "requirements-dev.txt").touch()
        (temp_repo / "requirements-prod.txt").touch()
        
        # Test glob pattern
        assert _matches(temp_repo, {"glob": "requirements-*.txt"})
        
        # Test glob with no matches
        assert not _matches(temp_repo, {"glob": "*.lock"})
    
    @mock.patch("src.code_confluence_flow_bridge.parser.package_manager.detectors.registry.RULES")
    def test_detect_manager(self, mock_rules, temp_repo):
        # Setup mock rules
        mock_rules.get.return_value = [
            {
                "manager": "poetry",
                "signatures": [
                    {"file": "poetry.lock"},
                    {"file": "pyproject.toml", "contains": "[tool.poetry]"}
                ]
            },
            {
                "manager": "pip",
                "signatures": [
                    "requirements.txt",
                    {"glob": "requirements-*.txt"}
                ]
            }
        ]
        
        # Create a requirements.txt file
        (temp_repo / "requirements.txt").touch()
        
        # Test detection
        assert detect_manager(temp_repo, "python") == "pip"
        
        # Create a poetry.lock file (should be detected first due to order)
        (temp_repo / "poetry.lock").touch()
        assert detect_manager(temp_repo, "python") == "poetry"
        
        # Test with no matches
        mock_rules.get.return_value = []
        assert detect_manager(temp_repo, "python") is None
        
    def test_detect_manager_integration(self, temp_repo):
        """Integration test using actual rules.yaml"""
        # Create a requirements.txt file
        (temp_repo / "requirements.txt").touch()
        
        # Test detection
        assert detect_manager(temp_repo, "python") == "pip"
        
        # Create a poetry.lock file (should take precedence)
        (temp_repo / "poetry.lock").touch()
        assert detect_manager(temp_repo, "python") == "poetry"
        
        # Create a uv.lock file (should take precedence over poetry)
        (temp_repo / "uv.lock").touch()
        assert detect_manager(temp_repo, "python") == "uv"
