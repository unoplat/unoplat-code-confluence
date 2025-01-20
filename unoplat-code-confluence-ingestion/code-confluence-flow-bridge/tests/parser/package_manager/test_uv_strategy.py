# Standard Library
from pathlib import Path
import pytest

# First Party
from src.code_confluence_flow_bridge.models.configuration.settings import (
    ProgrammingLanguageMetadata,
    ProgrammingLanguage,
    PackageManagerType
)
from src.code_confluence_flow_bridge.parser.package_manager.uv.uv_strategy import UvStrategy

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
        language_version="3.11.0"
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
    assert metadata.package_name == "Code-Confluence-Flow-Bridge"
    assert metadata.project_version == "0.1.0"
    assert metadata.description == "Bridge between Code Confluence User and Ingestion Workflow"
    assert metadata.programming_language == "python"
    assert metadata.package_manager == "uv"
    assert metadata.programming_language_version == ">=3.11"
    assert metadata.readme == "README.md"

def test_dependencies_parsing(uv_strategy: UvStrategy, pyproject_dir: Path, mock_metadata: ProgrammingLanguageMetadata):
    """Test parsing of dependencies with version constraints and extras."""
    metadata = uv_strategy.process_metadata(str(pyproject_dir), mock_metadata)
    deps = metadata.dependencies
    
    # Check main dependencies
    assert "fastapi" in deps
    assert deps["fastapi"].version.specifier == ">=0.115.6"
    assert deps["fastapi"].extras == ["standard"]
    
    assert "pydantic" in deps
    assert deps["pydantic"].version.specifier == ">=2.10.4"
    assert deps["pydantic"].extras == ["email"]
    assert deps["pydantic"].environment_marker == "python_version >=3.8"

def test_optional_dependencies(uv_strategy: UvStrategy, pyproject_dir: Path, mock_metadata: ProgrammingLanguageMetadata):
    """Test parsing of optional dependencies in different groups."""
    metadata = uv_strategy.process_metadata(str(pyproject_dir), mock_metadata)
    deps = metadata.dependencies
    
    # Test group
    assert "pytest" in deps
    assert deps["pytest"].version.specifier == ">=8.3.4"
    assert deps["pytest"].group == "test"
    
    # Dev group
    assert "black" in deps
    assert deps["black"].version.specifier == ">=23.0.0"
    assert deps["black"].group == "dev"

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
    
    assert "unoplat-code-confluence-commons" in deps
    git_dep = deps["unoplat-code-confluence-commons"]
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
    assert len(metadata.dependencies) == 0

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