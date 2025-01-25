# Standard Library
from typing import Dict, List, Optional

# Third Party
from loguru import logger
from tree_sitter import Node, TreeCursor

# First Party
from src.code_confluence_flow_bridge.models.chapi.chapi_annotation import ChapiAnnotation, ChapiAnnotationKeyVal
from src.code_confluence_flow_bridge.models.chapi.chapi_class_global_fieldmodel import ClassGlobalFieldModel
from src.code_confluence_flow_bridge.models.chapi.chapi_function import ChapiFunction
from src.code_confluence_flow_bridge.models.chapi.chapi_position import Position
from src.code_confluence_flow_bridge.parser.tree_sitter.code_confluence_tree_sitter import CodeConfluenceTreeSitter


# The class is responsible for parsing global and class variables that is classvar and instance variables defined in a class but outside of any functions..
class NodeVariablesParser:
    def __init__(self, code_confluence_tree_sitter: CodeConfluenceTreeSitter):
        self.parser = code_confluence_tree_sitter.get_parser()
        # Change to simple string key since we no longer track scope
        self.variables_dict: Dict[str, ClassGlobalFieldModel] = {}

    # Here the content refers to content of a file where it can contain multiple classes/procedural functions and variables
    def parse_global_variables(self, content_of_file: str) -> List[ClassGlobalFieldModel]:
        """Parse variables from Python content."""
        tree = self.parser.parse(bytes(content_of_file, "utf8"))

        self.variables_dict = {}
        cursor = tree.walk()
        # this is for class and global variables
        self.__traverse_global_variables(cursor)

        return list(self.variables_dict.values())

    # It should parse class variables and instance variables defined in a class but outside of any functions based on content of class
    # and then should use list of functions to check if there are any instance variables or class run variables defined in the functions and add them. Make sure there is no duplication.
    def parse_class_variables(self, content_of_class_code: str, list_of_functions: List[ChapiFunction]) -> List[ClassGlobalFieldModel]:
        """Parse class-level and instance variables from class content.

        First parses variables defined at class level (outside functions),
        then processes function contents for instance/runtime variables.

        Args:
            content_of_class_code: Content of just the class definition
            list_of_functions: List of functions to check for instance/runtime variables

        Returns:
            List[ClassGlobalFieldModel]: All unique class variables including:
                - ClassVar variables
                - Instance variables defined at class level
                - Instance variables from methods (self.x)
                - Runtime class variables from @classmethod (cls.x)
        """
        # Phase 1: Parse class-level variables
        tree = self.parser.parse(bytes(content_of_class_code, "utf8"))
        self.variables_dict = {}  # Reset for new parsing
        cursor = tree.walk()
        logger.debug("Before class variables: {}", len(self.variables_dict))
        self.__traverse_class_variables(cursor)
        logger.debug("After class variables: {}", len(self.variables_dict))

        # Track seen variables to avoid duplicates
        seen_variables = {v.class_field_name for v in self.variables_dict.values()}
        logger.debug("Seen variables: {}", seen_variables)

        # Phase 2: Parse variables from function contents
        for function in list_of_functions:
            if not function.content:
                continue

            logger.debug("Processing function: {}", function.name)
            logger.debug("Function content: {}", function.content)

            func_tree = self.parser.parse(bytes(function.content, "utf8"))
            func_cursor = func_tree.walk()
            self.__traverse_function_variables(cursor=func_cursor, seen_variables=seen_variables)
            logger.debug("Variables after function: {}", len(self.variables_dict))

        return list(self.variables_dict.values())

    def __traverse_global_variables(self, cursor: TreeCursor) -> None:
        """Traverse AST to find only global variables (outside any class/function)."""
        inside_function = False
        inside_class = False
        current_decorators: List[ChapiAnnotation] = []
        processed_decorators: set[tuple[int, int]] = set()

        # Move cursor to first child if exists
        should_traverse_children = cursor.goto_first_child()

        while should_traverse_children:
            node = cursor.node

            # Track scope
            if node.type == "function_definition":
                inside_function = True
            elif node.type == "class_definition":
                inside_class = True

            # Process global variables
            if node.type == "expression_statement":
                if not inside_function and not inside_class and node.children and node.children[0].type == "assignment":
                    assignment_node = node.children[0]
                    self.__process_assignment(assignment_node, current_decorators)
                    current_decorators = []
                    processed_decorators.clear()

            # Try to move to next sibling
            if cursor.goto_next_sibling():
                # If we moved to sibling, check if we're exiting a scope
                if inside_function and node.type == "function_definition":
                    inside_function = False
                elif inside_class and node.type == "class_definition":
                    inside_class = False
                continue

            # No more siblings, go back to parent
            if not cursor.goto_parent():
                # We've reached the root, stop traversal
                break

            # Reset scope flags when exiting their definitions
            if inside_function and node.type == "function_definition":
                inside_function = False
            elif inside_class and node.type == "class_definition":
                inside_class = False

    def __traverse_class_variables(self, cursor: TreeCursor) -> None:
        """Parse variables defined at class level (outside any function)."""
        inside_function = False
        current_decorators: List[ChapiAnnotation] = []

        # Move down the tree until we find a class_definition node
        while cursor.node.type != "class_definition":
            if not cursor.goto_first_child():
                return

        # Enter class_definition internals
        if not cursor.goto_first_child():
            return

        # Skip until we hit 'block' (class body)
        while cursor.node.type != "block":
            if not cursor.goto_next_sibling():
                return

        # Enter the block
        if not cursor.goto_first_child():
            return

        while True:
            # Update node at the start of each iteration
            node = cursor.node

            # If we were inside a function previously, check if we've left it
            if inside_function and node.type != "function_definition":
                # Moved on from function definition node, reset inside_function
                inside_function = False

            if node.type == "function_definition":
                inside_function = True

            elif node.type == "decorator" and not inside_function:
                annotation = self.__get_annotation(node)
                if annotation:
                    current_decorators.append(annotation)

            elif not inside_function and node.type == "expression_statement":
                if node.children and node.children[0].type == "assignment":
                    self.__process_assignment(node.children[0], current_decorators)
                    current_decorators = []

            # Move to next sibling if possible
            if cursor.goto_next_sibling():
                # Don't update node here, rely on next iteration's node = cursor.node
                continue

            break  # No more siblings

    def __traverse_function_variables(self, cursor: TreeCursor, seen_variables: set[str]) -> None:
        """Parse variables from function body."""

        # Step 1: Navigate to function_definition or decorated_definition
        while cursor.node.type not in ["function_definition", "decorated_definition"]:
            if not cursor.goto_first_child():
                logger.error("Failed to find function/decorated definition")
                return

        # If decorated, move to the function_definition within
        if cursor.node.type == "decorated_definition":
            if not cursor.goto_first_child():
                return
            while cursor.node.type != "function_definition":
                if not cursor.goto_next_sibling():
                    return

        # Step 2: Move down into the function_definition's children
        if not cursor.goto_first_child():
            logger.error("Failed to enter function internals")
            return

        # Step 3: Iterate siblings until we find the block node
        # The block node is the actual function body.
        while cursor.node.type != "block":
            if not cursor.goto_next_sibling():
                logger.error("Failed to find block")
                return

        # Now cursor.node is 'block', enter it
        if not cursor.goto_first_child():
            logger.error("Failed to enter block contents")
            return

        # Step 4: We are now inside the function body. Iterate over statements.
        while True:
            node = cursor.node

            if node.type == "expression_statement" and node.children:
                first_child = node.children[0]
                if first_child.type == "assignment":
                    lhs = first_child.children[0] if first_child.children else None
                    if lhs and lhs.type == "attribute":
                        attr_text = lhs.text.decode("utf8")
                        # Check for instance/class variable assignments (self.x or cls.x)
                        if attr_text.startswith(("self.", "cls.")):
                            var_name = attr_text.split(".", 1)[1]
                            if var_name not in seen_variables:
                                seen_variables.add(var_name)
                                # Process the assignment as needed
                                self.__process_assignment(first_child, [])
                                # If needed, rename the variable in self.variables_dict here

            if not cursor.goto_next_sibling():
                break  # No more siblings in block

    def __get_annotation(self, node: Node) -> Optional[ChapiAnnotation]:
        """Extract annotation from decorator node."""
        # Skip @ symbol
        for child in node.children:
            if child.type == "identifier":
                # Simple decorator without arguments
                return ChapiAnnotation(Name=child.text.decode("utf8"))
            elif child.type == "call":
                # Decorator with arguments
                func_name = None
                for call_child in child.children:
                    if call_child.type == "identifier":
                        func_name = call_child.text.decode("utf8")
                        break

                if func_name:
                    key_values = self.__extract_annotation_arguments(child)
                    return ChapiAnnotation(Name=func_name, KeyValues=key_values if key_values else None)
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
                                key = arg.children[i - 1].text.decode("utf8")
                                # Get value (everything after =)
                                value = arg.children[i + 1].text.decode("utf8")
                                key_values.append(ChapiAnnotationKeyVal(Key=key, Value=value))
                                break
                    elif arg.type not in ["(", ")", ","]:
                        # Handle positional arguments
                        key_values.append(ChapiAnnotationKeyVal(Key=str(pos_arg_index), Value=arg.text.decode("utf8")))
                        pos_arg_index += 1

        return key_values

    def __process_assignment(self, node: Node, decorators: List[ChapiAnnotation]) -> None:
        """Process an assignment node to extract variable information.
        Only captures variables on their first occurrence."""
        if not node.children:
            return

        lhs = node.children[0]  # Left-hand side of assignment

        # Get variable names based on node type
        var_names = []
        if lhs.type == "identifier":
            var_names.append(lhs.text.decode("utf8"))
            start_point = lhs.start_point
            end_point = lhs.end_point
        elif lhs.type == "pattern_list":
            # Handle tuple unpacking (x, y = ...)
            for pattern_child in lhs.children:
                if pattern_child.type == "identifier":
                    var_names.append(pattern_child.text.decode("utf8"))
                    # For tuple unpacking, use each identifier's position
                    start_point = pattern_child.start_point
                    end_point = pattern_child.end_point
        elif lhs.type == "attribute":
            # Handle self.x or cls.x attributes
            if len(lhs.children) >= 3:  # Need at least 3 parts: self/cls, ., var_name
                prefix = lhs.children[0].text.decode("utf8")
                if prefix in ("self", "cls"):
                    var_name_node = lhs.children[2]
                    var_names.append(var_name_node.text.decode("utf8"))
                    # For attributes, use the variable part's position
                    start_point = var_name_node.start_point
                    end_point = var_name_node.end_point

        if not var_names:
            return

        # Get type hint if present
        type_hint = None
        values = []

        # Look for type hint and values
        for i, child in enumerate(node.children):
            if child.type == ":" and i + 1 < len(node.children):
                type_node = node.children[i + 1]
                type_hint = type_node.text.decode("utf8")
            elif child.type == "=" and i + 1 < len(node.children):
                value_node = node.children[i + 1]
                if value_node.type == "expression_list":
                    # Handle tuple values (1, 2)
                    for value_child in value_node.children:
                        if value_child.type not in [",", "(", ")"]:
                            values.append(value_child.text.decode("utf8").strip())
                else:
                    # Single value - normalize dictionary/object literals
                    value = value_node.text.decode("utf8")
                    if value_node.type == "dictionary":
                        # Remove newlines and extra whitespace
                        value = "".join(value.split())
                    values.append(value)

        # Create variables for each name-value pair, but only if not already captured
        for i, var_name in enumerate(var_names):
            # Skip if variable already exists
            if var_name in self.variables_dict:
                continue

            value = values[i] if i < len(values) else None

            # Create position object
            position = Position(
                StartLine=start_point[0],  # Convert to 1-based line numbers
                StartLinePosition=start_point[1],
                StopLine=end_point[0],
                StopLinePosition=end_point[1],
            )

            var = ClassGlobalFieldModel(
                TypeValue=var_name,
                TypeType=type_hint,
                DefaultValue=value,
                Annotations=decorators if decorators else None,
                Position=position,  # Add position information
            )
            self.variables_dict[var_name] = var
