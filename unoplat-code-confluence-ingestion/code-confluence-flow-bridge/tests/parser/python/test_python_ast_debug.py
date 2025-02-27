from typing import Dict, List, Optional

import pytest
import json
from tree_sitter import Parser, Node

from src.code_confluence_flow_bridge.models.configuration.settings import ProgrammingLanguage
from src.code_confluence_flow_bridge.parser.tree_sitter.code_confluence_tree_sitter import CodeConfluenceTreeSitter

@pytest.fixture
def extractor() -> Parser:
    """Create tree-sitter parser for Python."""
    parser: Parser = CodeConfluenceTreeSitter(language=ProgrammingLanguage.PYTHON).get_parser()
    return parser

def node_to_dict(node: Node, source: str) -> dict:
    """Convert a tree-sitter node to a dictionary for easier inspection."""
    # Create a dictionary for this node
    result = {
        "type": node.type,
        "start_byte": node.start_byte,
        "end_byte": node.end_byte,
        "text": source[node.start_byte:node.end_byte]
    }
    
    # Add field information (if any)
    fields = {}
    for field_name in ["left", "right", "function"]:
        field_node = node.child_by_field_name(field_name)
        if field_node:
            fields[field_name] = {
                "type": field_node.type,
                "text": source[field_node.start_byte:field_node.end_byte]
            }
    if fields:
        result["fields"] = fields
    
    # Add children recursively
    if node.child_count > 0:
        result["children"] = [node_to_dict(child, source) for child in node.children]
    
    return result

def test_debug_ast_structure(extractor: Parser) -> None:
    """Parse a sample Python source and save its AST structure as JSON."""
    debug_source = """
# Simple assignment
calculator = Calculator()

# Tuple unpacking
x, y = Point(), Vector()

# Assignment with type annotation
data: DataClass = DataClass()

# List with class instantiation
items = [Item()]

# Dictionary with class instantiation
mapping = {"key": Value()}

# Conditional assignment
result = FirstOption() if condition else SecondOption()
"""
    
    # Parse the code with Tree-sitter
    tree = extractor.parse(bytes(debug_source, "utf8"))
    
    # Convert the entire AST to a dictionary
    ast_dict = node_to_dict(tree.root_node, debug_source)
    
    # Save to JSON file
    output_file = "ast_debug.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(ast_dict, f, indent=2)
    
    print(f"AST structure saved to {output_file}")