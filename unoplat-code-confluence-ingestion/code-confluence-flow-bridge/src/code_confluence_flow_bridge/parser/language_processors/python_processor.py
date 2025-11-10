# Standard Library
import asyncio
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Set

# Third Party
from aiofile import async_open
from loguru import logger

# First Party
from src.code_confluence_flow_bridge.detector.data_model_detector import (
    detect_data_model,
)
from src.code_confluence_flow_bridge.engine.python.import_alias_extractor import (
    extract_imports_from_source,
)
from src.code_confluence_flow_bridge.models.code_confluence_parsing_models.unoplat_file import (
    UnoplatFile,
)
from src.code_confluence_flow_bridge.parser.language_processors.base import (
    LanguageCodebaseProcessor,
)
from src.code_confluence_flow_bridge.parser.language_processors.language_processor_context import (
    LanguageProcessorContext,
)
from src.code_confluence_flow_bridge.parser.tree_sitter_config import (
    TreeSitterExtractorConfig,
)
from src.code_confluence_flow_bridge.parser.tree_sitter_structural_signature import (
    TreeSitterPythonStructuralSignatureExtractor,
)

# ---------------------------------------------------------------------------
# Python-specific configuration constants
# ---------------------------------------------------------------------------

# Base directory for Python query files
_BASE_DIR = Path(__file__).resolve().parent.parent
_PYTHON_QUERY_DIR = _BASE_DIR / "queries" / "python"

# Python query file paths
PYTHON_QUERY_FILES: Dict[str, Path] = {
    "module_docstring": _PYTHON_QUERY_DIR / "module_docstring.scm",
    "global_variables": _PYTHON_QUERY_DIR / "global_variables.scm",
    "module_functions": _PYTHON_QUERY_DIR / "module_functions.scm",
    "module_classes": _PYTHON_QUERY_DIR / "module_classes.scm",
    "class_variables": _PYTHON_QUERY_DIR / "class_variables.scm",
    "class_methods": _PYTHON_QUERY_DIR / "class_methods.scm",
    "nested_functions": _PYTHON_QUERY_DIR / "nested_functions.scm",
    "function_calls": _PYTHON_QUERY_DIR / "function_calls.scm",
    "instance_variables": _PYTHON_QUERY_DIR / "instance_variables.scm",
    "nested_classes": _PYTHON_QUERY_DIR / "nested_classes.scm",
}

# Python capture name mappings (semantic key → Tree-sitter capture name)
PYTHON_CAPTURE_MAPPINGS: Dict[str, str] = {
    "module": "docstring",
    "function": "docstring",
    "class": "class_docstring",
    "method": "method_docstring",
    "nested_function": "nested_docstring",
    "nested_class": "nested_class_docstring",
}

# Python container node types (delimits top-level scope)
PYTHON_CONTAINER_NODES: Set[str] = {"function_definition", "class_definition"}

# Python block node types (code block navigation)
PYTHON_BLOCK_NODES: Set[str] = {"block"}

# Optional query keys (can be missing without error)
PYTHON_OPTIONAL_QUERIES: Set[str] = {
    "function_calls",
    "instance_variables",
    "nested_classes",
}

# Python file extensions
PYTHON_EXTENSIONS: Set[str] = {".py"}

# Python ignored files
PYTHON_IGNORED_FILES: Set[str] = {"__init__.py"}


def clean_python_docstring(text: str) -> str:
    """Strip Python string literal quotes/triple-quotes.

    Args:
        text: Raw docstring with quotes

    Returns:
        Cleaned docstring without quotes
    """
    if text.startswith('"""') and text.endswith('"""'):
        return text[3:-3]
    if text.startswith("'''") and text.endswith("'''"):
        return text[3:-3]
    if text.startswith('"') and text.endswith('"'):
        return text[1:-1]
    if text.startswith("'") and text.endswith("'"):
        return text[1:-1]
    return text


def build_python_extractor_config() -> TreeSitterExtractorConfig:
    """Build TreeSitterExtractorConfig for Python.

    Returns:
        Configured TreeSitterExtractorConfig instance for Python
    """
    return TreeSitterExtractorConfig(
        query_file_paths=PYTHON_QUERY_FILES,
        capture_mappings=PYTHON_CAPTURE_MAPPINGS,
        container_node_types=PYTHON_CONTAINER_NODES,
        block_node_types=PYTHON_BLOCK_NODES,
        optional_query_keys=PYTHON_OPTIONAL_QUERIES,
        doc_cleaner=clean_python_docstring,
    )


class PythonLanguageProcessor(LanguageCodebaseProcessor):
    """Language processor implementing Python structural extraction."""

    def __init__(self, context: LanguageProcessorContext) -> None:
        super().__init__(context)
        # Build Python extractor config and pass to extractor
        self._extractor_config = build_python_extractor_config()
        self.extractor = TreeSitterPythonStructuralSignatureExtractor(
            language_name="python", config=self._extractor_config
        )

    @property
    def supported_extensions(self) -> Set[str]:
        """Return Python file extensions."""
        return PYTHON_EXTENSIONS

    @property
    def ignored_file_names(self) -> Set[str]:
        """Return Python ignored file names."""
        return PYTHON_IGNORED_FILES

    @staticmethod
    def _calculate_file_checksum(content: bytes) -> str:
        try:
            return hashlib.md5(content).hexdigest()
        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.warning("Failed to calculate checksum | error={}", exc)
            return ""

    @staticmethod
    def _extract_imports(source_code: str) -> List[str]:
        try:
            return extract_imports_from_source(source_code, "python")
        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.error("Failed to extract imports | error={}", exc)
            return []

    async def extract_file_data(self, file_path: str) -> Optional[UnoplatFile]:
        metadata = self.context.programming_language_metadata
        try:
            async with async_open(file_path, "rb") as afp:
                content_bytes = await afp.read()

            content = content_bytes.decode("utf-8")
            checksum = await asyncio.to_thread(
                self._calculate_file_checksum, content_bytes
            )
            signature = await asyncio.to_thread(
                self.extractor.extract_structural_signature, content_bytes
            )
            imports = await asyncio.to_thread(self._extract_imports, content)

            data_model_detected, data_model_positions = detect_data_model(
                source_code=content,
                imports=imports,
                language=metadata.language.value,
                structural_signature=signature,
            )

            custom_features_list = None
            framework_service = self.context.framework_detection_service
            if framework_service:
                try:
                    detections = await framework_service.detect_features(
                        source_code=content,
                        imports=imports,
                        structural_signature=signature,
                        programming_language=metadata.language.value,
                    )
                    custom_features_list = detections if detections else None
                except Exception as exc:  # pylint: disable=broad-exception-caught
                    logger.warning(
                        "Framework feature detection failed | file_path={} | error={}",
                        file_path,
                        str(exc),
                    )

            return UnoplatFile(
                file_path=file_path,
                checksum=checksum,
                structural_signature=signature,
                imports=imports,
                custom_features_list=custom_features_list,
                has_data_model=data_model_detected,
                data_model_positions=data_model_positions,
            )

        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.error(
                "Failed to process file | file_path={} | error={}", file_path, exc
            )
            return None
