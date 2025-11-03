"""
Extensible data model detection for multiple programming languages.

This module provides language-agnostic data model detection by dispatching to
language-specific detection logic via factory pattern. It identifies files that
define data models such as dataclasses, entities, DTOs, schemas, etc.
"""

from typing import List, Optional, Tuple

from unoplat_code_confluence_commons.base_models import DataModelPosition
from unoplat_code_confluence_commons.programming_language_metadata import (
    ProgrammingLanguage,
)

from src.code_confluence_flow_bridge.detector.data_model_detector_factory import (
    DataModelDetectorFactory,
    UnsupportedLanguageForDataModelDetectionError,
)


def detect_data_model(
    source_code: str,
    imports: Optional[List[str]] = None,
    language: str = "",
    structural_signature: Optional[object] = None,
) -> Tuple[bool, DataModelPosition]:
    """
    Detect if a file contains data model definitions for any supported language.

    Args:
        source_code: The source code content
        imports: Optional list of import statements (already extracted)
        language: Programming language (e.g., "python", "typescript")
        structural_signature: Optional structural signature (for future use)

    Returns:
        Tuple containing:
            - bool: True if data models exist, False otherwise
            - DataModelPosition: Positions of detected data models

    Raises:
        UnsupportedLanguageForDataModelDetectionError: If language is not supported
    """
    try:
        # Convert string language to ProgrammingLanguage enum
        programming_language = ProgrammingLanguage(language.lower())
    except ValueError:
        # If language string is not a valid enum value, return no data models found
        return (False, DataModelPosition())

    try:
        # Get appropriate strategy from factory
        strategy = DataModelDetectorFactory.get_strategy(programming_language)

        # Delegate detection to language-specific strategy
        return strategy.detect(
            source_code=source_code,
            imports=imports,
            structural_signature=structural_signature,
        )
    except UnsupportedLanguageForDataModelDetectionError:
        # Language not supported for data model detection
        return (False, DataModelPosition())