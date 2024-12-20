# Standard Library
import os
import shutil
from pathlib import Path

# Third Party
import pytest

# First Party
from unoplat_code_confluence.configuration.settings import AppSettings
from unoplat_code_confluence.confluence_git.github_helper import GithubHelper

# Use the example config file path
TEST_CONFIG_PATH = Path(__file__).parent.parent.parent / "example_config_code_confluence.json"
TEST_OUTPUT_DIR = Path("test_output")

@pytest.fixture(scope="module")
def settings():
    """Load test settings"""
    assert TEST_CONFIG_PATH.exists(), f"Config file not found at {TEST_CONFIG_PATH}"
    return AppSettings.get_settings(str(TEST_CONFIG_PATH))

@pytest.fixture(scope="module")
def github_helper(settings):
    """Create GithubHelper instance"""
    return GithubHelper(settings)

@pytest.fixture(autouse=True)
def cleanup():
    """Clean up test directories before and after tests"""
    # Clean up before test
    if TEST_OUTPUT_DIR.exists():
        shutil.rmtree(TEST_OUTPUT_DIR)
    TEST_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    yield
    
    # Clean up after test
    if TEST_OUTPUT_DIR.exists():
        shutil.rmtree(TEST_OUTPUT_DIR)

class TestGithubHelper:
    
    def test_clone_repository(self, github_helper, settings):
        """Test cloning a real repository"""
        # Get the first repository config
        repo_config = settings.repositories[0]
        
        # Clone repository
        repo = github_helper.clone_repository(repo_config)
        
        # Assertions
        assert repo is not None
        assert repo.repository_url == repo_config.git_url
        assert repo.repository_name == "unoplat-code-confluence"
        assert repo.github_organization == "unoplat"
        
        # Check repository metadata
        assert repo.repository_metadata is not None
        assert "stars" in repo.repository_metadata
        assert "forks" in repo.repository_metadata
        assert "language" in repo.repository_metadata
        assert repo.repository_metadata["language"] == "Python"
        
        # Check codebases
        assert len(repo.codebases) == len(repo_config.codebases)
        for codebase, config in zip(repo.codebases, repo_config.codebases):
            assert codebase.name == config.root_package_name
            assert os.path.exists(codebase.local_path)
            assert codebase.package_manager_metadata.programming_language == "python"
            assert codebase.package_manager_metadata.package_manager == "poetry"
            
        # Check README
        assert repo.readme is not None
        assert len(repo.readme) > 0
        

        