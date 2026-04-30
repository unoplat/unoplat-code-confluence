"""Shared TypeScript source context for tree-sitter based detection."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Dict, List

from pydantic import BaseModel, ConfigDict
import tree_sitter
from tree_sitter_language_pack import get_language, get_parser

_IMPORT_QUERY_PATH = Path(__file__).resolve().parent / "queries" / "imports.scm"


@lru_cache(maxsize=1)
def _get_import_query() -> tree_sitter.Query:
    """Return the compiled tree-sitter import query, cached after first call."""
    language = get_language("typescript")  # type: ignore[arg-type]
    query_source = _IMPORT_QUERY_PATH.read_text(encoding="utf-8")
    return tree_sitter.Query(language, query_source)


def _extract_imports_from_tree(
    root_node: tree_sitter.Node, source_bytes: bytes
) -> List[str]:
    """Run the import query on a parsed tree and return raw import statements.

    Args:
        root_node: Root node of the tree-sitter parse tree.
        source_bytes: UTF-8 encoded source used to extract node text.

    Returns:
        List of raw import statement strings captured by the query.
    """
    cursor = tree_sitter.QueryCursor(_get_import_query())
    captures: Dict[str, List[tree_sitter.Node]] = cursor.captures(root_node)

    imports: List[str] = []
    for nodes in captures.values():
        for node in nodes:
            imports.append(
                source_bytes[node.start_byte : node.end_byte].decode("utf-8")
            )

    return imports


def _record_import_alias(
    mapping: Dict[str, str], full_path: str, alias: str
) -> None:
    """Record an import alias, keeping only the first mapping per path."""
    if full_path not in mapping:
        mapping[full_path] = alias


def _get_string_value(node: tree_sitter.Node, source_bytes: bytes) -> str:
    """Extract the string value from a TypeScript string node (strips quotes)."""
    text = source_bytes[node.start_byte : node.end_byte].decode("utf-8")
    return text.strip("'\"")


def build_import_aliases(imports: List[str]) -> Dict[str, str]:
    """
    Return a mapping from fully-qualified import path to its local alias.

    Supported forms:
    - Named:          import { NextRequest } from 'next/server'
                      → {next/server.NextRequest: NextRequest}
    - Named aliased:  import { NextRequest as NR } from 'next/server'
                      → {next/server.NextRequest: NR}
    - Default:        import Next from 'next/server'
                      → {next/server: Next}
    - Type-only named: import type { NextRequest } from 'next/server'
                       → same as named
    - Namespace:      import * as ns from 'next/server'  → skipped (v1)
    """
    parser = get_parser("typescript")  # type: ignore[arg-type]
    mapping: Dict[str, str] = {}

    for import_statement in imports:
        if not import_statement.strip():
            continue

        tree = parser.parse(bytes(import_statement, "utf8"))
        src_bytes = bytes(import_statement, "utf8")

        for node in tree.root_node.children:
            if node.type != "import_statement":
                continue

            # Find the module path (string node after 'from')
            module_str_node = next(
                (c for c in node.children if c.type == "string"), None
            )
            if module_str_node is None:
                continue
            module_path = _get_string_value(module_str_node, src_bytes)

            # Find import_clause
            import_clause = next(
                (c for c in node.children if c.type == "import_clause"), None
            )
            if import_clause is None:
                continue

            for clause_child in import_clause.children:
                if clause_child.type == "identifier":
                    # Default import: import Foo from 'mod'
                    alias = src_bytes[
                        clause_child.start_byte : clause_child.end_byte
                    ].decode("utf-8")
                    _record_import_alias(mapping, module_path, alias)

                elif clause_child.type == "named_imports":
                    # Named imports: { Foo, Bar as B }
                    for specifier in clause_child.children:
                        if specifier.type != "import_specifier":
                            continue
                        identifiers = [
                            c
                            for c in specifier.children
                            if c.type == "identifier"
                        ]
                        if len(identifiers) == 1:
                            # Simple named: { Foo }
                            name = src_bytes[
                                identifiers[0].start_byte : identifiers[0].end_byte
                            ].decode("utf-8")
                            _record_import_alias(
                                mapping, f"{module_path}.{name}", name
                            )
                        elif len(identifiers) >= 2:
                            # Aliased named: { Foo as Bar }
                            # identifiers[0] = original name, identifiers[-1] = alias
                            original = src_bytes[
                                identifiers[0].start_byte : identifiers[0].end_byte
                            ].decode("utf-8")
                            alias = src_bytes[
                                identifiers[-1].start_byte : identifiers[-1].end_byte
                            ].decode("utf-8")
                            _record_import_alias(
                                mapping, f"{module_path}.{original}", alias
                            )

                elif clause_child.type == "namespace_import":
                    # Namespace import: import * as ns from 'mod' → skipped in v1
                    pass

    return mapping


class TypeScriptSourceContext(BaseModel):
    """Shared parsed source context for TypeScript detection paths."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    source_bytes: bytes
    tree: tree_sitter.Tree
    root_node: tree_sitter.Node
    imports: List[str]
    import_aliases: Dict[str, str]

    @classmethod
    def from_bytes(cls, source_bytes: bytes) -> "TypeScriptSourceContext":
        """Parse TypeScript bytes and build a fully-populated context.

        Args:
            source_bytes: Raw TypeScript source bytes.

        Returns:
            A ``TypeScriptSourceContext`` with the parse tree, extracted
            imports, and resolved import-alias mapping ready for detection.
        """
        parser = get_parser("typescript")  # type: ignore[arg-type]
        tree = parser.parse(source_bytes)
        root_node = tree.root_node
        imports = _extract_imports_from_tree(root_node, source_bytes)
        import_aliases = build_import_aliases(imports)
        return cls(
            source_bytes=source_bytes,
            tree=tree,
            root_node=root_node,
            imports=imports,
            import_aliases=import_aliases,
        )
