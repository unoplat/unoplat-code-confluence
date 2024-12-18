from typing import List, Optional, Dict, Tuple
from tree_sitter import Node, TreeCursor
from unoplat_code_confluence.data_models.chapi.chapi_function import ChapiFunction
from unoplat_code_confluence.data_models.chapi.chapi_functioncall import ChapiFunctionCall
from unoplat_code_confluence.data_models.chapi.chapi_parameter import ChapiParameter

from unoplat_code_confluence.data_models.chapi.chapi_function_field_model import ChapiFunctionFieldModel
from unoplat_code_confluence.data_models.chapi.chapi_annotation import ChapiAnnotation
from unoplat_code_confluence.parser.tree_sitter.code_confluence_tree_sitter import CodeConfluenceTreeSitter
from unoplat_code_confluence.configuration.settings import ProgrammingLanguage

class FunctionMetadataParser:
    def __init__(self, tree_sitter: CodeConfluenceTreeSitter):
        self.parser = tree_sitter.get_parser()

    def process_functions(self, functions: List[ChapiFunction]) -> List[ChapiFunction]:
        updated_functions = []
        for func in functions:
            updated_functions.append(self.__get_function_metadata(func))
        return updated_functions

    def __get_function_metadata(self, chapi_function: ChapiFunction) -> ChapiFunction:
        if not chapi_function.content:
            return chapi_function

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
        cursor = tree.walk()
        reached_root = False
        while not reached_root:
            node = cursor.node
            if node.type == "function_definition":
                for child in node.children:
                    if child.type == "type":
                        return child.text.decode('utf8').strip(": ")
            if cursor.goto_first_child():
                continue
            if cursor.goto_next_sibling():
                continue
            retracing = True
            while retracing:
                if not cursor.goto_parent():
                    reached_root = True
                elif cursor.goto_next_sibling():
                    retracing = False
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
                NameOfField=var_name,
                TypeOfField=None,
                ValueOfField=value
            )

    def __process_local_variable(self, node: Node, local_vars: Dict[str, ChapiFunctionFieldModel]) -> None:
        var_names = self.__get_variable_names_from_assignment(node)
        if not var_names:
            return

        var_type = self.__get_type_hint(node)
        values = self.__get_value(node)

        for i, var_name in enumerate(var_names):
            if var_name in local_vars:
                # already recorded (first assignment only)
                continue
            value = values[i] if i < len(values) else None
            local_vars[var_name] = ChapiFunctionFieldModel(
                NameOfField=var_name,
                TypeOfField=var_type if var_type else None,
                ValueOfField=value if value else None
            )

    def __get_variable_names_from_assignment(self, node: Node) -> List[str]:
        """
        Extract variable names from the left-hand side of an assignment.
        Structure can be:
        - Simple: identifier = value
        - Type hint: identifier : type = value
        - Tuple: (a, b) = value
        - Pattern: a, *b, c = value
        """
        names = []
        for c in node.children:
            if c.type == "identifier":
                # Direct identifier - capture the name
                names.append(c.text.decode('utf8'))
            elif c.type in ["pattern_list", "tuple_pattern", "list_splat_pattern"]:
                # Handle tuple unpacking and patterns
                names.extend(self.__extract_var_names_from_pattern(c))
            elif c.type in {"=", ":="}:
                # Stop when we hit the assignment operator
                break

        return names

    def __extract_var_names_from_pattern(self, node: Node) -> List[str]:
        """
        Recursively extract variable names from patterns:
        - identifier: return [identifier]
        - pattern_list: a,b,c
        - tuple_pattern: (x, y)
        - list_splat_pattern: *middle
        We ignore attributes (self.x) as local variables.
        """
        names = []
        if node.type == "identifier":
            var_name = node.text.decode('utf8')
            names.append(var_name)
        elif node.type in ["pattern_list"]:
            for c in node.children:
                if c.type in ["identifier", "pattern_list", "tuple_pattern", "list_splat_pattern"]:
                    names.extend(self.__extract_var_names_from_pattern(c))
        elif node.type == "tuple_pattern":
            # tuple_pattern children can contain identifiers, tuple_patterns, etc.
            for c in node.children:
                if c.type in ["identifier", "pattern_list", "tuple_pattern", "list_splat_pattern"]:
                    names.extend(self.__extract_var_names_from_pattern(c))
        elif node.type == "list_splat_pattern":
            # *middle scenario
            # children: '*' and 'identifier'
            for c in node.children:
                if c.type == "identifier":
                    var_name = c.text.decode('utf8')
                    names.append(var_name)

        # If there's a parenthesized expression or generic patterns,
        # handle them similarly by recursing.
        # For completeness:
        elif node.type == "parenthesized_expression":
            # Just go inside
            for c in node.children:
                names.extend(self.__extract_var_names_from_pattern(c))

        return names

    def __get_type_hint(self, node: Node) -> Optional[str]:
        for child in node.children:
            if child.type == "type":
                return child.text.decode('utf8').strip(": ")
        return None

    def __get_value(self, node: Node) -> List[str]:
        values = []
        found_equal = False
        for child in node.children:
            if child.type in {"=", ":="}:
                found_equal = True
                continue
            if found_equal:
                if child.type == "expression_list":
                    # Handle tuple unpacking - keep per variable behavior
                    for expr_child in child.children:
                        if expr_child.type not in [",", "(", ")"]:
                            values.append(expr_child.text.decode('utf8'))
                else:
                    # For single variable assignment, capture entire RHS
                    values.append(child.text.decode('utf8'))
                    # Only break if this is a single value assignment
                    if len(values) == 1:  # If we have one value, it's a single assignment
                        break
        return values

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