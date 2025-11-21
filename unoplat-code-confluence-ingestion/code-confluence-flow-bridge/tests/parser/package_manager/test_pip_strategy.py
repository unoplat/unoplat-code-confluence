# Standard Library
from pathlib import Path

import pytest
from src.code_confluence_flow_bridge.parser.package_manager.pip.pip_strategy import (
    PipStrategy,
)

# First Party
from unoplat_code_confluence_commons.programming_language_metadata import (
    PackageManagerType,
    ProgrammingLanguage,
    ProgrammingLanguageMetadata,
)

# Constants
TEST_DATA_DIR = Path(__file__).parent.parent.parent / "test_data"


@pytest.fixture
def pip_strategy() -> PipStrategy:
    """Create a PipStrategy instance."""
    return PipStrategy()


@pytest.fixture
def mock_metadata() -> ProgrammingLanguageMetadata:
    """Create mock metadata for testing."""
    return ProgrammingLanguageMetadata(
        language=ProgrammingLanguage.PYTHON,
        package_manager=PackageManagerType.PIP,
        language_version="3.8.0",
    )


@pytest.fixture
def requirements_dir(tmp_path: Path) -> Path:
    """Create a temporary directory with test requirement files."""
    req_dir = tmp_path / "requirements"
    req_dir.mkdir()

    # Copy test requirement files
    for filename in ["requirements.txt", "requirements-dev.txt"]:
        src = TEST_DATA_DIR / "requirements" / filename
        dst = req_dir.parent / filename
        dst.write_text(src.read_text())

    # Copy setup.py for -e . to work
    setup_src = TEST_DATA_DIR / "setup" / "setup.py"
    setup_dst = req_dir.parent / "setup.py"
    setup_dst.write_text(setup_src.read_text())

    return req_dir.parent


@pytest.fixture
def types_requirements_dir(tmp_path: Path) -> Path:
    """Create a temporary directory with types requirements file."""
    # Create directory
    req_dir = tmp_path / "requirements"
    req_dir.mkdir()

    # Copy only the types requirements file
    src = TEST_DATA_DIR / "requirements" / "requirements-types.txt"
    dst = req_dir.parent / "requirements-types.txt"
    dst.write_text(src.read_text())

    return req_dir.parent


def test_setup_py_parsing(
    pip_strategy: PipStrategy,
    requirements_dir: Path,
    mock_metadata: ProgrammingLanguageMetadata,
):
    """Test parsing of core dependencies and metadata from setup.py."""
    metadata = pip_strategy.process_metadata(str(requirements_dir), mock_metadata)

    # Check basic metadata
    assert metadata.package_name == "test-package"
    assert metadata.project_version == "1.0.0"
    assert metadata.description == "Test package for setup.py parsing"
    assert metadata.license == {"text": "MIT"}
    assert metadata.authors and "Test Author <test@example.com>" in metadata.authors

    # Check programming language metadata
    assert metadata.programming_language == ProgrammingLanguage.PYTHON.value
    assert metadata.package_manager == PackageManagerType.PIP.value
    assert metadata.programming_language_version == ">=3.7"

    # Check grouped structure
    deps = metadata.dependencies
    assert "default" in deps

    # Check core dependencies (from setup.py install_requires → default group)
    assert "requests" in deps["default"]
    assert deps["default"]["requests"].version.specifier == ">=2.0.0"

    assert "flask" in deps["default"]
    assert deps["default"]["flask"].version.specifier == ">=2.0.0"

    assert "redis" in deps["default"]
    assert (
        deps["default"]["redis"].extras and "hiredis" in deps["default"]["redis"].extras
    )
    assert deps["default"]["redis"].version.specifier == ">=4.0.0"

    # Check conditional dependency
    assert "importlib-metadata" in deps["default"]
    assert (
        deps["default"]["importlib-metadata"].environment_marker
        == 'python_version < "3.8"'
    )

    # Check dev dependencies (from setup.py extras_require["dev"] → dev group)
    assert "dev" in deps
    assert "black" in deps["dev"]
    assert deps["dev"]["black"].version.specifier == "==22.3.0"

    # Check aws dependencies (from setup.py extras_require["aws"] → aws group)
    assert "aws" in deps
    assert "boto3" in deps["aws"]
    assert deps["aws"]["boto3"].version.specifier == ">=1.20.0"


def test_requirements_parsing(
    pip_strategy: PipStrategy,
    requirements_dir: Path,
    mock_metadata: ProgrammingLanguageMetadata,
):
    """Test parsing of additional dependencies from requirements.txt."""
    metadata = pip_strategy.process_metadata(str(requirements_dir), mock_metadata)
    deps = metadata.dependencies

    # Check grouped structure
    assert "default" in deps

    # Check URL dependencies (from requirements.txt → default group)
    assert "urllib3" in deps["default"]
    assert (
        deps["default"]["urllib3"].version.specifier
        == "!=1.25.0,!=1.25.1,<1.26,>=1.21.1"
    )

    # Check dependencies with extras
    assert "celery" in deps["default"]
    assert deps["default"]["celery"].extras and set(
        deps["default"]["celery"].extras
    ) == {"redis", "rabbitmq"}
    assert deps["default"]["celery"].version.specifier == ">=5.0.0"


def test_vcs_dependencies(
    pip_strategy: PipStrategy,
    requirements_dir: Path,
    mock_metadata: ProgrammingLanguageMetadata,
):
    """Test parsing of VCS dependencies from requirements.txt."""
    metadata = pip_strategy.process_metadata(str(requirements_dir), mock_metadata)
    deps = metadata.dependencies

    # Check grouped structure
    assert "default" in deps

    # Check Git dependencies (from requirements.txt → default group)
    assert "flask-vcs" in deps["default"]
    flask_vcs = deps["default"]["flask-vcs"]
    assert flask_vcs.source == "git"
    assert flask_vcs.source_url == "https://github.com/pallets/flask-vcs.git"
    assert flask_vcs.source_reference == "2.0.0"

    assert "requests-vcs" in deps["default"]
    requests_vcs = deps["default"]["requests-vcs"]
    assert requests_vcs.source == "git"
    assert requests_vcs.source_url == "https://github.com/psf/requests-vcs.git"
    assert requests_vcs.source_reference == "main"
    # For non-version references, specifier should remain None
    assert requests_vcs.version.specifier is None


def test_environment_markers(
    pip_strategy: PipStrategy,
    requirements_dir: Path,
    mock_metadata: ProgrammingLanguageMetadata,
):
    """Test parsing of dependencies with environment markers from setup.py."""
    metadata = pip_strategy.process_metadata(str(requirements_dir), mock_metadata)
    deps = metadata.dependencies

    # Check grouped structure
    assert "default" in deps

    # Check environment marker (from setup.py install_requires → default group)
    assert "importlib-metadata" in deps["default"]
    assert (
        deps["default"]["importlib-metadata"].environment_marker
        == 'python_version < "3.8"'
    )


def test_development_dependencies(
    pip_strategy: PipStrategy,
    requirements_dir: Path,
    mock_metadata: ProgrammingLanguageMetadata,
):
    """Test parsing of development dependencies from setup.py extras and requirements-dev.txt."""
    metadata = pip_strategy.process_metadata(str(requirements_dir), mock_metadata)
    deps = metadata.dependencies

    # Check dev group exists
    assert "dev" in deps

    # From setup.py extras_require["dev"] → dev group
    assert "black" in deps["dev"]
    assert deps["dev"]["black"].version.specifier == "==22.3.0"

    assert "flake8" in deps["dev"]
    assert deps["dev"]["flake8"].version.specifier == ">=3.9.0"

    assert "mypy" in deps["dev"]
    assert deps["dev"]["mypy"].version.specifier == ">=0.900"

    # From requirements-dev.txt → dev group (based on filename)
    assert "pytest" in deps["dev"]
    assert deps["dev"]["pytest"].version.specifier == ">=6.0.0"


def test_entry_points(
    pip_strategy: PipStrategy,
    requirements_dir: Path,
    mock_metadata: ProgrammingLanguageMetadata,
):
    """Test parsing of entry points from setup.py."""
    metadata = pip_strategy.process_metadata(str(requirements_dir), mock_metadata)

    assert "test-cli" in metadata.entry_points
    assert metadata.entry_points["test-cli"] == "test_package.cli:main"
    assert metadata.entry_points["serve"] == "test_package.server:run"


def test_types_requirements_parsing(
    pip_strategy: PipStrategy,
    types_requirements_dir: Path,
    mock_metadata: ProgrammingLanguageMetadata,
):
    """Test parsing of type stubs and development dependencies."""
    metadata = pip_strategy.process_metadata(str(types_requirements_dir), mock_metadata)
    deps = metadata.dependencies

    # Check grouped structure (requirements-types.txt → types group)
    assert "types" in deps

    # Test type stubs
    assert "boto3-stubs" in deps["types"]
    assert deps["types"]["boto3-stubs"].version.specifier == "==1.34.133"
    assert (
        deps["types"]["boto3-stubs"].extras
        and "s3" in deps["types"]["boto3-stubs"].extras
    )

    assert "types-requests" in deps["types"]
    assert deps["types"]["types-requests"].version.specifier == "==2.28.11.17"

    # Test ML dependencies
    assert "cohere" in deps["types"]
    assert deps["types"]["cohere"].version.specifier == "==5.6.1"

    assert "sentence-transformers" in deps["types"]
    assert deps["types"]["sentence-transformers"].version.specifier == "==2.6.1"

    # Test development tools
    assert "black" in deps["types"]
    assert deps["types"]["black"].version.specifier == "==23.3.0"

    assert "ruff" in deps["types"]
    assert deps["types"]["ruff"].version.specifier == "==0.0.286"

    assert "pre-commit" in deps["types"]
    assert deps["types"]["pre-commit"].version.specifier == "==3.2.2"

    # Test data processing
    assert "pandas" in deps["types"]
    assert deps["types"]["pandas"].version.specifier == "==2.2.3"

    assert "lxml" in deps["types"]
    assert deps["types"]["lxml"].version.specifier == "==5.3.0"

    # Test testing tools
    assert "pytest" in deps["types"]
    assert deps["types"]["pytest"].version.specifier == "==7.4.4"

    assert "pytest-asyncio" in deps["types"]
    assert deps["types"]["pytest-asyncio"].version.specifier == "==0.22.0"


def test_requirement_file_includes(
    pip_strategy: PipStrategy,
    tmp_path: Path,
    mock_metadata: ProgrammingLanguageMetadata,
):
    """Test -r include handling."""
    # Create base requirements
    base_req = tmp_path / "requirements.txt"
    base_req.write_text("requests>=2.0.0\n-r requirements-dev.txt\n")

    # Create dev requirements
    dev_req = tmp_path / "requirements-dev.txt"
    dev_req.write_text("pytest>=6.0.0\nblack==22.3.0\n")

    metadata = pip_strategy.process_metadata(str(tmp_path), mock_metadata)

    # Base requirements in default group
    assert "default" in metadata.dependencies
    assert "requests" in metadata.dependencies["default"]

    # Dev requirements in dev group (from filename)
    assert "dev" in metadata.dependencies
    assert "pytest" in metadata.dependencies["dev"]
    assert "black" in metadata.dependencies["dev"]


def test_no_duplicate_dependencies_from_includes(
    pip_strategy: PipStrategy,
    tmp_path: Path,
    mock_metadata: ProgrammingLanguageMetadata,
):
    """Test that -r includes don't duplicate dependencies in parent group."""
    # Create base requirements with -r include
    base_req = tmp_path / "requirements.txt"
    base_req.write_text("requests>=2.0.0\n-r requirements-dev.txt\n")

    # Create dev requirements
    dev_req = tmp_path / "requirements-dev.txt"
    dev_req.write_text("pytest>=6.0.0\nblack==22.3.0\n")

    metadata = pip_strategy.process_metadata(str(tmp_path), mock_metadata)

    # Verify pytest and black are ONLY in dev, NOT in default
    assert "pytest" not in metadata.dependencies["default"]
    assert "black" not in metadata.dependencies["default"]

    # Verify they ARE in dev
    assert "pytest" in metadata.dependencies["dev"]
    assert "black" in metadata.dependencies["dev"]

    # Verify requests is only in default
    assert "requests" in metadata.dependencies["default"]
    assert "dev" in metadata.dependencies  # dev group exists
    assert "requests" not in metadata.dependencies["dev"]  # But requests not in dev


def test_circular_include_detection(
    pip_strategy: PipStrategy,
    tmp_path: Path,
    mock_metadata: ProgrammingLanguageMetadata,
):
    """Test that circular includes raise ValueError."""
    req1 = tmp_path / "requirements.txt"
    req1.write_text("-r requirements-dev.txt\n")

    req2 = tmp_path / "requirements-dev.txt"
    req2.write_text("-r requirements.txt\n")  # Circular!

    with pytest.raises(ValueError, match="Circular requirement include"):
        pip_strategy.process_metadata(str(tmp_path), mock_metadata)


def test_editable_install(
    pip_strategy: PipStrategy,
    tmp_path: Path,
    mock_metadata: ProgrammingLanguageMetadata,
):
    """Test -e editable install parsing."""
    req = tmp_path / "requirements.txt"
    req.write_text("-e git+https://github.com/user/repo.git@main#egg=mypackage\n")

    metadata = pip_strategy.process_metadata(str(tmp_path), mock_metadata)

    assert "default" in metadata.dependencies
    assert "mypackage" in metadata.dependencies["default"]
    dep = metadata.dependencies["default"]["mypackage"]
    assert dep.source == "git"
    assert dep.source_url == "https://github.com/user/repo.git"
    assert dep.source_reference == "main"


def test_group_mapping_from_subdirectory(
    pip_strategy: PipStrategy,
    tmp_path: Path,
    mock_metadata: ProgrammingLanguageMetadata,
):
    """Test requirements/{group}.txt pattern."""
    req_dir = tmp_path / "requirements"
    req_dir.mkdir()

    test_req = req_dir / "test.txt"
    test_req.write_text("pytest>=6.0.0\n")

    metadata = pip_strategy.process_metadata(str(tmp_path), mock_metadata)

    assert "test" in metadata.dependencies
    assert "pytest" in metadata.dependencies["test"]
    assert metadata.dependencies["test"]["pytest"].version.specifier == ">=6.0.0"


def test_package_name_normalization(
    pip_strategy: PipStrategy,
    tmp_path: Path,
    mock_metadata: ProgrammingLanguageMetadata,
):
    """Test PEP 503 package name normalization with consecutive special chars."""
    # Create requirements with edge case package names
    req = tmp_path / "requirements.txt"
    req.write_text(
        "Foo..Bar>=1.0.0\nbaz__qux>=2.0.0\ntest--pkg>=3.0.0\nMix._-Ed>=4.0.0\n"
    )

    metadata = pip_strategy.process_metadata(str(tmp_path), mock_metadata)

    # All should normalize to single-dash form
    assert "foo-bar" in metadata.dependencies["default"]
    assert "baz-qux" in metadata.dependencies["default"]
    assert "test-pkg" in metadata.dependencies["default"]
    assert "mix-ed" in metadata.dependencies["default"]

    # Should NOT have multi-dash forms
    assert "foo--bar" not in metadata.dependencies["default"]
    assert "baz__qux" not in metadata.dependencies["default"]


def test_group_name_normalization(
    pip_strategy: PipStrategy,
    tmp_path: Path,
    mock_metadata: ProgrammingLanguageMetadata,
):
    """Test PEP 735 group name normalization with consecutive special chars."""
    # Create requirements file with special chars in name
    req = tmp_path / "requirements-dev__test.txt"
    req.write_text("pytest>=6.0.0\n")

    metadata = pip_strategy.process_metadata(str(tmp_path), mock_metadata)

    # Group name should normalize dev__test -> dev-test
    assert "dev-test" in metadata.dependencies
    assert "pytest" in metadata.dependencies["dev-test"]

    # Should NOT have multi-underscore form
    assert "dev__test" not in metadata.dependencies
