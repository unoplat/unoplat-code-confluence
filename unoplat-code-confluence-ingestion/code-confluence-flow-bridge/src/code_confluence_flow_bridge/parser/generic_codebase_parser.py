"""
Generic codebase parser with language-agnostic Tree-Sitter extraction and Neo4j ingestion.

This module provides a language-neutral parser that uses TreeSitterStructuralSignatureExtractor
for AST analysis and ingests results into Neo4j using neomodel operations.
"""

from src.code_confluence_flow_bridge.engine.framework_detection_service import (
    FrameworkDetectionService,
)
from src.code_confluence_flow_bridge.engine.python.import_alias_extractor import (
    extract_imports_from_source,
)
from src.code_confluence_flow_bridge.engine.python.python_framework_detection_service import (
    PythonFrameworkDetectionService,
)
from src.code_confluence_flow_bridge.models.code_confluence_parsing_models.unoplat_file import (
    UnoplatFile,
)
from src.code_confluence_flow_bridge.models.configuration.settings import (
    EnvironmentSettings,
    ProgrammingLanguageMetadata,
)
from src.code_confluence_flow_bridge.parser.language_configs import (
    LanguageConfig,
    get_config,
)
from src.code_confluence_flow_bridge.parser.tree_sitter_structural_signature import (
    TreeSitterStructuralSignatureExtractor,
)

import asyncio

# No longer need graph_context - using neomodel operations directly with global connection
import hashlib
from pathlib import Path
from typing import TYPE_CHECKING, Any, AsyncGenerator, Dict, List, Optional, Set

if TYPE_CHECKING:
    from src.code_confluence_flow_bridge.processor.db.graph_db.code_confluence_graph import (
        CodeConfluenceGraph,
    )

from aiofile import async_open
from loguru import logger
from neo4j import AsyncSession
from neomodel import (  # type: ignore  # imported lazily to avoid circular deps
    AsyncRelationshipTo,
    AsyncZeroOrMore,
    adb,
)
from unoplat_code_confluence_commons.graph_models.base_models import (
    ContainsRelationship,
)
from unoplat_code_confluence_commons.graph_models.code_confluence_codebase import (
    CodeConfluenceCodebase,
)
from unoplat_code_confluence_commons.graph_models.code_confluence_package import (
    CodeConfluencePackage,
)


class GenericCodebaseParser:
    """
    Language-agnostic codebase parser with Neo4j ingestion.

    Uses TreeSitterStructuralSignatureExtractor for AST analysis and neomodel
    for all database operations. This implementation prioritizes simplicity
    and correctness over performance optimization.
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

        # Initialize components (deferred to avoid import issues)
        self.extractor = None
        self.language_config: Optional[LanguageConfig] = None
        self.framework_detection_service: Optional[FrameworkDetectionService] = None

        # Use provided environment settings or fall back to environment variables
        self.config: EnvironmentSettings = (
            code_confluence_env
            if code_confluence_env is not None
            else EnvironmentSettings()
        )

        # Metrics tracking
        self.files_processed = 0
        self.packages_created = 0

        # Language-specific file extensions
        self.file_extensions = self._get_file_extensions()

        logger.info(
            "Parser initialized | codebase_name={} | language={}",
            self.codebase_name,
            self.programming_language_metadata.language,
        )

    def _get_file_extensions(self) -> Set[str]:
        """Get file extensions for the programming language."""
        extension_map = {
            "python": {".py"},
            "java": {".java"},
            "typescript": {".ts", ".tsx"},
            "go": {".go"},
        }
        return extension_map.get(self.programming_language_metadata.language, {".py"})

    def _initialize_components(self) -> None:
        """Initialize extractor components (lazy loading)."""
        if self.extractor is None:
            # Import here to avoid circular imports

            self.extractor = TreeSitterStructuralSignatureExtractor(
                self.programming_language_metadata.language.value
            )  # type: ignore

        # ----------------------------------------------------------------------------------
        # Ensure that the CodeConfluencePackage.sub_packages relationship is **directed**
        # so that querying `pkg.sub_packages` only returns true child packages and not
        # its parent packages. The version of `unoplat_code_confluence_commons` currently
        # exposes `sub_packages` as an undirected `AsyncRelationship`, which results in
        # symmetric traversal (child → parent as well as parent → child). The integration
        # tests bundled with this repository expect a *directed* edge from parent → child.
        # Runtime monkey-patching is used here to avoid modifying the external library.
        # ----------------------------------------------------------------------------------
        existing_rel = getattr(CodeConfluencePackage, "sub_packages", None)

        # Patch only if it is undirected; we detect this heuristically by checking the type name
        if existing_rel.__class__.__name__ != "AsyncRelationshipTo":  # type: ignore[attr-defined]
            logger.debug(
                "Patching CodeConfluencePackage.sub_packages to be directed (AsyncRelationshipTo)"
            )

            # Use the actual class object here (or an absolute import path) so that
            # `neomodel` doesn't attempt a relative import that points to the
            # *current* module (``src.code_confluence_flow_bridge.parser``), which
            # resulted in a ``ModuleNotFoundError`` during traversal installation
            # inside the async matcher. Passing the class object avoids the string
            # import resolution step altogether and guarantees the correct target.
            CodeConfluencePackage.sub_packages = AsyncRelationshipTo(
                CodeConfluencePackage,  # type: ignore[arg-type]
                "CONTAINS_PACKAGE",
                model=ContainsRelationship,
                cardinality=AsyncZeroOrMore,
            )  # type: ignore[assignment]

        # Load language configuration
        if self.language_config is None:
            try:
                self.language_config = get_config(
                    self.programming_language_metadata.language.value
                )
                logger.debug(
                    "Loaded language config for {} with ignored files: {}",
                    self.programming_language_metadata.language.value,
                    self.language_config.ignored_files,
                )
            except KeyError:
                logger.warning(
                    "No language configuration found for {}",
                    self.programming_language_metadata.language.value,
                )

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

    def _should_ignore_file(self, file_path: Path) -> bool:
        """Check if file should be ignored based on language configuration."""
        if self.language_config and self.language_config.ignored_files:
            # Check exact filename match
            if file_path.name in self.language_config.ignored_files:
                return True
            # Check for suffix match (e.g., for .d.ts files)
            for ignored in self.language_config.ignored_files:
                if ignored.startswith(".") and file_path.name.endswith(ignored):
                    return True
        return False

    

    async def _handle_node_creation_managed(
        self, session: AsyncSession, node_type: str, node_dict: Dict[str, Any]
    ) -> str:
        """
        Safely create or retrieve a node using managed transactions with raw Cypher MERGE operations.

        Args:
            session: Neo4j async session from connection pool
            node_type: Node type (e.g., "CodeConfluencePackage", "CodeConfluenceFile")
            node_dict: Dictionary containing node properties

        Returns:
            Node qualified_name or identifier
        """
        try:
            if node_type == "CodeConfluencePackage":
                query = """
                MERGE (n:CodeConfluencePackage {qualified_name: $qualified_name})
                ON CREATE SET 
                    n.name = $name,
                    n.created_at = datetime(),
                    n.updated_at = datetime()
                ON MATCH SET 
                    n.updated_at = datetime()
                RETURN n.qualified_name as identifier
                """
            elif node_type == "CodeConfluenceFile":
                query = """
                MERGE (n:CodeConfluenceFile {file_path: $file_path})
                ON CREATE SET 
                    n.checksum = $checksum,
                    n.structural_signature = $structural_signature,
                    n.imports = $imports,
                    n.created_at = datetime(),
                    n.updated_at = datetime()
                ON MATCH SET 
                    n.checksum = $checksum,
                    n.structural_signature = $structural_signature,
                    n.imports = $imports,
                    n.updated_at = datetime()
                RETURN n.file_path as identifier
                """
            elif node_type == "CodeConfluenceFrameworkFeature":
                query = """
                MERGE (n:CodeConfluenceFrameworkFeature {qualified_name: $qualified_name})
                ON CREATE SET 
                    n.language = $language,
                    n.library = $library,
                    n.feature_key = $feature_key,
                    n.created_at = datetime(),
                    n.updated_at = datetime()
                ON MATCH SET 
                    n.updated_at = datetime()
                RETURN n.qualified_name as identifier
                """
            else:
                raise ValueError(f"Unsupported node type: {node_type}")

            result = await session.execute_write(lambda tx: tx.run(query, node_dict))
            record = await result.single()
            return record["identifier"] if record else ""

        except Exception as e:
            logger.error(
                f"Unexpected error creating {node_type} with managed transactions: {e}"
            )
            raise

    def discover_packages(self) -> Dict[str, List[str]]:
        """Discover packages by absolute directory path (Linux/Posix)."""
        logger.info(
            "Discovering packages | codebase_path={} | language={}",
            self.codebase_path,
            self.programming_language_metadata.language.value,
        )

        root_path = self.codebase_path.resolve()
        package_files: Dict[str, List[str]] = {}

        # 1️⃣ walk every source file and group by its parent directory (absolute path)
        for file_path in root_path.rglob("*"):
            if file_path.is_file() and file_path.suffix in self.file_extensions:
                if self._should_ignore_file(file_path):
                    continue

                pkg_path = file_path.parent.resolve()
                pkg_qname = pkg_path.as_posix()  # absolute path string
                package_files.setdefault(pkg_qname, []).append(str(file_path.resolve()))

        # 2️⃣ ensure that every ancestor folder between the repo root and any discovered
        #     package is present in the mapping (even if it contains no source files)
        for pkg_q in list(package_files.keys()):
            current = Path(pkg_q)
            
            if current == root_path:
                continue
            
            while current != root_path and current.parent != current:
                current = current.parent
                package_files.setdefault(current.as_posix(), [])

        logger.info(
            "Discovered packages with source files | package_count={}",
            len(package_files),
        )
        return package_files

    def build_package_hierarchy(
        self, package_files: Dict[str, List[str]]
    ) -> Dict[str, str]:
        """Map child-package absolute path → parent absolute path."""
        hierarchy: Dict[str, str] = {}
        for child_q in package_files.keys():
            parent_q = Path(child_q).parent.as_posix()
            if parent_q in package_files:
                hierarchy[child_q] = parent_q
        return hierarchy

    def calculate_file_checksum(self, content: bytes) -> str:
        """Calculate MD5 checksum from byte content."""
        try:
            return hashlib.md5(content).hexdigest()
        except Exception as e:
            logger.warning(
                "Failed to calculate checksum | error={}",
                str(e),
            )
            return ""

    def _extract_imports_from_source(self, source_code: str) -> List[str]:
        """Extract import statements directly from source code using tree-sitter."""
        try:
            return extract_imports_from_source(
                source_code, self.programming_language_metadata.language.value
            )
        except Exception as e:
            logger.error("Failed to extract imports | error={}", str(e))
            return []

    async def extract_file_data(self, file_path: str) -> Optional[UnoplatFile]:
        """
        Extract structural signature and metadata for a single file.

        Args:
            file_path: Path to the source file

        Returns:
            UnoplatFile or None if processing fails
        """
        try:
            # Read file content once as bytes (async)
            async with async_open(file_path, "rb") as afp:
                content_bytes = await afp.read()
            
            # Decode to string for text operations
            content = content_bytes.decode("utf-8")

            # Calculate checksum from bytes
            checksum: str = await asyncio.to_thread(self.calculate_file_checksum,content_bytes)

            # Extract structural signature from bytes (no async needed)
            signature = await asyncio.to_thread(self.extractor.extract_structural_signature,content_bytes)  # type: ignore

            # Extract imports directly from source code
            imports = await asyncio.to_thread(self._extract_imports_from_source,content)

            # Detect framework features using the structural signature
            custom_features_list = None
            if self.framework_detection_service:
                try:
                    detections = await self.framework_detection_service.detect_features(
                        source_code=content,
                        imports=imports,
                        structural_signature=signature,
                        programming_language=self.programming_language_metadata.language.value,
                    )
                    custom_features_list = detections if detections else None
                except Exception as e:
                    logger.warning(
                        "Framework feature detection failed | file_path={} | error={}",
                        file_path,
                        str(e),
                    )

            # Create UnoplatFile instance
            unoplat_file = UnoplatFile(
                file_path=file_path,
                checksum=checksum,
                structural_signature=signature,  # Store the actual object, not dict
                imports=imports,
                custom_features_list=custom_features_list,
            )

            return unoplat_file

        except Exception as e:
            logger.error(
                "Failed to process file | file_path={} | error={}", file_path, str(e)
            )
            return None

    async def extract_files(
        self, package_files: Dict[str, List[str]]
    ) -> AsyncGenerator[UnoplatFile, None]:
        """
        Generator that yields file processing data with controlled concurrency.
        
        Maintains a configurable number of concurrent tasks (default 3), preventing memory explosion
        while providing parallel processing benefits. Concurrency is controlled by the
        CODEBASE_PARSER_FILE_PROCESSING_CONCURRENCY environment variable.

        Args:
            package_files: Map of package name to files

        Yields:
            UnoplatFile for each successfully processed file
        """
        # Log package information
        for package_name, files in package_files.items():
            logger.info(
                "Processing files in package | package_name={} | file_count={}",
                package_name,
                len(files),
            )
        
        # Flatten all file paths for processing
        all_files = [f for files in package_files.values() for f in files]
        
        if not all_files:
            return
        
        # Create iterator for lazy evaluation
        file_iter = iter(all_files)
        
        # Get concurrency limit from environment settings
        concurrency_limit = self.config.codebase_parser_file_processing_concurrency
        
        # Start with initial tasks (up to concurrency limit or fewer if less files)
        active_tasks = set()
        for _ in range(min(concurrency_limit, len(all_files))):
            try:
                file_path = next(file_iter)
                task = asyncio.create_task(self.extract_file_data(file_path))
                active_tasks.add(task)
            except StopIteration:
                break
        
        # Process files in streaming fashion
        while active_tasks:
            # Wait for any task to complete
            done, active_tasks = await asyncio.wait(
                active_tasks, 
                return_when=asyncio.FIRST_COMPLETED
            )
            
            # Process completed tasks
            for task in done:
                try:
                    file_data = await task
                    if file_data:
                        self.files_processed += 1
                        yield file_data
                except Exception as e:
                    logger.error(f"Task failed during file extraction: {e}")
            
            # Start new tasks to maintain pool size
            while len(active_tasks) < concurrency_limit:
                try:
                    file_path = next(file_iter)
                    task = asyncio.create_task(self.extract_file_data(file_path))
                    active_tasks.add(task)
                except StopIteration:
                    break  # No more files to process


    async def create_packages_managed(
        self, session: "AsyncSession", package_names: List[str]
    ) -> None:
        """
        Create package nodes using managed transactions with raw Cypher MERGE operations.

        Args:
            session: Neo4j async session from connection pool
            package_names: List of package qualified names to create
        """
        try:
            for package_name in package_names:
                # Extract simple name using pathlib
                simple_name = Path(package_name).name

                # Create package using raw Cypher MERGE following neomodel's create_or_update pattern
                # MERGE only on required properties (qualified_name), then use ON CREATE/MATCH SET
                create_package_query = """
                MERGE (p:CodeConfluencePackage {qualified_name: $qualified_name})
                ON CREATE SET p.name = $name
                ON MATCH SET p.name = $name
                RETURN p
                """

                await session.execute_write(
                    lambda tx: tx.run(
                        create_package_query,
                        {"qualified_name": package_name, "name": simple_name},
                    )
                )

            logger.info(
                f"Created/updated {len(package_names)} packages using managed transactions"
            )

        except Exception as e:
            logger.error("Failed to create packages with managed transactions: {}", e)
            raise

    async def create_package_hierarchy_old(
        self, package_hierarchy: Dict[str, str]
    ) -> None:
        """
        Create package parent-child relationships using neomodel.

        NOTE: Soon to be deprecated - use create_package_hierarchy_managed() instead

        Args:
            package_hierarchy: Map of child package to parent package
        """
        if not package_hierarchy:
            return

        try:
            for child_pkg_name, parent_pkg_name in package_hierarchy.items():
                async with adb.transaction:
                    # Get parent and child packages
                    parent = await CodeConfluencePackage.nodes.get(
                        qualified_name=parent_pkg_name
                    )
                    child = await CodeConfluencePackage.nodes.get(
                        qualified_name=child_pkg_name
                    )

                    # Connect them using the sub_packages relationship
                    await parent.sub_packages.connect(child)
                    await child.parent_package.connect(parent)

                    logger.debug(
                        f"Connected packages: {parent_pkg_name} -> {child_pkg_name}"
                    )

            logger.info("Created {} package relationships", len(package_hierarchy))

        except Exception as e:
            logger.error("Failed to create package hierarchy: {}", e)
            raise

    async def create_package_hierarchy_managed(
        self, session: AsyncSession, package_hierarchy: Dict[str, str]
    ) -> None:
        """
        Create package parent-child relationships using managed transactions with raw Cypher MERGE operations.

        Args:
            session: Neo4j async session from connection pool
            package_hierarchy: Map of child package to parent package
        """
        if not package_hierarchy:
            return

        try:
            for child_pkg_name, parent_pkg_name in package_hierarchy.items():
                # Create package hierarchy relationships using raw Cypher MERGE
                create_hierarchy_query = """
                MATCH (parent:CodeConfluencePackage {qualified_name: $parent_qualified_name})
                MATCH (child:CodeConfluencePackage {qualified_name: $child_qualified_name})
                MERGE (parent)-[:CONTAINS_PACKAGE]->(child)
                MERGE (child)-[:PART_OF_PACKAGE]->(parent)
                RETURN parent, child
                """

                await session.execute_write(
                    lambda tx: tx.run(
                        create_hierarchy_query,
                        {
                            "parent_qualified_name": parent_pkg_name,
                            "child_qualified_name": child_pkg_name,
                        },
                    )
                )

                logger.debug(
                    f"Connected packages: {parent_pkg_name} -> {child_pkg_name}"
                )

            logger.info(
                f"Created {len(package_hierarchy)} package relationships using managed transactions"
            )

        except Exception as e:
            logger.error(
                f"Failed to create package hierarchy with managed transactions: {e}"
            )
            raise

    async def _connect_root_packages_old(
        self, package_files: Dict[str, List[str]]
    ) -> None:
        """Connect top-level packages (direct children of the codebase) to the CodeConfluenceCodebase node.

        NOTE: Soon to be deprecated - use _connect_root_packages_managed() instead

        Args:
            package_files: Map of package qualified names to their file lists.
        """
        try:
            # Import lazily to avoid circular import issues
            async with adb.transaction:
                # Fetch the codebase node (it must already exist – created during git ingestion step)
                codebase_node = await CodeConfluenceCodebase.nodes.get(
                    qualified_name=self.codebase_name
                )

                root_package_names = []
                for pkg_name in package_files.keys():
                    if Path(pkg_name).parent == self.codebase_path.resolve():
                        root_package_names.append(pkg_name)

                if not root_package_names:
                    logger.warning(
                        "No root packages discovered for codebase {} – skipping relationship creation",
                        self.codebase_name,
                    )
                    return

                for root_pkg in root_package_names:
                    try:
                        pkg_node = await CodeConfluencePackage.nodes.get(
                            qualified_name=root_pkg
                        )
                        # Connect both directions using safe pattern
                        await codebase_node.packages.connect(pkg_node)
                        await pkg_node.codebase.connect(codebase_node)
                    except Exception as e:
                        logger.warning(
                            "Failed to connect root package {} to codebase {}: {}",
                            root_pkg,
                            self.codebase_name,
                            str(e),
                        )

                logger.info(
                    "Connected {} root packages to codebase {}",
                    len(root_package_names),
                    self.codebase_name,
                )
        except Exception as outer_err:
            logger.error(
                "Error while connecting root packages for codebase {}: {}",
                self.codebase_name,
                str(outer_err),
            )

    async def _connect_root_packages_managed(
        self, session: AsyncSession, package_files: Dict[str, List[str]]
    ) -> None:
        """Connect top-level packages (direct children of the codebase) to the CodeConfluenceCodebase node using managed transactions.

        Args:
            session: Neo4j async session from connection pool
            package_files: Map of package qualified names to their file lists.
        """
        try:
            # Identify root packages (direct children of codebase path)
            root_package_names = []
            for pkg_name in package_files.keys():
                if Path(pkg_name).parent == self.codebase_path.resolve():
                    root_package_names.append(pkg_name)

            if not root_package_names:
                logger.warning(
                    "No root packages discovered for codebase {} – skipping relationship creation",
                    self.codebase_name,
                )
                return

            # Connect root packages to codebase using raw Cypher MERGE
            for root_pkg in root_package_names:
                try:
                    connect_root_query = """
                    MATCH (codebase:CodeConfluenceCodebase {qualified_name: $codebase_qualified_name})
                    MATCH (pkg:CodeConfluencePackage {qualified_name: $package_qualified_name})
                    MERGE (codebase)-[:CONTAINS_PACKAGE]->(pkg)
                    MERGE (pkg)-[:PART_OF_CODEBASE]->(codebase)
                    RETURN codebase, pkg
                    """

                    await session.execute_write(
                        lambda tx: tx.run(
                            connect_root_query,
                            {
                                "codebase_qualified_name": self.codebase_name,
                                "package_qualified_name": root_pkg,
                            },
                        )
                    )
                except Exception as e:
                    logger.warning(
                        "Failed to connect root package {} to codebase {}: {}",
                        root_pkg,
                        self.codebase_name,
                        str(e),
                    )

            logger.info(
                "Connected {} root packages to codebase {} using managed transactions",
                len(root_package_names),
                self.codebase_name,
            )
        except Exception as outer_err:
            logger.error(
                "Error while connecting root packages for codebase {} with managed transactions: {}",
                self.codebase_name,
                str(outer_err),
            )


    async def insert_files_managed(
        self,
        session: AsyncSession,
        file_data_list: List[UnoplatFile],
        package_files: Dict[str, List[str]],
    ) -> None:
        """
        Insert files using managed transactions with raw Cypher MERGE operations.

        Args:
            session: Neo4j async session from connection pool
            file_data_list: List of UnoplatFile objects
            package_files: Map of package name to files for determining package relationships
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
                }

                # Follow neomodel's create_or_update pattern: MERGE only on required properties (file_path)
                create_file_query = """
                MERGE (f:CodeConfluenceFile {file_path: $file_path})
                ON CREATE SET 
                    f.checksum = $checksum,
                    f.structural_signature = $structural_signature,
                    f.imports = $imports
                ON MATCH SET 
                    f.checksum = $checksum,
                    f.structural_signature = $structural_signature,
                    f.imports = $imports
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
                        MERGE (f)-[r:USES_FEATURE]->(feat)
                        SET r.start_line = $start_line, r.end_line = $end_line
                        
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
                                },
                            )
                        )

                # Connect file to its package
                package_qualified_name = None
                for pkg_name, files in package_files.items():
                    if unoplat_file.file_path in files:
                        package_qualified_name = pkg_name
                        break

                if package_qualified_name:
                    connect_file_package_query = """
                    MATCH (f:CodeConfluenceFile {file_path: $file_path})
                    MATCH (p:CodeConfluencePackage {qualified_name: $package_qualified_name})
                    MERGE (f)-[:PART_OF_PACKAGE]->(p)
                    MERGE (p)-[:CONTAINS_FILE]->(f)
                    RETURN f, p
                    """

                    await session.execute_write(
                        lambda tx: tx.run(
                            connect_file_package_query,
                            {
                                "file_path": unoplat_file.file_path,
                                "package_qualified_name": package_qualified_name,
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
            self._initialize_components()

            logger.info(f"Starting codebase processing: {self.codebase_name}")

            # 1. Discover packages and files
            package_files = self.discover_packages()

            if not package_files:
                logger.warning(f"No source files found in {self.codebase_path}")
                return

            # Use managed session from shared connection pool
            if not self.code_confluence_graph:
                raise ValueError(
                    "CodeConfluenceGraph instance is required for managed transactions"
                )

            async with self.code_confluence_graph.get_session() as session:
                logger.debug("Started managed Neo4j session for codebase processing")

                # 2. Create all packages
                await self.create_packages_managed(session, list(package_files.keys()))

                # 3. Create package hierarchy
                hierarchy = self.build_package_hierarchy(package_files)
                await self.create_package_hierarchy_managed(session, hierarchy)

                # 3b. Connect root-level packages (depth-1) to the CodeConfluenceCodebase node
                await self._connect_root_packages_managed(session, package_files)

                # 4. Process and insert files
                await self.process_files_managed(session, package_files)

                logger.debug("Completed all Neo4j operations within managed session")

            logger.info(
                f"Completed codebase processing: {self.files_processed} files, "
                f"{self.packages_created} packages"
            )

        except Exception as e:
            logger.error(f"Codebase processing failed for {self.codebase_name}: {e}")
            raise

    async def process_files_managed(
        self, session: AsyncSession, package_files: Dict[str, List[str]]
    ) -> None:
        """
        Process all files sequentially using managed transactions.

        Args:
            session: Neo4j async session from connection pool
            package_files: Map of package name to files
        """
        try:
            async for file_data in self.extract_files(package_files):
                await self.insert_files_managed(session, [file_data], package_files)

            logger.info(
                f"Processed {self.files_processed} files using managed transactions"
            )

        except Exception as e:
            logger.error(f"Failed to process files with managed transactions: {e}")
            raise
