"""
Abstract base class for language-specific framework detection services.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List, Optional

from unoplat_code_confluence_commons.base_models import (
    Detection,
    PythonStructuralSignature,
    TypeScriptStructuralSignature,
)

if TYPE_CHECKING:
    from src.code_confluence_flow_bridge.engine.programming_language.python.python_source_context import (
        PythonSourceContext,
    )
    from src.code_confluence_flow_bridge.engine.programming_language.typescript.typescript_source_context import (
        TypeScriptSourceContext,
    )


class FrameworkDetectionService(ABC):
    """Abstract base for language-specific framework detection services."""

    @abstractmethod
    async def detect_features(
        self,
        source_code: Optional[str],
        imports: List[str],
        structural_signature: PythonStructuralSignature | TypeScriptStructuralSignature | None,
        programming_language: str,
        source_context: PythonSourceContext | TypeScriptSourceContext | None = None,
    ) -> List[Detection]:
        """
        Detect framework features in source code using imports and structural signature.

        Args:
            source_code: Source code to analyze
            imports: List of imports in the file
            structural_signature: Structural signature of the file (optional)
            programming_language: Programming language (e.g., "python", "typescript")
            source_context: Pre-parsed source context to avoid double-parsing (optional)

        Returns:
            List of Detection objects for framework features found
        """
        pass
