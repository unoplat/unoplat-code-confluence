# Standard Library
# First Party

from src.code_confluence_flow_bridge.models.chapi.chapi_functioncall import ChapiFunctionCall
from src.code_confluence_flow_bridge.models.chapi.chapi_node import ChapiNode
from src.code_confluence_flow_bridge.models.chapi.chapi_position import Position
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_function_call_type import FunctionCallType
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_import import UnoplatImport
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_import_type import ImportType
from src.code_confluence_flow_bridge.parser.tree_sitter.code_confluence_tree_sitter import CodeConfluenceTreeSitter

from typing import Dict, List, Optional

# Third Party
from tree_sitter import Parser, Tree


class PythonExtractFunctionCalls:
    def __init__(self, code_confluence_tree_sitter: CodeConfluenceTreeSitter) -> None:
        """Initialize the function call extractor with Python Tree-sitter parser."""
        self.parser: Parser = code_confluence_tree_sitter.get_parser()

    def _handle_node_functions(self, node: ChapiNode, imports: List[UnoplatImport], entire_code: str, 
                              class_nodes_map: Optional[Dict[str, ChapiNode]] = None) -> None:
        """
        Common logic for processing functions in a node (either procedural or class).
        Builds the instantiation map and import map, extracts function calls for each function,
        processes them, and updates the function's function_calls list.
        
        Args:
            node: The node to process
            imports: List of imports
            entire_code: The entire source code
            class_nodes_map: Map of class nodes in the same file (for cross-class calls)
        """
        if class_nodes_map is None:
            class_nodes_map = {}
        
        inst_map: Dict[str, str] = self.extract_instantiations_ts(entire_code)
        import_map: Dict[str, str] = self._build_import_map(imports)
        if node.functions:
            for function in node.functions:
                if function.content:
                    function_calls: List[ChapiFunctionCall] = self._extract_function_calls_from_content(function.content)
                    processed_calls: List[ChapiFunctionCall] = []
                    for call in function_calls:
                        processed_call: Optional[ChapiFunctionCall] = self._process_function_call(
                            call, inst_map, import_map, node, class_nodes_map
                        )
                        if processed_call:
                            processed_calls.append(processed_call)
                    function.function_calls = processed_calls

    def handle_procedural_code(self, node: ChapiNode, imports: List[UnoplatImport], entire_code: str,
                              class_nodes_map: Optional[Dict[str, ChapiNode]] = None) -> None:
        """
        Handle procedural code by processing functions in a procedural node.
        
        Args:
            node: The procedural node to process
            imports: List of imports
            entire_code: The entire source code
            class_nodes_map: Map of class nodes in the same file (for cross-class calls)
        """
        self._handle_node_functions(node, imports, entire_code, class_nodes_map)

    def handle_class_code(self, node: ChapiNode, imports: List[UnoplatImport], entire_code: str,
                           class_nodes_map: Optional[Dict[str, ChapiNode]] = None) -> None:
        """
        Handle class code by processing methods in a class node.
        This maps function calls made within the same class (methods) and also calls to external procedures or
        classes' functions in the codebase.
        
        Args:
            node: The class node to process
            imports: List of imports
            entire_code: The entire source code
            class_nodes_map: Map of class nodes in the same file (for cross-class calls)
        """
        self._handle_node_functions(node, imports, entire_code, class_nodes_map)

    def extract_function_calls(self, file_path_nodes: dict[str, List[ChapiNode]], imports: List[UnoplatImport], entire_code: str) -> dict[str, List[ChapiNode]]:
        """
        Extract function calls from the given function content using Tree-sitter parser.
        Updates nodes by linking function calls to their targets based on whether a node is procedural or a class.
        
        Args:
            file_path_nodes: Dictionary mapping file paths to lists of ChapiNodes
            imports: List of imports in the file
            entire_code: The entire source code of the file
            
        Returns:
            The updated file_path_nodes dictionary with function calls linked to their targets
        """
        # Process each node per file path
        for _, nodes in file_path_nodes.items():
            # Build a class nodes map for each file to handle cross-class calls
            class_nodes_map: Dict[str, ChapiNode] = {}
            procedural_node: Optional[ChapiNode] = None
            
            # First pass: identify class nodes and procedural node
            for node in nodes:
                if node.type == "CLASS" and node.node_name:
                    class_nodes_map[node.node_name] = node
                elif not node.type or node.type == "" or node.type != "CLASS":
                    # This is a procedural node
                    procedural_node = node
            
            # Process each node in the file
            for node in nodes:
                if not node.type or node.type == "" or node.type != "CLASS":
                    # Process procedural node
                    self.handle_procedural_code(node, imports, entire_code, class_nodes_map)
                elif node.type == "CLASS":
                    # Process class node with procedural node info if available
                    context_map = class_nodes_map.copy()
                    # If we have a procedural node, include it for cross-references
                    if procedural_node and procedural_node.node_name:
                        context_map["_procedural_"] = procedural_node
                    self.handle_class_code(node, imports, entire_code, context_map)
        
        return file_path_nodes

    def _extract_function_calls_from_content(self, content: str) -> List[ChapiFunctionCall]:
        """
        Extract function calls from the given content using Tree-sitter.
        Excludes object instantiations (calls where function name starts with uppercase).
        
        Args:
            content: The content to analyze
            
        Returns:
            List of ChapiFunctionCall objects representing the function calls found
        """
        tree: Tree = self.parser.parse(bytes(content, "utf8"))
        
        # Define the query to capture function calls
        query_source = r"""
        ; 1. Simple function call
        (call
          function: (identifier) @function_name) @call
        
        ; 2. Method call on object (but not part of a deeper chain)
        (call
          function: (attribute
                     object: [(identifier) (subscript)] @object  ; Allow identifier or subscript as object
                     attribute: (identifier) @method_name)) @method_call
                     
        ; 3. Nested attribute calls with at least two levels deep
        (call
          function: (attribute
                     object: (attribute) @nested_object  ; Only match if object is an attribute itself
                     attribute: (identifier) @nested_method)) @nested_call
                     
        ; 4. Chained method calls (calls on the result of another call)
        (call
          function: (attribute
                     object: (call) @chained_call_source
                     attribute: (identifier) @chained_method)) @chained_call
        """
        
        query = self.parser.language.query(query_source)  # type: ignore
        matches = query.matches(tree.root_node)
        
        # Keep track of already processed call nodes to avoid duplicates
        processed_call_nodes = set()
        
        function_calls = []
        for pattern_index, capture_dict in matches:
            if pattern_index == 0:  # Simple function call
                if "function_name" in capture_dict and "call" in capture_dict:
                    function_name_node = capture_dict["function_name"][0]
                    call_node = capture_dict["call"][0]
                    
                    # Skip if we've already processed this call node
                    call_node_id = (call_node.start_byte, call_node.end_byte)
                    if call_node_id in processed_call_nodes:
                        continue
                    processed_call_nodes.add(call_node_id)
                    
                    func_name = content[function_name_node.start_byte:function_name_node.end_byte]
                    
                    # Skip object instantiations (calls where function name starts with uppercase)
                    if func_name and func_name[0].isupper():
                        continue
                    
                    # Create a ChapiFunctionCall object
                    function_call = ChapiFunctionCall(
                        FunctionName=func_name,
                        Parameters=[],  # Skip parameter extraction for now
                        Position=Position(
                            StartLine=call_node.start_point[0] + 1,
                            StartLinePosition=call_node.start_point[1] + 1,
                            StopLine=call_node.end_point[0] + 1,
                            StopLinePosition=call_node.end_point[1] + 1
                        )
                    )
                    function_calls.append(function_call)
                    
            elif pattern_index == 1:  # Method call on object
                if "object" in capture_dict and "method_name" in capture_dict and "method_call" in capture_dict:
                    object_node = capture_dict["object"][0]
                    method_name_node = capture_dict["method_name"][0]
                    call_node = capture_dict["method_call"][0]
                    
                    # Skip if we've already processed this call node
                    call_node_id = (call_node.start_byte, call_node.end_byte)
                    if call_node_id in processed_call_nodes:
                        continue
                    processed_call_nodes.add(call_node_id)
                    
                    object_text = content[object_node.start_byte:object_node.end_byte]
                    method_name = content[method_name_node.start_byte:method_name_node.end_byte]
                    
                    # Create a ChapiFunctionCall object for method call
                    function_call = ChapiFunctionCall(
                        NodeName=object_text,
                        FunctionName=method_name,
                        Parameters=[],  # Skip parameter extraction for now
                        Position=Position(
                            StartLine=call_node.start_point[0] + 1,
                            StartLinePosition=call_node.start_point[1] + 1,
                            StopLine=call_node.end_point[0] + 1,
                            StopLinePosition=call_node.end_point[1] + 1
                        )
                    )
                    function_calls.append(function_call)
                    
            elif pattern_index == 2:  # Nested attribute call
                if "nested_object" in capture_dict and "nested_method" in capture_dict and "nested_call" in capture_dict:
                    nested_obj_node = capture_dict["nested_object"][0]
                    nested_method_node = capture_dict["nested_method"][0]
                    call_node = capture_dict["nested_call"][0]
                    
                    # Skip if we've already processed this call node
                    call_node_id = (call_node.start_byte, call_node.end_byte)
                    if call_node_id in processed_call_nodes:
                        continue
                    processed_call_nodes.add(call_node_id)
                    
                    nested_obj_text = content[nested_obj_node.start_byte:nested_obj_node.end_byte]
                    nested_method = content[nested_method_node.start_byte:nested_method_node.end_byte]
                    
                    # Create a ChapiFunctionCall object for nested method call
                    function_call = ChapiFunctionCall(
                        NodeName=nested_obj_text,
                        FunctionName=nested_method,
                        Parameters=[],  # Skip parameter extraction for now
                        Position=Position(
                            StartLine=call_node.start_point[0] + 1,
                            StartLinePosition=call_node.start_point[1] + 1,
                            StopLine=call_node.end_point[0] + 1,
                            StopLinePosition=call_node.end_point[1] + 1
                        )
                    )
                    function_calls.append(function_call)
                    
            elif pattern_index == 3:  # Chained method call
                if "chained_method" in capture_dict and "chained_call" in capture_dict:
                    method_name_node = capture_dict["chained_method"][0]
                    call_node = capture_dict["chained_call"][0]
                    
                    # Skip if we've already processed this call node
                    call_node_id = (call_node.start_byte, call_node.end_byte)
                    if call_node_id in processed_call_nodes:
                        continue
                    processed_call_nodes.add(call_node_id)
                    
                    method_name = content[method_name_node.start_byte:method_name_node.end_byte]
                    
                    # Create a ChapiFunctionCall object for chained method call
                    # The NodeName is None because this is a method on a temporary object
                    function_call = ChapiFunctionCall(
                        FunctionName=method_name,
                        Parameters=[],  # Skip parameter extraction for now
                        Position=Position(
                            StartLine=call_node.start_point[0] + 1,
                            StartLinePosition=call_node.start_point[1] + 1,
                            StopLine=call_node.end_point[0] + 1,
                            StopLinePosition=call_node.end_point[1] + 1
                        )
                    )
                    function_calls.append(function_call)
                
        return function_calls

    
    def _process_function_call(self, call: ChapiFunctionCall, 
                              inst_map: Dict[str, str], 
                              import_map: Dict[str, str],
                              node: ChapiNode,
                              class_nodes_map: Optional[Dict[str, ChapiNode]] = None) -> Optional[ChapiFunctionCall]:
        """
        Process a function call to link it to its target.
        
        Args:
            call: The ChapiFunctionCall object to process
            inst_map: Dictionary mapping variable names to class names
            import_map: Dictionary mapping local names to qualified names
            node: The ChapiNode representing the procedural code
            class_nodes_map: Map of class nodes in the same file (for cross-class calls)
            
        Returns:
            Updated ChapiFunctionCall with linked information or None if the call should be ignored
        """
        if class_nodes_map is None:
            class_nodes_map = {}
        
        # Step 1: Check if it's a same-file function call in the current node
        is_local_procedure: bool = False
        if node.functions:
            for function in node.functions:
                # For procedural nodes or direct method calls (without "self.")
                # check if node_name is None and function name matches
                if function.name == call.function_name and call.node_name is None:
                    call.type = FunctionCallType.SAME_FILE.value
                    is_local_procedure = True
                    break
        
        if is_local_procedure:
            return call

        # Step 2: Check for self-referencing method calls in class nodes
        if call.node_name == "self" and node.type == "CLASS" and node.functions:
            for function in node.functions:
                if function.name == call.function_name:
                    call.type = FunctionCallType.SAME_FILE.value
                    # Clear node_name for clarity, as it's a self-reference
                    call.node_name = None
                    return call

        # Step 3: Check for direct calls to other classes in the same file
        if class_nodes_map and call.node_name:
            # Special case for procedural node
            if call.node_name == "_procedural_" and "_procedural_" in class_nodes_map:
                procedural_node = class_nodes_map["_procedural_"]
                if procedural_node.functions:
                    for function in procedural_node.functions:
                        if function.name == call.function_name:
                            call.type = FunctionCallType.SAME_FILE.value
                            call.node_name = procedural_node.node_name
                            return call
            
            # Direct class reference (ClassName.method_name())
            if call.node_name in class_nodes_map:
                other_class_node = class_nodes_map[call.node_name]
                if other_class_node.functions:
                    for function in other_class_node.functions:
                        if function.name == call.function_name:
                            call.type = FunctionCallType.SAME_FILE.value
                            return call
            
            # Instance of another class in the same file
            if call.node_name in inst_map:
                class_name = inst_map[call.node_name]
                if class_name in class_nodes_map:
                    other_class_node = class_nodes_map[class_name]
                    if other_class_node.functions:
                        for function in other_class_node.functions:
                            if function.name == call.function_name:
                                call.type = FunctionCallType.SAME_FILE.value
                                call.node_name = class_name  # Update node_name to the class name
                                return call
                                
        # Step 4: Check for calls to procedural functions in the same file (without class prefix)
        if call.node_name is None and "_procedural_" in class_nodes_map:
            procedural_node = class_nodes_map["_procedural_"]
            if procedural_node.functions:
                for function in procedural_node.functions:
                    if function.name == call.function_name:
                        call.type = FunctionCallType.SAME_FILE.value
                        call.node_name = procedural_node.node_name
                        return call

        # Step 5: Check for static class methods directly in import_map
        if call.node_name and call.node_name[0].isupper() and call.node_name in import_map:
            call.node_name = import_map[call.node_name]
            call.type = FunctionCallType.INTERNAL_CODEBASE.value
            return call
        
        # Step 6: Check if the function itself is imported (without a node_name)
        if not call.node_name and call.function_name in import_map:
            import_qualified_name: str = import_map[call.function_name]
            call.node_name = import_qualified_name
            call.type = FunctionCallType.INTERNAL_CODEBASE.value
            
            return call
        
        # Step 7: Check instance methods using inst_map and import_map
        if call.node_name and call.node_name in inst_map:
            class_qualified_name: str = inst_map[call.node_name]
            if class_qualified_name in import_map:
                call.node_name = import_map[class_qualified_name]
                call.type = FunctionCallType.INTERNAL_CODEBASE.value
                return call
        
        # Step 8: If we reach here, we couldn't identify the call type
        call.type = FunctionCallType.UNKNOWN.value
        return call
    
    def extract_instantiations_ts(self, file_source: str) -> Dict[str, str]:
        """
        Extracts object instantiations from the entire file content using a tree-sitter query.
        Returns a dictionary mapping variable names to the class name being instantiated.
        Only considers calls where the function name follows PascalCase convention (likely a class).
        """
        tree: Tree = self.parser.parse(bytes(file_source, "utf8"))
        
        # Define the query to capture instantiations
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
        
        for _, capture_dict in matches:
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
    
    def _build_import_map(self, imports: List[UnoplatImport]) -> Dict[str, str]:
        """
        Builds a map of local names to their qualified names for specific imports.

        For class imports (if original name is PascalCase i.e., starts with an uppercase letter),
        the qualified name is "source.original_name".
        For procedural method imports (if original name does not start with an uppercase letter),
        the qualified name is just "source".

        Args:
            imports: List of UnoplatImport objects.

        Returns:
            Dictionary mapping local names to qualified names.
        """
        import_map: Dict[str, str] = {}
        for imp in imports:
            if imp.import_type == ImportType.INTERNAL and imp.usage_names:
                for name in imp.usage_names:
                    local_name: str = name.alias if name.alias is not None else name.original_name #type: ignore
                    if local_name and name.original_name and imp.source:
                        if name.original_name[0].isupper() and name.original_name != name.original_name.upper():
                            qualified_name: str = f"{imp.source}.{name.original_name}"
                        else:
                            qualified_name = imp.source
                        import_map[local_name] = qualified_name
        return import_map