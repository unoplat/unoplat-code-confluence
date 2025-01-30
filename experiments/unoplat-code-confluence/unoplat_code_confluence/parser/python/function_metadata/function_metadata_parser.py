# Standard Library
from typing import Dict, List, Optional, Tuple

# Third Party
from tree_sitter import Node, TreeCursor

# First Party
from unoplat_code_confluence.data_models.chapi.chapi_function import ChapiFunction
from unoplat_code_confluence.data_models.chapi.chapi_function_field_model import ChapiFunctionFieldModel
from unoplat_code_confluence.data_models.chapi.chapi_functioncall import ChapiFunctionCall
from unoplat_code_confluence.data_models.chapi.chapi_parameter import ChapiParameter
from unoplat_code_confluence.parser.tree_sitter.code_confluence_tree_sitter import CodeConfluenceTreeSitter


class FunctionMetadataParser:
    def __init__(self, tree_sitter: CodeConfluenceTreeSitter):
        self.parser = tree_sitter.get_parser()
        self.seen_variables: set[str] = set()  # Track variables we've seen

    def process_functions(self, functions: List[ChapiFunction]) -> List[ChapiFunction]:
        updated_functions = []
        for func in functions:
            func.local_variables = []
            updated_functions.append(self.__get_function_metadata(func))
        return updated_functions

    def __get_function_metadata(self, chapi_function: ChapiFunction) -> ChapiFunction:
        if not chapi_function.content:
            return chapi_function

        self.seen_variables.clear()

        tree = self.parser.parse(bytes(chapi_function.content, "utf8"))
        function_calls: List[ChapiFunctionCall] = []
        local_vars: Dict[str, ChapiFunctionFieldModel] = {}

        self.__traverse_tree(tree.walk(), function_calls, local_vars)

        # Extract return type if any
        return_type = self.__get_return_type(tree)
        if return_type:
            chapi_function.return_type = return_type

        chapi_function.local_variables = list(local_vars.values())
        chapi_function.function_calls = function_calls

        return chapi_function
    
    def __get_return_type(self, tree) -> Optional[str]:
    # Instead of manually navigating cursor, we can do a DFS using the tree's children.
        root = tree.root_node
        stack = [root]

        while stack:
            node = stack.pop()
            if node.type == "function_definition":
                # Check children for a 'type' node
                for child in node.children:
                    if child.type == "type":
                        return child.text.decode('utf8').strip(": ")
            # Push children into stack to continue traversal
            for child in reversed(node.children):
                stack.append(child)

        return None

    def __traverse_tree(self, cursor: TreeCursor, function_calls: List[ChapiFunctionCall], local_vars: Dict[str, ChapiFunctionFieldModel]) -> None:
        """
        Traverse the AST and:
        - Capture function calls
        - Capture local variables from 'assignment' and 'named_expression'
        """
        reached_root = False
        while not reached_root:
            node = cursor.node

            # Identify function calls
            if node.type == "call":
                call_obj = self.__extract_function_call(node)
                if call_obj:
                    function_calls.append(call_obj)

            # Identify local variables from assignment: `x = ...`
            if node.type == "expression_statement":
                for child in node.children:
                    if child.type == "assignment":
                        self.__process_local_variable(child, local_vars)
                    # Check if named_expressions appear top-level in an expression_statement
                    # Usually they might appear inside conditions or comprehensions, but let's also scan
                    # children for named_expression
                    self.__extract_named_expressions(child, local_vars)

            # Also extract named expressions outside `expression_statement`
            # because they can appear in conditions or comprehensions (e.g. in 'if', 'while')
            if node.type not in ["expression_statement", "function_definition"]:
                self.__extract_named_expressions(node, local_vars)

            if cursor.goto_first_child():
                continue
            if cursor.goto_next_sibling():
                continue
            # Retrace upwards
            retracing = True
            while retracing:
                if not cursor.goto_parent():
                    retracing = False
                    reached_root = True
                elif cursor.goto_next_sibling():
                    retracing = False

    def __extract_named_expressions(self, node: Node, local_vars: Dict[str, ChapiFunctionFieldModel]) -> None:
        """
        Recursively look for named_expression nodes inside given node to capture walrus-operator introduced variables.
        """
        for child in node.children:
            if child.type == "named_expression":
                # Named expression looks like: identifier := value
                self.__process_named_expression(child, local_vars)
            # Recurse
            self.__extract_named_expressions(child, local_vars)

    def __process_named_expression(self, node: Node, local_vars: Dict[str, ChapiFunctionFieldModel]) -> None:
        """
        Handle named_expressions like (matched := regex.match(...))
        The AST: named_expression -> identifier, ":=", value
        We treat this like a local variable assignment.
        """
        # Example structure: matched := regex.match(...)
        # Children: [identifier('matched'), ':=', call(...)]

        var_name = None
        value = None
        found_assign = False
        for c in node.children:
            if c.type == "identifier" and var_name is None:
                # Potential variable name
                var_name = c.text.decode('utf8')
            elif c.type in {"=", ":="}:
                found_assign = True
            elif found_assign:
                # Everything after := is the value
                # We'll take the entire text of this node as value from here onward
                # For named_expression, let's just grab the entire right-hand side node's text
                value = c.text.decode('utf8')
                break

        if var_name and var_name not in local_vars:
            local_vars[var_name] = ChapiFunctionFieldModel(
                TypeValue=var_name,
                TypeType=None,
                DefaultValue=value
            )

    def __process_local_variable(self, node: Node, local_vars: Dict[str, ChapiFunctionFieldModel]) -> None:
        var_name = self.__get_variable_names_from_assignment(node)
        if not var_name:
            return

        # Skip if we've seen this variable before (only keep initial assignment)
        if var_name in self.seen_variables:
            return
            
        self.seen_variables.add(var_name)  # Mark as seen
        
        var_type = self.__get_type_hint(node)
        value = self.__get_value(node)
        
        local_vars[var_name] = ChapiFunctionFieldModel(
            TypeValue=var_name,
            TypeType=var_type if var_type else None,
            DefaultValue=value if value else None
        )

    def __get_variable_names_from_assignment(self, node: Node) -> str:
        """
        Extract the entire LHS of the assignment as a single 'variable name'.

        For example:
        - "x = 1"  -> "x"
        - "x: int = 1" -> "x"
        - "(c, (d, e)) = (3, (4, 5))" -> "(c, (d, e))"

        We skip 'type' nodes here because __get_type_hint handles them separately.
        """
        lhs_parts = []
        for c in node.children:
            if c.type in {"=", ":="}:
                break
            elif c.type == ":":
                continue
            elif c.type == "type":
                continue
            lhs_parts.append(c.text.decode('utf8'))

        lhs = "".join(lhs_parts).strip()
        return lhs if lhs else ''

    def __get_type_hint(self, node: Node) -> Optional[str]:
        for child in node.children:
            if child.type == "type":
                return child.text.decode('utf8').strip(": ")
        return None

    def __get_value(self, node: Node) -> str:
        found_equal = False
        rhs_parts = []
        for child in node.children:
            if child.type in {"=", ":="}:
                found_equal = True
                continue
            if found_equal:
                # Append all parts of the RHS into one string
                rhs_parts.append(child.text.decode('utf8'))

        rhs = "".join(rhs_parts).strip()
        return rhs

    def __extract_function_call(self, call_node: Node) -> Optional[ChapiFunctionCall]:
        func_name, node_name = None, None
        args = []

        arg_list = None
        # Identify function name and arguments
        for child in call_node.children:
            if child.type == "identifier":
                func_name = child.text.decode('utf8')
            elif child.type == "attribute":
                func_name, node_name = self.__extract_attribute_name(child)
            elif child.type == "argument_list":
                arg_list = child

        if arg_list:
            args = self.__extract_call_parameters(arg_list)

        return ChapiFunctionCall(
            NodeName=node_name,
            FunctionName=func_name,
            Parameters=args
        )

    def __extract_attribute_name(self, attribute_node: Node) -> Tuple[str, Optional[str]]:
        # attribute: identifier '.' identifier
        parts = []
        for c in attribute_node.children:
            if c.type == "identifier":
                parts.append(c.text.decode('utf8'))
        if len(parts) == 2:
            # obj.method
            return parts[1], parts[0]
        # fallback if unusual structure
        return parts[-1] if parts else None, None #type: ignore

    def __extract_call_parameters(self, arg_list_node: Node) -> List[ChapiParameter]:
        params = []
        pos_arg_index = 0
        for arg in arg_list_node.children:
            if arg.type == "keyword_argument":
                key, val = None, None
                for i, kw_child in enumerate(arg.children):
                    if kw_child.type == "=":
                        key = arg.children[i-1].text.decode('utf8')
                        val = arg.children[i+1].text.decode('utf8')
                        break
                if key and val:
                    params.append(ChapiParameter(TypeValue=val, TypeType=key))
            elif arg.type not in ["(", ")", ",", "**", "*"]:
                # positional argument
                val = arg.text.decode('utf8')
                params.append(ChapiParameter(TypeValue=val, TypeType=str(pos_arg_index)))
                pos_arg_index += 1
        return params