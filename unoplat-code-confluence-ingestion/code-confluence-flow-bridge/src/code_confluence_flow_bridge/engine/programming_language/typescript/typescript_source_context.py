"""Shared TypeScript source context for tree-sitter based detection."""

from __future__ import annotations

from typing import Dict, Final, List

import tree_sitter
from tree_sitter_language_pack import get_parser

from code_confluence_flow_bridge.engine.programming_language.common.source_context import (
    BaseSourceContext,
    ImportAliasStrategy,
    LanguagePackImportExtractor,
    SourceContextBuilder,
)

_LANGUAGE_NAME: Final = "typescript"


def _record_import_alias(
    mapping: Dict[str, str], full_path: str, alias: str
) -> None:
    """Record an import alias, keeping only the first mapping per path."""
    if full_path not in mapping:
        mapping[full_path] = alias


def _get_string_value(node: tree_sitter.Node, source_bytes: bytes) -> str:
    """Extract the string value from a TypeScript string node (strips quotes)."""
    text = source_bytes[node.start_byte : node.end_byte].decode(
        "utf-8", errors="ignore"
    )
    return text.strip("'\"")


class TypeScriptImportAliasStrategy(ImportAliasStrategy):
    """Resolve TypeScript import statements into local aliases."""

    def build_import_aliases(self, imports: List[str]) -> Dict[str, str]:
        """
        Return a mapping from fully-qualified import path to its local alias.

        Supported forms:
        - Named:           import { NextRequest } from 'next/server'
        - Named aliased:   import { NextRequest as NR } from 'next/server'
        - Default:         import Next from 'next/server'
        - Type-only named: import type { NextRequest } from 'next/server'
        - Namespace:       import * as ns from 'next/server' → skipped (v1)
        """
        parser = get_parser(_LANGUAGE_NAME)
        mapping: Dict[str, str] = {}

        for import_statement in imports:
            if not import_statement.strip():
                continue

            tree = parser.parse(bytes(import_statement, "utf8"))
            src_bytes = bytes(import_statement, "utf8")

            for node in tree.root_node.children:
                if node.type != "import_statement":
                    continue
                self._handle_import_statement(node, src_bytes, mapping)

        return mapping

    def _handle_import_statement(
        self,
        node: tree_sitter.Node,
        src_bytes: bytes,
        mapping: Dict[str, str],
    ) -> None:
        module_str_node = next((c for c in node.children if c.type == "string"), None)
        if module_str_node is None:
            return
        module_path = _get_string_value(module_str_node, src_bytes)

        import_clause = next(
            (c for c in node.children if c.type == "import_clause"), None
        )
        if import_clause is None:
            return

        for clause_child in import_clause.children:
            if clause_child.type == "identifier":
                alias = src_bytes[
                    clause_child.start_byte : clause_child.end_byte
                ].decode("utf-8")
                _record_import_alias(mapping, module_path, alias)

            elif clause_child.type == "named_imports":
                self._handle_named_imports(clause_child, src_bytes, module_path, mapping)

            elif clause_child.type == "namespace_import":
                # Namespace import: import * as ns from 'mod' → skipped in v1
                pass

    def _handle_named_imports(
        self,
        node: tree_sitter.Node,
        src_bytes: bytes,
        module_path: str,
        mapping: Dict[str, str],
    ) -> None:
        for specifier in node.children:
            if specifier.type != "import_specifier":
                continue
            identifiers = [c for c in specifier.children if c.type == "identifier"]
            if len(identifiers) == 1:
                name = src_bytes[
                    identifiers[0].start_byte : identifiers[0].end_byte
                ].decode("utf-8")
                _record_import_alias(mapping, f"{module_path}.{name}", name)
            elif len(identifiers) >= 2:
                original = src_bytes[
                    identifiers[0].start_byte : identifiers[0].end_byte
                ].decode("utf-8")
                alias = src_bytes[
                    identifiers[-1].start_byte : identifiers[-1].end_byte
                ].decode("utf-8")
                _record_import_alias(mapping, f"{module_path}.{original}", alias)


def build_import_aliases(imports: List[str]) -> Dict[str, str]:
    """Backward-local helper used by tests; delegates to the strategy."""
    return TypeScriptImportAliasStrategy().build_import_aliases(imports)


class TypeScriptSourceContext(BaseSourceContext):
    """Shared parsed source context for TypeScript detection paths."""

    @classmethod
    def from_bytes(cls, source_bytes: bytes) -> "TypeScriptSourceContext":
        """Parse TypeScript bytes and build a fully-populated context."""
        base_context = SourceContextBuilder(
            language_name=_LANGUAGE_NAME,
            import_extractor=LanguagePackImportExtractor(language_name=_LANGUAGE_NAME),
            alias_strategy=TypeScriptImportAliasStrategy(),
        ).from_bytes(source_bytes)
        return cls(
            source_bytes=base_context.source_bytes,
            tree=base_context.tree,
            root_node=base_context.root_node,
            imports=base_context.imports,
            import_aliases=base_context.import_aliases,
        )
