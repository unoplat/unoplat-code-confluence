"""PostgreSQL codebase parser with relational ingestion."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Set, cast

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from unoplat_code_confluence_commons.base_models import (
    CallExpressionInfo,
    ProgrammingLanguageMetadata,
    ValidationStatus,
)

from src.code_confluence_flow_bridge.engine.framework_detection_service import (
    FrameworkDetectionService,
)
from src.code_confluence_flow_bridge.engine.programming_language.python.python_framework_detection_service import (
    PythonFrameworkDetectionService,
)
from src.code_confluence_flow_bridge.engine.programming_language.typescript.typescript_framework_detection_service import (
    TypeScriptFrameworkDetectionService,
)
from src.code_confluence_flow_bridge.models.configuration.settings import (
    EnvironmentSettings,
)
from src.code_confluence_flow_bridge.parser.language_processors.base import (
    LanguageCodebaseProcessor,
)
from src.code_confluence_flow_bridge.parser.language_processors.language_processor_context import (
    LanguageProcessorContext,
)
from src.code_confluence_flow_bridge.parser.language_processors.python_processor import (
    PythonLanguageProcessor,
)
from src.code_confluence_flow_bridge.parser.language_processors.typescript_processor import (
    TypeScriptLanguageProcessor,
)
from src.code_confluence_flow_bridge.processor.db.postgres.code_confluence_relational_ingestion import (
    CodeConfluenceRelationalIngestion,
)

LOW_CONFIDENCE_CALL_EXPRESSION_THRESHOLD = 0.70


def _resolve_match_confidence(detection: object) -> float:
    metadata = getattr(detection, "metadata", None)
    if not isinstance(metadata, dict):
        return 1.0

    metadata_map = cast(dict[str, object], metadata)

    raw_confidence = metadata_map.get("match_confidence")
    if isinstance(raw_confidence, (int, float)) and not isinstance(
        raw_confidence, bool
    ):
        numeric_confidence = float(raw_confidence)
        if 0.0 <= numeric_confidence <= 1.0:
            return numeric_confidence

    return 1.0


def _resolve_validation_status(
    detection: object,
    *,
    match_confidence: float,
) -> str:
    if not isinstance(detection, CallExpressionInfo):
        return ValidationStatus.COMPLETED.value

    if match_confidence < LOW_CONFIDENCE_CALL_EXPRESSION_THRESHOLD:
        return ValidationStatus.PENDING.value

    return ValidationStatus.COMPLETED.value


def _build_evidence_json(detection: object) -> Optional[dict[str, object]]:
    evidence: dict[str, object] = {}
    metadata = getattr(detection, "metadata", None)
    if isinstance(metadata, dict):
        metadata_map = cast(dict[str, object], metadata)
        for key, value in metadata_map.items():
            evidence[key] = value

    if isinstance(detection, CallExpressionInfo):
        evidence["callee"] = detection.callee
        evidence["args_text"] = detection.args_text

    if not evidence:
        return None

    return evidence


class CodeConfluenceCodebaseParser:
    """
    Language-agnostic codebase parser with PostgreSQL ingestion.

    Uses language-specific processors for file extraction and stores results
    in relational tables via CodeConfluenceRelationalIngestion.
    """

    def __init__(
        self,
        codebase_name: str,
        codebase_path: str,
        root_packages: List[str],
        programming_language_metadata: ProgrammingLanguageMetadata,
        trace_id: str,
        session: AsyncSession,
        *,
        code_confluence_env: Optional[EnvironmentSettings] = None,
    ) -> None:
        self.codebase_name = codebase_name
        self.codebase_path = Path(codebase_path)
        self.root_packages = root_packages
        self.programming_language_metadata = programming_language_metadata
        self.trace_id = trace_id
        self.session = session
        self.ingestion = CodeConfluenceRelationalIngestion(session)

        self.framework_detection_service: Optional[FrameworkDetectionService] = None
        self.config: EnvironmentSettings = (
            code_confluence_env
            if code_confluence_env is not None
            else EnvironmentSettings()
        )

        self.files_processed = 0
        self._known_frameworks: Set[str] = set()
        self._known_features: Set[tuple[str, str, str]] = set()

        self._initialize_components()
        self.language_processor: LanguageCodebaseProcessor = (
            self._initialize_language_processor()
        )

        logger.info(
            "Parser initialized | codebase_name={} | language={}",
            self.codebase_name,
            self.programming_language_metadata.language,
        )

    def _initialize_components(self) -> None:
        if self.framework_detection_service is None:
            if self.programming_language_metadata.language.value == "python":
                self.framework_detection_service = PythonFrameworkDetectionService()
                logger.debug("Initialized Python framework detection service")
            elif self.programming_language_metadata.language.value == "typescript":
                self.framework_detection_service = TypeScriptFrameworkDetectionService()
                logger.debug("Initialized TypeScript framework detection service")
            else:
                logger.debug(
                    "No framework detection service available for language: {}",
                    self.programming_language_metadata.language.value,
                )

    def _initialize_language_processor(self) -> LanguageCodebaseProcessor:
        language_key = self.programming_language_metadata.language.value
        processor_map: Dict[str, type[LanguageCodebaseProcessor]] = {
            "python": PythonLanguageProcessor,
            "typescript": TypeScriptLanguageProcessor,
        }
        processor_cls = processor_map.get(language_key)
        if not processor_cls:
            supported_languages = ", ".join(processor_map.keys())
            raise ValueError(
                f"Unsupported language for codebase processing: '{language_key}'. "
                f"Supported languages: {supported_languages}. "
                f"To add support for {language_key}, implement a {language_key.capitalize()}LanguageProcessor."
            )

        context = LanguageProcessorContext(
            codebase_name=self.codebase_name,
            codebase_path=self.codebase_path,
            root_packages=self.root_packages,
            programming_language_metadata=self.programming_language_metadata,
            env_config=self.config,
            framework_detection_service=self.framework_detection_service,
            concurrency_limit=self.config.codebase_parser_file_processing_concurrency,
            increment_files_processed=self._increment_files_processed,
        )
        processor = processor_cls(context)
        logger.debug(
            "Initialized {} language processor | extensions={}",
            language_key,
            processor.supported_extensions,
        )
        return processor

    def _should_ignore_file(self, file_path: Path) -> bool:
        return self.language_processor.should_ignore(file_path)

    def discover_source_files(self) -> List[str]:
        logger.info(
            "Discovering source files | codebase_path={} | language={} | extensions={}",
            self.codebase_path,
            self.programming_language_metadata.language.value,
            self.language_processor.supported_extensions,
        )

        root_path = self.codebase_path.resolve()
        supported_extensions = self.language_processor.supported_extensions
        discovered_files: List[str] = []

        for file_path in root_path.rglob("*"):
            if not file_path.is_file():
                continue
            if file_path.suffix not in supported_extensions:
                continue
            if self._should_ignore_file(file_path):
                logger.debug("Ignoring file: {}", file_path)
                continue

            discovered_files.append(str(file_path.resolve()))

        discovered_files.sort()

        logger.info(
            "Discovered source files | file_count={}",
            len(discovered_files),
        )
        return discovered_files

    def _increment_files_processed(self, count: int) -> None:
        self.files_processed += count

    async def _load_framework_catalog(self) -> None:
        language = self.programming_language_metadata.language.value
        self._known_frameworks = set(
            await self.ingestion.get_framework_libraries_for_language(language)
        )
        self._known_features = set(
            await self.ingestion.get_framework_features_for_language(language)
        )
        logger.debug(
            "Loaded framework catalog | language={} | frameworks={} | features={}",
            language,
            len(self._known_frameworks),
            len(self._known_features),
        )

    async def process_and_insert_codebase(self) -> None:
        try:
            logger.info("Starting codebase processing: {}", self.codebase_name)

            file_paths = self.discover_source_files()
            if not file_paths:
                logger.warning("No source files found in {}", self.codebase_path)
                return

            await self._load_framework_catalog()
            await self.process_files(file_paths)

            logger.info("Completed codebase processing: {} files", self.files_processed)

        except Exception as exc:
            logger.error(
                "Codebase processing failed for {}: {}", self.codebase_name, exc
            )
            raise

    async def process_files(self, file_paths: List[str]) -> None:
        frameworks_used: Set[tuple[str, str]] = set()
        language = self.programming_language_metadata.language.value

        async for file_data in self.language_processor.iter_files(file_paths):
            await self.ingestion.upsert_files(self.codebase_name, [file_data])

            detections = file_data.custom_features_list or []
            logger.opt(lazy=True).debug(
                "File detections | file={} | count={} | frameworks={} | features={}",
                lambda: file_data.file_path,
                lambda: len(detections),
                lambda: len(self._known_frameworks),
                lambda: len(self._known_features),
            )
            if detections:
                feature_rows: list[dict[str, object]] = []
                for detection in detections:
                    library = detection.library
                    capability_key = detection.capability_key
                    operation_key = detection.operation_key
                    feature_key = detection.feature_key

                    if library not in self._known_frameworks:
                        logger.debug(
                            "Skipping unknown framework | library={} | file={}",
                            library,
                            file_data.file_path,
                        )
                        continue

                    if (
                        library,
                        capability_key,
                        operation_key,
                    ) not in self._known_features:
                        logger.debug(
                            "Skipping unknown feature | library={} | capability_key={} | operation_key={} | file={}",
                            library,
                            capability_key,
                            operation_key,
                            file_data.file_path,
                        )
                        continue

                    logger.debug(
                        "Storing feature | library={} | feature_key={} | file={} | lines={}-{}",
                        library,
                        feature_key,
                        file_data.file_path,
                        detection.start_line,
                        detection.end_line,
                    )

                    match_confidence = _resolve_match_confidence(detection)
                    feature_rows.append(
                        {
                            "feature_language": language,
                            "feature_library": library,
                            "feature_capability_key": capability_key,
                            "feature_operation_key": operation_key,
                            "start_line": detection.start_line,
                            "end_line": detection.end_line,
                            "match_text": detection.match_text,
                            "match_confidence": match_confidence,
                            "validation_status": _resolve_validation_status(
                                detection,
                                match_confidence=match_confidence,
                            ),
                            "evidence_json": _build_evidence_json(detection),
                        }
                    )
                    frameworks_used.add((language, library))

                if feature_rows:
                    await self.ingestion.upsert_file_features(
                        file_data.file_path, feature_rows
                    )

        if frameworks_used:
            await self.ingestion.upsert_codebase_frameworks(
                self.codebase_name, frameworks_used
            )
