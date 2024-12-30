# Standard Library
from typing import Dict

# First Party
from src.code_confluence_flow_bridge.parser.python.package_manager.package_manager_strategy import PackageManagerStrategy
from src.code_confluence_flow_bridge.parser.python.package_manager.pip.pip_strategy import PipStrategy
from src.code_confluence_flow_bridge.parser.python.package_manager.poetry.poetry_strategy import PythonPoetryStrategy


class PackageManagerStrategyFactory:
    _strategies: Dict[str, type[PackageManagerStrategy]] = {
        "poetry": PythonPoetryStrategy,
        "pip": PipStrategy   
    }

    @classmethod
    def get_strategy(cls, package_manager: str) -> PackageManagerStrategy:
        
        if package_manager not in cls._strategies:
            raise UnsupportedPackageManagerError(
                f"Unsupported package manager {package_manager}"
            )
        
        return cls._strategies[package_manager]()

class UnsupportedPackageManagerError(Exception):
    pass 