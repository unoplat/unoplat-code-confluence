"""Abstract base strategy for data model detection across programming languages."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Tuple

from unoplat_code_confluence_commons.base_models import DataModelPosition

from code_confluence_flow_bridge.engine.programming_language.common.source_context import (
    BaseSourceContext,
)


class DataModelDetectorStrategy(ABC):
    """Abstract base class for language-specific data model detection strategies."""

    @abstractmethod
    def detect(
        self,
        source_context: BaseSourceContext,
    ) -> Tuple[bool, DataModelPosition]:
        """
        Detect if a file contains data model definitions and their locations.

        Args:
            source_context: Pre-parsed source context containing
                source bytes, imports, import aliases, and the tree-sitter root.
        Returns:
            Tuple containing:
                - bool: True if data models exist, False otherwise
                - DataModelPosition: Positions of detected data models
        """
        pass
