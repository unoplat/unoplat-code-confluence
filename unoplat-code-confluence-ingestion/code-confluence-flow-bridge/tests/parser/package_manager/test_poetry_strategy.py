from pathlib import Path
from typing import Dict

import pytest
from src.code_confluence_flow_bridge.models.code_confluence_parsing_models import (
    UnoplatProjectDependency,
)
from src.code_confluence_flow_bridge.parser.package_manager.poetry.poetry_strategy import (
    PythonPoetryStrategy,
)
from src.code_confluence_flow_bridge.utility.author_utils import normalize_authors
import tomlkit
from unoplat_code_confluence_commons.programming_language_metadata import (
    PackageManagerType,
    ProgrammingLanguage,
    ProgrammingLanguageMetadata,
)

# Constants
TEST_DATA_DIR = Path(__file__).parent.parent.parent / "test_data"


def flatten_dependencies(grouped: Dict[str, Dict[str, UnoplatProjectDependency]]) -> Dict[str, UnoplatProjectDependency]:
    """Utility to collapse grouped dependencies into a single-level dict."""

    flattened: Dict[str, UnoplatProjectDependency] = {}
    for group_deps in grouped.values():
        flattened.update(group_deps)
    return flattened

def load_toml_content(filename: str) -> str:
    """Helper function to load TOML content from test data directory"""
    file_path = TEST_DATA_DIR / filename
    if not file_path.exists():
        raise FileNotFoundError(f"Test data file not found: {file_path}")
    return file_path.read_text(encoding="utf-8")

@pytest.fixture
def mock_pyproject_all_required() -> str:
    """Returns pyproject.toml content with all required Poetry sections"""
    return load_toml_content("pyproject_all_required.toml")

@pytest.fixture
def mock_pyproject_optional_sections_only() -> str:
    """Returns pyproject.toml content with only optional sections"""
    return load_toml_content("pyproject_optional_sections.toml")

@pytest.fixture
def mock_pyproject_unoplat() -> str:
    """Returns pyproject.toml content from unoplat project"""
    return load_toml_content("pyproject_unoplat.toml")

@pytest.fixture
def mock_poetry_strategy() -> PythonPoetryStrategy:
    """Create a fixture to return an instance of PythonPoetryStrategy"""
    return PythonPoetryStrategy()

@pytest.fixture
def mock_metadata() -> ProgrammingLanguageMetadata:
    """Create mock metadata to be passed into the strategy's process_metadata method"""
    return ProgrammingLanguageMetadata(
        language=ProgrammingLanguage.PYTHON,
        package_manager=PackageManagerType.POETRY,
        language_version="3.8.0",
        
    )

def writepyproject(content: str, tmp_path: Path) -> Path:
    """Helper function to write the given TOML content to a temporary pyproject.toml file"""
    pyproject_path = tmp_path / "pyproject.toml"
    pyproject_path.write_text(content, encoding="utf-8")
    return pyproject_path

@pytest.mark.parametrize("toml_filename", [
    "pyproject_all_required.toml",
    "pyproject_optional_sections.toml",
    "pyproject_unoplat.toml"
])
def test_pyproject_is_written_correctly(toml_filename: str, tmp_path: Path):
    """Test that TOML files can be read and parsed correctly"""
    content = load_toml_content(toml_filename)
    pyproject_path = writepyproject(content, tmp_path)
    
    with open(pyproject_path, "r", encoding="utf-8") as f:
        data = tomlkit.parse(f.read())
    assert data is not None

def test_process_metadata_all_required_sections(
    tmp_path: Path,
    mock_poetry_strategy: PythonPoetryStrategy,
    mock_pyproject_all_required: str,
    mock_metadata: ProgrammingLanguageMetadata
):
    """Test processing of pyproject.toml with all required sections"""
    writepyproject(mock_pyproject_all_required, tmp_path)

    package_metadata = mock_poetry_strategy.process_metadata(str(tmp_path), mock_metadata)

    # Test basic metadata
    assert package_metadata is not None
    assert package_metadata.package_name == "test_package"
    assert package_metadata.project_version == "0.1.0"
    assert package_metadata.description == "Sample description"
    assert any("Test Author <test@example.com>" in author for author in package_metadata.authors or [])
    assert package_metadata.programming_language == "python"
    assert package_metadata.package_manager == "poetry"
    assert package_metadata.programming_language_version == ">=3.9,<4.0"

    # Test additional metadata fields
    assert package_metadata.license == {"text": "MIT"}
    assert package_metadata.homepage == "https://example.com"
    assert package_metadata.repository == "https://github.com/example/test_package"
    assert package_metadata.documentation == "https://docs.example.com"
    assert "test" in (package_metadata.keywords or [])
    assert any("Maintainer <maintainer@example.com>" in maintainer for maintainer in package_metadata.maintainers or [])
    assert package_metadata.readme == "README.md"

    # Test dependencies from all groups
    grouped_deps: Dict[str, Dict[str, UnoplatProjectDependency]] = package_metadata.dependencies

    assert "default" in grouped_deps
    assert "dev" in grouped_deps
    assert "docs" in grouped_deps

    default_deps = grouped_deps["default"]
    dev_deps = grouped_deps["dev"]
    docs_deps = grouped_deps["docs"]

    # Main dependencies
    assert "requests" in default_deps
    assert "git_dep" in default_deps
    assert "path_dep" in default_deps
    assert default_deps["requests"].version.specifier == ">=2.0.0,<2.0.0"

    # Dev dependencies
    assert "pytest" in dev_deps
    assert "black" in dev_deps

    # Docs dependencies
    assert "sphinx" in docs_deps
    assert "mkdocs" in docs_deps

    # Test scripts/entry points
    assert package_metadata.entry_points is not None
    assert package_metadata.entry_points["cli"] == "test_package.module:function"
    assert package_metadata.entry_points["serve"] == "uvicorn main:app --reload"

def test_process_metadata_unoplat(
    tmp_path: Path,
    mock_poetry_strategy: PythonPoetryStrategy,
    mock_pyproject_unoplat: str,
    mock_metadata: ProgrammingLanguageMetadata
):
    """Test processing of unoplat's pyproject.toml"""
    writepyproject(mock_pyproject_unoplat, tmp_path)

    package_metadata = mock_poetry_strategy.process_metadata(str(tmp_path), mock_metadata)

    # Test basic metadata
    assert package_metadata is not None
    assert package_metadata.package_name == "unoplat-code-confluence"
    assert package_metadata.project_version == "0.17.0"
    assert package_metadata.description == "codebase understanding"
    assert any("JayGhiya <ghiya6548@gmail.com>" in author for author in package_metadata.authors or [])
    assert package_metadata.programming_language == "python"
    assert package_metadata.package_manager == "poetry"
    assert package_metadata.programming_language_version == "^3.10, <=3.13"
    assert package_metadata.readme == "README.md"

    # Test dependencies
    grouped_deps: Dict[str, Dict[str, UnoplatProjectDependency]] = package_metadata.dependencies
    flattened_deps = flatten_dependencies(grouped_deps)

    # Check core dependencies
    core_deps = [
        "pydantic", "ruff", "loguru", "pygithub", "pypdf", "pydantic-settings",
        "litellm", "pytest", "dspy-ai", "packaging", "progiter", "sentence-transformers",
        "einops", "rich", "neo4j", "neomodel", "requirements-parser", "tomlkit",
        "stdlib-list", "pytest-cov", "gitpython", "tree-sitter", "tree-sitter-python", "black"
    ]
    for dep in core_deps:
        assert dep in flattened_deps, f"Core dependency {dep} not found"
    
    # Check specific version constraints
    assert flattened_deps["pygithub"].version.specifier == ">=1.59.1,<2.0.0"
    assert flattened_deps["neo4j"].version.specifier == "5.19.0"
    
    # Check git dependency
    assert "unoplat-code-confluence-commons" in flattened_deps
    git_dep = flattened_deps["unoplat-code-confluence-commons"]
    assert git_dep.source == "git"
    assert git_dep.source_url == "https://github.com/unoplat/unoplat-code-confluence.git"
    assert git_dep.source_reference == "main"
    assert git_dep.subdirectory == "unoplat-code-confluence-commons"
    
    # Check dev dependencies
    dev_deps = ["ipykernel", "mypy", "types-requests"]
    for dep in dev_deps:
        assert dep in grouped_deps.get("dev", {}), f"Dev dependency {dep} not found"

    # Test scripts/entry points
    assert package_metadata.entry_points is not None
    assert package_metadata.entry_points["unoplat-code-confluence"] == "unoplat_code_confluence.__main__:main"

def test_process_metadata_with_optional_sections(
    tmp_path: Path,
    mock_poetry_strategy: PythonPoetryStrategy,
    mock_pyproject_optional_sections_only: str,
    mock_metadata: ProgrammingLanguageMetadata
):
    """Test processing of pyproject.toml without Poetry sections"""
    writepyproject(mock_pyproject_optional_sections_only, tmp_path)

    package_metadata = mock_poetry_strategy.process_metadata(str(tmp_path), mock_metadata)

    assert package_metadata is not None
    assert package_metadata.package_manager is not None
    
    # Verify fallback behavior
    if package_metadata.package_manager == PackageManagerType.POETRY.value:
        pytest.fail("Expected fallback to pip or empty metadata, but got poetry")
    
    # Confirm empty dependencies when no requirements found (default bucket present but empty)
    assert set(package_metadata.dependencies.keys()) == {"default"}
    assert package_metadata.dependencies["default"] == {}

def test_normalize_authors_poetry():
    poetry_authors = ["Test Author <test@example.com>", "Another Author <another@example.com>"]
    result = normalize_authors(poetry_authors)
    assert result == poetry_authors

def test_normalize_authors_pep621():
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

def test_process_metadata_authors_format_all_required_sections(
    tmp_path: Path,
    mock_poetry_strategy: PythonPoetryStrategy,
    mock_pyproject_all_required: str,
    mock_metadata: ProgrammingLanguageMetadata
):
    writepyproject(mock_pyproject_all_required, tmp_path)
    package_metadata = mock_poetry_strategy.process_metadata(str(tmp_path), mock_metadata)
    assert package_metadata.authors is not None
    for author in package_metadata.authors:
        assert "<" in author and ">" in author

def test_process_metadata_authors_format_unoplat(
    tmp_path: Path,
    mock_poetry_strategy: PythonPoetryStrategy,
    mock_pyproject_unoplat: str,
    mock_metadata: ProgrammingLanguageMetadata
):
    writepyproject(mock_pyproject_unoplat, tmp_path)
    package_metadata = mock_poetry_strategy.process_metadata(str(tmp_path), mock_metadata)
    assert package_metadata.authors is not None
    for author in package_metadata.authors:
        assert "<" in author and ">" in author