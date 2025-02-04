# Standard Library
# First Party
from src.code_confluence_flow_bridge.models.configuration.settings import (
    PackageManagerType,
    ProgrammingLanguage,
)
from src.code_confluence_flow_bridge.parser.package_manager.package_manager_strategy import (
    PackageManagerStrategy,
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

from typing import Dict, Tuple


class PackageManagerStrategyFactory:
    # Map (language, package_manager) pairs to their strategy classes
    _strategies: Dict[Tuple[ProgrammingLanguage, PackageManagerType], type[PackageManagerStrategy]] = {
        (ProgrammingLanguage.PYTHON, PackageManagerType.POETRY): PythonPoetryStrategy,
        (ProgrammingLanguage.PYTHON, PackageManagerType.PIP): PipStrategy,
        (ProgrammingLanguage.PYTHON, PackageManagerType.UV): UvStrategy,
    }

    @classmethod
    def get_strategy(cls, programming_language: ProgrammingLanguage, package_manager_type: PackageManagerType) -> PackageManagerStrategy:
        """
        Get appropriate package manager strategy based on programming language and package manager

        Args:
            metadata: Programming language metadata from config

        Returns:
            PackageManagerStrategy: Appropriate strategy instance

        Raises:
            UnsupportedPackageManagerError: If combination is not supported
        """
        key = (programming_language, package_manager_type)

        if key not in cls._strategies:
            raise UnsupportedPackageManagerError(f"Unsupported combination - Language: {programming_language}, " f"Package Manager: {package_manager_type}")

        return cls._strategies[key]()


class UnsupportedPackageManagerError(Exception):
    pass
