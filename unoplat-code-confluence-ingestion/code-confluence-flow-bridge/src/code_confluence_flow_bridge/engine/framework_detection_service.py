"""
Abstract base class for language-specific framework detection services.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from unoplat_code_confluence_commons.base_models import StructuralSignature, Detection


class FrameworkDetectionService(ABC):
    """Abstract base for language-specific framework detection services."""
    
    @abstractmethod
    async def detect_features(
        self, 
        source_code: Optional[str],
        imports: List[str],
        structural_signature: StructuralSignature | None,
        programming_language: str
    ) -> List[Detection]:
        """
        Detect framework features in source code using imports and structural signature.
        
        Args:
            source_code: Source code to analyze
            imports: List of imports in the file
            structural_signature: Structural signature of the file (optional)
            programming_language: Programming language (e.g., "python")
            
        Returns:
            List of Detection objects for framework features found
        """
        pass