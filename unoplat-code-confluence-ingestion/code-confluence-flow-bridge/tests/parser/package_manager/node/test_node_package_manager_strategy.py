# Standard Library
from pathlib import Path

# Third Party
import pytest

# First Party
from src.code_confluence_flow_bridge.parser.package_manager.node.node_package_manager_strategy import (
    NodePackageManagerStrategy,
)
from unoplat_code_confluence_commons.programming_language_metadata import (
    PackageManagerType,
    ProgrammingLanguage,
    ProgrammingLanguageMetadata,
)

# Constants
TEST_DATA_DIR = (
    Path(__file__).parent.parent.parent.parent / "test_data" / "package_manager" / "node"
)


@pytest.fixture
def node_strategy() -> NodePackageManagerStrategy:
    """Create a NodePackageManagerStrategy instance."""
    return NodePackageManagerStrategy()


@pytest.fixture
def node_metadata() -> ProgrammingLanguageMetadata:
    """Create metadata for Node.js projects."""
    return ProgrammingLanguageMetadata(
        language=ProgrammingLanguage.TYPESCRIPT,
        package_manager=PackageManagerType.NPM,
        language_version=None,
        manifest_path="package.json",
    )


@pytest.fixture
def library_package_dir(tmp_path: Path) -> Path:
    """Write library package.json to temporary directory."""
    package_json = tmp_path / "package.json"
    src = TEST_DATA_DIR / "npm-lib-package.json"
    package_json.write_text(src.read_text())
    return tmp_path


@pytest.fixture
def application_package_dir(tmp_path: Path) -> Path:
    """Write application package.json to temporary directory."""
    package_json = tmp_path / "package.json"
    src = TEST_DATA_DIR / "npm-application-package.json"
    package_json.write_text(src.read_text())
    return tmp_path


def test_library_package_metadata(node_strategy: NodePackageManagerStrategy, node_metadata: ProgrammingLanguageMetadata, library_package_dir: Path) -> None:
    """Ensure library packages surface TypeScript metadata and entry points."""
    metadata = node_strategy.process_metadata(str(library_package_dir), node_metadata)

    # TypeScript version prefers devDependencies entry
    assert metadata.programming_language_version == "^5.3.0"

    # Entry points include simple fields and flattened exports
    entry_points = metadata.entry_points
    assert entry_points["main"] == "dist/index.js"
    assert entry_points["module"] == "dist/index.mjs"
    assert entry_points["types"] == "dist/index.d.ts"
    assert entry_points["export:.:import"] == "./dist/index.mjs"
    assert entry_points["export:./utils:require"] == "./dist/utils/index.js"

    # Repository pulled from object form without normalization
    assert metadata.repository == "https://github.com/unoplat/example-library.git"

    # Maintainers normalized to string representations
    assert "Maintainer One <maintainer1@unoplat.com>" in metadata.maintainers
    assert "Maintainer Two <maintainer2@unoplat.com>" in metadata.maintainers

    # License normalized to dict
    assert metadata.license == {"text": "MIT"}

    # Dependency groups converted to UnoplatProjectDependency instances
    deps = metadata.dependencies
    assert deps["default"]["chalk"].version.specifier == "^5.3.0"
    assert deps["dev"]["typescript"].version.specifier == "^5.3.0"
    assert deps["peer"]["typescript"].version.specifier == ">=4.5.0"


def test_application_package_engine_fallback(node_strategy: NodePackageManagerStrategy, node_metadata: ProgrammingLanguageMetadata, application_package_dir: Path) -> None:
    """Verify TypeScript inference falls back to engines.node when no TypeScript deps."""
    metadata = node_strategy.process_metadata(str(application_package_dir), node_metadata)

    # No typescript in dev/peer; engine fallback should drive language version
    assert metadata.programming_language_version == ">=18.0.0"

    # Override entries parsed as dependencies
    overrides = metadata.dependencies["override"]
    assert overrides["lodash"].version.specifier == "^4.17.21"
    assert overrides["axios"].version.specifier == "^1.6.2"
