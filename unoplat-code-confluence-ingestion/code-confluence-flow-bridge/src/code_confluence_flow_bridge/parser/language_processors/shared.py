"""Shared Template Method implementation for tree-sitter language processors."""

from __future__ import annotations

import asyncio
import hashlib
from typing import Optional

from aiofile import async_open
from loguru import logger
from unoplat_code_confluence_commons.base_models import Detection

from code_confluence_flow_bridge.engine.detector.data_model_detector import (
    detect_data_model,
)
from code_confluence_flow_bridge.engine.programming_language.common.language_service import (
    LanguageServiceSpec,
)
from code_confluence_flow_bridge.models.code_confluence_parsing_models.unoplat_file import (
    UnoplatFile,
)
from code_confluence_flow_bridge.parser.language_processors.base import (
    LanguageCodebaseProcessor,
)


class SharedTreeSitterLanguageProcessor(LanguageCodebaseProcessor):
    """Template Method processor for tree-sitter-backed languages."""

    language_service: LanguageServiceSpec

    @property
    def supported_extensions(self) -> set[str]:
        """Return extensions from the language service spec."""
        return set(self.language_service.supported_extensions)

    @property
    def ignored_file_names(self) -> set[str]:
        """Return ignored names from the language service spec."""
        return set(self.language_service.ignored_file_names)

    @staticmethod
    def _calculate_file_checksum(content: bytes) -> str:
        """Generate an md5 checksum for change tracking."""
        try:
            return hashlib.md5(content).hexdigest()
        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.warning("Failed to calculate checksum | error={}", exc)
            return ""

    async def extract_file_data(self, file_path: str) -> Optional[UnoplatFile]:
        """Read, parse, detect metadata, and emit an `UnoplatFile`."""
        metadata = self.context.programming_language_metadata

        try:
            async with async_open(file_path, "rb") as afp:
                content_bytes = await afp.read()

            checksum = await asyncio.to_thread(
                self._calculate_file_checksum, content_bytes
            )
            source_context = await asyncio.to_thread(
                self.language_service.create_source_context_builder().from_bytes,
                content_bytes,
            )

            has_data_model, data_model_positions = detect_data_model(
                source_context=source_context,
                language=metadata.language.value,
            )

            custom_features_list: Optional[list[Detection]] = None
            if self.context.framework_detection_service is not None:
                try:
                    detections = await self.context.framework_detection_service.detect_features(
                        source_context=source_context,
                        programming_language=metadata.language.value,
                    )
                    custom_features_list = detections or None
                except Exception as exc:  # pylint: disable=broad-exception-caught
                    logger.warning(
                        "Framework feature detection failed | file_path={} | error={}",
                        file_path,
                        str(exc),
                    )

            return UnoplatFile(
                file_path=file_path,
                checksum=checksum,
                imports=source_context.imports or [],
                custom_features_list=custom_features_list,
                has_data_model=has_data_model,
                data_model_positions=data_model_positions,
            )

        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.error(
                "Failed to process file | file_path={} | error={}", file_path, exc
            )
            return None
