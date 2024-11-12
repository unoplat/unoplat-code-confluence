from typing import Dict
from unoplat_code_confluence.language_custom_parsing.python.package_manager.package_manager_strategy import PackageManagerStrategy
from unoplat_code_confluence.language_custom_parsing.python.package_naming.package_naming_strategy import UnsupportedLanguageError
from unoplat_code_confluence.language_custom_parsing.python.package_manager.poetry.poetry_strategy import PythonPoetryStrategy
#from unoplat_code_confluence.language_custom_parsing.package_manager.pip.pip_strategy import PythonPipStrategy



class PackageManagerStrategyFactory:
    _strategies: Dict[str, Dict[str, type[PackageManagerStrategy]]] = {
        "python": {
            "poetry": PythonPoetryStrategy,
           # "pip": PythonPipStrategy
        }
    }

    @classmethod
    def get_strategy(cls, programming_language: str, package_manager: str) -> PackageManagerStrategy:
        if programming_language not in cls._strategies:
            raise UnsupportedLanguageError(f"Unsupported programming language: {programming_language}")
        
        if package_manager not in cls._strategies[programming_language]:
            raise UnsupportedPackageManagerError(
                f"Unsupported package manager {package_manager} for language {programming_language}"
            )
        
        return cls._strategies[programming_language][package_manager]()

class UnsupportedPackageManagerError(Exception):
    pass 