# Standard Library
from pathlib import Path
import pytest

# First Party
from src.code_confluence_flow_bridge.models.configuration.settings import (
    ProgrammingLanguageMetadata,
    ProgrammingLanguage,
    PackageManagerType
)
from src.code_confluence_flow_bridge.parser.package_manager.pip.pip_strategy import PipStrategy

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
        language_version="3.8.0"
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

def test_setup_py_parsing(pip_strategy: PipStrategy, requirements_dir: Path, mock_metadata: ProgrammingLanguageMetadata):
    """Test parsing of core dependencies and metadata from setup.py."""
    metadata = pip_strategy.process_metadata(str(requirements_dir), mock_metadata)
    
    # Check basic metadata
    assert metadata.package_name == "test-package"
    assert metadata.project_version == "1.0.0"
    assert metadata.description == "Test package for setup.py parsing"
    assert metadata.license == "MIT"
    assert "Test Author <test@example.com>" in metadata.authors
    
    # Check programming language metadata
    assert metadata.programming_language == ProgrammingLanguage.PYTHON.value
    assert metadata.package_manager == PackageManagerType.PIP.value
    assert metadata.programming_language_version == ">=3.7"
    
    # Check core dependencies
    deps = metadata.dependencies
    assert "requests" in deps
    assert deps["requests"].version.minimum_version == ">=2.0.0"
    
    assert "flask" in deps
    assert deps["flask"].version.minimum_version == ">=2.0.0"
    
    assert "redis" in deps
    assert deps["redis"].extras == ["hiredis"]
    assert deps["redis"].version.minimum_version == ">=4.0.0"

def test_requirements_parsing(pip_strategy: PipStrategy, requirements_dir: Path, mock_metadata: ProgrammingLanguageMetadata):
    """Test parsing of additional dependencies from requirements.txt."""
    metadata = pip_strategy.process_metadata(str(requirements_dir), mock_metadata)
    deps = metadata.dependencies
    
    # Check additional runtime dependencies
    assert "urllib3" in deps
    assert deps["urllib3"].version.minimum_version == ">=1.21.1"
    assert deps["urllib3"].version.maximum_version == "<1.26"
    
    # Check dependencies with extras
    assert "celery" in deps
    assert set(deps["celery"].extras) == {"redis", "rabbitmq"}
    assert deps["celery"].version.minimum_version == ">=5.0.0"

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
    assert deps["black"].version.current_version == "==22.3.0"
    assert deps["black"].group == "dev"
    
    assert "flake8" in deps
    assert deps["flake8"].version.minimum_version == ">=3.9.0"
    assert deps["flake8"].group == "dev"
    
    assert "mypy" in deps
    assert deps["mypy"].version.minimum_version == ">=0.900"
    assert deps["mypy"].group == "dev"
    
    # From requirements-dev.txt
    assert "pytest" in deps
    assert deps["pytest"].version.minimum_version == ">=6.0.0"

def test_entry_points(pip_strategy: PipStrategy, requirements_dir: Path, mock_metadata: ProgrammingLanguageMetadata):
    """Test parsing of entry points from setup.py."""
    metadata = pip_strategy.process_metadata(str(requirements_dir), mock_metadata)
    
    assert "test-cli" in metadata.entry_points
    assert metadata.entry_points["test-cli"] == "test_package.cli:main"
    assert metadata.entry_points["serve"] == "test_package.server:run" 