"""Base class for Tree-sitter structural signature extractors.

This module provides the foundation for language-specific extractors,
encapsulating caching strategies for Tree-sitter Language, Parser, and Query objects.
"""

from typing import Dict

import tree_sitter
from tree_sitter_language_pack import get_language, get_parser

from src.code_confluence_flow_bridge.parser.tree_sitter_config import (
    TreeSitterExtractorConfig,
)

# ---------------------------------------------------------------------------
# Multi-level caches: language ► parser ► compiled query
# ---------------------------------------------------------------------------
# TODO: Cache key currently assumes single config per language_name.
# If TypeScript/TSX require different query sets, either:
# 1. Use distinct language names ("typescript" vs "tsx"), OR
# 2. Extend key to (language_name, config_hash), OR
# 3. Implement cache eviction on config mismatch
# Current "last writer wins" behavior will cause silent bugs with multiple configs.
_LANGUAGE_CACHE: Dict[str, tree_sitter.Language] = {}
_PARSER_CACHE: Dict[str, tree_sitter.Parser] = {}
_QUERY_CACHE: Dict[str, Dict[str, tree_sitter.Query]] = {}


class TreeSitterExtractorBase:
    """Base class providing caching utilities for Tree-sitter extractors.

    This class encapsulates the module-level caching strategy for Tree-sitter
    Language, Parser, and compiled Query objects. Subclasses (Python, TypeScript)
    inherit cache access methods while implementing language-specific extraction logic.

    Architecture:
    - Module-level caches (_LANGUAGE_CACHE, _PARSER_CACHE, _QUERY_CACHE) remain at
      module scope for shared access across all extractor instances
    - Subclasses should expose wrapper properties for test introspection compatibility
    - Cache keys use language_name only (assumes single config per language)

    Cache Key Limitation:
    Current implementation assumes one TreeSitterExtractorConfig per language_name.
    If multiple configs are needed for the same language (e.g., TypeScript vs TSX),
    use distinct language names or extend cache key to include config hash to avoid
    "last writer wins" bugs.

    Subclass Responsibilities:
    - Call base __init__ with config
    - Implement language-specific extraction methods
    - Optionally expose cache properties for test compatibility
    """

    def __init__(self, language_name: str, config: TreeSitterExtractorConfig):
        """Initialize extractor with language and configuration.

        Args:
            language_name: Programming language identifier (e.g., "python", "typescript")
            config: TreeSitterExtractorConfig with query paths, captures, node types
        """
        self.config: TreeSitterExtractorConfig = config
        self.language_name: str = language_name
        self.language: tree_sitter.Language = self._get_language(language_name)
        self.parser: tree_sitter.Parser = self._get_parser(language_name)
        self.queries: Dict[str, tree_sitter.Query] = self._get_compiled_queries()

    @staticmethod
    def _get_language(language_name: str) -> tree_sitter.Language:
        """Fetch a tree-sitter Language with caching.

        Args:
            language_name: Language identifier

        Returns:
            Cached or newly loaded tree-sitter Language object
        """
        if language_name not in _LANGUAGE_CACHE:
            _LANGUAGE_CACHE[language_name] = get_language(language_name)  # type: ignore[arg-type]
        return _LANGUAGE_CACHE[language_name]

    @staticmethod
    def _get_parser(language_name: str) -> tree_sitter.Parser:
        """Fetch a tree-sitter Parser with caching.

        Args:
            language_name: Language identifier

        Returns:
            Cached or newly created tree-sitter Parser object
        """
        if language_name not in _PARSER_CACHE:
            _PARSER_CACHE[language_name] = get_parser(language_name)  # type: ignore[arg-type]
        return _PARSER_CACHE[language_name]

    def _get_compiled_queries(self) -> Dict[str, tree_sitter.Query]:
        """Compile and cache queries for the current language on-demand.

        Uses language_name as cache key. Assumes single config per language.

        Returns:
            Dictionary mapping query names to compiled Query objects
        """
        if self.language_name not in _QUERY_CACHE:
            query_strings: Dict[str, str] = self._create_queries()
            _QUERY_CACHE[self.language_name] = {
                name: self.language.query(qstr) for name, qstr in query_strings.items()
            }
        return _QUERY_CACHE[self.language_name]

    def _create_queries(self) -> Dict[str, str]:
        """Load query strings from config file paths.

        Returns:
            Dictionary mapping query names to raw query strings

        Raises:
            FileNotFoundError: If required query file missing
        """
        query_strings: Dict[str, str] = {}

        for key, file_path in self.config.query_file_paths.items():
            if not file_path.exists():
                # Check if this query is optional
                if self.config.is_optional_query(key):
                    continue
                raise FileNotFoundError(f"Query file not found: {file_path}")
            query_strings[key] = file_path.read_text()

        return query_strings