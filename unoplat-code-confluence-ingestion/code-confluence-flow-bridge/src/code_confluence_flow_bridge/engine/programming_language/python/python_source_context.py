"""Shared Python source context for tree-sitter based detection."""

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

_LANGUAGE_NAME: Final = "python"


def _record_import_alias(
    mapping: Dict[str, str], full_path: str, alias: str
) -> None:
    if full_path not in mapping:
        mapping[full_path] = alias


class PythonImportAliasStrategy(ImportAliasStrategy):
    """Resolve Python import statements into fully-qualified path aliases."""

    def build_import_aliases(self, imports: List[str]) -> Dict[str, str]:
        """
        Return a mapping from fully-qualified import path to its alias in the file.

        Examples
        --------
            import fastapi as fp              → {"fastapi": "fp"}
            import fastapi                    → {"fastapi": "fastapi"}
            from fastapi import FastAPI       → {"fastapi.FastAPI": "FastAPI"}
            from fastapi import FastAPI as fp → {"fastapi.FastAPI": "fp"}
        """
        parser = get_parser(_LANGUAGE_NAME)
        mapping: Dict[str, str] = {}

        for import_statement in imports:
            if not import_statement.strip():
                continue

            tree = parser.parse(bytes(import_statement, "utf8"))
            src_bytes = bytes(import_statement, "utf8")

            for node in tree.root_node.children:
                if node.type == "import_statement":
                    self._handle_import_statement(node, src_bytes, mapping)
                elif node.type == "import_from_statement":
                    self._handle_import_from_statement(node, src_bytes, mapping)

        return mapping

    def _handle_import_statement(
        self,
        node: tree_sitter.Node,
        src_bytes: bytes,
        mapping: Dict[str, str],
    ) -> None:
        for child in node.named_children:
            if child.type == "dotted_name":
                module = src_bytes[child.start_byte : child.end_byte].decode()
                alias = module.split(".")[-1]
                _record_import_alias(mapping, module, alias)
            elif child.type == "aliased_import":
                module_node = None
                alias_node = None
                for grandchild in child.children:
                    if grandchild.type == "dotted_name":
                        module_node = grandchild
                    elif (
                        grandchild.type == "identifier"
                        and grandchild != child.children[0]
                    ):
                        alias_node = grandchild
                if module_node:
                    module = src_bytes[
                        module_node.start_byte : module_node.end_byte
                    ].decode()
                    alias = (
                        src_bytes[alias_node.start_byte : alias_node.end_byte].decode()
                        if alias_node
                        else module.split(".")[-1]
                    )
                    _record_import_alias(mapping, module, alias)

    def _handle_import_from_statement(
        self,
        node: tree_sitter.Node,
        src_bytes: bytes,
        mapping: Dict[str, str],
    ) -> None:
        module_node = next((c for c in node.children if c.type == "dotted_name"), None)
        if not module_node:
            return
        base_module = src_bytes[module_node.start_byte : module_node.end_byte].decode()

        import_started = False
        for child in node.children:
            if child.type == "import":
                import_started = True
                continue
            if not import_started:
                continue

            if child.type == "dotted_name":
                name = src_bytes[child.start_byte : child.end_byte].decode()
                full_path = f"{base_module}.{name}"
                _record_import_alias(mapping, full_path, name.split(".")[-1])

            elif child.type == "aliased_import":
                name_node = None
                alias_node = None
                for grandchild in child.children:
                    if grandchild.type == "dotted_name":
                        name_node = grandchild
                    elif (
                        grandchild.type == "identifier"
                        and grandchild != child.children[0]
                    ):
                        alias_node = grandchild
                if name_node:
                    name = src_bytes[name_node.start_byte : name_node.end_byte].decode()
                    alias = (
                        src_bytes[alias_node.start_byte : alias_node.end_byte].decode()
                        if alias_node
                        else name.split(".")[-1]
                    )
                    full_path = f"{base_module}.{name}"
                    _record_import_alias(mapping, full_path, alias)


def build_import_aliases(imports: List[str]) -> Dict[str, str]:
    """Backward-local helper used by tests; delegates to the strategy."""
    return PythonImportAliasStrategy().build_import_aliases(imports)


class PythonSourceContext(BaseSourceContext):
    """Shared parsed source context for Python detection paths."""

    @classmethod
    def from_bytes(cls, source_bytes: bytes) -> "PythonSourceContext":
        base_context = SourceContextBuilder(
            language_name=_LANGUAGE_NAME,
            import_extractor=LanguagePackImportExtractor(language_name=_LANGUAGE_NAME),
            alias_strategy=PythonImportAliasStrategy(),
        ).from_bytes(source_bytes)
        return cls(
            source_bytes=base_context.source_bytes,
            tree=base_context.tree,
            root_node=base_context.root_node,
            imports=base_context.imports,
            import_aliases=base_context.import_aliases,
        )
