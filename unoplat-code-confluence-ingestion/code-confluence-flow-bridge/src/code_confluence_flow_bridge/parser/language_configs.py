from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, Set

__all__ = [
    "LanguageConfig",
    "register_language",
    "get_config",
]


@dataclass(frozen=True, slots=True)
class LanguageConfig:
    """Declarative description of language-specific parsing details."""

    name: str  # Human/registry name, e.g. "python", "java"
    query_dir: Path  # Directory that contains the language's .scm query files

    # Node kinds that delimit top-level scope (i.e. if any of these is found among
    # a node's ancestors, the node is *not* considered top level).
    container_nodes: Set[str] = field(default_factory=set)

    # Node kinds that represent methods inside a class (used to avoid treating
    # assignments within methods as class-level variables).
    method_nodes: Set[str] = field(default_factory=set)
    
    # Node types that represent code blocks (e.g., "block" in Python)
    block_nodes: Set[str] = field(default_factory=lambda: {"block"})

    # Callable that cleans documentation string literals / comments.
    clean_doc: Callable[[str], str] = lambda s: s

    # Mapping of semantic keys to capture names used in query files.
    doc_captures: Dict[str, str] = field(default_factory=dict)
    
    # Set of filenames to ignore during parsing (e.g., "__init__.py" for Python)
    ignored_files: Set[str] = field(default_factory=set)

    # Convenience accessor
    def cap(self, key: str) -> str:  # noqa: D401
        """Return the capture name for a given semantic key (falls back to key)."""
        return self.doc_captures.get(key, key)


# ---------------------------------------------------------------------------
# Registry helpers
# ---------------------------------------------------------------------------
_REGISTRY: Dict[str, LanguageConfig] = {}


def register_language(config: LanguageConfig) -> None:
    """Register a :class:`LanguageConfig` for later retrieval."""
    _REGISTRY[config.name] = config


def get_config(name: str) -> LanguageConfig:
    """Return a registered :class:`LanguageConfig`.

    Raises
    ------
    KeyError
        If the requested language has not been registered.
    """
    return _REGISTRY[name]


# ---------------------------------------------------------------------------
# Built-in Python config (serves as example and default)
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent

def _py_clean_doc(text: str) -> str:
    """Strip Python string literal quotes/triple-quotes."""
    if text.startswith('"""') and text.endswith('"""'):
        return text[3:-3]
    if text.startswith("'''") and text.endswith("'''"):
        return text[3:-3]
    if text.startswith('"') and text.endswith('"'):
        return text[1:-1]
    if text.startswith("'") and text.endswith("'"):
        return text[1:-1]
    return text

register_language(
    LanguageConfig(
        name="python",
        query_dir=BASE_DIR / "queries" / "python",
        container_nodes={"function_definition", "class_definition"},
        method_nodes={"function_definition"},
        block_nodes={"block"},  # Python uses 'block' for function/class bodies
        clean_doc=_py_clean_doc,
        doc_captures={
            "module": "docstring",
            "function": "docstring",
            "class": "class_docstring",
            "method": "method_docstring",
            "nested_function": "nested_docstring",
            "nested_class": "nested_class_docstring",
        },
        ignored_files={"__init__.py"},
    )
)

# ---------------------------------------------------------------------------
# Java configuration
# ---------------------------------------------------------------------------
register_language(
    LanguageConfig(
        name="java",
        query_dir=BASE_DIR / "queries" / "java",
        container_nodes={"class_declaration", "interface_declaration", "enum_declaration"},
        method_nodes={"method_declaration", "constructor_declaration"},
        ignored_files={"package-info.java"},
    )
)

# ---------------------------------------------------------------------------
# TypeScript configuration
# ---------------------------------------------------------------------------
register_language(
    LanguageConfig(
        name="typescript",
        query_dir=BASE_DIR / "queries" / "typescript",
        container_nodes={"class_declaration", "interface_declaration", "function_declaration"},
        method_nodes={"method_definition", "constructor"},
        ignored_files={".d.ts"},  # Ignore TypeScript declaration files by extension check
    )
)

# ---------------------------------------------------------------------------
# Go configuration
# ---------------------------------------------------------------------------
register_language(
    LanguageConfig(
        name="go",
        query_dir=BASE_DIR / "queries" / "go",
        container_nodes={"type_declaration", "function_declaration"},
        method_nodes={"method_declaration"},
        ignored_files={"doc.go"},  # Common Go documentation files
    )
) 