from typing import Dict, List, Optional, Tuple
from tree_sitter import Node, TreeCursor
from unoplat_code_confluence.parser.confluence_tree_sitter.code_confluence_tree_sitter import CodeConfluenceTreeSitter
from unoplat_code_confluence.data_models.chapi.chapi_class_global_fieldmodel import ClassGlobalFieldModel
from unoplat_code_confluence.data_models.chapi.class_global_field_metadata import ClassGlobalFieldMetadata
from unoplat_code_confluence.data_models.chapi.chapi_annotation import ChapiAnnotation, ChapiAnnotationKeyVal
from loguru import logger
import json
import os
from datetime import datetime
from unoplat_code_confluence.data_models.chapi.class_global_field_scope import ClassGlobalFieldScope
# THe class is responsible for parsing global ,class and local function variables
class NodeVariablesParser:
    
    def __init__(self, code_confluence_tree_sitter: CodeConfluenceTreeSitter):
        self.parser = code_confluence_tree_sitter.get_parser()
        # Key: (scope_str, var_name), Value: ClassGlobalFieldModel
        self.variables_dict: Dict[Tuple[str, str], ClassGlobalFieldModel] = {}
    
    def parse_variables(self, content: str) -> List[ClassGlobalFieldModel]:
        """Parse variables from Python content."""
        tree = self.parser.parse(bytes(content, "utf8"))
        
        # Debug: Save AST to JSON (optional)
        debug_dir = "debug_output"
        os.makedirs(debug_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        def node_to_dict(node):
            result = {
                "type": node.type,
                "text": node.text.decode('utf8') if node.text else None,
                "start_point": node.start_point,
                "end_point": node.end_point,
            }
            if len(node.children) > 0:
                result["children"] = [node_to_dict(child) for child in node.children]
            return result
            
        ast_dict = node_to_dict(tree.root_node)
        with open(f"{debug_dir}/tree_structure_{timestamp}.json", "w") as f:
            json.dump(ast_dict, f, indent=2)
        
        self.variables_dict = {}
        cursor = tree.walk()
        self.__traverse_tree(cursor, current_scope="")
        return list(self.variables_dict.values())
    
    def __traverse_tree(self, cursor: TreeCursor, current_scope: str) -> None:
        """Traverse AST to find variables and their annotations."""
        reached_root = False
        current_decorators: List[ChapiAnnotation] = []
        processed_decorators: set[tuple[int, int]] = set()
        inside_function = False

        while not reached_root:
            node = cursor.node

            if node.type == "function_definition":
                inside_function = True
                
            elif node.type == "class_definition":
                class_name = node.children[1].text.decode('utf8')
                current_scope = class_name
                current_decorators = []
                processed_decorators.clear()
                
            elif node.type == "ERROR":
                if (node.children and 
                    node.children[0].type == "decorator" and 
                    not self.__is_class_decorator(node)):
                    for child in node.children:
                        if child.type == "decorator":
                            pos = (child.start_point[0], child.start_point[1])
                            if pos not in processed_decorators:
                                annotation = self.__get_annotation(child)
                                if annotation:
                                    current_decorators.append(annotation)
                                    processed_decorators.add(pos)
                            
            elif node.type == "decorator":
                if not self.__is_class_decorator(node):
                    pos = (node.start_point[0], node.start_point[1])
                    if pos not in processed_decorators:
                        annotation = self.__get_annotation(node)
                        if annotation:
                            current_decorators.append(annotation)
                            processed_decorators.add(pos)
                    
            elif node.type == "expression_statement":
                if not inside_function and node.children and node.children[0].type == "assignment":
                    assignment_node = node.children[0]
                    self.__process_assignment(assignment_node, current_decorators, current_scope)
                    current_decorators = []
                    processed_decorators.clear()

            if cursor.goto_first_child():
                continue
                
            if cursor.goto_next_sibling():
                continue
                
            retracing = True
            while retracing:
                if not cursor.goto_parent():
                    retracing = False
                    reached_root = True
                elif cursor.goto_next_sibling():
                    retracing = False
                    if node.type == "function_definition":
                        inside_function = False
                    elif node.type == "class_definition":
                        current_scope = ""

    def __is_class_decorator(self, node: Node) -> bool:
        """Check if decorator is for a class definition."""
        next_sibling = node.next_sibling
        while next_sibling:
            if next_sibling.type == "class_definition":
                return True
            if next_sibling.type not in ["NEWLINE", "ERROR", "decorator"]:
                return False
            next_sibling = next_sibling.next_sibling
        return False

    def __get_annotation(self, node: Node) -> Optional[ChapiAnnotation]:
        """Extract annotation from decorator node."""
        # Skip @ symbol
        for child in node.children:
            if child.type == "identifier":
                # Simple decorator without arguments
                return ChapiAnnotation(Name=child.text.decode('utf8'))
            elif child.type == "call":
                # Decorator with arguments
                func_name = None
                for call_child in child.children:
                    if call_child.type == "identifier":
                        func_name = call_child.text.decode('utf8')
                        break
                
                if func_name:
                    key_values = self.__extract_annotation_arguments(child)
                    return ChapiAnnotation(
                        Name=func_name,
                        KeyValues=key_values if key_values else None
                    )
        return None

    def __extract_annotation_arguments(self, call_node: Node) -> List[ChapiAnnotationKeyVal]:
        """Extract arguments from a decorator call node.
        
        Examples:
            @decorator(1, x=2)           -> [("0", "1"), ("x", "2")]
            @decorator("str", y="test")  -> [("0", "\"str\""), ("y", "\"test\"")]
            @decorator(key="value")      -> [("key", "\"value\"")]
            @decorator(1, 2, 3)          -> [("0", "1"), ("1", "2"), ("2", "3")]
        """
        key_values: List[ChapiAnnotationKeyVal] = []
        
        # Find argument_list node
        for child in call_node.children:
            if child.type == "argument_list":
                pos_arg_index = 0
                
                # Process each argument
                for arg in child.children:
                    if arg.type == "keyword_argument":
                        # Handle key=value style arguments
                        for i, kw_child in enumerate(arg.children):
                            if kw_child.type == "=":
                                # Get key (everything before =)
                                key = arg.children[i-1].text.decode('utf8')
                                # Get value (everything after =)
                                value = arg.children[i+1].text.decode('utf8')
                                key_values.append(ChapiAnnotationKeyVal(
                                    Key=key,
                                    Value=value
                                ))
                                break
                    elif arg.type not in ["(", ")", ","]:
                        # Handle positional arguments
                        key_values.append(ChapiAnnotationKeyVal(
                            Key=str(pos_arg_index),
                            Value=arg.text.decode('utf8')
                        ))
                        pos_arg_index += 1
                        
        return key_values

    def __process_assignment(self, node: Node, annotations: List[ChapiAnnotation], current_scope: str) -> None:
        var_names = self.__get_variable_name(node)
        if not var_names:
            return

        type_hint = self.__get_type_hint(node)
        values = self.__get_value(node)

        # Determine scope from current_scope
        
        if current_scope:
            scope_enum = ClassGlobalFieldScope.CLASS
        else:
            scope_enum = ClassGlobalFieldScope.GLOBAL

        for i, var_name in enumerate(var_names):
            value = values[i] if i < len(values) else None
            
            # Create metadata for this assignment
            metadata = ClassGlobalFieldMetadata(
                Type=type_hint,
                DefaultValue=value,
                Annotations=annotations if annotations else None
            )

            var_key = (current_scope, var_name)
            if var_key in self.variables_dict:
                # Add metadata to existing variable
                self.variables_dict[var_key].field_metadata.append(metadata)
            else:
                # Create new variable with initial metadata
                self.variables_dict[var_key] = ClassGlobalFieldModel(
                    Scope=scope_enum.value,  # Assign the enum's value as a string for serialization
                    TypeKey=var_name,
                    FieldMetadata=[metadata]
                )
    
    def __get_variable_name(self, node: Node) -> List[str]:
        """Extract variable name(s) from assignment node."""
        names = []
        for child in node.children:
            if child.type == "identifier":
                name = child.text.decode('utf8')
                if name:
                    names.append(name)
            elif child.type == "pattern_list":
                # Handle tuple unpacking (x, y = ...)
                for pattern_child in child.children:
                    if pattern_child.type == "identifier":
                        name = pattern_child.text.decode('utf8')
                        if name:
                            names.append(name)
        return names
    
    def __get_type_hint(self, node: Node) -> Optional[str]:
        """Extract type hint if present."""
        for child in node.children:
            if child.type == "type":
                return child.text.decode('utf8').strip(": ")
        return None
    
    def __get_value(self, node: Node) -> List[str]:
        """Extract value(s) from assignment node."""
        values = []
        found_equal = False
        for child in node.children:
            if child.type in {"=", ":="}:
                found_equal = True
                continue
            if found_equal:
                # After '=' or ':=', we handle tuple or single values
                if child.type == "expression_list":
                    # tuple values
                    for expr_child in child.children:
                        if expr_child.type not in [",", "(", ")"]:
                            values.append(expr_child.text.decode('utf8'))
                elif child.type not in [",", "(", ")", "NEWLINE"]:
                    # single value or complex expression
                    values.append(child.text.decode('utf8'))
        return values