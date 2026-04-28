# Standard Library
import os
import json
from pathlib import Path
from urllib.parse import quote

from dotenv import load_dotenv

# Third Party
import pytest
from src.code_confluence_flow_bridge.confluence_git.github_helper import (
    GithubHelper,
    _build_authenticated_url,
)
from src.code_confluence_flow_bridge.models.github.github_repo import (
    RepositoryRequestConfiguration,
)

# First Party
from unoplat_code_confluence_commons.base_models import RepositorySettings
from unoplat_code_confluence_commons.credential_enums import ProviderKey

# Use the example config file path
TEST_CONFIG_PATH = Path(__file__).parent.parent / "test_data" / "example_config.json"
NESTED_CONFIG_PATH = (
    Path(__file__).parent.parent / "test_data" / "nested_package_git_config.json"
)
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
    token = os.getenv("GITHUB_PAT_TOKEN")

    if not token:
        # If not in env, try loading from .env.testing
        env_file = Path(__file__).parent.parent / ".env.testing"
        if env_file.exists():
            load_dotenv(env_file)
            token = os.getenv("GITHUB_PAT_TOKEN")

    if not token:
        pytest.fail("GITHUB_PAT_TOKEN not found in environment or .env.testing file")

    return token


def _assert_token_not_persisted(repo_path: str, github_pat_token: str) -> None:
    """Ensure authenticated git URLs are not persisted to local git config."""
    git_config_path = Path(repo_path) / ".git" / "config"
    assert git_config_path.exists()

    git_config = git_config_path.read_text()
    assert github_pat_token not in git_config
    assert quote(github_pat_token, safe="") not in git_config
    assert "x-access-token" not in git_config


def repository_settings_to_github_request(
    settings: RepositorySettings,
) -> RepositoryRequestConfiguration:
    """Convert RepositorySettings to RepositoryRequestConfiguration for test compatibility."""
    # Extract organization and repo name from git_url
    # Supports: https://github.com/org/repo(.git) or git@github.com:org/repo(.git)
    git_url = settings.git_url
    if git_url.startswith("git@"):
        repo_path = git_url.split("github.com:")[-1]
    else:
        repo_path = git_url.split("github.com/")[-1]
    repo_path = repo_path.replace(".git", "")
    parts = repo_path.split("/")
    if len(parts) < 2:
        raise ValueError(f"Invalid git_url: {git_url}")
    org, repo = parts[0], parts[1]
    return RepositoryRequestConfiguration(
        repository_name=repo,
        repository_git_url=git_url,
        repository_owner_name=org,
        provider_key=ProviderKey.GITHUB_OPEN,
        repository_metadata=settings.codebases,
    )


class TestGithubHelper:
    def test_build_authenticated_url_uses_token_for_https_and_ssh_urls(self) -> None:
        token = "ghp_example/token:with@special chars"

        https_url = _build_authenticated_url(
            "https://github.com/unoplat/unoplat-code-confluence.git", token
        )
        assert https_url == (
            "https://x-access-token:"
            "ghp_example%2Ftoken%3Awith%40special%20chars"
            "@github.com/unoplat/unoplat-code-confluence.git"
        )

        ssh_url = _build_authenticated_url(
            "git@github.com:unoplat/unoplat-code-confluence.git", token
        )
        assert ssh_url == (
            "https://x-access-token:"
            "ghp_example%2Ftoken%3Awith%40special%20chars"
            "@github.com/unoplat/unoplat-code-confluence.git"
        )

    def test_clone_repository(
        self,
        github_helper: GithubHelper,
        settings: RepositorySettings,
        github_pat_token: str,
    ) -> None:
        """Test cloning a real repository using example_config.json"""
        repo_request: RepositoryRequestConfiguration = (
            repository_settings_to_github_request(settings)
        )
        repo = github_helper.clone_repository(
            repo_request, github_token=github_pat_token
        )

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
        assert isinstance(repo.repository_metadata["language"], str)
        assert len(repo.repository_metadata["language"]) > 0

        # Check codebases
        assert len(repo.codebases) == len(settings.codebases)
        for codebase, config in zip(repo.codebases, settings.codebases):
            # Codebase name should match first root package or codebase_folder
            expected_name = config.codebase_folder
            if config.root_packages and len(config.root_packages) > 0:
                first_root_package = config.root_packages[0]
                if first_root_package != ".":
                    expected_name = first_root_package
            assert codebase.name == expected_name

            # Verify root_packages are valid paths
            assert len(codebase.root_packages) > 0
            for root_package_path in codebase.root_packages:
                assert os.path.exists(root_package_path)

            assert codebase.package_manager_metadata.programming_language == "python"
            assert codebase.package_manager_metadata.package_manager == "uv"

            # Build expected paths
            repo_base = os.path.join(
                os.path.expanduser("~"),
                ".unoplat",
                "repositories",
                "unoplat-code-confluence",
            )

            # Expected codebase_path (base directory for the codebase)
            expected_codebase_path = os.path.join(
                repo_base,
                config.codebase_folder
                if config.codebase_folder and config.codebase_folder != "."
                else "",
            )
            assert codebase.codebase_path == expected_codebase_path

            # Expected root_packages should include full paths to each root package
            if config.root_packages:
                for i, root_package in enumerate(config.root_packages):
                    if root_package == ".":
                        expected_root_path = expected_codebase_path
                    else:
                        expected_root_path = os.path.join(
                            expected_codebase_path, root_package
                        )
                    assert codebase.root_packages[i] == expected_root_path

        # Check README
        assert repo.readme is not None
        assert len(repo.readme) > 0

        repo_base = os.path.join(
            os.path.expanduser("~"),
            ".unoplat",
            "repositories",
            "unoplat-code-confluence",
        )
        _assert_token_not_persisted(repo_base, github_pat_token)

    def test_clone_nested_repository(
        self,
        github_helper: GithubHelper,
        nested_settings: RepositorySettings,
        github_pat_token: str,
    ) -> None:
        """Test cloning a repository with nested package structure using nested_package_git_config.json"""
        repo_request: RepositoryRequestConfiguration = (
            repository_settings_to_github_request(nested_settings)
        )
        repo = github_helper.clone_repository(
            repo_request, github_token=github_pat_token
        )

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
        assert isinstance(repo.repository_metadata["language"], str)
        assert len(repo.repository_metadata["language"]) > 0

        # Check codebases with nested structure
        assert len(repo.codebases) == len(nested_settings.codebases)
        for codebase, config in zip(repo.codebases, nested_settings.codebases):
            # Codebase name should match first root package or codebase_folder
            expected_name = config.codebase_folder
            if config.root_packages and len(config.root_packages) > 0:
                first_root_package = config.root_packages[0]
                if first_root_package != ".":
                    expected_name = first_root_package
            assert codebase.name == expected_name

            # Verify root_packages are valid paths
            assert len(codebase.root_packages) > 0
            for root_package_path in codebase.root_packages:
                assert os.path.exists(root_package_path)

            assert codebase.package_manager_metadata.programming_language == "python"
            assert codebase.package_manager_metadata.package_manager == "uv"

            # Build expected paths
            repo_base = os.path.join(
                os.path.expanduser("~"),
                ".unoplat",
                "repositories",
                "unoplat-code-confluence",
            )

            # Expected codebase_path (base directory for the codebase)
            expected_codebase_path = os.path.join(
                repo_base,
                config.codebase_folder
                if config.codebase_folder and config.codebase_folder != "."
                else "",
            )
            assert codebase.codebase_path == expected_codebase_path

            # Expected root_packages should include full paths to each root package
            if config.root_packages:
                for i, root_package in enumerate(config.root_packages):
                    if root_package == ".":
                        expected_root_path = expected_codebase_path
                    else:
                        expected_root_path = os.path.join(
                            expected_codebase_path, root_package
                        )
                    assert codebase.root_packages[i] == expected_root_path

        # Check README
        assert repo.readme is not None
        assert len(repo.readme) > 0

        repo_base = os.path.join(
            os.path.expanduser("~"),
            ".unoplat",
            "repositories",
            "unoplat-code-confluence",
        )
        _assert_token_not_persisted(repo_base, github_pat_token)

    def test_github_connection(self, github_pat_token):
        """Test GitHub connection - remains synchronous as it just validates the token"""
        assert github_pat_token is not None
        # ... rest of your test
