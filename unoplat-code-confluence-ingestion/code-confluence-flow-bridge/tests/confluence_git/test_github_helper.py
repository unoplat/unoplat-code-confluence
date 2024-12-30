# Standard Library
import json
import os
import shutil
from pathlib import Path

# Third Party
import pytest
from src.code_confluence_flow_bridge.confluence_git.github_helper import GithubHelper
from dotenv import load_dotenv

# First Party
from src.code_confluence_flow_bridge.models.configuration.settings import RepositorySettings

# Use the example config file path
TEST_CONFIG_PATH = Path(__file__).parent.parent/"data"/ "example_config.json"
TEST_OUTPUT_DIR = Path("test_output")


# Method 1: Using Path
def load_config(config_path: Path) -> RepositorySettings:
    data = json.loads(config_path.read_text())
    repository_settings = data["repositories"][0]
    return RepositorySettings.model_validate(repository_settings)

@pytest.fixture(scope="module")
def settings():
    """Load test settings"""
    assert TEST_CONFIG_PATH.exists(), f"Config file not found at {TEST_CONFIG_PATH}"
    
    return load_config(TEST_CONFIG_PATH)

@pytest.fixture(scope="module")
def github_helper():
    """Create GithubHelper instance"""
    return GithubHelper()

@pytest.fixture
def github_pat_token():
    """
    Fixture that provides GitHub PAT token.
    First tries to read from environment variable, then falls back to .env.testing file
    """
    # Try getting from environment first
    token = os.getenv('GITHUB_PAT_TOKEN')
    
    if not token:
        # If not in env, try loading from .env.testing
        env_file = Path(__file__).parent.parent / '.env.testing'
        if env_file.exists():
            load_dotenv(env_file)
            token = os.getenv('GITHUB_PAT_TOKEN')
    
    if not token:
        pytest.fail("GITHUB_PAT_TOKEN not found in environment or .env.testing file")
        
    return token

class TestGithubHelper:
    
    def test_clone_repository(self, github_helper: GithubHelper, settings: RepositorySettings, github_pat_token: str):
        """Test cloning a real repository"""
        # Get the first repository config
        
        
        # Clone repository
        repo = github_helper.clone_repository(settings, github_token=github_pat_token)
        
        # Assertions
        assert repo is not None
        assert repo.repository_url == settings.git_url
        assert repo.repository_name == "unoplat-code-confluence"
        assert repo.github_organization == "unoplat"
        
        # Check repository metadata
        assert repo.repository_metadata is not None
        assert "stars" in repo.repository_metadata
        assert "forks" in repo.repository_metadata
        assert "language" in repo.repository_metadata
        assert repo.repository_metadata["language"] == "Python"
        
        # Check codebases
        assert len(repo.codebases) == len(settings.codebases)
        for codebase, config in zip(repo.codebases, settings.codebases):
            assert codebase.name == config.root_package_name
            assert os.path.exists(codebase.local_path)
            assert codebase.package_manager_metadata.programming_language == "python"
            assert codebase.package_manager_metadata.package_manager == "poetry"
            
        # Check README
        assert repo.readme is not None
        assert len(repo.readme) > 0
        

    def test_github_connection(self, github_pat_token):
        # Use github_pat_token in your test
        assert github_pat_token is not None
        # ... rest of your test
        

        