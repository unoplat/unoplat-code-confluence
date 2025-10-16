"""Configuration model for Tree-sitter structural signature extractors.

This module provides a reusable configuration pattern for Tree-sitter-based
extractors across different programming languages (Python, TypeScript, etc.).
"""

from pathlib import Path
from typing import Callable, Dict, Set

from pydantic import BaseModel, ConfigDict, Field


class TreeSitterExtractorConfig(BaseModel):
    """Configuration for Tree-sitter structural signature extraction.

    This model encapsulates all language-specific configuration needed
    by Tree-sitter extractors, providing a consistent pattern for Python,
    TypeScript, and future language implementations.

    Attributes:
        query_file_paths: Mapping of query type to `.scm` file path.
            Example keys: "module_functions", "class_methods", "global_variables"
        capture_mappings: Mapping of semantic keys to Tree-sitter capture names.
            Allows language-specific capture name customization while maintaining
            consistent semantic keys in the extractor code.
            Example: {"function": "docstring", "class": "class_docstring"}
        container_node_types: Set of AST node types that delimit top-level scope.
            Nodes with these types in their ancestry are NOT considered top-level.
            Example (Python): {"function_definition", "class_definition"}
        block_node_types: Set of AST node types representing code blocks.
            Used for navigation when determining immediate child relationships.
            Example (Python): {"block"}
        optional_query_keys: Set of query keys that can be missing without error.
            Enables gradual feature rollout and backward compatibility.
            Example: {"function_calls", "instance_variables", "nested_classes"}
        doc_cleaner: Optional callable to clean documentation string literals.
            Takes raw doc string and returns cleaned version.
            If None, returns doc strings unchanged.
            Example (Python): Strip triple quotes from docstrings

    Example:
        >>> from pathlib import Path
        >>> config = TreeSitterExtractorConfig(
        ...     query_file_paths={
        ...         "module_functions": Path("queries/python/module_functions.scm"),
        ...         "class_methods": Path("queries/python/class_methods.scm"),
        ...     },
        ...     capture_mappings={
        ...         "function": "docstring",
        ...         "class": "class_docstring",
        ...     },
        ...     container_node_types={"function_definition", "class_definition"},
        ...     block_node_types={"block"},
        ...     optional_query_keys={"function_calls"},
        ... )
    """

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    query_file_paths: Dict[str, Path]
    capture_mappings: Dict[str, str] = Field(default_factory=dict)
    container_node_types: Set[str] = Field(default_factory=set)
    block_node_types: Set[str] = Field(default_factory=set)
    optional_query_keys: Set[str] = Field(default_factory=set)
    doc_cleaner: Callable[[str], str] = Field(default=lambda s: s)

    def get_capture_name(self, semantic_key: str) -> str:
        """Get Tree-sitter capture name for a semantic key.

        Falls back to the semantic key itself if no mapping exists,
        allowing flexibility in query file design.

        Args:
            semantic_key: Semantic identifier (e.g., "function", "class")

        Returns:
            Capture name to use in Tree-sitter queries (e.g., "docstring")

        Example:
            >>> config.get_capture_name("function")
            "docstring"
            >>> config.get_capture_name("unmapped_key")
            "unmapped_key"
        """
        return self.capture_mappings.get(semantic_key, semantic_key)

    def is_optional_query(self, query_key: str) -> bool:
        """Check if a query is optional and can be missing.

        Args:
            query_key: Query identifier (e.g., "function_calls")

        Returns:
            True if query can be missing without error, False otherwise

        Example:
            >>> config.is_optional_query("function_calls")
            True
            >>> config.is_optional_query("module_functions")
            False
        """
        return query_key in self.optional_query_keys
