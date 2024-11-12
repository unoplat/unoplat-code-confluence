from typing import Dict
from unoplat_code_confluence.language_custom_parsing.qualified_name.qualified_name_strategy import QualifiedNameStrategy
from unoplat_code_confluence.language_custom_parsing.qualified_name.python.python_qualified_name_strategy import PythonQualifiedNameStrategy

class UnsupportedLanguageError(Exception):
    pass

class QualifiedNameStrategyFactory:
    _strategies: Dict[str, type[QualifiedNameStrategy]] = {
        "python": PythonQualifiedNameStrategy
    }

    @classmethod
    def get_strategy(cls, programming_language: str) -> QualifiedNameStrategy:
        """Get the appropriate qualified name strategy for the given programming language.
        
        Args:
            programming_language: The programming language to get the strategy for
            
        Returns:
            QualifiedNameStrategy: The strategy for the given language
            
        Raises:
            UnsupportedLanguageError: If the language is not supported
        """
        if programming_language not in cls._strategies:
            raise UnsupportedLanguageError(f"Unsupported programming language: {programming_language}")
        
        return cls._strategies[programming_language]() 