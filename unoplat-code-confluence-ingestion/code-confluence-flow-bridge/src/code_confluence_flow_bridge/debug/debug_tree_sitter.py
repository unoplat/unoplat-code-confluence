import os
from datetime import datetime

# For walking multiple lists if needed.
import json
from typing import Any, Dict, List, Optional, Tuple

from tree_sitter import Language, Node, Parser
import tree_sitter_python

# Internal prefix used to mark internal imports.
INTERNAL_PREFIX = "src.code_confluence_flow_bridge"

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

def parse_from_import_node(node: Node, code_bytes: bytes) -> Optional[Dict[str, Any]]:
    """
    Parse a from-import statement node using Tree-sitter's AST.
    Extract the module (source) and all imported names and aliases.
    
    Args:
        node: The from-import AST node.
        code_bytes: The original source bytes.
    
    Returns:
        A dict with keys "Source", "UsageName" (list of {original_name, alias}),
        and "ImportType" (to be set later) or None if parsing fails.
    """
    # Attempt to get the module name from the field "module_name"
    module_node = node.child_by_field_name("module_name")
    if module_node is None:
        # Fallback: search for a node of type "dotted_name" among the children.
        for child in node.children:
            if child.type == "dotted_name":
                module_node = child
                break
    if module_node is None:
        return None
    source: str = code_bytes[module_node.start_byte:module_node.end_byte].decode("utf8").strip()

    usage_names: List[Dict[str, Optional[str]]] = []
    for child in node.children:
        if child.type == "aliased_import":
            name_node = child.child_by_field_name("name")
            if name_node is None:
                continue
            name_text: str = code_bytes[name_node.start_byte:name_node.end_byte].decode("utf8").strip()
            alias_text: Optional[str] = None
            alias_node = child.child_by_field_name("alias")
            if alias_node is not None:
                alias_text = code_bytes[alias_node.start_byte:alias_node.end_byte].decode("utf8").strip()
            usage_names.append({"original_name": name_text, "alias": alias_text})
    if not usage_names:
        return None
    return {
        "Source": source,
        "UsageName": usage_names,
        "ImportType": None  # Will be set later based on INTERNAL_PREFIX.
    }

def parse_plain_import_node(node: Node, code_bytes: bytes) -> Optional[Dict[str, Any]]:
    """
    Parse a plain import statement node and extract the imported identifiers and aliases.
    
    Args:
        node: The plain import AST node.
        code_bytes: The original source code bytes.
    
    Returns:
        A dict with keys "Source" (None), "UsageName" (list of {original_name, alias}),
        and "ImportType" (to be set later), or None if nothing is parsed.
    """
    usage_names: List[Dict[str, Optional[str]]] = []
    for child in node.children:
        if child.type == "aliased_import":
            name_node = child.child_by_field_name("name")
            if name_node is None:
                continue
            name_text: str = code_bytes[name_node.start_byte:name_node.end_byte].decode("utf8").strip()
            alias_text: Optional[str] = None
            alias_node = child.child_by_field_name("alias")
            if alias_node is not None:
                alias_text = code_bytes[alias_node.start_byte:alias_node.end_byte].decode("utf8").strip()
            usage_names.append({"original_name": name_text, "alias": alias_text})
    if not usage_names:
        return None
    return {
        "Source": None,
        "UsageName": usage_names,
        "ImportType": None  # Will be set later.
    }

def test_import_query() -> None:
    """
    Test to analyze Tree-sitter query results for Python imports.
    This version uses a simplified query to capture full import statements (plain and from-import)
    and then re-parses their text via Tree-sitter to extract module names and imported identifiers.
    """
    code: str = """
# Standard Library
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Third Party
import pytest
from loguru import logger
import requests as req
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# First Party (internal imports) - single line
from src.code_confluence_flow_bridge.models.chapi.chapi_node import ChapiNode as Node, Program as pm

# First Party (internal imports) - multi-line using parentheses
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_import import (
    ImportedName,
    UnoplatImport as Import
)

# Local imports
from .utils import helper
from ..common import constants
"""
    code_bytes: bytes = code.encode("utf8")
    
    # 1) Create and configure parser.
    parser: Parser = Parser()
    PY_LANGUAGE: Language = Language(tree_sitter_python.language())  # type: ignore
    parser.language = PY_LANGUAGE  # type: ignore
    
    # 2) Parse the code.
    tree = parser.parse(code_bytes)
    
    # 3) Define a simplified query.
    # We capture complete statements only:
    query = PY_LANGUAGE.query(
        r"""
        (import_statement) @plain_import_stmt
        (import_from_statement) @from_import_stmt
        """
    )
    
    # 4) Get the matches.
    # Each match is a 2-tuple: (pattern index, dict[capture_name, list[Node]])
    matches: List[Tuple[int, Dict[str, List[Node]]]] = query.matches(tree.root_node)
    
    # 5) Build a simplified list where each match is represented by its capture name and full text.
    simple_matches: List[Dict[str, str]] = []
    for _, cap_map in matches:
        for cap_name, nodes in cap_map.items():
            for node in nodes:
                simple_matches.append({
                    "capture_name": cap_name,
                    "text": serialize_node(node, code_bytes)["text"]
                })
    
    # Write the simple matches to a file (for debugging).
    debug_dir = "debug_output"
    os.makedirs(debug_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    raw_output_file: str = os.path.join(debug_dir, f"raw_captures_{timestamp}.json")
    with open(raw_output_file, "w", encoding="utf8") as f:
        json.dump(simple_matches, f, indent=2)
    print(f"DEBUG: Simple matches written to {raw_output_file}")
    
    # 6) Process each simple match using the Tree-sitter AST.
    # For each captured import statement, re-parse its text into a mini-tree and use helper functions.
    raw_imports: List[Dict[str, Any]] = []
    for sm in simple_matches:
        stmt_text: str = sm["text"]
        cap_name: str = sm["capture_name"]
        mini_tree = parser.parse(stmt_text.encode("utf8"))
        import_node = mini_tree.root_node
        if cap_name == "from_import_stmt":
            imp_info = parse_from_import_node(import_node, stmt_text.encode("utf8"))
            if imp_info:
                raw_imports.append(imp_info)
        elif cap_name == "plain_import_stmt":
            imp_info = parse_plain_import_node(import_node, stmt_text.encode("utf8"))
            if imp_info:
                raw_imports.append(imp_info)
        # Else: ignore any other captures.
    
    # 7) Mark internal imports by checking against INTERNAL_PREFIX.
    for imp in raw_imports:
        if imp["Source"]:
            if imp["Source"].startswith(INTERNAL_PREFIX):
                imp["ImportType"] = "internal"
        else:
            # For plain imports, check each imported name.
            for usage in imp["UsageName"]:
                if usage["original_name"].startswith(INTERNAL_PREFIX):
                    imp["ImportType"] = "internal"
                    break
    
    # 8) Merge from-imports with the same Source by combining their UsageName lists.
    merged_imports: Dict[str, Dict[str, Any]] = {}
    plain_imports: List[Dict[str, Any]] = []
    for imp in raw_imports:
        if imp["Source"]:
            if imp["Source"] in merged_imports:
                merged_imports[imp["Source"]]["UsageName"].extend(imp["UsageName"])
            else:
                merged_imports[imp["Source"]] = imp
        else:
            plain_imports.append(imp)
    unoplat_imports: List[Dict[str, Any]] = list(merged_imports.values()) + plain_imports
    
    # 9) Write the final UnoplatImport–like structure to a separate JSON output file.
    unoplat_output_file: str = os.path.join(debug_dir, f"unoplat_imports_{timestamp}.json")
    with open(unoplat_output_file, "w", encoding="utf8") as f:
        json.dump(unoplat_imports, f, indent=2)
    print(f"DEBUG: UnoplatImport data written to {unoplat_output_file}")
    
if __name__ == "__main__":
    test_import_query()