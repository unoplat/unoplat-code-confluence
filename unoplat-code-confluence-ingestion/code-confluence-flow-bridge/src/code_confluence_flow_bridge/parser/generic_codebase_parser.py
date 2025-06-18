"""
Generic codebase parser with language-agnostic Tree-Sitter extraction and Neo4j ingestion.

This module provides a language-neutral parser that uses TreeSitterStructuralSignatureExtractor
for AST analysis and ingests results into Neo4j using neomodel operations.
"""

from src.code_confluence_flow_bridge.models.code_confluence_parsing_models.unoplat_file import UnoplatFile
from src.code_confluence_flow_bridge.models.configuration.settings import (
    EnvironmentSettings,
    ProgrammingLanguageMetadata,
)
from src.code_confluence_flow_bridge.parser.language_configs import LanguageConfig, get_config
from src.code_confluence_flow_bridge.parser.tree_sitter_structural_signature import (
    TreeSitterStructuralSignatureExtractor,
)
from src.code_confluence_flow_bridge.processor.db.graph_db.graph_context import graph_ingestion_ctx

import asyncio
import hashlib
from pathlib import Path
from typing import AsyncGenerator, Dict, List, Optional, Set

from loguru import logger
from neomodel import AsyncRelationshipTo, AsyncZeroOrMore  # imported lazily to avoid circular deps
from neomodel.exceptions import UniqueProperty
from unoplat_code_confluence_commons.graph_models.base_models import ContainsRelationship
from unoplat_code_confluence_commons.graph_models.code_confluence_codebase import (
    CodeConfluenceCodebase,
)
from unoplat_code_confluence_commons.graph_models.code_confluence_file import CodeConfluenceFile
from unoplat_code_confluence_commons.graph_models.code_confluence_package import CodeConfluencePackage


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
        
        # Initialize components (deferred to avoid import issues)
        self.extractor = None
        self.language_config: Optional[LanguageConfig] = None
        
        # Use provided environment settings or fall back to environment variables
        self.config: EnvironmentSettings = (
            code_confluence_env if code_confluence_env is not None else EnvironmentSettings()
        )
        
        # Metrics tracking
        self.files_processed = 0
        self.packages_created = 0
        
        # Language-specific file extensions
        self.file_extensions = self._get_file_extensions()
        
        logger.info(
            "Parser initialized | codebase_name={} | language={}",
            self.codebase_name, self.programming_language_metadata.language
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

    def _initialize_components(self):
        """Initialize extractor components (lazy loading)."""
        if self.extractor is None:
            # Import here to avoid circular imports
            
            self.extractor = TreeSitterStructuralSignatureExtractor(
                self.programming_language_metadata.language.value
            )
            
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
            logger.debug("Patching CodeConfluencePackage.sub_packages to be directed (AsyncRelationshipTo)")

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
                self.language_config = get_config(self.programming_language_metadata.language.value)
                logger.debug(
                    "Loaded language config for {} with ignored files: {}",
                    self.programming_language_metadata.language.value,
                    self.language_config.ignored_files
                )
            except KeyError:
                logger.warning(
                    "No language configuration found for {}",
                    self.programming_language_metadata.language.value
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

    async def _handle_node_creation(self, node_class, node_dict):
        """
        Safely create or retrieve a node, handling duplicates gracefully.
        
        Uses create_or_update for atomic operations, falls back to 
        retrieval if UniqueProperty exception occurs.
        """
        try:
            # create_or_update returns a list
            results = await node_class.create_or_update(node_dict)
            return results[0] if results else None
        except UniqueProperty as e:
            # Node exists, retrieve it
            logger.info(f"Node already exists: {node_class.__name__} with qualified_name={node_dict.get('qualified_name')}. Retrieving existing node.")
            
            # Try to find by qualified_name (all BaseNode descendants have this)
            if 'qualified_name' in node_dict:
                existing = await node_class.nodes.filter(
                    qualified_name=node_dict['qualified_name']
                ).first_or_none()
                if existing:
                    return existing
            
            # Try file_path for CodeConfluenceFile
            if 'file_path' in node_dict and node_class == CodeConfluenceFile:
                existing = await node_class.nodes.filter(
                    file_path=node_dict['file_path']
                ).first_or_none()
                if existing:
                    return existing
            
            logger.warning(f"Could not retrieve existing {node_class.__name__} after UniqueProperty error")
            return None
        except Exception as e:
            logger.error(f"Unexpected error creating {node_class.__name__}: {e}")
            raise

    def discover_packages(self) -> Dict[str, List[str]]:
        """
        Discover packages (directories containing source files).
        
        Returns:
            Dict mapping package path to list of source files in that package
            Only includes directories that contain source files (directly or transitively)
        """
        logger.info(
            "Discovering packages | codebase_path={} | language={}",
            self.codebase_path, self.programming_language_metadata.language.value
        )
        
        package_files: Dict[str, List[str]] = {}
        
        # Walk the filesystem to find all source files
        for file_path in self.codebase_path.rglob("*"):
            if file_path.is_file() and file_path.suffix in self.file_extensions:
                # Check if file should be ignored
                if self._should_ignore_file(file_path):
                    logger.debug(
                        "Ignoring file | file_path={} | language={}",
                        file_path, self.programming_language_metadata.language.value
                    )
                    continue
                    
                # Get the package path (directory containing the file)
                package_path = file_path.parent
                
                # Convert to relative path from codebase root
                try:
                    relative_package = package_path.relative_to(self.codebase_path)
                    package_qualified_name = str(relative_package).replace("/", ".").replace("\\", ".")
                    
                    # Handle root package case
                    if package_qualified_name == ".":
                        package_qualified_name = self.codebase_name
                    else:
                        package_qualified_name = f"{self.codebase_name}.{package_qualified_name}"
                    
                    # Add file to package
                    if package_qualified_name not in package_files:
                        package_files[package_qualified_name] = []
                    
                    package_files[package_qualified_name].append(str(file_path))
                    
                except ValueError:
                    # File is outside codebase path, skip
                    continue
        
        logger.info(
            "Discovered packages with source files | package_count={}",
            len(package_files)
        )

        # ------------------------------------------------------------------
        # Ensure that all intermediate parent packages are included, even if
        # they do not directly contain source files. This guarantees that
        # multi-level nested packages are connected in the hierarchy.
        # ------------------------------------------------------------------
        all_packages: List[str] = list(package_files.keys())  # snapshot to avoid dict size change

        for pkg in all_packages:
            # Split on dots to walk up the hierarchy (skip the codebase name)
            parts = pkg.split(".")

            # parts[0] is always `self.codebase_name` – we never create a
            # package node just for the codebase itself.
            for i in range(2, len(parts)):  # start from 2 to keep at least codebase + first segment
                parent_pkg = ".".join(parts[:i])

                # Skip if this is the codebase root (already handled separately)
                if parent_pkg == self.codebase_name:
                    continue

                # Ensure entry exists (using empty list for folders without source files)
                if parent_pkg not in package_files:
                    package_files[parent_pkg] = []

        # Re-log after adding parent packages for easier debugging
        logger.debug(
            "Package discovery augmented with parents | total_packages={}",
            len(package_files)
        )

        return package_files

    def build_package_hierarchy(self, package_files: Dict[str, List[str]]) -> Dict[str, str]:
        """
        Build parent-child relationships for packages.
        
        Args:
            package_files: Map of package name to files
            
        Returns:
            Dict mapping child package to parent package
        """
        hierarchy = {}
        
        for package_name in package_files.keys():
            # Find parent package
            parts = package_name.split(".")
            if len(parts) > 1:
                parent_name = ".".join(parts[:-1])
                if parent_name in package_files:
                    hierarchy[package_name] = parent_name
        
        return hierarchy

    def calculate_file_checksum(self, file_path: str) -> str:
        """Calculate MD5 checksum of file content."""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                return hashlib.md5(content).hexdigest()
        except Exception as e:
            logger.warning(
                "Failed to calculate checksum | file_path={} | error={}",
                file_path, str(e)
            )
            return ""
    
    def _extract_imports_from_source(self, source_code: str) -> List[str]:
        """Extract import statements directly from source code using tree-sitter."""
        if not self.extractor:
            return []
            
        try:
            # Parse the source code
            tree = self.extractor.parser.parse(bytes(source_code, "utf8"))
            root_node = tree.root_node
            
            # Load the imports query from the query file
            query_dir = Path(__file__).parent / "queries" / self.programming_language_metadata.language.value
            imports_query_file = query_dir / "imports.scm"
            
            if not imports_query_file.exists():
                logger.warning(
                    "No imports query file found for language: {}",
                    self.programming_language_metadata.language.value
                )
                return []
            
            # Read and compile the query
            import_query_string = imports_query_file.read_text()
            import_query = self.extractor.language.query(import_query_string)
            
            # Execute query
            captures = import_query.captures(root_node)
            
            imports = []
            # NOTE: py-tree-sitter >=0.23 returns a **dict** mapping capture names to
            # a list of nodes, whereas older versions return a **list** of
            # (node, capture_name) tuples.  Handle both for forward/backward
            # compatibility.
            if isinstance(captures, dict):  # New API (>=0.23)
                for nodes in captures.values():
                    for node in nodes:
                        import_text = source_code[node.start_byte:node.end_byte]
                        imports.append(import_text)
            else:  # Old API (<=0.22)
                for node, _capture_name in captures:
                    import_text = source_code[node.start_byte:node.end_byte]
                    imports.append(import_text)
            
            return imports
            
        except Exception as e:
            logger.warning(
                "Failed to extract imports | error={}",
                str(e)
            )
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
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Calculate checksum
            checksum = self.calculate_file_checksum(file_path)
            
            # Extract structural signature
            signature = await asyncio.to_thread(
                self.extractor.extract_structural_signature, # type: ignore
                file_path
            )
            
            # Extract imports directly from source code
            imports = self._extract_imports_from_source(content)
            
            # Add basic POI labels
            poi_labels = [self.programming_language_metadata.language, "source_file"]
            if signature and signature.functions:
                poi_labels.append("has_functions")
            if signature and signature.classes:
                poi_labels.append("has_classes")
            
            # Create UnoplatFile instance
            unoplat_file = UnoplatFile(
                file_path=file_path,
                content=content,
                checksum=checksum,
                structural_signature=signature,  # Store the actual object, not dict
                imports=imports,
                poi_labels=poi_labels
            )
            
            return unoplat_file
            
        except Exception as e:
            logger.error(
                "Failed to process file | file_path={} | error={}",
                file_path, str(e)
            )
            return None

    async def extract_files(self, package_files: Dict[str, List[str]]) -> AsyncGenerator[UnoplatFile, None]:
        """
        Generator that yields file processing data for all source files.
        
        Args:
            package_files: Map of package name to files
            
        Yields:
            UnoplatFile for each successfully processed file
        """
        for package_name, files in package_files.items():
            logger.info(
                "Processing files in package | package_name={} | file_count={}",
                package_name, len(files)
            )
            
            for file_path in files:
                file_data = await self.extract_file_data(file_path)
                if file_data:
                    self.files_processed += 1
                    yield file_data

    async def create_packages(self, package_names: List[str]) -> None:
        """
        Create package nodes using neomodel.
        
        Args:
            package_names: List of package qualified names to create
        """
        try:
            # No nested transaction - the caller should manage the transaction
            for package_name in package_names:
                # Extract simple name from qualified name
                simple_name = package_name.split(".")[-1]
                
                # Create package node using helper method
                package_dict = {
                    "qualified_name": package_name,
                    "name": simple_name
                }
                package_node = await self._handle_node_creation(CodeConfluencePackage, package_dict)
                
                if package_node:
                    self.packages_created += 1
                    logger.debug(f"Created/retrieved package: {package_name}")
            
            logger.info(f"Created {self.packages_created} packages")
            
        except Exception as e:
            logger.error(f"Failed to create packages: {e}")
            raise

    async def create_package_hierarchy(self, package_hierarchy: Dict[str, str]) -> None:
        """
        Create package parent-child relationships using neomodel.
        
        Args:
            package_hierarchy: Map of child package to parent package
        """
        if not package_hierarchy:
            return
            
        try:
            for child_pkg_name, parent_pkg_name in package_hierarchy.items():
                # Get parent and child packages
                parent = await CodeConfluencePackage.nodes.get(qualified_name=parent_pkg_name)
                child = await CodeConfluencePackage.nodes.get(qualified_name=child_pkg_name)
                
                # Connect them using the sub_packages relationship
                await parent.sub_packages.connect(child)
                
                logger.debug(f"Connected packages: {parent_pkg_name} -> {child_pkg_name}")
            
            logger.info(f"Created {len(package_hierarchy)} package relationships")
            
        except Exception as e:
            logger.error(f"Failed to create package hierarchy: {e}")
            raise

    async def _connect_root_packages(self, package_files: Dict[str, List[str]]) -> None:
        """Connect top-level packages (direct children of the codebase) to the CodeConfluenceCodebase node.

        Args:
            package_files: Map of package qualified names to their file lists.
        """
        try:
            # Import lazily to avoid circular import issues
            

            # Fetch the codebase node (it must already exist – created during git ingestion step)
            codebase_node = await CodeConfluenceCodebase.nodes.get(
                qualified_name=self.codebase_name
            )

            root_package_names = []
            for pkg_name in package_files.keys():
                # Determine direct children of the codebase: codebase_name.<segment>
                parent_name = ".".join(pkg_name.split(".")[:-1])
                if parent_name == self.codebase_name:
                    root_package_names.append(pkg_name)

            if not root_package_names:
                logger.warning(
                    "No root packages discovered for codebase {} – skipping relationship creation",
                    self.codebase_name,
                )
                return

            for root_pkg in root_package_names:
                try:
                    pkg_node = await CodeConfluencePackage.nodes.get(qualified_name=root_pkg)
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

    async def insert_files(self, file_data_list: List[UnoplatFile], package_files: Dict[str, List[str]]) -> None:
        """
        Insert files using neomodel.
        
        Args:
            file_data_list: List of UnoplatFile objects
            package_files: Map of package name to files for determining package relationships
        """
        try:
            # Reuse ambient transaction if present; otherwise operations will execute auto-commit.
            for unoplat_file in file_data_list:
                # Create file node using helper method
                file_dict = {
                    "file_path": unoplat_file.file_path,
                    "content": unoplat_file.content,
                    "checksum": unoplat_file.checksum,
                    "structural_signature": unoplat_file.structural_signature.model_dump() if unoplat_file.structural_signature else {},
                    "imports": unoplat_file.imports,
                    "poi_labels": unoplat_file.poi_labels
                }
                file_node = await self._handle_node_creation(CodeConfluenceFile, file_dict)
                
                if not file_node:
                    logger.warning(f"Failed to create/retrieve file node: {unoplat_file.file_path}")
                    continue
                
                # Find the package for this file
                package_qualified_name = None
                for pkg_name, files in package_files.items():
                    if unoplat_file.file_path in files:
                        package_qualified_name = pkg_name
                        break
                
                if package_qualified_name:
                    # Get the package and connect
                    package = await CodeConfluencePackage.nodes.get(
                        qualified_name=package_qualified_name
                    )

                    # Establish both directions to keep graph consistent
                    # (file) -[:PART_OF_PACKAGE]-> (package)
                    # (package) -[:CONTAINS_FILE]-> (file)
                    if not await file_node.package.is_connected(package):
                        await file_node.package.connect(package)

                    if not await package.files.is_connected(file_node):
                        await package.files.connect(file_node)
                
                logger.debug(f"Created file: {unoplat_file.file_path}")
            
            logger.info(f"Inserted {len(file_data_list)} files")
            
        except Exception as e:
            logger.error(f"Failed to insert files: {e}")
            raise

    async def process_files(self, package_files: Dict[str, List[str]]) -> None:
        """
        Process all files sequentially without batching.
        
        Args:
            package_files: Map of package name to files
        """
        try:
            async for file_data in self.extract_files(package_files):
                await self.insert_files([file_data], package_files)
            
            logger.info(f"Processed {self.files_processed} files")
            
        except Exception as e:
            logger.error(f"Failed to process files: {e}")
            raise

    async def process_and_insert_codebase(self) -> None:
        """
        Main processing method with fresh Neo4j connection.
        Each call gets its own Neo4j session to avoid transaction conflicts.
        """
        try:
            self._initialize_components()
            
            logger.info(f"Starting codebase processing: {self.codebase_name}")
            
            # 1. Discover packages and files
            package_files = self.discover_packages()
            
            if not package_files:
                logger.warning(f"No source files found in {self.codebase_path}")
                return
            
            # Use fresh Neo4j session for all database operations
            async with graph_ingestion_ctx(self.config) as graph:
                # We don't actually need the graph object here since we're using
                # neomodel operations directly, but we need the connection initialized
                
                # 2. Create all packages
                await self.create_packages(list(package_files.keys()))
                
                # 3. Create package hierarchy
                hierarchy = self.build_package_hierarchy(package_files)
                await self.create_package_hierarchy(hierarchy)

                # 3b. Connect root-level packages (depth-1) to the CodeConfluenceCodebase node
                await self._connect_root_packages(package_files)

                # 4. Process and insert files
                await self.process_files(package_files)
            
            logger.info(
                f"Completed codebase processing: {self.files_processed} files, "
                f"{self.packages_created} packages"
            )
            
        except Exception as e:
            logger.error(
                f"Codebase processing failed for {self.codebase_name}: {e}"
            )
            raise