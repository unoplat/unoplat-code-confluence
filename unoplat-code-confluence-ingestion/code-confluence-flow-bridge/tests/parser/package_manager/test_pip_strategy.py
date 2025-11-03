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

def test_setup_py_parsing(pip_strategy: PipStrategy, requirements_dir: Path, mock_metadata: ProgrammingLanguageMetadata):
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
    
    # Check core dependencies
    deps = metadata.dependencies
    assert "requests" in deps
    assert deps["requests"].version.specifier == ">=2.0.0"
    
    assert "flask" in deps
    assert deps["flask"].version.specifier == ">=2.0.0"
    
    assert "redis" in deps
    assert deps["redis"].extras and "hiredis" in deps["redis"].extras
    assert deps["redis"].version.specifier == ">=4.0.0"
    
    # Check conditional dependency
    assert "importlib-metadata" in deps
    assert deps["importlib-metadata"].environment_marker == 'python_version < "3.8"'
    
    # Check dev dependencies
    assert "black" in deps
    assert deps["black"].version.specifier == "==22.3.0"
    assert deps["black"].group == "dev"
    
    # Check aws dependencies
    assert "boto3" in deps
    assert deps["boto3"].version.specifier == ">=1.20.0"
    assert deps["boto3"].group == "aws"

def test_requirements_parsing(pip_strategy: PipStrategy, requirements_dir: Path, mock_metadata: ProgrammingLanguageMetadata):
    """Test parsing of additional dependencies from requirements.txt."""
    metadata = pip_strategy.process_metadata(str(requirements_dir), mock_metadata)
    deps = metadata.dependencies
    
    # Check URL dependencies
    assert "urllib3" in deps
    assert deps["urllib3"].version.specifier == "!=1.25.0,!=1.25.1,<1.26,>=1.21.1"
    
    # Check dependencies with extras
    assert "celery" in deps
    assert deps["celery"].extras and set(deps["celery"].extras) == {"redis", "rabbitmq"}
    assert deps["celery"].version.specifier == ">=5.0.0"

def test_vcs_dependencies(pip_strategy: PipStrategy, requirements_dir: Path, mock_metadata: ProgrammingLanguageMetadata):
    """Test parsing of VCS dependencies from requirements.txt."""
    metadata = pip_strategy.process_metadata(str(requirements_dir), mock_metadata)
    deps = metadata.dependencies
    
    # Check Git dependencies
    assert "flask-vcs" in deps
    flask_vcs = deps["flask-vcs"]
    assert flask_vcs.source == "git"
    assert flask_vcs.source_url == "https://github.com/pallets/flask-vcs.git"
    assert flask_vcs.source_reference == "2.0.0"
    
    assert "requests-vcs" in deps
    requests_vcs = deps["requests-vcs"]
    assert requests_vcs.source == "git"
    assert requests_vcs.source_url == "https://github.com/psf/requests-vcs.git"
    assert requests_vcs.source_reference == "main"
    # For non-version references, specifier should remain None
    assert requests_vcs.version.specifier is None

def test_environment_markers(pip_strategy: PipStrategy, requirements_dir: Path, mock_metadata: ProgrammingLanguageMetadata):
    """Test parsing of dependencies with environment markers from setup.py."""
    metadata = pip_strategy.process_metadata(str(requirements_dir), mock_metadata)
    deps = metadata.dependencies
    
    assert "importlib-metadata" in deps
    assert deps["importlib-metadata"].environment_marker == 'python_version < "3.8"'

def test_development_dependencies(pip_strategy: PipStrategy, requirements_dir: Path, mock_metadata: ProgrammingLanguageMetadata):
    """Test parsing of development dependencies from setup.py extras and requirements-dev.txt."""
    metadata = pip_strategy.process_metadata(str(requirements_dir), mock_metadata)
    deps = metadata.dependencies
    
    # From setup.py dev extras
    assert "black" in deps
    assert deps["black"].version.specifier == "==22.3.0"
    assert deps["black"].group == "dev"
    
    assert "flake8" in deps
    assert deps["flake8"].version.specifier == ">=3.9.0"
    assert deps["flake8"].group == "dev"
    
    assert "mypy" in deps
    assert deps["mypy"].version.specifier == ">=0.900"
    assert deps["mypy"].group == "dev"
    
    # From requirements-dev.txt
    assert "pytest" in deps
    assert deps["pytest"].version.specifier == ">=6.0.0"

def test_entry_points(pip_strategy: PipStrategy, requirements_dir: Path, mock_metadata: ProgrammingLanguageMetadata):
    """Test parsing of entry points from setup.py."""
    metadata = pip_strategy.process_metadata(str(requirements_dir), mock_metadata)
    
    assert "test-cli" in metadata.entry_points
    assert metadata.entry_points["test-cli"] == "test_package.cli:main"
    assert metadata.entry_points["serve"] == "test_package.server:run"

def test_types_requirements_parsing(pip_strategy: PipStrategy, types_requirements_dir: Path, mock_metadata: ProgrammingLanguageMetadata):
    """Test parsing of type stubs and development dependencies."""
    metadata = pip_strategy.process_metadata(str(types_requirements_dir), mock_metadata)
    deps = metadata.dependencies
    
    # Test type stubs
    assert "boto3-stubs" in deps
    assert deps["boto3-stubs"].version.specifier == "==1.34.133"
    assert deps["boto3-stubs"].extras and "s3" in deps["boto3-stubs"].extras
    
    assert "types-requests" in deps
    assert deps["types-requests"].version.specifier == "==2.28.11.17"
    
    # Test ML dependencies
    assert "cohere" in deps
    assert deps["cohere"].version.specifier == "==5.6.1"
    
    assert "sentence-transformers" in deps
    assert deps["sentence-transformers"].version.specifier == "==2.6.1"
    
    # Test development tools
    assert "black" in deps
    assert deps["black"].version.specifier == "==23.3.0"
    
    assert "ruff" in deps
    assert deps["ruff"].version.specifier == "==0.0.286"
    
    assert "pre-commit" in deps
    assert deps["pre-commit"].version.specifier == "==3.2.2"
    
    # Test data processing
    assert "pandas" in deps
    assert deps["pandas"].version.specifier == "==2.2.3"
    
    assert "lxml" in deps
    assert deps["lxml"].version.specifier == "==5.3.0"
    
    # Test testing tools
    assert "pytest" in deps
    assert deps["pytest"].version.specifier == "==7.4.4"
    
    assert "pytest-asyncio" in deps
    assert deps["pytest-asyncio"].version.specifier == "==0.22.0" 