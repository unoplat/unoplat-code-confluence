"""Factory for creating language-specific data model detector strategies."""

from typing import Dict

from unoplat_code_confluence_commons.programming_language_metadata import (
    ProgrammingLanguage,
)

from src.code_confluence_flow_bridge.engine.detector.data_model_detector_strategy import (
    DataModelDetectorStrategy,
)
from src.code_confluence_flow_bridge.engine.programming_language.python.python_data_model_detector_strategy import (
    PythonDataModelDetectorStrategy,
)
from src.code_confluence_flow_bridge.engine.programming_language.typescript.typescript_data_model_detector_strategy import (
    TypeScriptDataModelDetectorStrategy,
)


class DataModelDetectorFactory:
    """Factory for creating data model detector strategies based on programming language."""

    # Map programming languages to their detector strategy classes
    _strategies: Dict[ProgrammingLanguage, type[DataModelDetectorStrategy]] = {
        ProgrammingLanguage.PYTHON: PythonDataModelDetectorStrategy,
        ProgrammingLanguage.TYPESCRIPT: TypeScriptDataModelDetectorStrategy,
    }

    @classmethod
    def get_strategy(
        cls, programming_language: ProgrammingLanguage
    ) -> DataModelDetectorStrategy:
        """
        Get appropriate data model detector strategy based on programming language.

        Args:
            programming_language: Programming language enum value

        Returns:
            DataModelDetectorStrategy: Appropriate strategy instance

        Raises:
            UnsupportedLanguageForDataModelDetectionError: If language is not supported
        """
        if programming_language not in cls._strategies:
            raise UnsupportedLanguageForDataModelDetectionError(
                f"Unsupported language for data model detection: {programming_language}"
            )

        return cls._strategies[programming_language]()


class UnsupportedLanguageForDataModelDetectionError(Exception):
    """Raised when data model detection is not supported for a given language."""

    pass
