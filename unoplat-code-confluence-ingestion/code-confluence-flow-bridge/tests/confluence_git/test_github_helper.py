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
TEST_CONFIG_PATH = Path(__file__).parent.parent/"test_data"/ "example_config.json"
NESTED_CONFIG_PATH = Path(__file__).parent.parent/"test_data"/ "nested_package_git_config.json"
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
def nested_settings():
    """Load nested package test settings"""
    assert NESTED_CONFIG_PATH.exists(), f"Config file not found at {NESTED_CONFIG_PATH}"
    
    return load_config(NESTED_CONFIG_PATH)

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
    
    @pytest.mark.asyncio  # Mark test as async
    async def test_clone_repository(self, github_helper: GithubHelper, settings: RepositorySettings, github_pat_token: str):
        """Test cloning a real repository using example_config.json"""
        # Clone repository - now with await
        repo = await github_helper.clone_repository(settings, github_token=github_pat_token)
        
        # Basic repository assertions
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
            assert codebase.name == config.root_package
            assert os.path.exists(codebase.local_path)
            assert codebase.package_manager_metadata.programming_language == "python"
            assert codebase.package_manager_metadata.package_manager == "uv"
            
            # Build expected paths
            repo_base = os.path.join(
                os.path.expanduser("~"), 
                ".unoplat", 
                "repositories",
                "unoplat-code-confluence"
            )
            
            # Expected local_path includes root_package
            expected_path = os.path.join(
                repo_base,
                config.codebase_folder,
                config.root_package
            )
            assert codebase.local_path == expected_path
            
            # Verify source_directory (should be codebase folder path)
            expected_source_dir = os.path.join(
                repo_base,
                config.codebase_folder if config.codebase_folder and config.codebase_folder != "." else ""
            )
            assert codebase.source_directory == expected_source_dir
        
        # Check README
        assert repo.readme is not None
        assert len(repo.readme) > 0

    @pytest.mark.asyncio  # Mark test as async
    async def test_clone_nested_repository(self, github_helper: GithubHelper, nested_settings: RepositorySettings, github_pat_token: str):
        """Test cloning a repository with nested package structure using nested_package_git_config.json"""
        # Clone repository - now with await
        repo = await github_helper.clone_repository(nested_settings, github_token=github_pat_token)
        
        # Basic repository assertions
        assert repo is not None
        assert repo.repository_url == nested_settings.git_url
        assert repo.repository_name == "unoplat-code-confluence"
        assert repo.github_organization == "unoplat"
        
        # Check repository metadata
        assert repo.repository_metadata is not None
        assert "stars" in repo.repository_metadata
        assert "forks" in repo.repository_metadata
        assert "language" in repo.repository_metadata
        assert repo.repository_metadata["language"] == "Python"
        
        # Check codebases with nested structure
        assert len(repo.codebases) == len(nested_settings.codebases)
        for codebase, config in zip(repo.codebases, nested_settings.codebases):
            assert codebase.name == config.root_package
            assert os.path.exists(codebase.local_path)
            assert codebase.package_manager_metadata.programming_language == "python"
            assert codebase.package_manager_metadata.package_manager == "uv"
            
            # Build expected paths
            repo_base = os.path.join(
                os.path.expanduser("~"), 
                ".unoplat", 
                "repositories",
                "unoplat-code-confluence"
            )
            
            # Expected local_path includes root_package
            expected_path = os.path.join(
                repo_base,
                config.codebase_folder,
                config.root_package
            )
            assert codebase.local_path == expected_path
            
            # Verify source_directory (should be codebase folder path)
            expected_source_dir = os.path.join(
                repo_base,
                config.codebase_folder if config.codebase_folder and config.codebase_folder != "." else ""
            )
            assert codebase.source_directory == expected_source_dir
        
        # Check README
        assert repo.readme is not None
        assert len(repo.readme) > 0

    def test_github_connection(self, github_pat_token):
        """Test GitHub connection - remains synchronous as it just validates the token"""
        assert github_pat_token is not None
        # ... rest of your test
        

        