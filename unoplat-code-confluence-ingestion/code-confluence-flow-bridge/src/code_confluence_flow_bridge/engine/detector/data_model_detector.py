"""
Extensible data model detection for multiple programming languages.

This module provides language-agnostic data model detection by dispatching to
language-specific detection logic via factory pattern. It identifies files that
define data models such as dataclasses, entities, DTOs, schemas, etc.
"""

from __future__ import annotations

from typing import Tuple

from unoplat_code_confluence_commons.base_models import DataModelPosition
from unoplat_code_confluence_commons.programming_language_metadata import (
    ProgrammingLanguage,
)

from code_confluence_flow_bridge.engine.detector.data_model_detector_factory import (
    DataModelDetectorFactory,
    UnsupportedLanguageForDataModelDetectionError,
)
from code_confluence_flow_bridge.engine.programming_language.common.source_context import (
    BaseSourceContext,
)


def detect_data_model(
    source_context: BaseSourceContext,
    language: str = "",
) -> Tuple[bool, DataModelPosition]:
    """
    Detect if a file contains data model definitions for any supported language.

    Args:
        source_context: Pre-parsed source context containing
            source bytes, imports, import aliases, and the tree-sitter root.
        language: Programming language (e.g., "python", "typescript")
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
        return strategy.detect(source_context=source_context)
    except UnsupportedLanguageForDataModelDetectionError:
        # Language not supported for data model detection
        return (False, DataModelPosition())
