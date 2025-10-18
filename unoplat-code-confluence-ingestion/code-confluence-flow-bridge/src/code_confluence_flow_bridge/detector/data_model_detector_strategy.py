"""Abstract base strategy for data model detection across programming languages."""

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from unoplat_code_confluence_commons.base_models import DataModelPosition


class DataModelDetectorStrategy(ABC):
    """Abstract base class for language-specific data model detection strategies."""

    @abstractmethod
    def detect(
        self,
        source_code: str,
        imports: Optional[List[str]] = None,
        structural_signature: Optional[object] = None,
    ) -> Tuple[bool, DataModelPosition]:
        """
        Detect if a file contains data model definitions and their locations.

        Args:
            source_code: The source code content
            imports: Optional list of import statements (already extracted)
            structural_signature: Optional structural signature for advanced detection

        Returns:
            Tuple containing:
                - bool: True if data models exist, False otherwise
                - DataModelPosition: Positions of detected data models
        """
        pass
