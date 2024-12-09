from typing import List, Dict, Optional

from unoplat_code_confluence.data_models.chapi.chapi_function import ChapiFunction
from unoplat_code_confluence.data_models.chapi.chapi_functioncall import ChapiFunctionCall
from unoplat_code_confluence.data_models.chapi.chapi_parameter import ChapiParameter
from unoplat_code_confluence.data_models.chapi.chapi_position import Position
from loguru import logger
from unoplat_code_confluence.parser.tree_sitter.code_confluence_tree_sitter import CodeConfluenceTreeSitter
from tree_sitter import Node, TreeCursor
from unoplat_code_confluence.data_models.chapi.chapi_function_field_model import ChapiFunctionFieldModel


class FunctionMetadataParser:
    def __init__(self, code_confluence_tree_sitter: CodeConfluenceTreeSitter):
        # Initialize Tree-sitter parser
        self.parser = code_confluence_tree_sitter.get_parser()
    
    def get_function_metadata(self, function_node: ChapiFunction) -> ChapiFunction:
        """Extract metadata from function content and update the function node.
        
        Args:
            function_node: ChapiFunction with content to parse
            
        Returns:
            The same function node, modified in place with:
            - function_calls: List of function calls found
            - local_variables: List of local variables with their latest values
            - return_type: Function return type if specified
        """
        tree = self.parser.parse(bytes(function_node.content, "utf8")) #type: ignore
        
        # Track function calls (existing functionality)
        function_calls: List[ChapiFunctionCall] = []
        
        # Track local variables with latest values
        local_vars: Dict[str, ChapiFunctionFieldModel] = {}
        
        cursor = tree.walk()
        self.__traverse_tree(cursor, function_calls, local_vars)
        
        # Update function node in place
        function_node.function_calls = function_calls
        function_node.local_variables = list(local_vars.values())
        
        # Extract return type if present
        function_node.return_type = self.__get_return_type(tree.root_node)
        
        return function_node
    
    def __get_return_type(self, root_node: Node) -> Optional[str]:
        """Extract return type annotation from function definition."""
        def find_function_def(node: Node) -> Optional[Node]:
            """Find function definition node, even if decorated."""
            if node.type == "function_definition":
                return node
            if node.type == "decorated_definition":
                for child in node.children:
                    if child.type == "function_definition":
                        return child
            return None

        for child in root_node.children:
            if func_node := find_function_def(child):
                for def_child in func_node.children:
                    if def_child.type == "type":
                        return def_child.text.decode('utf8').strip(" ->:")
        return None
    
    def __extract_pattern_names(self, pattern_node: Node) -> List[str]:
        """Extract variable names from pattern using stack."""
        names = []
        stack = [pattern_node]
        
        while stack:
            current = stack.pop()
            for child in reversed(current.children):  # Reverse to maintain order
                if child.type == "identifier":
                    names.append(child.text.decode('utf8'))
                elif child.type in ["pattern_list", "tuple_pattern"]:
                    stack.append(child)
        return names
    
    def __extract_values(self, value_node: Node) -> List[str]:
        """Extract values from tuple/list structure using stack."""
        values = []
        stack = [value_node]
        
        while stack:
            current = stack.pop()
            for child in reversed(current.children):  # Reverse to maintain order
                if child.type in ["integer", "string", "float", "true", "false"]:
                    values.append(child.text.decode('utf8'))
                elif child.type in ["tuple", "list"]:
                    stack.append(child)
        return values
    
    def __clean_function_call(self, value: str) -> str:
        """Clean function call value to get just the function name.
        
        Args:
            value: Function call string (e.g., "inner()", "obj.method(arg)")
            
        Returns:
            str: Cleaned function name (e.g., "inner", "obj.method")
        """
        if '(' in value and value.endswith(')'):
            # Extract everything before the parentheses
            return value.split('(')[0]
        return value
    
    def __process_local_variable(self, node: Node, local_vars: Dict[str, ChapiFunctionFieldModel]) -> None:
        """Process a local variable assignment."""
        # Handle pattern-based assignment
        lhs_node = node.children[0] if node.children else None
        if lhs_node and lhs_node.type in ["pattern_list", "tuple_pattern"]:
            # Get all variable names using stack
            var_names = self.__extract_pattern_names(lhs_node)
            
            # Get all values using stack
            values = []
            for child in node.children:
                if child.type in ["expression_list", "tuple", "list"]:
                    values.extend(self.__extract_values(child))

            # Create variables
            for i, var_name in enumerate(var_names):
                if var_name not in local_vars:
                    val = values[i] if i < len(values) else None
                    local_vars[var_name] = ChapiFunctionFieldModel(
                        NameOfField=var_name,
                        TypeOfField=None,
                        ValueOfField=val
                    )
            return

        # Handle single variable assignment
        var_name: Optional[str] = None
        type_hint: Optional[str] = None
        value: Optional[str] = None

        for child in node.children:
            if child.type == "identifier":
                var_name = child.text.decode('utf8')
            elif child.type == "type":
                type_hint = child.text.decode('utf8').strip(": ")
            elif child.type in {"=", ":="} and child.next_sibling:
                value = child.next_sibling.text.decode('utf8')
                if child.next_sibling.type == "call":
                    # Clean function call value
                    value = self.__clean_function_call(value)

        if var_name and var_name not in local_vars:
            local_vars[var_name] = ChapiFunctionFieldModel(
                NameOfField=var_name,
                TypeOfField=type_hint,
                ValueOfField=value
            )

    def extract_variables_iter(self, pattern_node: Node) -> List[str]:
        """Iteratively extract variable names from a pattern_list or tuple_pattern without recursion."""
        vars_found = []
        stack = [pattern_node]

        while stack:
            current = stack.pop()
            if current.type in ["pattern_list", "tuple_pattern"]:
                # Check children for identifiers or further patterns
                for child in current.children:
                    if child.type == "identifier":
                        vars_found.append(child.text.decode('utf8'))
                    elif child.type in ["pattern_list", "tuple_pattern"]:
                        stack.append(child)
        return vars_found
     
     
    
    def __extract_call_parameters(self,call_node) -> List[ChapiParameter]:
        """
        Extract parameters from a function call node, handling both positional and keyword arguments.
        
        Args:
            call_node (Node): Tree-sitter Node object representing a function call
                            The node should be of type "call"
        
        Returns:
            List[ChapiParameter]: List of parameters found in the function call
                                Each parameter contains:
                                - type_value: The value of the argument
                                - type_type: The parameter name (for keyword arguments)
        
        Example:
            For a call like: func(1, x=2)
            Returns: [
                ChapiParameter(type_value="1"),
                ChapiParameter(type_value="2", type_type="x")
            ]
        """
        parameters = []
        
        # Find the arguments node
        for child in call_node.children:
            if child.type == "argument_list":
                logger.debug("Processing argument list: {}", child.text.decode('utf8'))
                for arg in child.children:
                    if arg.type not in ["(", ")", ","]:
                        arg_text = arg.text.decode('utf8')
                        logger.debug("Processing argument: {}", arg_text)
                        
                        # Handle keyword arguments (e.g., "key=value")
                        if "=" in arg_text and arg.type == "keyword_argument":
                            key, value = arg_text.split("=", 1)
                            param = ChapiParameter(
                                TypeValue=value.strip(),
                                TypeType=key.strip()  # Using TypeType to store the parameter name
                            )
                        else:
                            # Handle positional arguments
                            param = ChapiParameter(
                                TypeValue=arg_text
                            )
                        parameters.append(param)
                        logger.debug("Found argument: value={}, type={}", param.type_value, param.type_type)
        
        return parameters
    
    
    def __extract_function_call(self,node) -> ChapiFunctionCall:
        """
        Extract detailed information about a function call from its AST node.
        
        Args:
            node (Node): Tree-sitter Node object representing a function call
                        The node should be of type "call"
        
        Returns:
            ChapiFunctionCall: Object containing:
                - function_name: Name of the called function (part after last dot)
                - node_name: Object/module name (part before dot)
                - parameters: List of parameters passed to the function
                - position: Location of the function call in the source code
        
        Examples:
            For: print("Hello", end="\\n")
            Returns: ChapiFunctionCall(
                function_name="print",
                parameters=[...],
                position=Position(...)
            )
            
            For: self.do_something()
            Returns: ChapiFunctionCall(
                function_name="do_something",
                node_name="self",
                parameters=[],
                position=Position(...)
            )
        """
        logger.debug("\nProcessing call node at lines {}-{}", node.start_point[0]+1, node.end_point[0]+1)
        
        # Get full function name (first child of call node)
        full_name = node.children[0].text.decode('utf8')
        logger.debug("Full name: {}", full_name)
        
        # Split function name if it contains dots
        if "." in full_name:
            parts = full_name.split(".")
            node_name = ".".join(parts[:-1])  # Everything before the last dot
            func_name = parts[-1]  # Last part after the dot
            logger.debug("Split into node: {}, function: {}", node_name, func_name)
        else:
            node_name = None
            func_name = full_name
            logger.debug("Simple function: {}", func_name)
        
        # Get position
        position = Position(
            StartLine=node.start_point[0] + 1,
            StartLinePosition=node.start_point[1],
            StopLine=node.end_point[0] + 1,
            StopLinePosition=node.end_point[1]
        )
        
        # Get parameters
        parameters = self.__extract_call_parameters(node)
        
        return ChapiFunctionCall(
            FunctionName=func_name,
            NodeName=node_name,
            Parameters=parameters,
            Position=position
        )
    
    
    
    def __process_named_expression(self, node: Node, local_vars: Dict[str, ChapiFunctionFieldModel]) -> None:
        """Process walrus operator (:=) assignments."""
        var_name = None
        value = None
        
        # Extract components
        for child in node.children:
            if child.type == "identifier" and not var_name:
                var_name = child.text.decode('utf8')
            elif child.type == ":=":
                continue
            else:
                # Get the full expression text for the value
                value = node.text.decode('utf8')
                break
        
        # Create variable if not exists
        if var_name and var_name not in local_vars:
            local_vars[var_name] = ChapiFunctionFieldModel(
                NameOfField=var_name,
                TypeOfField=None,
                ValueOfField=value  # Store full expression
            )

    def __traverse_tree(self, cursor: TreeCursor, function_calls: List[ChapiFunctionCall], 
                       local_vars: Dict[str, ChapiFunctionFieldModel]) -> None:
        """Traverse AST to collect function calls and local variables."""
        reached_root = False
        function_depth = 0  # Track nested function depth
        
        while not reached_root:
            node = cursor.node
            
            # Track function scope
            if node.type == "function_definition":
                function_depth += 1
                if function_depth > 1:
                    # Skip only the inner function's content
                    cursor.goto_first_child()  # Move to function body
                    cursor.goto_next_sibling()  # Skip to next sibling after function
                    function_depth -= 1
                    continue
            
            # Only process variables if not inside inner function
            if function_depth <= 1:  # Allow main function but not inner ones
                if node.type == "call":
                    function_calls.append(self.__extract_function_call(node))
                elif node.type == "expression_statement":
                    if node.children and node.children[0].type == "assignment":
                        self.__process_local_variable(node.children[0], local_vars)
                elif node.type == "named_expression":
                    self.__process_named_expression(node, local_vars)
            
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
                        function_depth -= 1
    
        