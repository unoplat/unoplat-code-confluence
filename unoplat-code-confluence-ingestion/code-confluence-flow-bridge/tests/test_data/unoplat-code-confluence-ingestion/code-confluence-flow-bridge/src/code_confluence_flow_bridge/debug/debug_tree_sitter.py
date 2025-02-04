import os
from datetime import datetime

# For walking multiple lists if needed.
import json
from typing import Any, Dict, List, Optional, Tuple

from tree_sitter import Language, Node, Parser
import tree_sitter_python


def serialize_node(node: Node, code_bytes: bytes) -> Dict[str, Any]:
    """
    Serialize a tree-sitter Node into a JSON-serializable dictionary.
    
    Args:
        node: The tree-sitter Node.
        code_bytes: The original source code bytes.
    
    Returns:
        A dictionary with node type, start/end points, and the extracted text.
    """
    start_byte: int = node.start_byte
    end_byte: int = node.end_byte
    return {
        "type": node.type,
        "start_point": node.start_point,
        "end_point": node.end_point,
        "text": code_bytes[start_byte:end_byte].decode("utf8", errors="replace").strip()
    }

def process_from_import_statement(node: Node, code_bytes: bytes) -> Optional[Dict[str, Any]]:
    """
    Process a from-import statement AST node using next_named_sibling to walk through imports.
    
    Args:
        node: The from-import statement node (dotted_name node captured as @module).
        code_bytes: The original source code bytes.
    
    Returns:
        A dict matching UnoplatImport structure or None if parsing fails.
    """
    # Get the source from the dotted_name node (which is our @module capture)
    source: str = code_bytes[node.start_byte:node.end_byte].decode("utf8").strip()
    
    usage_names: List[Dict[str, Optional[str]]] = []
    
    # Start with the first aliased_import after the 'import' keyword
    current = node.next_named_sibling  
    
    # Walk through all aliased_imports using next_named_sibling
    while current:
        if current.type == "aliased_import":
            name_node = current.child(0)
            alias_node = current.child(2)
            
            if name_node:
                name_text: str = name_node.text.decode("utf8").strip() #type: ignore
                alias_text: Optional[str] = None
                
                if alias_node:
                    alias_text = alias_node.text.decode("utf8").strip() #type: ignore
                
                usage_names.append({
                    "original_name": name_text,
                    "alias": alias_text
                })
        elif current.type == "dotted_name":
            name_node = current.child(0)
            if name_node:
                name_text: str = name_node.text.decode("utf8").strip() #type: ignore
                usage_names.append({"original_name": name_text})
                
                 
        
        # Move to next sibling
        current = current.next_named_sibling
    
    if not usage_names:
        return None
        
    return {
        "Source": source,
        "UsageName": usage_names,
        "ImportType": "internal" if source.startswith(INTERNAL_PREFIX) else None
    }

def test_import_query() -> None:
    """Test to analyze Tree-sitter query results for Python imports."""
    code: str = """
# First Party (internal imports) - single line
from src.code_confluence_flow_bridge.models.chapi.chapi_node import ChapiNode as Node, Program as pm
from src.code_confluence_flow_bridge.models.code import Function, Class as cs
from src.code_confluence_flow_bridge.models.utils import get_all_utils
# First Party (internal imports) - multi-line using parentheses
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_import import (
    ImportedName,
    UnoplatImport as Import
)
"""
    code_bytes: bytes = code.encode("utf8")
    
    # 1) Create and configure parser
    parser: Parser = Parser()
    PY_LANGUAGE: Language = Language(tree_sitter_python.language())  # type: ignore
    parser.language = PY_LANGUAGE  # type: ignore
    
    # 2) Parse the code
    tree = parser.parse(code_bytes)
    
    # 3) Define query to capture internal from-imports
    query = PY_LANGUAGE.query(
        r"""
        (
          import_from_statement
             module_name: (dotted_name) @module
             (#match? @module "^src\\.code_confluence_flow_bridge")
        )
        """
    )
    
    # 4) Get matches
    matches: List[Tuple[int, Dict[str, List[Node]]]] = query.matches(tree.root_node)
    
    # 5) Process each match using next_named_sibling traversal
    unoplat_imports: List[Dict[str, Any]] = []
    for _, captures in matches:
        module_nodes = captures.get("module", [])
        for module_node in module_nodes:
            if result := process_from_import_statement(module_node, code_bytes):
                unoplat_imports.append(result)
    
    # 6) Write output
    debug_dir = "debug_output"
    os.makedirs(debug_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(debug_dir, f"unoplat_imports_{timestamp}.json")
    with open(output_file, "w", encoding="utf8") as f:
        json.dump(unoplat_imports, f, indent=2)
    print(f"DEBUG: UnoplatImport data written to {output_file}")

if __name__ == "__main__":
    test_import_query()