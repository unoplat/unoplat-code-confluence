import os
from pathlib import Path
from typing import Dict, List
import pytest
from packaging.requirements import Requirement

from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_package_manager_metadata import UnoplatPackageManagerMetadata
from src.code_confluence_flow_bridge.models.configuration.settings import (
    ProgrammingLanguageMetadata,
    ProgrammingLanguage,
    PackageManagerType
)
from src.code_confluence_flow_bridge.parser.package_manager.pip.pip_strategy import PipStrategy
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_project_dependency import UnoplatProjectDependency

# TODO: 4. Potential Edge Cases or Rare Scenarios
# While you do have strong coverage, here are a few scenarios you might want to confirm or test for completeness:
# Nested Requirements: If a requirements.txt references another file (e.g., “-r common.txt”) recursively. This is somewhat less common, but can occur in multi-file setups.
# Editable Installs (-e . or -e <vcs_url>): If you want to track these as dependencies.
# Markers that are more complex (e.g., platform_system == "Linux" or python_full_version).
# Extra advanced features like optional sub-dependencies under a VCS reference.
# Most people won’t need these, but if you run across them, you might add separate dedicated tests.

# Constants
TEST_DATA_DIR = Path(__file__).parent.parent.parent / "data"

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
    for filename in ["requirements.txt", "requirements-dev.txt", "constraints.txt"]:
        src = TEST_DATA_DIR / "requirements" / filename
        dst = req_dir.parent / filename
        dst.write_text(src.read_text())
    
    return req_dir.parent

@pytest.fixture
def setup_dir(tmp_path: Path) -> Path:
    """Create a temporary directory with test setup.py."""
    setup_file = tmp_path / "setup.py"
    src = TEST_DATA_DIR / "setup" / "setup.py"
    setup_file.write_text(src.read_text())
    return tmp_path

def test_basic_requirements_parsing(pip_strategy: PipStrategy, requirements_dir: Path):
    """Test parsing of basic requirements without environment markers or extras."""
    deps = pip_strategy._parse_all_requirements(str(requirements_dir))
    
    # Check basic version constraints
    assert "requests" in deps
    assert deps["requests"].version.minimum_version == ">=2.0.0"
    assert deps["requests"].version.maximum_version == "<3.0.0"
    
    assert "flask" in deps
    assert deps["flask"].version.current_version == "==2.0.0"

def test_vcs_dependencies(pip_strategy: PipStrategy, requirements_dir: Path):
    """Test parsing of VCS dependencies."""
    deps = pip_strategy._parse_all_requirements(str(requirements_dir))
    
    # Check Git dependency
    flask_vcs = deps["flask-vcs"]
    assert flask_vcs.source == "git"
    assert flask_vcs.source_url == "https://github.com/pallets/flask-vcs.git"
    assert flask_vcs.source_reference == "2.0.0"

def test_environment_markers(pip_strategy: PipStrategy, requirements_dir: Path):
    """Test parsing of dependencies with environment markers."""
    deps = pip_strategy._parse_all_requirements(str(requirements_dir))
    
    assert "importlib-metadata" in deps
    assert deps["importlib-metadata"].environment_marker == 'python_version < "3.8"'

def test_extras_parsing(pip_strategy: PipStrategy, requirements_dir: Path):
    """Test parsing of dependencies with extras."""
    deps = pip_strategy._parse_all_requirements(str(requirements_dir))
    
    assert "redis" in deps
    assert "hiredis" in deps["redis"].extras
    
    assert "celery" in deps
    assert set(deps["celery"].extras) == {"redis", "rabbitmq"}

def test_constraint_merging(pip_strategy: PipStrategy, requirements_dir: Path):
    """Test that constraints are properly merged with requirements."""
    deps = pip_strategy._parse_all_requirements(str(requirements_dir))
    
    # Check that pytest version constraint includes both requirement and constraint
    assert "pytest" in deps
    assert deps["pytest"].version.minimum_version == ">=6.0.0"
    assert deps["pytest"].version.maximum_version == "<=7.0.0"

def test_setup_py_parsing(pip_strategy: PipStrategy, setup_dir: Path, mock_metadata: ProgrammingLanguageMetadata):
    """Test parsing of setup.py metadata and dependencies."""
    metadata: UnoplatPackageManagerMetadata = pip_strategy.process_metadata(str(setup_dir), mock_metadata)
    
    # Check basic metadata
    assert metadata.package_name == "test-package"
    assert metadata.project_version == "1.0.0"
    assert metadata.description == "Test package for setup.py parsing"
    assert metadata.license == "MIT"
    assert "Test Author <test@example.com>" in metadata.authors
    
    # Check programming language metadata
    assert metadata.programming_language == ProgrammingLanguage.PYTHON.value
    assert metadata.package_manager == PackageManagerType.PIP.value
    assert metadata.programming_language_version == ">=3.7"  # From setup.py python_requires
    
    # Check dependencies
    deps = metadata.dependencies
    assert "requests" in deps
    assert deps["requests"].version.minimum_version == ">=2.0.0"
    assert "flask" in deps
    assert deps["flask"].version.minimum_version == ">=2.0.0"
    assert "redis" in deps
    assert deps["redis"].extras == ["hiredis"]
    assert deps["redis"].version.minimum_version == ">=4.0.0"
    
    # Check entry points
    assert metadata.entry_points["test-cli"] == "test_package.cli:main"
    assert metadata.entry_points["serve"] == "test_package.server:run"

def test_combined_requirements_and_setup(
    pip_strategy: PipStrategy,
    requirements_dir: Path,
    setup_dir: Path,
    mock_metadata: ProgrammingLanguageMetadata
):
    """Test combining dependencies from both requirements files and setup.py."""
    # Copy setup.py to requirements directory
    setup_py = setup_dir / "setup.py"
    (requirements_dir / "setup.py").write_text(setup_py.read_text())
    
    metadata: UnoplatPackageManagerMetadata = pip_strategy.process_metadata(str(requirements_dir), mock_metadata)
    
    # Check basic metadata is from setup.py
    assert metadata.package_name == "test-package"
    assert metadata.project_version == "1.0.0"
    assert metadata.description == "Test package for setup.py parsing"
    assert metadata.license == "MIT"
    
    # Check programming language metadata
    assert metadata.programming_language == ProgrammingLanguage.PYTHON.value
    assert metadata.package_manager == PackageManagerType.PIP.value
    assert metadata.programming_language_version == ">=3.7"  # From setup.py python_requires
    
    # Should have dependencies from both sources with merged version constraints
    deps = metadata.dependencies
    
    # From both requirements.txt and setup.py
    assert "requests" in deps
    assert deps["requests"].version.minimum_version == ">=2.0.0"
    assert deps["requests"].version.maximum_version == "<3.0.0"  # From constraints.txt
    
    # From both but with different versions
    assert "flask" in deps
    assert deps["flask"].version.minimum_version == ">=2.0.0"  # From setup.py
    
    # From requirements-dev.txt only
    assert "black" in deps
    assert deps["black"].version.current_version == "==22.3.0"
    assert "flake8" in deps
    assert deps["flake8"].version.minimum_version == ">=3.9.0"
    
    # From setup.py extras_require only
    assert "boto3" in deps
    assert deps["boto3"].version.minimum_version == ">=1.20.0"
    assert "s3transfer" in deps
    assert deps["s3transfer"].version.minimum_version == ">=0.5.0" 