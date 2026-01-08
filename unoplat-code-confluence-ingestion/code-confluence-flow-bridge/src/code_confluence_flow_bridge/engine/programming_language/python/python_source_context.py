"""Shared Python source context for tree-sitter based detection."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Dict, List

import tree_sitter
from pydantic import BaseModel, ConfigDict
from tree_sitter_language_pack import get_language, get_parser


_IMPORT_QUERY_PATH = Path(__file__).resolve().parent / "queries" / "imports.scm"


@lru_cache(maxsize=1)
def _get_import_query() -> tree_sitter.Query:
    language = get_language("python")  # type: ignore[arg-type]
    query_source = _IMPORT_QUERY_PATH.read_text(encoding="utf-8")
    return tree_sitter.Query(language, query_source)


def _extract_imports_from_tree(
    root_node: tree_sitter.Node, source_bytes: bytes
) -> List[str]:
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
    if full_path not in mapping:
        mapping[full_path] = alias


def build_import_aliases(imports: List[str]) -> Dict[str, str]:
    """
    Return a mapping from fully-qualified import path to its alias in the file.

    Examples
    --------
        import fastapi as fp              → {"fastapi": "fp"}
        import fastapi                    → {"fastapi": "fastapi"}
        from fastapi import FastAPI       → {"fastapi.FastAPI": "FastAPI"}
        from fastapi import FastAPI as fp → {"fastapi.FastAPI": "fp"}
    """
    parser = get_parser("python")
    mapping: Dict[str, str] = {}

    for import_statement in imports:
        if not import_statement.strip():
            continue

        tree = parser.parse(bytes(import_statement, "utf8"))
        src_bytes = bytes(import_statement, "utf8")

        for node in tree.root_node.children:
            if node.type == "import_statement":
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
                                src_bytes[
                                    alias_node.start_byte : alias_node.end_byte
                                ].decode()
                                if alias_node
                                else module.split(".")[-1]
                            )
                            _record_import_alias(mapping, module, alias)

            elif node.type == "import_from_statement":
                module_node = next(
                    (c for c in node.children if c.type == "dotted_name"), None
                )
                if not module_node:
                    continue
                base_module = src_bytes[
                    module_node.start_byte : module_node.end_byte
                ].decode()

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
                            name = src_bytes[
                                name_node.start_byte : name_node.end_byte
                            ].decode()
                            alias = (
                                src_bytes[
                                    alias_node.start_byte : alias_node.end_byte
                                ].decode()
                                if alias_node
                                else name.split(".")[-1]
                            )
                            full_path = f"{base_module}.{name}"
                            _record_import_alias(mapping, full_path, alias)

    return mapping


class PythonSourceContext(BaseModel):
    """Shared parsed source context for Python detection paths."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    source_code: str
    source_bytes: bytes
    tree: tree_sitter.Tree
    root_node: tree_sitter.Node
    imports: List[str]
    import_aliases: Dict[str, str]

    @classmethod
    def from_source(cls, source_code: str) -> "PythonSourceContext":
        source_bytes = source_code.encode("utf-8", errors="ignore")
        parser = get_parser("python")
        tree = parser.parse(source_bytes)
        root_node = tree.root_node
        imports = _extract_imports_from_tree(root_node, source_bytes)
        import_aliases = build_import_aliases(imports)
        return cls(
            source_code=source_code,
            source_bytes=source_bytes,
            tree=tree,
            root_node=root_node,
            imports=imports,
            import_aliases=import_aliases,
        )
