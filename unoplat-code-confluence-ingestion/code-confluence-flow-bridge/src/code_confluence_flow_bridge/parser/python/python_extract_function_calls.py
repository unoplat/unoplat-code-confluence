# Standard Library
# First Party

import json
from src.code_confluence_flow_bridge.models.chapi.chapi_node import ChapiNode
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_import import UnoplatImport
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_import_type import ImportType
from src.code_confluence_flow_bridge.parser.tree_sitter.code_confluence_tree_sitter import CodeConfluenceTreeSitter

from typing import Dict, List, Tuple

# Third Party
from tree_sitter import Node, Parser, Tree


class PythonExtractFunctionCalls:
    def __init__(self, code_confluence_tree_sitter: CodeConfluenceTreeSitter) -> None:
        """Initialize the function call extractor with Python Tree-sitter parser."""
        self.parser: Parser = code_confluence_tree_sitter.get_parser()

    def extract_function_calls(self, file_path_nodes:dict[str, List[ChapiNode]], imports: List[UnoplatImport],entire_code: str) -> dict[str, List[ChapiNode]]:
        """
        Extract function calls from the given function content using Tree-sitter.
        
        Args:
            function_content: The content of the function to analyze
            
        Returns:
            List of ChapiFunctionCall objects representing the function calls found
        """
        # Parse the content
        for file_path, nodes in file_path_nodes.items():
            if len(nodes) == 1 and (nodes[0].type is None or not nodes[0].type or nodes[0].type == "" or nodes[0].type != "CLASS"):
               self.handle_procedural_code(nodes[0],imports,entire_code) 
        
        return None #type: ignore

    def handle_procedural_code(self,node: ChapiNode,imports: List[UnoplatImport],entire_code: str) -> None:
        """
        Handle procedural code by extracting function calls.
        
        Args:
            node: The ChapiNode representing the procedural code
            imports: List of UnoplatImport objects.
            entire_code: The entire code of the file
        """
        pass
            # Iterate through each function call within the function
                

    
    def extract_instantiations_ts(self, file_source: str) -> Dict[str, str]:
        """
        Extracts object instantiations from the entire file content using a tree-sitter query.
        Returns a dictionary mapping variable names to the class name being instantiated.
        Only considers calls where the function name follows PascalCase convention (likely a class).
        """
        tree: Tree = self.parser.parse(bytes(file_source, "utf8"))
        
        # Print the AST representation for debugging
        print(tree.root_node)
        
        query_source = r"""
        ; 1. Simple assignment instantiation
        (assignment
          left: (identifier) @variable
          right: (call
                  function: (identifier) @class_name)
        )

        ; 2. Type annotated assignment instantiation
        (assignment
          left: (identifier) @variable
          type: (type)
          right: (call
                  function: (identifier) @class_name)
        )

        ; 3. Attribute assignment instantiation
        (assignment
          left: (attribute
                 object: (identifier) @object
                 attribute: (identifier) @attribute)
          right: (call
                  function: (identifier) @attr_class_name)
        )

        ; 4. Tuple unpacking assignment instantiation
        (assignment
          left: (pattern_list) @pattern_list
          right: (expression_list) @expr_list
        )
        """
        
        query = self.parser.language.query(query_source)  # type: ignore
        inst_map: Dict[str, str] = {}
        matches = query.matches(tree.root_node)
        
        for _pattern_index, capture_dict in matches:
            # Handle standard assignment pattern (patterns 1 and 2)
            if "variable" in capture_dict and "class_name" in capture_dict:
                var_node = capture_dict["variable"][0]
                class_node = capture_dict["class_name"][0]
                variable = file_source[var_node.start_byte:var_node.end_byte]
                class_name = file_source[class_node.start_byte:class_node.end_byte]
                
                # Only include if the class name starts with an uppercase letter (likely a class)
                if class_name and class_name[0].isupper():
                    inst_map[variable] = class_name
            
            # Handle attribute assignment (pattern 3)
            elif "object" in capture_dict and "attribute" in capture_dict and "attr_class_name" in capture_dict:
                obj_node = capture_dict["object"][0]
                attr_node = capture_dict["attribute"][0]
                class_node = capture_dict["attr_class_name"][0]
                
                obj_name = file_source[obj_node.start_byte:obj_node.end_byte]
                attr_name = file_source[attr_node.start_byte:attr_node.end_byte]
                class_name = file_source[class_node.start_byte:class_node.end_byte]
                
                # Only include if the class name starts with an uppercase letter (likely a class)
                if class_name and class_name[0].isupper():
                    inst_map[f"{obj_name}.{attr_name}"] = class_name
            
            # Handle tuple unpacking pattern (pattern 4)
            elif "pattern_list" in capture_dict and "expr_list" in capture_dict:
                pattern_list_node = capture_dict["pattern_list"][0]
                expr_list_node = capture_dict["expr_list"][0]
                
                # Extract variable identifiers in order
                variables: List[str] = []
                for child in pattern_list_node.children:
                    if child.type == "identifier":
                        variables.append(file_source[child.start_byte:child.end_byte])
                
                # Extract class identifiers in order, only considering those starting with uppercase
                class_names: List[str] = []
                for child in expr_list_node.children:
                    if child.type == "call":
                        function_node = child.child_by_field_name("function")
                        if function_node and function_node.type == "identifier":
                            class_name = file_source[function_node.start_byte:function_node.end_byte]
                            # Only include if it starts with an uppercase letter (likely a class)
                            if class_name and class_name[0].isupper():
                                class_names.append(class_name)
                
                # Match variables with class names by position
                for i in range(min(len(variables), len(class_names))):
                    inst_map[variables[i]] = class_names[i]
        
        return inst_map
    
      
    def _build_import_map(self, imports: List[UnoplatImport]) -> Dict[str, Tuple[str, str]]:
        """
        Builds a map of local names to their source module and original name for specific imports.

        Args:
            imports: List of UnoplatImport objects.

        Returns:
            Dictionary mapping local names to (module_path, original_name).
        """
        import_map: dict[str, tuple[str, str]] = {}
        for imp in imports:
            if imp.import_type == ImportType.INTERNAL and imp.usage_names:
                for name in imp.usage_names:
                    local_name = name.alias if name.alias else name.original_name
                    if local_name and name.original_name:
                        import_map[local_name] = (imp.source, name.original_name) # type: ignore
        return import_map