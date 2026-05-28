"""
Abstract base class for language-specific framework detection services.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from unoplat_code_confluence_commons.base_models import Detection

from code_confluence_flow_bridge.engine.programming_language.common.source_context import (
    BaseSourceContext,
)


class FrameworkDetectionService(ABC):
    """Abstract base for language-specific framework detection services."""

    @abstractmethod
    async def detect_features(
        self,
        source_context: BaseSourceContext,
        programming_language: str,
    ) -> List[Detection]:
        """
        Detect framework features in source code using parsed source context.

        Args:
            source_context: Parsed source context containing source
                bytes, imports, import aliases, and the tree-sitter root node.
            programming_language: Programming language (e.g., "python", "typescript")

        Returns:
            List of Detection objects for framework features found
        """
        pass
