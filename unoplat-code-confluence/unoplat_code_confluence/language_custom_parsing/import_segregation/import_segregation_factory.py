from typing import Dict

from unoplat_code_confluence.language_custom_parsing.import_segregation.import_segregation_strategy import ImportSegregationStrategy
from unoplat_code_confluence.language_custom_parsing.import_segregation.python.python_import_segregation_strategy import PythonImportSegregationStrategy
from unoplat_code_confluence.language_custom_parsing.package_naming.package_naming_strategy import UnsupportedLanguageError

class ImportSegregationStrategyFactory:
    _strategies: Dict[str, type[ImportSegregationStrategy]] = {
        "python": PythonImportSegregationStrategy
    }

    @classmethod
    def get_strategy(cls, programming_language: str, programming_language_version: str | None = None) -> ImportSegregationStrategy:
        """Get the appropriate import segregation strategy for the given programming language.
        
        Args:
            programming_language: The programming language to get the strategy for
            programming_language_version: The version of the programming language to get the strategy for
        Returns:
            ImportSegregationStrategy: The strategy for the given language
            
        Raises:
            UnsupportedLanguageError: If the language is not supported
        """
        if programming_language not in cls._strategies:
            raise UnsupportedLanguageError(f"Unsupported programming language: {programming_language}")
        strategy = cls._strategies[programming_language]
        
        return strategy(programming_language_version)
