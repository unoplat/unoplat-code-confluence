"""
Import alias extraction for Python.

This module processes import statements and builds a dictionary
mapping aliases to fully qualified module names.
"""

from pathlib import Path
from typing import List

import tree_sitter
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
    

    parser: tree_sitter.Parser = get_parser(language)
    tree: tree_sitter.Tree = parser.parse(bytes(source_code, "utf8"))
    root_node: tree_sitter.Node = tree.root_node
    
    # Load the imports query from the query file
    query_dir = Path(__file__).parent.parent.parent / "parser" / "queries" / language
    imports_query_file = query_dir / "imports.scm"
    
    if not imports_query_file.exists():
        # Fallback: return empty list if no query file found
        return []
    
    # Read and compile the query
    import_query_string = imports_query_file.read_text()
    language_obj: tree_sitter.Language = parser.language #type: ignore
    import_query = language_obj.query(import_query_string)
    
    # Execute query using QueryCursor (tree-sitter 0.25.x API)
    cursor = tree_sitter.QueryCursor(import_query)
    captures = cursor.captures(root_node)
    
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