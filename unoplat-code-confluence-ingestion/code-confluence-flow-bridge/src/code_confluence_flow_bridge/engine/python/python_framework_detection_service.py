"""
Python-specific framework detection service implementation.
"""

from src.code_confluence_flow_bridge.models.code_confluence_parsing_models.structural_signature import (
    StructuralSignature,
)

from typing import List, Optional

from code_confluence_flow_bridge.engine.framework_detection_service import (
    FrameworkDetectionService,
)
from code_confluence_flow_bridge.engine.models import Detection
from code_confluence_flow_bridge.engine.python.import_alias_extractor import (
    build_import_aliases,
)
from code_confluence_flow_bridge.engine.python.simplified_python_detector import (
    SimplifiedPythonDetector,
)
from code_confluence_flow_bridge.processor.db.postgres.db import get_session_cm
from code_confluence_flow_bridge.processor.db.postgres.framework_query_service import (
    get_framework_features_for_imports,
)
from loguru import logger


class PythonFrameworkDetectionService(FrameworkDetectionService):
    """Python-specific framework detection service."""
    
    def __init__(self) -> None:
        """Initialize Python framework detection service."""
        self.detector = SimplifiedPythonDetector()
    
    async def detect_features(
        self, 
        source_code: Optional[str],
        imports: List[str],
        structural_signature: StructuralSignature | None,
        programming_language: str
    ) -> List[Detection]:
        """
        Detect framework features in Python source code using structural signature.
        
        Args:
            source_code: Python source code to analyze
            imports: List of imports in the file (unused - kept for interface compatibility)
            structural_signature: Structural signature of the file (optional)
            programming_language: Programming language (should be "python")
            
        Returns:
            List of Detection objects for framework features found
        """
        if programming_language.lower() != "python":
            logger.warning(f"PythonFrameworkDetectionService called with language: {programming_language}")
            return []
            
        if structural_signature is None:
            logger.debug("No structural signature provided")
            return []
        
        try:
            # Step 1: Extract import aliases from the imports list
            import_aliases = build_import_aliases(imports)
            
            if not import_aliases:
                logger.debug("No import aliases found in imports")
                return []
            
            # Step 2: Query database for framework features matching the imports
            async with get_session_cm() as session:
                # Get all absolute paths from the import aliases
                absolute_paths = list(import_aliases.keys())
                
                feature_specs = await get_framework_features_for_imports(
                    session, 
                    programming_language.lower(), 
                    absolute_paths
                )
            
            if not feature_specs:
                logger.debug(f"No framework features found for imports: {absolute_paths}")
                return []
            
            # Step 3: Use SimplifiedPythonDetector to detect features from structural signature
            detections = self.detector.detect_from_structural_signature(
                structural_signature, 
                feature_specs, 
                import_aliases
            )
            
            logger.debug(
                f"Detected {len(detections)} framework features from "
                f"{len(feature_specs)} feature specs using structural signature"
            )
            
            return detections
            
        except Exception as e:
            logger.error(f"Error in Python framework detection: {e}")
            return []