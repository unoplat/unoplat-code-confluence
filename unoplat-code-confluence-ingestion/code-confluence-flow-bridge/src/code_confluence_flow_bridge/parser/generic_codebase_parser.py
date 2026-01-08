"""Generic codebase parser with language-agnostic Tree-Sitter extraction and Neo4j ingestion."""

# No longer need graph_context - using neomodel operations directly with global connection
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Optional

from unoplat_code_confluence_commons.base_models import (
    ProgrammingLanguageMetadata,
)

from src.code_confluence_flow_bridge.engine.framework_detection_service import (
    FrameworkDetectionService,
)
from src.code_confluence_flow_bridge.engine.programming_language.python.python_framework_detection_service import (
    PythonFrameworkDetectionService,
)
from src.code_confluence_flow_bridge.models.code_confluence_parsing_models.unoplat_file import (
    UnoplatFile,
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

if TYPE_CHECKING:
    from src.code_confluence_flow_bridge.processor.db.graph_db.code_confluence_graph import (
        CodeConfluenceGraph,
    )

from loguru import logger
from neo4j import AsyncSession

# Note: persistence relies on raw Cypher via the Neo4j driver—graph models are not imported here.


class GenericCodebaseParser:
    """
    Language-agnostic codebase parser with Neo4j ingestion.

    Delegates structural extraction to language-specific processors
    (e.g., PythonLanguageProcessor wraps TreeSitterPythonStructuralSignatureExtractor).
    Uses neomodel for all database operations. This implementation prioritizes
    simplicity and correctness over performance optimization.
    """

    def __init__(
        self,
        codebase_name: str,
        codebase_path: str,
        root_packages: List[str],
        programming_language_metadata: ProgrammingLanguageMetadata,
        trace_id: str,
        *,
        code_confluence_graph: Optional["CodeConfluenceGraph"] = None,
        code_confluence_env: Optional[EnvironmentSettings] = None,
    ) -> None:
        """
        Initialize parser.

        Args:
            codebase_name: Name of the codebase
            codebase_path: File system path to codebase root
            root_packages: List of root package names
            programming_language_metadata: Language configuration
            trace_id: Trace ID for logging and error context
            code_confluence_env: Optional environment settings
        """
        self.codebase_name = codebase_name
        self.codebase_path = Path(codebase_path)
        self.root_packages = root_packages
        self.programming_language_metadata = programming_language_metadata
        self.trace_id = trace_id
        self.code_confluence_graph = code_confluence_graph

        # Initialize framework detection service (deferred to avoid import issues)
        self.framework_detection_service: Optional[FrameworkDetectionService] = None

        # Use provided environment settings or fall back to environment variables
        self.config: EnvironmentSettings = (
            code_confluence_env
            if code_confluence_env is not None
            else EnvironmentSettings()
        )

        # Metrics tracking
        self.files_processed = 0

        # Initialize components immediately
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
        """Initialize supporting services."""
        # Initialize framework detection service based on language
        if self.framework_detection_service is None:
            if self.programming_language_metadata.language.value == "python":
                self.framework_detection_service = PythonFrameworkDetectionService()
                logger.debug("Initialized Python framework detection service")
            # Add other languages as needed
            else:
                logger.debug(
                    "No framework detection service available for language: {}",
                    self.programming_language_metadata.language.value,
                )

    def _initialize_language_processor(self) -> LanguageCodebaseProcessor:
        """Instantiate language-specific processor.

        Raises:
            ValueError: If the language is not supported (no processor available)
        """
        language_key = self.programming_language_metadata.language.value
        processor_map: Dict[str, type[LanguageCodebaseProcessor]] = {
            "python": PythonLanguageProcessor,
            "typescript": TypeScriptLanguageProcessor,
            # "java": JavaLanguageProcessor,
            # "go": GoLanguageProcessor,
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
        """Check if file should be ignored based on language processor rules.

        Args:
            file_path: Path to the file to check

        Returns:
            True if file should be ignored, False otherwise
        """
        return self.language_processor.should_ignore(file_path)

    def discover_source_files(self) -> List[str]:
        """Discover source files under the codebase root filtered by supported extensions."""
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
        """Increment processed files counter."""
        self.files_processed += count

    # todo: ideally insertion should happen as part of code_Confluence_graph_ingestion
    async def insert_files_managed(
        self,
        session: AsyncSession,
        file_data_list: List[UnoplatFile],
    ) -> None:
        """
        Insert files using managed transactions with raw Cypher MERGE operations.

        Args:
            session: Neo4j async session from connection pool
            file_data_list: List of UnoplatFile objects
        """
        try:
            for unoplat_file in file_data_list:
                # Create file node using raw Cypher MERGE - use Pydantic's model_dump_json() for Neo4j JSONProperty
                file_dict = {
                    "file_path": unoplat_file.file_path,
                    "checksum": unoplat_file.checksum,
                    "structural_signature": unoplat_file.structural_signature.model_dump_json()
                    if unoplat_file.structural_signature
                    else "{}",
                    "imports": unoplat_file.imports or [],
                    "has_data_model": unoplat_file.has_data_model,
                    "data_model_positions": unoplat_file.data_model_positions.model_dump_json(),
                }

                # Follow neomodel's create_or_update pattern: MERGE only on required properties (file_path)
                create_file_query = """
                MERGE (f:CodeConfluenceFile {file_path: $file_path})
                ON CREATE SET
                    f.checksum = $checksum,
                    f.structural_signature = $structural_signature,
                    f.imports = $imports,
                    f.has_data_model = $has_data_model,
                    f.data_model_positions = $data_model_positions
                ON MATCH SET
                    f.checksum = $checksum,
                    f.structural_signature = $structural_signature,
                    f.imports = $imports,
                    f.has_data_model = $has_data_model,
                    f.data_model_positions = $data_model_positions
                RETURN f
                """

                await session.execute_write(
                    lambda tx: tx.run(create_file_query, file_dict)
                )

                # Handle framework features
                if unoplat_file.custom_features_list:
                    for det in unoplat_file.custom_features_list:
                        lang = self.programming_language_metadata.language.value
                        lib = det.library
                        feature_key = det.feature_key

                        # Create framework feature and relationships using raw Cypher
                        framework_qualified_name = f"{lang}.{lib}"
                        feature_qualified_name = f"{lang}.{lib}.{feature_key}"

                        create_feature_query = """
                        // First ensure framework exists
                        MERGE (fw:CodeConfluenceFramework {qualified_name: $framework_qualified_name})
                        ON CREATE SET 
                            fw.language = $language,
                            fw.library = $library
                        ON MATCH SET
                            fw.language = $language,
                            fw.library = $library
                        
                        // Create feature - merge only on unique constraint property
                        MERGE (feat:CodeConfluenceFrameworkFeature {qualified_name: $feature_qualified_name})
                        ON CREATE SET 
                            feat.language = $language,
                            feat.library = $library,
                            feat.feature_key = $feature_key
                        ON MATCH SET
                            feat.language = $language,
                            feat.library = $library,
                            feat.feature_key = $feature_key
                        
                        // Connect framework -> feature
                        MERGE (fw)-[:HAS_FEATURE]->(feat)
                        
                        // WITH is required between MERGE (write) and MATCH (read) clauses
                        WITH fw, feat
                        MATCH (f:CodeConfluenceFile {file_path: $file_path})
                        MERGE (f)-[r:USES_FEATURE {start_line: $start_line, end_line: $end_line, match_text: $match_text}]->(feat)
                        
                        RETURN fw, feat, f
                        """

                        await session.execute_write(
                            lambda tx: tx.run(
                                create_feature_query,
                                {
                                    "framework_qualified_name": framework_qualified_name,
                                    "feature_qualified_name": feature_qualified_name,
                                    "language": lang,
                                    "library": lib,
                                    "feature_key": feature_key,
                                    "file_path": unoplat_file.file_path,
                                    "start_line": det.start_line,
                                    "end_line": det.end_line,
                                    "match_text": getattr(det, "match_text", ""),
                                },
                            )
                        )

                connect_file_codebase_query = """
                MATCH (f:CodeConfluenceFile {file_path: $file_path})
                MATCH (c:CodeConfluenceCodebase {qualified_name: $codebase_qualified_name})
                MERGE (c)-[:CONTAINS_FILE]->(f)
                MERGE (f)-[:PART_OF_CODEBASE]->(c)
                RETURN f, c
                """

                await session.execute_write(
                    lambda tx: tx.run(
                        connect_file_codebase_query,
                        {
                            "file_path": unoplat_file.file_path,
                            "codebase_qualified_name": self.codebase_name,
                        },
                    )
                )

                logger.debug("Created file: {}", unoplat_file.file_path)

            logger.info(
                f"Inserted {len(file_data_list)} files using managed transactions"
            )

        except Exception as e:
            logger.error("Failed to insert files with managed transactions: {}", e)
            raise

    async def process_and_insert_codebase(self) -> None:
        """
        Main processing method with managed transactions from shared session pool.
        Uses managed transactions to prevent concurrent access conflicts.
        """
        try:
            logger.info(f"Starting codebase processing: {self.codebase_name}")

            # 1. Discover all source files within the codebase
            file_paths = self.discover_source_files()

            if not file_paths:
                logger.warning(f"No source files found in {self.codebase_path}")
                return

            # Use managed session from shared connection pool
            if not self.code_confluence_graph:
                raise ValueError(
                    "CodeConfluenceGraph instance is required for managed transactions"
                )

            async with self.code_confluence_graph.get_session() as session:
                logger.debug("Started managed Neo4j session for codebase processing")

                # 2. Process and insert files
                await self.process_files_managed(session, file_paths)

                logger.debug("Completed all Neo4j operations within managed session")

            logger.info(f"Completed codebase processing: {self.files_processed} files")

        except Exception as e:
            logger.error(f"Codebase processing failed for {self.codebase_name}: {e}")
            raise

    async def process_files_managed(
        self, session: AsyncSession, file_paths: List[str]
    ) -> None:
        """
        Process all files sequentially using managed transactions.

        Args:
            session: Neo4j async session from connection pool
            file_paths: List of file paths to process
        """
        try:
            async for file_data in self.language_processor.iter_files(file_paths):
                await self.insert_files_managed(session, [file_data])

            logger.info(
                f"Processed {self.files_processed} files using managed transactions"
            )

        except Exception as e:
            logger.error(f"Failed to process files with managed transactions: {e}")
            raise
