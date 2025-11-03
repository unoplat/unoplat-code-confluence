# Standard Library
import asyncio
import hashlib
from typing import Optional, Set

# Third Party
from aiofile import async_open
from loguru import logger

# First Party
from src.code_confluence_flow_bridge.detector.data_model_detector import (
    detect_data_model,
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


class TypeScriptLanguageProcessor(LanguageCodebaseProcessor):
    """Language processor responsible for parsing TypeScript source files.

    Version 1 deliberately focuses on data-model detection only. Structural
    signatures and import extraction will be wired once the dedicated
    Tree-sitter extractor is ready. `.tsx` support is deferred because it
    requires loading a distinct grammar and query set.
    """

    _SUPPORTED_EXTENSIONS: Set[str] = {".ts"}
    _IGNORED_FILE_NAMES: Set[str] = {".d.ts"}

    def __init__(self, context: LanguageProcessorContext) -> None:
        super().__init__(context)

    @property
    def supported_extensions(self) -> Set[str]:
        """Return TypeScript file extensions supported in v1."""
        return self._SUPPORTED_EXTENSIONS

    @property
    def ignored_file_names(self) -> Set[str]:
        """Ignore declaration files that should not be parsed for data models."""
        return self._IGNORED_FILE_NAMES

    @staticmethod
    def _calculate_file_checksum(content: bytes) -> str:
        """Generate an md5 checksum for change tracking."""
        try:
            return hashlib.md5(content).hexdigest()
        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.warning("Failed to calculate checksum | error={}", exc)
            return ""

    async def extract_file_data(self, file_path: str) -> Optional[UnoplatFile]:
        """Read a TypeScript file and emit an `UnoplatFile` with data-model metadata."""
        metadata = self.context.programming_language_metadata

        try:
            async with async_open(file_path, "rb") as afp:
                content_bytes = await afp.read()

            checksum = await asyncio.to_thread(
                self._calculate_file_checksum, content_bytes
            )

            content_text = content_bytes.decode("utf-8", errors="ignore")

            # Imports intentionally omitted in v1. Field is optional, so set None.
            imports = None

            has_data_model, data_model_positions = detect_data_model(
                source_code=content_text,
                imports=imports,
                language=metadata.language.value,
                structural_signature=None,
            )

            return UnoplatFile(
                file_path=file_path,
                checksum=checksum,
                imports=imports,
                structural_signature=None,
                custom_features_list=None,
                has_data_model=has_data_model,
                data_model_positions=data_model_positions,
            )

        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.error(
                "Failed to process TypeScript file | file_path={} | error={}",
                file_path,
                exc,
            )
            return None
