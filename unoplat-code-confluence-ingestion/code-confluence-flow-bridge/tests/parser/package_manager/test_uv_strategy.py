# Standard Library
from pathlib import Path

import pytest
from src.code_confluence_flow_bridge.parser.package_manager.uv.uv_strategy import (
    UvStrategy,
)
from src.code_confluence_flow_bridge.utility.author_utils import normalize_authors

# First Party
from unoplat_code_confluence_commons.programming_language_metadata import (
    PackageManagerType,
    ProgrammingLanguage,
    ProgrammingLanguageMetadata,
)

# Constants
TEST_DATA_DIR = Path(__file__).parent.parent.parent / "test_data"

@pytest.fixture
def uv_strategy() -> UvStrategy:
    """Create a UvStrategy instance."""
    return UvStrategy()

@pytest.fixture
def mock_metadata() -> ProgrammingLanguageMetadata:
    """Create mock metadata for testing."""
    return ProgrammingLanguageMetadata(
        language=ProgrammingLanguage.PYTHON,
        package_manager=PackageManagerType.UV,
        language_version="3.11.0",
        
    )

@pytest.fixture
def pyproject_dir(tmp_path: Path) -> Path:
    """Create a temporary directory with test pyproject.toml."""
    pyproject_path = tmp_path / "pyproject.toml"
    src = TEST_DATA_DIR / "pyproject_uv.toml"
    pyproject_path.write_text(src.read_text())
    return tmp_path

def test_basic_metadata_parsing(uv_strategy: UvStrategy, pyproject_dir: Path, mock_metadata: ProgrammingLanguageMetadata):
    """Test parsing of basic project metadata."""
    metadata = uv_strategy.process_metadata(str(pyproject_dir), mock_metadata)
    
    # Check basic metadata
    assert metadata.package_name == "code-confluence-flow-bridge"
    assert metadata.project_version == "0.99.0"
    assert metadata.description == "Bridge between Code Confluence User and Ingestion Workflow"
    assert metadata.programming_language == "python"
    assert metadata.package_manager == "uv"
    assert metadata.programming_language_version == ">=3.13"
    assert metadata.readme == "README.md"

def test_dependencies_parsing(uv_strategy: UvStrategy, pyproject_dir: Path, mock_metadata: ProgrammingLanguageMetadata):
    """Test parsing of dependencies with version constraints and extras."""
    metadata = uv_strategy.process_metadata(str(pyproject_dir), mock_metadata)

    deps = metadata.dependencies
    assert "default" in deps
    default_deps = deps["default"]

    # Check main dependencies
    assert "fastapi" in default_deps
    assert default_deps["fastapi"].version.specifier == ">=0.115.6"
    assert default_deps["fastapi"].extras == ["standard"]

    assert "pydantic" in default_deps
    assert default_deps["pydantic"].version.specifier == ">=2.10.4"
    assert default_deps["pydantic"].environment_marker == "python_version >=3.8"

    assert "unoplat-code-confluence-commons" in default_deps
    commons_dep = default_deps["unoplat-code-confluence-commons"]
    assert commons_dep.version.specifier == ">=0.24.0"
    assert commons_dep.source == "git"
    assert commons_dep.source_url == "https://github.com/unoplat/unoplat-code-confluence"

def test_optional_dependencies(uv_strategy: UvStrategy, pyproject_dir: Path, mock_metadata: ProgrammingLanguageMetadata):
    """Test parsing of optional dependencies in different groups."""
    metadata = uv_strategy.process_metadata(str(pyproject_dir), mock_metadata)
    deps = metadata.dependencies

    # Optional dependency tables -> named extras
    assert "observability" in deps
    assert "opentelemetry-sdk" in deps["observability"]
    assert deps["observability"]["opentelemetry-sdk"].version.specifier == ">=1.32.1"

    assert "aws" in deps
    assert "boto3" in deps["aws"]
    assert deps["aws"]["boto3"].version.specifier == ">=1.35.0"

    # UV dependency groups
    assert "test" in deps
    assert "pytest" in deps["test"]
    assert deps["test"]["pytest"].version.specifier == ">=8.3.5"
    assert "loguru" in deps["test"]
    assert "loguru" in deps["default"]

    assert "dev" in deps
    assert "mypy" in deps["dev"]
    assert deps["dev"]["mypy"].version.specifier == ">=1.16.0"

    assert "docs" in deps
    assert "mkdocs-material" in deps["docs"]
    assert deps["docs"]["mkdocs-material"].version.specifier == ">=9.5.0"
    assert "mkdocstrings" in deps["docs"]
    assert deps["docs"]["mkdocstrings"].extras == ["python"]

    assert "bench" in deps
    assert "pytest-benchmark" in deps["bench"]
    assert deps["bench"]["pytest-benchmark"].version.specifier == ">=4.0.0"

def test_git_source_parsing(uv_strategy: UvStrategy, pyproject_dir: Path, mock_metadata: ProgrammingLanguageMetadata):
    """Test parsing of git source dependencies from UV configuration.
    
    UV specifies git dependencies in tool.uv.sources section:
        [tool.uv.sources]
        package = { 
            git = "https://github.com/user/repo.git",
            rev = "main",
            subdirectory = "path" 
        }
    """
    metadata = uv_strategy.process_metadata(str(pyproject_dir), mock_metadata)
    deps = metadata.dependencies
    default_deps = deps["default"]

    assert "unoplat-code-confluence-commons" in default_deps
    git_dep = default_deps["unoplat-code-confluence-commons"]
    assert git_dep.source == "git"
    assert git_dep.source_url == "https://github.com/unoplat/unoplat-code-confluence"
    assert git_dep.source_reference == "unoplat-code-confluence-commons-v0.9.1"
    assert git_dep.subdirectory == "unoplat-code-confluence-commons"

def test_no_pyproject_handling(uv_strategy: UvStrategy, tmp_path: Path, mock_metadata: ProgrammingLanguageMetadata):
    """Test handling when no pyproject.toml exists."""
    metadata = uv_strategy.process_metadata(str(tmp_path), mock_metadata)
    
    assert metadata.package_name is None
    assert metadata.programming_language == "python"
    assert metadata.package_manager == "uv"
    assert "default" in metadata.dependencies
    assert metadata.dependencies["default"] == {}

def test_vcs_url_parsing(uv_strategy: UvStrategy):
    """Test parsing of git URLs in UV format.
    
    UV uses a simpler git URL format compared to pip's VCS URLs.
    Example from UV docs:
        [tool.uv.sources]
        package = { git = "https://github.com/user/repo.git", rev = "main" }
    """
    # Simple git URL
    url = "https://github.com/user/repo.git"
    base_url, ref, subdir, name = uv_strategy._parse_vcs_url(url)
    assert base_url == "https://github.com/user/repo"
    assert ref is None
    assert subdir is None
    assert name == "repo"
    
    # URL with subdirectory
    url = "https://github.com/unoplat/unoplat-code-confluence.git"
    base_url, ref, subdir, name = uv_strategy._parse_vcs_url(url)
    assert base_url == "https://github.com/unoplat/unoplat-code-confluence"
    assert ref is None
    assert subdir is None
    assert name == "unoplat-code-confluence"

def test_version_constraint_parsing(uv_strategy: UvStrategy):
    """Test parsing of version constraints."""
    # Simple version
    version = uv_strategy._parse_version_constraint(">=1.0.0")
    assert version.specifier == ">=1.0.0"
    
    # Complex version
    version = uv_strategy._parse_version_constraint(">=1.0.0,<2.0.0")
    assert version.specifier == ">=1.0.0,<2.0.0"
    
    # Exact version
    version = uv_strategy._parse_version_constraint("==1.0.0")
    assert version.specifier == "==1.0.0"

def test_normalize_authors_pep621_uv():
    pep621_authors = [
        {"name": "Test Author", "email": "test@example.com"},
        {"name": "Another Author", "email": "another@example.com"},
        {"name": "No Email"},
        {"email": "only@example.com"}
    ]
    result = normalize_authors(pep621_authors)
    assert result == [
        "Test Author <test@example.com>",
        "Another Author <another@example.com>",
        "No Email",
        "<only@example.com>"
    ]

def test_process_metadata_authors_format_uv(uv_strategy: UvStrategy, pyproject_dir: Path, mock_metadata: ProgrammingLanguageMetadata):
    # Patch the pyproject.toml to add authors in PEP 621 format
    pyproject_path = pyproject_dir / "pyproject.toml"
    content = pyproject_path.read_text()
    content = content.replace(
        '[project]',
        '[project]\nauthors = [\n    { name = "Test Author", email = "test@example.com" },\n    { name = "Another Author", email = "another@example.com" }\n]\n'
    )
    pyproject_path.write_text(content)
    metadata = uv_strategy.process_metadata(str(pyproject_dir), mock_metadata)
    assert metadata.authors is not None
    assert metadata.authors == ["Test Author <test@example.com>", "Another Author <another@example.com>"]
