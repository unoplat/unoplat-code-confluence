"""Abstract base strategy for data model detection across programming languages."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional, Tuple

from unoplat_code_confluence_commons.base_models import DataModelPosition

if TYPE_CHECKING:
    from src.code_confluence_flow_bridge.engine.programming_language.python.python_source_context import (
        PythonSourceContext,
    )
    from src.code_confluence_flow_bridge.engine.programming_language.typescript.typescript_source_context import (
        TypeScriptSourceContext,
    )


class DataModelDetectorStrategy(ABC):
    """Abstract base class for language-specific data model detection strategies."""

    @abstractmethod
    def detect(
        self,
        source_context: "PythonSourceContext | TypeScriptSourceContext",
        structural_signature: Optional[object] = None,
    ) -> Tuple[bool, DataModelPosition]:
        """
        Detect if a file contains data model definitions and their locations.

        Args:
            source_context: Pre-parsed language-specific source context containing
                source bytes, imports, import aliases, and the tree-sitter root.
            structural_signature: Optional structural signature for advanced detection

        Returns:
            Tuple containing:
                - bool: True if data models exist, False otherwise
                - DataModelPosition: Positions of detected data models
        """
        pass
