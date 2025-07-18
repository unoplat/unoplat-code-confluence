"""
Import alias extraction for Python.

This module processes import statements and builds a dictionary
mapping aliases to fully qualified module names.
"""

from pathlib import Path
from typing import Dict, List

from tree_sitter_language_pack import get_parser


def extract_imports_from_source(source_code: str, language: str = "python") -> List[str]:
    """
    Extract import statements directly from source code using tree-sitter.
    
    Args:
        source_code: Source code to analyze
        language: Programming language (default: "python")
        
    Returns:
        List of import statement strings
    """
    parser = get_parser(language)
    tree = parser.parse(bytes(source_code, "utf8"))
    root_node = tree.root_node
    
    # Load the imports query from the query file
    query_dir = Path(__file__).parent.parent.parent / "parser" / "queries" / language
    imports_query_file = query_dir / "imports.scm"
    
    if not imports_query_file.exists():
        # Fallback: return empty list if no query file found
        return []
    
    # Read and compile the query
    import_query_string = imports_query_file.read_text()
    language_obj = parser.language
    import_query = language_obj.query(import_query_string)
    
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


def build_import_aliases(imports: List[str]) -> Dict[str, str]:
    """
    Return a mapping *from fully–qualified import path → alias used in the file*.

    Examples
    --------
        import fastapi as fp              → {"fastapi": "fp"}
        import fastapi                    → {"fastapi": "fastapi"}            # alias == last component
        from fastapi import FastAPI       → {"fastapi.FastAPI": "FastAPI"}
        from fastapi import FastAPI as fp → {"fastapi.FastAPI": "fp"}

    This inverted map lets the detector start with a canonical
    framework symbol (e.g. ``fastapi.FastAPI``) and quickly discover
    which local identifiers refer to it.
    
    Args:
        imports: List of import statement strings to analyze
        
    Returns:
        Mapping from fully-qualified import paths to their aliases in the file
    """
    parser = get_parser("python")
    mapping: Dict[str, str] = {}

    def record(full_path: str, alias: str) -> None:
        # Don't overwrite if we already saw an explicit alias earlier.
        if full_path not in mapping:
            mapping[full_path] = alias

    for import_statement in imports:
        if not import_statement.strip():
            continue
            
        # Parse each import statement individually
        tree = parser.parse(bytes(import_statement, "utf8"))
        src_bytes = bytes(import_statement, "utf8")
        
        # The root should contain the import statement
        for node in tree.root_node.children:
            if node.type == "import_statement":
                # Handles: import mod [, mod2]  |  import mod as alias
                for child in node.named_children:
                    if child.type == "dotted_name":
                        module = src_bytes[child.start_byte:child.end_byte].decode()
                        alias = module.split(".")[-1]
                        record(module, alias)
                    elif child.type == "aliased_import":
                        module_node = None
                        alias_node = None
                        for grandchild in child.children:
                            if grandchild.type == "dotted_name":
                                module_node = grandchild
                            elif grandchild.type == "identifier" and grandchild != child.children[0]:
                                alias_node = grandchild
                        if module_node:
                            module = src_bytes[module_node.start_byte:module_node.end_byte].decode()
                            alias = (src_bytes[alias_node.start_byte:alias_node.end_byte].decode()
                                     if alias_node else module.split(".")[-1])
                            record(module, alias)

            elif node.type == "import_from_statement":
                # Handles: from module import name [, name2]  |  ... as alias
                module_node = next((c for c in node.children if c.type == "dotted_name"), None)
                if not module_node:
                    # Skip relative "from . import x" for now
                    continue
                base_module = src_bytes[module_node.start_byte:module_node.end_byte].decode()

                import_started = False
                for child in node.children:
                    if child.type == "import":
                        import_started = True
                        continue
                    if not import_started:
                        continue

                    if child.type == "dotted_name":
                        name = src_bytes[child.start_byte:child.end_byte].decode()
                        full_path = f"{base_module}.{name}"
                        record(full_path, name.split(".")[-1])

                    elif child.type == "aliased_import":
                        name_node = None
                        alias_node = None
                        for grandchild in child.children:
                            if grandchild.type == "dotted_name":
                                name_node = grandchild
                            elif grandchild.type == "identifier" and grandchild != child.children[0]:
                                alias_node = grandchild
                        if name_node:
                            name = src_bytes[name_node.start_byte:name_node.end_byte].decode()
                            alias = (src_bytes[alias_node.start_byte:alias_node.end_byte].decode()
                                     if alias_node else name.split(".")[-1])
                            full_path = f"{base_module}.{name}"
                            record(full_path, alias)

    return mapping