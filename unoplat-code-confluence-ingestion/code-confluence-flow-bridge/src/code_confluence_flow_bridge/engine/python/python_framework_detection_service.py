"""
Python-specific framework detection service implementation.
"""

from typing import Dict, List, Optional

from loguru import logger
from tree_sitter_language_pack import get_parser
from unoplat_code_confluence_commons.base_models import (
    Detection,
    PythonStructuralSignature,
)

from src.code_confluence_flow_bridge.engine.framework_detection_service import (
    FrameworkDetectionService,
)
from src.code_confluence_flow_bridge.engine.python.simplified_python_detector import (
    SimplifiedPythonDetector,
)
from src.code_confluence_flow_bridge.processor.db.postgres.db import get_session_cm
from src.code_confluence_flow_bridge.processor.db.postgres.framework_query_service import (
    get_framework_features_for_imports,
)


def build_import_aliases(imports: List[str]) -> Dict[str, str]:
    """
    Return a mapping *from fully–qualified import path → alias used in the file*.

    Examples
    --------
        import fastapi as fp              → {"fastapi": "fp"}
        import fastapi                    → {"fastapi": "fastapi"}            # alias == last component
        from fastapi import FastAPI       → {"fastapi.FastAPI": "FastAPI"}
        from fastapi import FastAPI as fp → {"fastapi.FastAPI": "fp"}

    This inverted map lets the detector start with a canonical
    framework symbol (e.g. ``fastapi.FastAPI``) and quickly discover
    which local identifiers refer to it.

    Args:
        imports: List of import statement strings to analyze

    Returns:
        Mapping from fully-qualified import paths to their aliases in the file
    """
    parser = get_parser("python")
    mapping: Dict[str, str] = {}

    def record(full_path: str, alias: str) -> None:
        # Don't overwrite if we already saw an explicit alias earlier.
        if full_path not in mapping:
            mapping[full_path] = alias

    for import_statement in imports:
        if not import_statement.strip():
            continue

        # Parse each import statement individually
        tree = parser.parse(bytes(import_statement, "utf8"))
        src_bytes = bytes(import_statement, "utf8")

        # The root should contain the import statement
        for node in tree.root_node.children:
            if node.type == "import_statement":
                # Handles: import mod [, mod2]  |  import mod as alias
                for child in node.named_children:
                    if child.type == "dotted_name":
                        module = src_bytes[child.start_byte:child.end_byte].decode()
                        alias = module.split(".")[-1]
                        record(module, alias)
                    elif child.type == "aliased_import":
                        module_node = None
                        alias_node = None
                        for grandchild in child.children:
                            if grandchild.type == "dotted_name":
                                module_node = grandchild
                            elif grandchild.type == "identifier" and grandchild != child.children[0]:
                                alias_node = grandchild
                        if module_node:
                            module = src_bytes[module_node.start_byte:module_node.end_byte].decode()
                            alias = (src_bytes[alias_node.start_byte:alias_node.end_byte].decode()
                                     if alias_node else module.split(".")[-1])
                            record(module, alias)

            elif node.type == "import_from_statement":
                # Handles: from module import name [, name2]  |  ... as alias
                module_node = next((c for c in node.children if c.type == "dotted_name"), None)
                if not module_node:
                    # Skip relative "from . import x" for now
                    continue
                base_module = src_bytes[module_node.start_byte:module_node.end_byte].decode()

                import_started = False
                for child in node.children:
                    if child.type == "import":
                        import_started = True
                        continue
                    if not import_started:
                        continue

                    if child.type == "dotted_name":
                        name = src_bytes[child.start_byte:child.end_byte].decode()
                        full_path = f"{base_module}.{name}"
                        record(full_path, name.split(".")[-1])

                    elif child.type == "aliased_import":
                        name_node = None
                        alias_node = None
                        for grandchild in child.children:
                            if grandchild.type == "dotted_name":
                                name_node = grandchild
                            elif grandchild.type == "identifier" and grandchild != child.children[0]:
                                alias_node = grandchild
                        if name_node:
                            name = src_bytes[name_node.start_byte:name_node.end_byte].decode()
                            alias = (src_bytes[alias_node.start_byte:alias_node.end_byte].decode()
                                     if alias_node else name.split(".")[-1])
                            full_path = f"{base_module}.{name}"
                            record(full_path, alias)

    return mapping


class PythonFrameworkDetectionService(FrameworkDetectionService):
    """Python-specific framework detection service."""
    
    def __init__(self) -> None:
        """Initialize Python framework detection service."""
        self.detector = SimplifiedPythonDetector()
    
    async def detect_features(
        self, 
        source_code: Optional[str],
        imports: List[str],
        structural_signature: PythonStructuralSignature | None,
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
            logger.warning("PythonFrameworkDetectionService called with language: {}", programming_language)
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
                logger.debug("No framework features found for imports: {}", absolute_paths)
                return []
            
            # Step 3: Use SimplifiedPythonDetector to detect features from structural signature
            detections = self.detector.detect_from_structural_signature(
                structural_signature, 
                feature_specs, 
                import_aliases
            )
            
            logger.opt(lazy=True).debug(
                "Detected {} framework features from {} feature specs using structural signature",
                lambda: len(detections),
                lambda: len(feature_specs)
            )
            
            return detections
            
        except Exception as e:
            logger.error("Error in Python framework detection: {}", e)
            return []