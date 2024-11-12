from typing import Dict, Type
from unoplat_code_confluence.language_custom_parsing.package_naming.package_naming_strategy import (
    PackageNamingStrategy,
    DefaultPackageNamingStrategy
)
from unoplat_code_confluence.language_custom_parsing.package_naming.python.python_package_naming_strategy import PythonPackageNamingStrategy
class PackageNamingStrategyFactory:
    """Factory for creating language-specific package naming strategies."""
    
    _strategies: Dict[str, Type[PackageNamingStrategy]] = {
        'python': PythonPackageNamingStrategy
    }
    
    @classmethod
    def get_strategy(cls, programming_language: str) -> PackageNamingStrategy:
        """
        Get the appropriate package naming strategy for the given programming language.
        
        Args:
            programming_language: The programming language identifier
            
        Returns:
            PackageNamingStrategy: An instance of the appropriate strategy
        """
        strategy_class = cls._strategies.get(programming_language.lower(), DefaultPackageNamingStrategy)
        return strategy_class() 