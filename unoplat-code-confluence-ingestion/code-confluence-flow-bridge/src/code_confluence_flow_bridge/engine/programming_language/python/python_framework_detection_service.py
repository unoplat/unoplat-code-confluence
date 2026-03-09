"""
Python-specific framework detection service implementation.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from loguru import logger
from unoplat_code_confluence_commons.base_models import (
    Detection,
    PythonStructuralSignature,
    TypeScriptStructuralSignature,
)

from src.code_confluence_flow_bridge.engine.framework_detection_service import (
    FrameworkDetectionService,
)
from src.code_confluence_flow_bridge.engine.programming_language.python.python_source_context import (
    PythonSourceContext,
)
from src.code_confluence_flow_bridge.engine.programming_language.python.python_tree_sitter_framework_detector import (
    PythonTreeSitterFrameworkDetector,
)
from src.code_confluence_flow_bridge.processor.db.postgres.db import get_session_cm
from src.code_confluence_flow_bridge.processor.db.postgres.framework_query_service import (
    get_framework_features_for_imports,
)

if TYPE_CHECKING:
    from src.code_confluence_flow_bridge.engine.programming_language.typescript.typescript_source_context import (
        TypeScriptSourceContext,
    )


def _expand_import_paths(import_paths: List[str]) -> List[str]:
    """Expand dotted import paths into all ancestor prefixes for DB lookup.

    Args:
        import_paths: Fully-qualified dotted import paths
            (e.g. ``["flask.blueprints.Blueprint"]``).

    Returns:
        Sorted, deduplicated list containing each original path plus every
        leading prefix (e.g. ``["flask", "flask.blueprints",
        "flask.blueprints.Blueprint"]``).
    """
    expanded: List[str] = []
    for path in import_paths:
        expanded.append(path)
        parts = path.split(".")
        # Generate every leading prefix so the DB query can match at any depth
        for idx in range(1, len(parts)):
            expanded.append(".".join(parts[:idx]))
    return sorted(set(expanded))


class PythonFrameworkDetectionService(FrameworkDetectionService):
    """Python-specific framework detection service."""

    def __init__(self) -> None:
        """Initialize Python framework detection service."""
        self.detector = PythonTreeSitterFrameworkDetector()

    async def detect_features(
        self,
        source_code: Optional[str],
        imports: List[str],
        structural_signature: PythonStructuralSignature | TypeScriptStructuralSignature | None,
        programming_language: str,
        source_context: PythonSourceContext | TypeScriptSourceContext | None = None,
    ) -> List[Detection]:
        """
        Detect framework features in Python source code using tree-sitter queries.

        Args:
            source_code: Python source code to analyze
            imports: List of imports in the file (unused - kept for interface compatibility)
            structural_signature: Structural signature of the file (unused)
            programming_language: Programming language (should be "python")
            source_context: Pre-parsed source context (unused in Python path)

        Returns:
            List of Detection objects for framework features found
        """
        _ = source_context  # unused in Python path
        if programming_language.lower() != "python":
            logger.warning(
                "PythonFrameworkDetectionService called with language: {}",
                programming_language,
            )
            return []

        if not source_code:
            logger.debug("No source code provided for framework detection")
            return []

        try:
            context = PythonSourceContext.from_source(source_code)
            logger.opt(lazy=True).debug(
                "Framework detection imports | count={} | aliases={}",
                lambda: len(context.import_aliases),
                lambda: sorted(context.import_aliases.keys()),
            )
            if not context.import_aliases:
                logger.debug("No import aliases found in source")
                return []

            # Step 2: Query database for framework features matching the imports
            async with get_session_cm() as session:
                # Get all absolute paths from the import aliases
                absolute_paths = _expand_import_paths(
                    list(context.import_aliases.keys())
                )

                feature_specs = await get_framework_features_for_imports(
                    session, programming_language.lower(), absolute_paths
                )

            logger.opt(lazy=True).debug(
                "Framework feature specs loaded | count={} | imports={}",
                lambda: len(feature_specs),
                lambda: absolute_paths,
            )

            if not feature_specs:
                logger.debug(
                    "No framework features found for imports: {}", absolute_paths
                )
                return []

            # Step 3: Detect features with tree-sitter queries
            detections = self.detector.detect(context, feature_specs)

            logger.opt(lazy=True).debug(
                "Detected {} framework features from {} feature specs using tree-sitter",
                lambda: len(detections),
                lambda: len(feature_specs),
            )

            return detections

        except Exception as e:
            logger.error("Error in Python framework detection: {}", e)
            return []
