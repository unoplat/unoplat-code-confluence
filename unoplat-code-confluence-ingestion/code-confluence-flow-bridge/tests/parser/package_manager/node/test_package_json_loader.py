# Standard Library
from pathlib import Path

# Third Party
import pytest

# First Party
from src.code_confluence_flow_bridge.parser.package_manager.node.package_json_loader import (
    load_package_json,
)
from unoplat_code_confluence_commons.programming_language_metadata import (
    PackageManagerType,
    ProgrammingLanguage,
    ProgrammingLanguageMetadata,
)

# Constants
TEST_DATA_DIR = (
    Path(__file__).parent.parent.parent.parent
    / "test_data"
    / "package_manager"
    / "node"
)


@pytest.fixture
def test_data_dir() -> Path:
    """Path to node package manager test data directory."""
    return TEST_DATA_DIR


@pytest.fixture
def mock_metadata() -> ProgrammingLanguageMetadata:
    """Mock metadata for Node.js/JavaScript projects."""
    return ProgrammingLanguageMetadata(
        language=ProgrammingLanguage.TYPESCRIPT,
        package_manager=PackageManagerType.NPM,
        language_version=">=18.0.0",
        manifest_path="package.json",
    )


@pytest.fixture
def application_package_dir(test_data_dir: Path, tmp_path: Path) -> Path:
    """Create temp directory with NPM application package.json."""
    package_json = tmp_path / "package.json"
    src = test_data_dir / "npm-application-package.json"
    package_json.write_text(src.read_text())
    return tmp_path


@pytest.fixture
def library_package_dir(test_data_dir: Path, tmp_path: Path) -> Path:
    """Create temp directory with NPM library package.json."""
    package_json = tmp_path / "package.json"
    src = test_data_dir / "npm-lib-package.json"
    package_json.write_text(src.read_text())
    return tmp_path


def test_application_package_comprehensive(
    application_package_dir: Path, mock_metadata: ProgrammingLanguageMetadata
) -> None:
    """Test comprehensive parsing of application package.json with all features."""
    manifest = load_package_json(str(application_package_dir), mock_metadata)

    # Basic metadata
    assert manifest.name == "unoplat-code-confluence-app"
    assert manifest.version == "1.5.0"
    assert (
        manifest.description
        == "A comprehensive test application package for validating package.json parsing"
    )
    assert manifest.manifest_path == "package.json"

    # Keywords
    assert manifest.keywords == ["testing", "package-manager", "nodejs", "application"]

    # Author as object
    assert manifest.author == {
        "name": "Unoplat Team",
        "email": "team@unoplat.com",
        "url": "https://unoplat.com",
    }

    # Contributors and maintainers as arrays
    assert len(manifest.contributors) == 2
    assert manifest.contributors[0]["name"] == "Contributor One"
    assert manifest.contributors[0]["email"] == "contributor1@unoplat.com"

    assert len(manifest.maintainers) == 1
    assert manifest.maintainers[0]["name"] == "Maintainer One"

    # License, repository, bugs, homepage
    assert manifest.license == "MIT"
    assert manifest.repository == {
        "type": "git",
        "url": "https://github.com/unoplat/unoplat-code-confluence.git",
    }
    assert manifest.bugs == {
        "url": "https://github.com/unoplat/unoplat-code-confluence/issues",
        "email": "bugs@unoplat.com",
    }
    assert (
        manifest.homepage == "https://github.com/unoplat/unoplat-code-confluence#readme"
    )

    # Scripts
    assert "build" in manifest.scripts
    assert manifest.scripts["build"] == "tsc"
    assert manifest.scripts["test"] == "jest"
    assert manifest.scripts["start"] == "node dist/index.js"

    # Bin should be empty dict for application (no bin field in test data)
    assert manifest.bin == {}

    # Dependencies - 5 groups (no bundled dependencies in npm-compliant version)
    deps = manifest.dependencies

    # Default dependencies
    assert "default" in deps
    assert "express" in deps["default"]
    assert deps["default"]["express"] == "^4.18.2"
    assert "typescript" in deps["default"]
    assert deps["default"]["typescript"] == "^5.3.0"
    assert "dotenv" in deps["default"]
    assert deps["default"]["dotenv"] == "^16.3.1"

    # Dev dependencies
    assert "dev" in deps
    assert "@types/node" in deps["dev"]
    assert deps["dev"]["@types/node"] == "^20.10.0"
    assert "jest" in deps["dev"]
    assert deps["dev"]["jest"] == "^29.7.0"

    # Peer dependencies
    assert "peer" in deps
    assert "react" in deps["peer"]
    assert deps["peer"]["react"] == ">=18.0.0"
    assert "react-dom" in deps["peer"]
    assert deps["peer"]["react-dom"] == ">=18.0.0"

    # Optional dependencies
    assert "optional" in deps
    assert "fsevents" in deps["optional"]
    assert deps["optional"]["fsevents"] == "^2.3.3"

    # Bundled dependencies should be empty (not used in npm-compliant version)
    assert "bundled" in deps
    assert deps["bundled"] == {}

    # Override dependencies (simple version strings per npm semantics)
    assert "override" in deps
    assert "lodash" in deps["override"]
    assert deps["override"]["lodash"] == "^4.17.21"
    assert "axios" in deps["override"]
    assert deps["override"]["axios"] == "^1.6.2"

    # Engines
    assert manifest.engines is not None
    assert manifest.engines["node"] == ">=18.0.0"
    assert manifest.engines["npm"] == ">=9.0.0"

    # Package manager field
    assert manifest.package_manager_field == "npm@10.2.3"

    # Workspaces
    assert manifest.workspaces == ["packages/*", "apps/*"]

    # Main and types
    assert manifest.main == "dist/index.js"
    assert manifest.types == "dist/index.d.ts"


def test_library_package_comprehensive(
    library_package_dir: Path, mock_metadata: ProgrammingLanguageMetadata
) -> None:
    """Test comprehensive parsing of library package.json with TypeScript features."""
    manifest = load_package_json(str(library_package_dir), mock_metadata)

    # Basic metadata
    assert manifest.name == "@unoplat/example-library"
    assert manifest.version == "2.3.1"
    assert (
        manifest.description
        == "A comprehensive test library package for validating package.json parsing with TypeScript support"
    )
    assert manifest.manifest_path == "package.json"

    # Keywords as array (npm-compliant)
    assert isinstance(manifest.keywords, list)
    assert manifest.keywords == ["typescript", "library", "utility", "package-manager"]

    # Author as string
    assert manifest.author == "Unoplat Team <team@unoplat.com>"

    # Maintainers as array
    assert len(manifest.maintainers) == 2
    assert manifest.maintainers[0]["name"] == "Maintainer One"
    assert manifest.maintainers[1]["email"] == "maintainer2@unoplat.com"

    # License, repository, bugs, homepage
    assert manifest.license == "MIT"
    assert manifest.repository == {
        "type": "git",
        "url": "https://github.com/unoplat/example-library.git",
    }
    assert manifest.bugs == {"url": "https://github.com/unoplat/example-library/issues"}
    assert manifest.homepage == "https://github.com/unoplat/example-library#readme"

    # Scripts
    assert "build" in manifest.scripts
    assert manifest.scripts["build"] == "tsc && rollup -c"
    assert manifest.scripts["test"] == "vitest"
    assert manifest.scripts["prepublishOnly"] == "npm run build && npm test"

    # Bin as object (npm-compliant format, already normalized in test data)
    assert isinstance(manifest.bin, dict)
    assert "unoplat-example-library" in manifest.bin
    assert manifest.bin["unoplat-example-library"] == "./bin/cli.js"

    # Dependencies
    deps = manifest.dependencies
    assert "default" in deps
    assert "chalk" in deps["default"]
    assert deps["default"]["chalk"] == "^5.3.0"
    assert "commander" in deps["default"]
    assert deps["default"]["commander"] == "^11.1.0"

    # Dev dependencies
    assert "dev" in deps
    assert "typescript" in deps["dev"]
    assert deps["dev"]["typescript"] == "^5.3.0"
    assert "vitest" in deps["dev"]
    assert deps["dev"]["vitest"] == "^1.0.4"

    # Peer dependencies
    assert "peer" in deps
    assert "typescript" in deps["peer"]
    assert deps["peer"]["typescript"] == ">=4.5.0"

    # TypeScript-specific fields
    assert manifest.main == "dist/index.js"
    assert manifest.module == "dist/index.mjs"
    assert manifest.types == "dist/index.d.ts"

    # Exports configuration
    assert manifest.exports is not None
    assert "." in manifest.exports
    assert "import" in manifest.exports["."]
    assert manifest.exports["."]["import"] == "./dist/index.mjs"
    assert manifest.exports["."]["require"] == "./dist/index.js"
    assert manifest.exports["."]["types"] == "./dist/index.d.ts"
    assert "./utils" in manifest.exports

    # typesVersions
    assert manifest.types_versions is not None
    assert ">=4.0" in manifest.types_versions
    assert manifest.types_versions[">=4.0"]["*"] == ["dist/*"]

    # Engines
    assert manifest.engines is not None
    assert manifest.engines["node"] == ">=16.0.0"
    assert manifest.engines["npm"] == ">=8.0.0"

    # Package manager field
    assert manifest.package_manager_field == "npm@10.2.3"

    # Workspaces should be None for library
    assert manifest.workspaces is None
