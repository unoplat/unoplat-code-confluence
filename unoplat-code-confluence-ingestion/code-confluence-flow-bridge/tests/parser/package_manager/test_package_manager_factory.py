"""Unit tests for PackageManagerStrategyFactory.

Tests verify that the factory correctly routes programming language and package manager
combinations to their appropriate strategy implementations.
"""

import pytest
from src.code_confluence_flow_bridge.parser.package_manager.node.node_package_manager_strategy import (
    NodePackageManagerStrategy,
)
from src.code_confluence_flow_bridge.parser.package_manager.package_manager_factory import (
    PackageManagerStrategyFactory,
    UnsupportedPackageManagerError,
)
from src.code_confluence_flow_bridge.parser.package_manager.pip.pip_strategy import (
    PipStrategy,
)
from src.code_confluence_flow_bridge.parser.package_manager.poetry.poetry_strategy import (
    PythonPoetryStrategy,
)
from src.code_confluence_flow_bridge.parser.package_manager.uv.uv_strategy import (
    UvStrategy,
)
from unoplat_code_confluence_commons.programming_language_metadata import (
    PackageManagerType,
    ProgrammingLanguage,
)


class TestPackageManagerStrategyFactory:
    """Test suite for PackageManagerStrategyFactory."""

    # TypeScript Package Manager Tests

    def test_get_strategy_typescript_npm(self) -> None:
        """Verify NPM returns NodePackageManagerStrategy for TypeScript."""
        strategy = PackageManagerStrategyFactory.get_strategy(
            ProgrammingLanguage.TYPESCRIPT, PackageManagerType.NPM
        )
        assert isinstance(strategy, NodePackageManagerStrategy)

    def test_get_strategy_typescript_yarn(self) -> None:
        """Verify YARN returns NodePackageManagerStrategy for TypeScript."""
        strategy = PackageManagerStrategyFactory.get_strategy(
            ProgrammingLanguage.TYPESCRIPT, PackageManagerType.YARN
        )
        assert isinstance(strategy, NodePackageManagerStrategy)

    def test_get_strategy_typescript_pnpm(self) -> None:
        """Verify PNPM returns NodePackageManagerStrategy for TypeScript."""
        strategy = PackageManagerStrategyFactory.get_strategy(
            ProgrammingLanguage.TYPESCRIPT, PackageManagerType.PNPM
        )
        assert isinstance(strategy, NodePackageManagerStrategy)

    def test_get_strategy_typescript_bun(self) -> None:
        """Verify BUN returns NodePackageManagerStrategy for TypeScript."""
        strategy = PackageManagerStrategyFactory.get_strategy(
            ProgrammingLanguage.TYPESCRIPT, PackageManagerType.BUN
        )
        assert isinstance(strategy, NodePackageManagerStrategy)

    # Python Package Manager Tests

    def test_get_strategy_python_poetry(self) -> None:
        """Verify Poetry returns PythonPoetryStrategy for Python."""
        strategy = PackageManagerStrategyFactory.get_strategy(
            ProgrammingLanguage.PYTHON, PackageManagerType.POETRY
        )
        assert isinstance(strategy, PythonPoetryStrategy)

    def test_get_strategy_python_pip(self) -> None:
        """Verify Pip returns PipStrategy for Python."""
        strategy = PackageManagerStrategyFactory.get_strategy(
            ProgrammingLanguage.PYTHON, PackageManagerType.PIP
        )
        assert isinstance(strategy, PipStrategy)

    def test_get_strategy_python_uv(self) -> None:
        """Verify UV returns UvStrategy for Python."""
        strategy = PackageManagerStrategyFactory.get_strategy(
            ProgrammingLanguage.PYTHON, PackageManagerType.UV
        )
        assert isinstance(strategy, UvStrategy)

    # Name-based Strategy Resolution Tests

    def test_get_strategy_from_name_npm(self) -> None:
        """Verify name-based lookup works for npm."""
        strategy = PackageManagerStrategyFactory.get_strategy_from_name(
            ProgrammingLanguage.TYPESCRIPT, "npm"
        )
        assert isinstance(strategy, NodePackageManagerStrategy)

    def test_get_strategy_from_name_yarn(self) -> None:
        """Verify name-based lookup works for yarn."""
        strategy = PackageManagerStrategyFactory.get_strategy_from_name(
            ProgrammingLanguage.TYPESCRIPT, "yarn"
        )
        assert isinstance(strategy, NodePackageManagerStrategy)

    def test_get_strategy_from_name_pnpm(self) -> None:
        """Verify name-based lookup works for pnpm."""
        strategy = PackageManagerStrategyFactory.get_strategy_from_name(
            ProgrammingLanguage.TYPESCRIPT, "pnpm"
        )
        assert isinstance(strategy, NodePackageManagerStrategy)

    def test_get_strategy_from_name_bun(self) -> None:
        """Verify name-based lookup works for bun."""
        strategy = PackageManagerStrategyFactory.get_strategy_from_name(
            ProgrammingLanguage.TYPESCRIPT, "bun"
        )
        assert isinstance(strategy, NodePackageManagerStrategy)

    def test_get_strategy_from_name_poetry(self) -> None:
        """Verify name-based lookup works for poetry."""
        strategy = PackageManagerStrategyFactory.get_strategy_from_name(
            ProgrammingLanguage.PYTHON, "poetry"
        )
        assert isinstance(strategy, PythonPoetryStrategy)

    def test_get_strategy_from_name_pip(self) -> None:
        """Verify name-based lookup works for pip."""
        strategy = PackageManagerStrategyFactory.get_strategy_from_name(
            ProgrammingLanguage.PYTHON, "pip"
        )
        assert isinstance(strategy, PipStrategy)

    def test_get_strategy_from_name_uv(self) -> None:
        """Verify name-based lookup works for uv."""
        strategy = PackageManagerStrategyFactory.get_strategy_from_name(
            ProgrammingLanguage.PYTHON, "uv"
        )
        assert isinstance(strategy, UvStrategy)

    # Error Case Tests

    def test_get_strategy_unsupported_combination(self) -> None:
        """Verify UnsupportedPackageManagerError for invalid language/manager combination."""
        # Python with TypeScript package manager should fail
        with pytest.raises(UnsupportedPackageManagerError) as exc_info:
            PackageManagerStrategyFactory.get_strategy(
                ProgrammingLanguage.PYTHON, PackageManagerType.NPM
            )

        assert "Unsupported combination" in str(exc_info.value)
        assert "python" in str(exc_info.value).lower()
        assert "npm" in str(exc_info.value).lower()

    def test_get_strategy_from_name_unknown_manager(self) -> None:
        """Verify UnsupportedPackageManagerError for unknown package manager name."""
        with pytest.raises(UnsupportedPackageManagerError) as exc_info:
            PackageManagerStrategyFactory.get_strategy_from_name(
                ProgrammingLanguage.TYPESCRIPT, "unknown-manager"
            )

        assert "Unsupported package manager name" in str(exc_info.value)
        assert "unknown-manager" in str(exc_info.value)

    # Parametrized Tests for All TypeScript Package Managers

    @pytest.mark.parametrize(
        "package_manager_type",
        [
            PackageManagerType.NPM,
            PackageManagerType.YARN,
            PackageManagerType.PNPM,
            PackageManagerType.BUN,
        ],
    )
    def test_all_typescript_managers_return_node_strategy(
        self, package_manager_type: PackageManagerType
    ) -> None:
        """Verify all TypeScript package managers return NodePackageManagerStrategy."""
        strategy = PackageManagerStrategyFactory.get_strategy(
            ProgrammingLanguage.TYPESCRIPT, package_manager_type
        )
        assert isinstance(strategy, NodePackageManagerStrategy)

    @pytest.mark.parametrize(
        "manager_name,expected_strategy_type",
        [
            ("npm", NodePackageManagerStrategy),
            ("yarn", NodePackageManagerStrategy),
            ("pnpm", NodePackageManagerStrategy),
            ("bun", NodePackageManagerStrategy),
            ("poetry", PythonPoetryStrategy),
            ("pip", PipStrategy),
            ("uv", UvStrategy),
        ],
    )
    def test_name_to_strategy_mapping(
        self, manager_name: str, expected_strategy_type: type
    ) -> None:
        """Verify name-based lookup returns correct strategy type."""
        # Determine language based on manager name
        language = (
            ProgrammingLanguage.TYPESCRIPT
            if manager_name in {"npm", "yarn", "pnpm", "bun"}
            else ProgrammingLanguage.PYTHON
        )

        strategy = PackageManagerStrategyFactory.get_strategy_from_name(
            language, manager_name
        )
        assert isinstance(strategy, expected_strategy_type)
