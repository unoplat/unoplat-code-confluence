"""TypeScript-specific framework detection service implementation."""

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
from src.code_confluence_flow_bridge.engine.programming_language.typescript.typescript_source_context import (
    TypeScriptSourceContext,
)
from src.code_confluence_flow_bridge.engine.programming_language.typescript.typescript_tree_sitter_framework_detector import (
    TypeScriptTreeSitterFrameworkDetector,
)
from src.code_confluence_flow_bridge.processor.db.postgres.db import get_session_cm
from src.code_confluence_flow_bridge.processor.db.postgres.framework_query_service import (
    get_framework_features_for_imports,
)

if TYPE_CHECKING:
    from src.code_confluence_flow_bridge.engine.programming_language.python.python_source_context import (
        PythonSourceContext,
    )


def _expand_import_paths(import_paths: List[str]) -> List[str]:
    """Expand dotted import paths into all ancestor prefixes for DB lookup.

    Args:
        import_paths: Fully-qualified dotted import paths
            (e.g. ``["next/server.NextRequest"]``).

    Returns:
        Sorted, deduplicated list containing each original path plus every
        leading prefix so the DB query can match at any depth.
    """
    expanded: List[str] = []
    for path in import_paths:
        expanded.append(path)
        parts = path.split(".")
        # Generate every leading prefix so the DB query can match at any depth
        for idx in range(1, len(parts)):
            expanded.append(".".join(parts[:idx]))
    return sorted(set(expanded))


class TypeScriptFrameworkDetectionService(FrameworkDetectionService):
    """TypeScript-specific framework detection service."""

    def __init__(self) -> None:
        """Initialize TypeScript framework detection service."""
        self.detector = TypeScriptTreeSitterFrameworkDetector()

    async def detect_features(
        self,
        source_code: Optional[str],
        imports: List[str],
        structural_signature: PythonStructuralSignature | TypeScriptStructuralSignature | None,
        programming_language: str,
        source_context: PythonSourceContext | TypeScriptSourceContext | None = None,
    ) -> List[Detection]:
        """
        Detect framework features in TypeScript source code using tree-sitter queries.

        Reuses pre-parsed source context when provided to avoid double-parsing.
        """
        if programming_language.lower() != "typescript":
            logger.warning(
                "TypeScriptFrameworkDetectionService called with language: {}",
                programming_language,
            )
            return []

        # Reuse already-parsed context if caller provides it (avoids double parse)
        if isinstance(source_context, TypeScriptSourceContext):
            context = source_context
        else:
            if not source_code:
                logger.debug("No source code provided for TypeScript framework detection")
                return []
            context = TypeScriptSourceContext.from_source(source_code)

        if not context.import_aliases:
            logger.debug("No import aliases found in TypeScript source")
            return []

        try:
            async with get_session_cm() as session:
                absolute_paths = _expand_import_paths(
                    list(context.import_aliases.keys())
                )
                feature_specs = await get_framework_features_for_imports(
                    session, "typescript", absolute_paths
                )

            logger.opt(lazy=True).debug(
                "TypeScript framework feature specs loaded | count={} | imports={}",
                lambda: len(feature_specs),
                lambda: absolute_paths,
            )

            if not feature_specs:
                logger.debug(
                    "No TypeScript framework features found for imports: {}",
                    absolute_paths,
                )
                return []

            detections = self.detector.detect(context, feature_specs)

            logger.opt(lazy=True).debug(
                "Detected {} TypeScript framework features from {} feature specs",
                lambda: len(detections),
                lambda: len(feature_specs),
            )

            return detections

        except Exception as e:
            logger.error("Error in TypeScript framework detection: {}", e)
            return []
