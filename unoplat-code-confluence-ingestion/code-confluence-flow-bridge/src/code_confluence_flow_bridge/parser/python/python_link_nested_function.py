# Standard Library
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_chapi_forge_function import UnoplatChapiForgeFunction
from src.code_confluence_flow_bridge.parser.tree_sitter.code_confluence_tree_sitter import CodeConfluenceTreeSitter

from typing import Dict, List, Optional, cast

# First Party
from loguru import logger

# Third Party
from tree_sitter import Language, Node, Parser, Tree


class PythonLinkNestedFunction:
    """
    Class for identifying nested functions in Python code and setting parent function names
    in UnoplatChapiForgeFunction objects.
    """

    def __init__(self, code_confluence_tree_sitter: CodeConfluenceTreeSitter) -> None:
        """
        Initialize the nested function identifier with Python Tree-sitter parser.
        
        Args:
            code_confluence_tree_sitter: Tree-sitter helper for Python parsing
        """
        self.parser: Parser = code_confluence_tree_sitter.get_parser()

    def process_nested_functions(self, functions: List[UnoplatChapiForgeFunction], file_content: str) -> None:
        """
        Process a list of functions to identify nested functions and set their parent function names.
        
        Args:
            functions: List of UnoplatChapiForgeFunction objects to process
            file_content: The content of the file containing the functions
        """
        if not functions or not file_content:
            return
        
        # Parse the file content with tree-sitter
        tree: Tree = self.parser.parse(bytes(file_content, "utf8"))
        
        # Create a map of function signatures to their UnoplatChapiForgeFunction objects
        function_map: Dict[str, UnoplatChapiForgeFunction] = {}
        for function in functions:
            if function.content:
                signature = self._extract_function_signature(function.content)
                if signature:
                    function_map[signature] = function
        
        # Find all function definitions in the file
        function_nodes: List[Node] = self._find_all_function_nodes(tree.root_node, file_content)
        
        # Process each function node to check for nesting
        for node in function_nodes:
            signature = self._get_node_signature(node)
            if not signature or signature not in function_map:
                continue
                
            # Check if this function is nested within another function
            parent_node = self._find_parent_function_node(node)
            if not parent_node:
                continue
                
            # Get the parent function's signature
            parent_signature = self._get_node_signature(parent_node)
            if not parent_signature or parent_signature not in function_map:
                continue
                
            # Set the parent function name in the UnoplatChapiForgeFunction object
            current_function = function_map[signature]
            parent_function = function_map[parent_signature]
            
            logger.debug(f"Found nested function: {current_function.name} inside {parent_function.name}")
            
            # Set the parent function's qualified name
            if parent_function.qualified_name:
                current_function.parent_function_name = parent_function.qualified_name
        
    def _extract_function_signature(self, function_content: str) -> Optional[str]:
        """
        Extract the function signature (line starting with 'def ') from the function content.
        This properly handles function annotations/decorators.
        
        Args:
            function_content: The function content
            
        Returns:
            The function signature if found, None otherwise
        """
        if not function_content:
            return None
            
        lines = function_content.strip().split('\n')
        if not lines:
            return None
        
        # Find the line that starts with 'def ' (the actual function definition)
        for line in lines:
            line = line.strip()
            if line.startswith('def '):
                return line
                
        # If no line starts with 'def ', fall back to the first line
        return lines[0].strip()

    def _find_all_function_nodes(self, root_node: Node, file_content: str) -> List[Node]:
        """
        Find all function definition nodes in the tree.
        
        Args:
            root_node: The root node of the tree
            file_content: The content of the file
            
        Returns:
            A list of function definition nodes
        """
        function_nodes: List[Node] = []
        
        # Query to find all function definitions
        query_string = """
        (function_definition) @function
        """
        
        language = cast(Language, self.parser.language)
        query = language.query(query_string)  # type: ignore
        
        # Following the pattern used in python_extract_function_calls.py
        matches = query.matches(root_node)
        
        for _, capture_dict in matches:
            if "function" in capture_dict:
                # Get the function node
                function_node = capture_dict["function"][0]
                function_nodes.append(function_node)
        
        return function_nodes

    def _get_node_signature(self, function_node: Node) -> Optional[str]:
        """
        Get the signature line (starting with 'def ') of a function node.
        
        Args:
            function_node: The function node
            
        Returns:
            The function signature if extractable, None otherwise
        """
        node_text = function_node.text
        if isinstance(node_text, bytes):
            content = node_text.decode("utf8")
            lines = content.strip().split("\n")
            
            # Find the line that starts with 'def '
            for line in lines:
                line = line.strip()
                if line.startswith('def '):
                    return line
                    
            # If no line starts with 'def ', fall back to the first line
            if lines:
                return lines[0].strip()
                
        return None
    
    def _find_parent_function_node(self, function_node: Node) -> Optional[Node]:
        """
        Find the parent function node of a nested function.
        
        Args:
            function_node: The tree-sitter node for the function
            
        Returns:
            The parent function node, or None if the function is not nested
        """
        current_node = function_node.parent
        
        while current_node:
            if current_node.type == "function_definition":
                return current_node
            current_node = current_node.parent
            
        return None 