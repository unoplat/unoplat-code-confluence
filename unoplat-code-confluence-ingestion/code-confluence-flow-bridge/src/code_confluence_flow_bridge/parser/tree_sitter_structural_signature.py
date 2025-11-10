"""
Tree-sitter structural signature extractor for code parsing.

This module provides Python-specific structural signature extraction using tree-sitter.
"""

from typing import Dict, List, Optional, Tuple

import tree_sitter
from unoplat_code_confluence_commons.base_models import (
    PythonClassInfo,
    PythonFunctionInfo,
    PythonStructuralSignature,
    PythonVariableInfo,
)

# Local imports
from src.code_confluence_flow_bridge.parser.tree_sitter_config import (
    TreeSitterExtractorConfig,
)
from src.code_confluence_flow_bridge.parser.tree_sitter_extractor_base import (
    _LANGUAGE_CACHE,
    _PARSER_CACHE,
    _QUERY_CACHE,
    TreeSitterExtractorBase,
)


class TreeSitterPythonStructuralSignatureExtractor(TreeSitterExtractorBase):
    """Extracts structural signatures from Python source code using tree-sitter queries.

    Inherits caching utilities from TreeSitterExtractorBase and implements
    Python-specific extraction logic for functions, classes, variables, etc.
    """

    def __init__(self, language_name: str, config: TreeSitterExtractorConfig):
        """Initialize parser & queries with multi-level caching and lazy compilation.

        Args:
            language_name: Programming language name (should be "python")
            config: TreeSitterExtractorConfig with query paths, captures, and node types
        """
        super().__init__(language_name, config)

    # Wrapper properties for test compatibility (self-extraction tests at lines 449, 492)
    @property
    def _LANGUAGE_CACHE(self) -> Dict[str, tree_sitter.Language]:
        """Expose module-level language cache for test introspection."""
        return _LANGUAGE_CACHE

    @property
    def _PARSER_CACHE(self) -> Dict[str, tree_sitter.Parser]:
        """Expose module-level parser cache for test introspection."""
        return _PARSER_CACHE

    @property
    def _QUERY_CACHE(self) -> Dict[str, Dict[str, tree_sitter.Query]]:
        """Expose module-level query cache for test introspection."""
        return _QUERY_CACHE

    def extract_structural_signature(
        self, source_bytes: bytes
    ) -> PythonStructuralSignature:
        """Extract structural signature from byte content."""
        # Parse the source code (tree-sitter expects bytes)
        tree: tree_sitter.Tree = self.parser.parse(source_bytes)
        root_node: tree_sitter.Node = tree.root_node

        # Extract components
        module_docstring: Optional[str] = self._extract_module_docstring(
            root_node, source_bytes
        )
        global_variables: List[PythonVariableInfo] = self._extract_global_variables(
            root_node, source_bytes
        )
        functions: List[PythonFunctionInfo] = self._extract_functions(
            root_node, source_bytes
        )
        classes: List[PythonClassInfo] = self._extract_classes(root_node, source_bytes)

        return PythonStructuralSignature(
            module_docstring=module_docstring,
            global_variables=global_variables,
            functions=functions,
            classes=classes,
        )

    def _extract_module_docstring(
        self, root_node: tree_sitter.Node, source: bytes
    ) -> Optional[str]:
        """Extract module-level docstring."""
        cursor = tree_sitter.QueryCursor(self.queries["module_docstring"])
        captures: Dict[str, List[tree_sitter.Node]] = cursor.captures(root_node)

        cap_name = self.config.get_capture_name("module")
        if cap_name in captures and captures[cap_name]:
            node: tree_sitter.Node = captures[cap_name][0]
            docstring: str = source[node.start_byte : node.end_byte].decode("utf-8")
            return self._clean_string_literal(docstring)

        return None

    def _extract_global_variables(
        self, root_node: tree_sitter.Node, source: bytes
    ) -> List[PythonVariableInfo]:
        """Extract module-level variable declarations."""
        cursor = tree_sitter.QueryCursor(self.queries["global_variables"])
        captures = cursor.captures(root_node)

        variables: List[PythonVariableInfo] = []
        seen_assignments: set = set()

        var_stmt_cap = self.config.get_capture_name("var_statement")

        if var_stmt_cap in captures:
            for node in captures[var_stmt_cap]:
                if self._is_at_module_level(node):
                    start_line = node.start_point[0] + 1
                    end_line = node.end_point[0] + 1
                    signature = (
                        source[node.start_byte : node.end_byte].decode("utf-8").strip()
                    )

                    if (start_line, signature) not in seen_assignments:
                        seen_assignments.add((start_line, signature))
                        variables.append(
                            PythonVariableInfo(
                                start_line=start_line,
                                end_line=end_line,
                                signature=signature,
                            )
                        )

        return variables

    def _extract_functions(
        self, root_node: tree_sitter.Node, source: bytes
    ) -> List[PythonFunctionInfo]:
        """Extract module-level function definitions using matches."""
        cursor = tree_sitter.QueryCursor(self.queries["module_functions"])
        matches: List[tuple] = cursor.matches(root_node)

        functions: List[PythonFunctionInfo] = []
        seen: set = set()

        for match_id, captures in matches:
            func_node: Optional[tree_sitter.Node] = None
            # Capture names used in query files
            func_with_decor_cap: str = self.config.get_capture_name(
                "func_with_decorators"
            )
            # The function definition node itself is captured as @function in the query
            function_node_cap: str = "function"

            if func_with_decor_cap in captures:
                func_node = captures[func_with_decor_cap][0]
            elif function_node_cap in captures:
                func_node = captures[function_node_cap][0]

            if func_node:
                if not self._is_at_module_level(func_node):
                    continue
                start_line: int = func_node.start_point[0] + 1
                end_line: int = func_node.end_point[0] + 1

                # Extract signature
                signature: str = source[
                    func_node.start_byte : func_node.end_byte
                ].decode("utf-8")
                signature_lines: List[str] = signature.split("\n")
                sig_parts: List[str] = []
                for line in signature_lines:
                    sig_parts.append(line)
                    if line.rstrip().endswith(":"):
                        break

                # Extract docstring if present (@docstring capture in query)
                docstring: Optional[str] = None
                func_doc_cap: str = self.config.get_capture_name(
                    "function"
                )  # maps to "docstring"
                if func_doc_cap in captures:
                    docstring_node: tree_sitter.Node = captures[func_doc_cap][0]
                    docstring = self._clean_string_literal(
                        source[
                            docstring_node.start_byte : docstring_node.end_byte
                        ].decode("utf-8")
                    )

                # Extract nested functions
                actual_func_def = captures.get(function_node_cap, [None])[0]
                nested_functions: List[PythonFunctionInfo] = []
                if actual_func_def:
                    nested_functions = self._extract_nested_functions_for_node(
                        actual_func_def, source
                    )

                # Extract function calls
                function_calls: List[str] = []
                if actual_func_def:
                    function_calls = self._extract_function_calls_for_node(
                        actual_func_def, source
                    )

                func_sig: str = "\n".join(sig_parts)
                key: tuple = (start_line, func_sig)
                if key not in seen:
                    seen.add(key)
                    functions.append(
                        PythonFunctionInfo(
                            start_line=start_line,
                            end_line=end_line,
                            signature=func_sig,
                            docstring=docstring,
                            function_calls=function_calls,
                            nested_functions=nested_functions,
                        )
                    )

        return sorted(functions, key=lambda f: f.start_line)

    def _extract_classes(
        self, root_node: tree_sitter.Node, source: bytes
    ) -> List[PythonClassInfo]:
        """Extract class definitions with their methods and variables using matches."""
        cursor = tree_sitter.QueryCursor(self.queries["module_classes"])
        matches = cursor.matches(root_node)

        classes = []

        for _, captures in matches:
            class_node: Optional[tree_sitter.Node] = None
            class_with_decor_cap = self.config.get_capture_name("class_with_decorators")
            class_def_cap = self.config.get_capture_name("class_def")

            if class_with_decor_cap in captures:
                class_node = captures[class_with_decor_cap][0]
            elif class_def_cap in captures:
                class_node = captures[class_def_cap][0]

            if class_node:
                start_line = class_node.start_point[0] + 1
                end_line = class_node.end_point[0] + 1

                # Extract signature
                signature = source[class_node.start_byte : class_node.end_byte].decode(
                    "utf-8"
                )
                signature_lines = signature.split("\n")
                sig_parts = []
                for line in signature_lines:
                    sig_parts.append(line)
                    if line.rstrip().endswith(":"):
                        break

                # Extract docstring if present
                docstring = None
                class_doc_cap = self.config.get_capture_name("class")
                if class_doc_cap in captures:
                    docstring_node = captures[class_doc_cap][0]
                    docstring = self._clean_string_literal(
                        source[
                            docstring_node.start_byte : docstring_node.end_byte
                        ].decode("utf-8")
                    )

                # Get the actual class_definition node for extracting variables and methods
                actual_class_def = (
                    captures[class_def_cap][0] if class_def_cap in captures else None
                )

                # Extract class variables and methods
                class_variables = []
                methods = []
                nested_classes = []

                if actual_class_def:
                    class_variables = self._extract_class_variables_for_node(
                        actual_class_def, source
                    )
                    methods = self._extract_methods_for_node(actual_class_def, source)
                    nested_classes = self._extract_nested_classes_for_node(
                        actual_class_def, source
                    )

                # Combine class variables with instance variables from all methods
                all_variables = class_variables.copy()
                instance_variables_seen = set()

                for method in methods:
                    for instance_var in method.instance_variables:
                        # Deduplicate instance variables (same variable might be assigned in multiple methods)
                        var_key = (
                            instance_var.signature.split("=")[0].strip(),
                            instance_var.signature,
                        )
                        if var_key not in instance_variables_seen:
                            instance_variables_seen.add(var_key)
                            all_variables.append(instance_var)

                # Sort all variables by line number
                all_variables.sort(key=lambda v: v.start_line)

                classes.append(
                    PythonClassInfo(
                        start_line=start_line,
                        end_line=end_line,
                        signature="\n".join(sig_parts),
                        docstring=docstring,
                        vars=all_variables,
                        methods=methods,
                        nested_classes=nested_classes,
                    )
                )

        return sorted(classes, key=lambda c: c.start_line)

    def _extract_class_variables_for_node(
        self, class_node: tree_sitter.Node, source: bytes
    ) -> List[PythonVariableInfo]:
        """Extract class variables for a specific class node, excluding nested class variables."""
        cursor = tree_sitter.QueryCursor(self.queries["class_variables"])
        captures = cursor.captures(class_node)

        # Get nested class ranges to exclude
        nested_ranges = self._get_nested_class_ranges(class_node)

        variables = []
        seen = set()

        var_stmt_cap = self.config.get_capture_name("var_statement")

        if var_stmt_cap in captures:
            for node in captures[var_stmt_cap]:
                # Check if this assignment is within any nested class
                assignment_start = node.start_byte
                is_within_nested = any(
                    start <= assignment_start < end for start, end in nested_ranges
                )
                if is_within_nested:
                    continue  # Skip variables that are inside nested classes
                # The updated Tree-sitter query now captures both class and instance variables
                # We filter out local variables (non-self assignments inside methods) programmatically
                start_line = node.start_point[0] + 1
                end_line = node.end_point[0] + 1
                signature = (
                    source[node.start_byte : node.end_byte].decode("utf-8").strip()
                )

                # The reverted query now only captures class-level variables, so no filtering needed
                key = (start_line, signature)
                if key not in seen:
                    seen.add(key)
                    variables.append(
                        PythonVariableInfo(
                            start_line=start_line,
                            end_line=end_line,
                            signature=signature,
                        )
                    )

        return variables

    def _extract_methods_for_node(
        self, class_node: tree_sitter.Node, source: bytes
    ) -> List[PythonFunctionInfo]:
        """Extract methods for a specific class node using matches, excluding nested class methods."""
        cursor = tree_sitter.QueryCursor(self.queries["class_methods"])
        matches = cursor.matches(class_node)

        # Get nested class ranges to exclude
        nested_ranges = self._get_nested_class_ranges(class_node)

        methods = []

        for _, captures in matches:
            method_node: Optional[tree_sitter.Node] = None
            method_with_decor_cap = self.config.get_capture_name(
                "method_with_decorators"
            )
            method_def_cap = self.config.get_capture_name("method_def")

            if method_with_decor_cap in captures:
                method_node = captures[method_with_decor_cap][0]
            elif method_def_cap in captures:
                method_node = captures[method_def_cap][0]

            if method_node:
                # Check if this method is within any nested class
                method_start = method_node.start_byte
                is_within_nested = any(
                    start <= method_start < end for start, end in nested_ranges
                )
                if is_within_nested:
                    continue  # Skip methods that are inside nested classes

                start_line = method_node.start_point[0] + 1
                end_line = method_node.end_point[0] + 1

                # Extract signature
                signature = source[
                    method_node.start_byte : method_node.end_byte
                ].decode("utf-8")
                signature_lines = signature.split("\n")
                sig_parts = []
                for line in signature_lines:
                    sig_parts.append(line)
                    if line.rstrip().endswith(":"):
                        break

                # Extract docstring if present
                docstring = None
                method_doc_cap = self.config.get_capture_name("method")
                if method_doc_cap in captures:
                    docstring_node = captures[method_doc_cap][0]
                    docstring = self._clean_string_literal(
                        source[
                            docstring_node.start_byte : docstring_node.end_byte
                        ].decode("utf-8")
                    )

                # Extract nested functions for this method
                actual_method_def = captures.get(method_def_cap, [None])[0]
                nested_functions = []
                if actual_method_def:
                    nested_functions = self._extract_nested_functions_for_node(
                        actual_method_def, source
                    )

                # Extract function calls inside this method
                function_calls: List[str] = []
                if actual_method_def:
                    function_calls = self._extract_function_calls_for_node(
                        actual_method_def, source
                    )

                # Extract instance variables inside this method
                instance_variables: List[PythonVariableInfo] = []
                if actual_method_def:
                    instance_variables = self._extract_instance_variables_for_method(
                        actual_method_def, source
                    )

                methods.append(
                    PythonFunctionInfo(
                        start_line=start_line,
                        end_line=end_line,
                        signature="\n".join(sig_parts),
                        docstring=docstring,
                        function_calls=function_calls,
                        nested_functions=nested_functions,
                        instance_variables=instance_variables,
                    )
                )

        return sorted(methods, key=lambda m: m.start_line)

    # TODO: look at doing this through dp . recursive solution are not good to read at
    def _extract_nested_functions_for_node(
        self, parent_func_node: tree_sitter.Node, source: bytes
    ) -> List[PythonFunctionInfo]:
        """Extract immediate nested functions within a specific function node.

        This method only extracts functions that are direct children of the parent
        function, not grandchildren or deeper descendants. Each extracted function
        is recursively processed to find its own nested functions.
        """
        cursor = tree_sitter.QueryCursor(self.queries["nested_functions"])
        matches: List[tuple] = cursor.matches(parent_func_node)

        nested_functions: List[PythonFunctionInfo] = []

        for _, captures in matches:
            nested_func_node: Optional[tree_sitter.Node] = None
            nested_with_decor_cap = self.config.get_capture_name(
                "nested_func_with_decorators"
            )
            nested_def_cap = self.config.get_capture_name("nested_func_def")

            if nested_with_decor_cap in captures:
                nested_func_node = captures[nested_with_decor_cap][0]
            elif nested_def_cap in captures:
                nested_func_node = captures[nested_def_cap][0]

            if nested_func_node:
                # Filter out grandchildren and deeper descendants
                if not self._is_immediate_child_function(
                    nested_func_node, parent_func_node
                ):
                    continue

                start_line: int = nested_func_node.start_point[0] + 1
                end_line: int = nested_func_node.end_point[0] + 1

                # Extract signature
                signature: str = source[
                    nested_func_node.start_byte : nested_func_node.end_byte
                ].decode("utf-8")
                signature_lines: List[str] = signature.split("\n")
                sig_parts: List[str] = []
                for line in signature_lines:
                    sig_parts.append(line)
                    if line.rstrip().endswith(":"):
                        break

                # Extract docstring if present
                docstring: Optional[str] = None
                nested_doc_cap = self.config.get_capture_name("nested_function")
                if nested_doc_cap in captures:
                    docstring_node: tree_sitter.Node = captures[nested_doc_cap][0]
                    docstring = self._clean_string_literal(
                        source[
                            docstring_node.start_byte : docstring_node.end_byte
                        ].decode("utf-8")
                    )

                # Recursively extract nested functions within this nested function
                actual_nested_def: Optional[tree_sitter.Node] = captures.get(
                    nested_def_cap, [None]
                )[0]
                deeper_nested_functions: List[PythonFunctionInfo] = []
                if actual_nested_def:
                    deeper_nested_functions = self._extract_nested_functions_for_node(
                        actual_nested_def, source
                    )

                nested_functions.append(
                    PythonFunctionInfo(
                        start_line=start_line,
                        end_line=end_line,
                        signature="\n".join(sig_parts),
                        docstring=docstring,
                        function_calls=self._extract_function_calls_for_node(
                            nested_func_node, source
                        ),
                        nested_functions=deeper_nested_functions,
                    )
                )

        return sorted(nested_functions, key=lambda f: f.start_line)

    def _is_at_module_level(self, node: tree_sitter.Node) -> bool:
        """Check if a node is at top-level scope using language config."""
        parent = node.parent
        while parent:
            if parent.type in self.config.container_node_types:
                return False
            parent = parent.parent
        return True

    def _clean_string_literal(self, string_literal: str) -> str:
        """Delegate string cleaning to language config."""
        return self.config.doc_cleaner(string_literal)

    def _is_immediate_child_function(
        self, child_node: tree_sitter.Node, parent_func_node: tree_sitter.Node
    ) -> bool:
        """Check if a function node is an immediate child of the parent function.

        This method traverses upward from the child node through any block nodes
        to determine if it's directly nested within the parent function, not a
        grandchild or deeper descendant.

        Args:
            child_node: The potential nested function node
            parent_func_node: The parent function being analyzed

        Returns:
            True if child_node is an immediate child of parent_func_node
        """
        # Defensive check: child must be within parent's range
        if child_node.start_byte < parent_func_node.start_byte:
            return False

        # Navigate up from child, skipping through block nodes
        current = child_node.parent
        while current and current.type in self.config.block_node_types:
            current = current.parent

        # Check if we reached the parent function directly
        return current == parent_func_node

    # -------------------------------------------------------------------
    # Function-call extraction helpers
    # -------------------------------------------------------------------

    def _get_nested_function_ranges(
        self, func_node: tree_sitter.Node
    ) -> List[Tuple[int, int]]:
        """Get byte ranges of immediate nested functions within a function node.

        Only returns ranges for functions that are direct children of the given
        function node, not grandchildren or deeper descendants.

        Returns:
            List of (start_byte, end_byte) tuples for each immediate child function.
        """
        if "nested_functions" not in self.queries:
            return []

        # Get all nested function nodes
        cursor = tree_sitter.QueryCursor(self.queries["nested_functions"])
        matches = cursor.matches(func_node)
        nested_ranges = []

        for match_id, captures in matches:
            # Look for the nested function node (with or without decorators)
            nested_func_node = None
            nested_with_decor_cap = self.config.get_capture_name(
                "nested_func_with_decorators"
            )
            nested_def_cap = self.config.get_capture_name("nested_func_def")

            if nested_with_decor_cap in captures:
                nested_func_node = captures[nested_with_decor_cap][0]
            elif nested_def_cap in captures:
                nested_func_node = captures[nested_def_cap][0]

            if nested_func_node:
                # Only include immediate children to match _extract_nested_functions_for_node behavior
                if not self._is_immediate_child_function(nested_func_node, func_node):
                    continue
                nested_ranges.append(
                    (nested_func_node.start_byte, nested_func_node.end_byte)
                )

        return nested_ranges

    def _get_nested_class_ranges(
        self, class_node: tree_sitter.Node
    ) -> List[Tuple[int, int]]:
        """Get byte ranges of immediate nested classes within a class node.

        Only returns ranges for classes that are direct children of the given
        class node, not grandchildren or deeper descendants.

        Returns:
            List of (start_byte, end_byte) tuples for each immediate child class.
        """
        if "nested_classes" not in self.queries:
            return []

        # Get all nested class nodes
        cursor = tree_sitter.QueryCursor(self.queries["nested_classes"])
        matches = cursor.matches(class_node)
        nested_ranges = []

        for match_id, captures in matches:
            # Look for the nested class node (with or without decorators)
            nested_class_node = None
            nested_with_decor_cap = self.config.get_capture_name(
                "nested_class_with_decorators"
            )
            nested_def_cap = self.config.get_capture_name("nested_class_def")

            if nested_with_decor_cap in captures:
                nested_class_node = captures[nested_with_decor_cap][0]
            elif nested_def_cap in captures:
                nested_class_node = captures[nested_def_cap][0]

            if nested_class_node:
                nested_ranges.append(
                    (nested_class_node.start_byte, nested_class_node.end_byte)
                )

        return nested_ranges

    def _extract_function_calls_for_node(
        self,
        func_node: tree_sitter.Node,
        source: bytes,
        start_line: Optional[int] = None,
        end_line: Optional[int] = None,
    ) -> List[str]:
        """Extract function call names inside a function node via language-specific query.

        This routine relies entirely on the `function_calls` query defined per
        language. Any language wishing to support call-tracking must provide
        a `function_calls.scm` under its queries directory and capture the
        callable expression as `@function_call` (or the language-specific
        alias specified via :py:meth:`LanguageConfig.cap`).

        This method now filters out calls that are within nested functions,
        returning only direct calls within the function body.

        Args:
            func_node: The function AST node
            source: The full source code
            start_line: Deprecated parameter (kept for compatibility)
            end_line: Deprecated parameter (kept for compatibility)
        """

        if "function_calls" not in self.queries:
            return []  # No query provided for this language → gracefully skip

        # Always use the original AST node approach
        cursor = tree_sitter.QueryCursor(self.queries["function_calls"])
        captures = cursor.captures(func_node)

        cap_name: str = self.config.get_capture_name("function_call")

        if cap_name not in captures:
            return []

        call_nodes: List[tree_sitter.Node] = captures[cap_name]

        # Get nested function ranges to filter out calls within them
        nested_ranges = self._get_nested_function_ranges(func_node)

        # Filter out calls that are within nested functions
        direct_call_nodes: List[tree_sitter.Node] = []
        for call_node in call_nodes:
            call_start = call_node.start_byte
            # Check if this call is within any nested function
            is_within_nested = any(
                start <= call_start < end for start, end in nested_ranges
            )
            if not is_within_nested:
                direct_call_nodes.append(call_node)

        # Sort by start byte to preserve lexical order
        direct_call_nodes_sorted = sorted(direct_call_nodes, key=lambda n: n.start_byte)

        # Extract and return the call text
        return [
            source[n.start_byte : n.end_byte].decode("utf-8").strip()
            for n in direct_call_nodes_sorted
        ]

    def _extract_instance_variables_for_method(
        self, method_node: tree_sitter.Node, source: bytes
    ) -> List[PythonVariableInfo]:
        """Extract instance variable assignments from a method node.

        This method extracts assignments to instance variables (self.* assignments)
        within a method body, filtering out assignments within nested functions.

        Args:
            method_node: The method AST node
            source: The full source code

        Returns:
            List of PythonVariableInfo objects for instance variable assignments
        """
        if "instance_variables" not in self.queries:
            return []  # No query provided for this language → gracefully skip

        # Run the instance variables query on the method node
        cursor = tree_sitter.QueryCursor(self.queries["instance_variables"])
        captures = cursor.captures(method_node)

        if "instance_assignment" not in captures:
            return []

        assignment_nodes: List[tree_sitter.Node] = captures["instance_assignment"]

        # Get nested function ranges to filter out assignments within them
        nested_ranges = self._get_nested_function_ranges(method_node)

        # Filter out assignments that are within nested functions
        direct_assignment_nodes: List[tree_sitter.Node] = []
        for assignment_node in assignment_nodes:
            assignment_start = assignment_node.start_byte
            # Check if this assignment is within any nested function
            is_within_nested = any(
                start <= assignment_start < end for start, end in nested_ranges
            )
            if not is_within_nested:
                direct_assignment_nodes.append(assignment_node)

        # Create PythonVariableInfo objects for each instance variable
        instance_variables: List[PythonVariableInfo] = []
        seen: set = set()

        for node in direct_assignment_nodes:
            assignment_text = (
                source[node.start_byte : node.end_byte].decode("utf-8").strip()
            )

            # Only capture self.* assignments
            if assignment_text.startswith("self."):
                start_line = node.start_point[0] + 1
                end_line = node.end_point[0] + 1

                key = (start_line, assignment_text)
                if key not in seen:
                    seen.add(key)
                    instance_variables.append(
                        PythonVariableInfo(
                            start_line=start_line,
                            end_line=end_line,
                            signature=assignment_text,
                        )
                    )

        return sorted(instance_variables, key=lambda v: v.start_line)

    def _extract_nested_classes_for_node(
        self, class_node: tree_sitter.Node, source: bytes
    ) -> List[PythonClassInfo]:
        """Extract nested class definitions within a class node."""
        if "nested_classes" not in self.queries:
            return []

        cursor = tree_sitter.QueryCursor(self.queries["nested_classes"])
        matches = cursor.matches(class_node)
        nested_classes = []

        for match_id, captures in matches:
            nested_node: Optional[tree_sitter.Node] = None
            nested_with_decor_cap = self.config.get_capture_name(
                "nested_class_with_decorators"
            )
            nested_def_cap = self.config.get_capture_name("nested_class_def")

            if nested_with_decor_cap in captures:
                nested_node = captures[nested_with_decor_cap][0]
            elif nested_def_cap in captures:
                nested_node = captures[nested_def_cap][0]

            if nested_node:
                start_line = nested_node.start_point[0] + 1
                end_line = nested_node.end_point[0] + 1

                # Extract signature
                signature = source[
                    nested_node.start_byte : nested_node.end_byte
                ].decode("utf-8")
                signature_lines = signature.split("\n")
                sig_parts = []
                for line in signature_lines:
                    sig_parts.append(line)
                    if line.rstrip().endswith(":"):
                        break

                # Extract docstring if present
                docstring = None
                nested_doc_cap = self.config.get_capture_name("nested_class")
                if nested_doc_cap in captures:
                    docstring_node = captures[nested_doc_cap][0]
                    docstring = self._clean_string_literal(
                        source[
                            docstring_node.start_byte : docstring_node.end_byte
                        ].decode("utf-8")
                    )

                # Get the actual class_definition node for extracting variables and methods
                actual_nested_def = (
                    captures[nested_def_cap][0] if nested_def_cap in captures else None
                )

                # Extract class variables and methods
                class_variables = []
                methods = []
                deeper_nested = []

                if actual_nested_def:
                    class_variables = self._extract_class_variables_for_node(
                        actual_nested_def, source
                    )
                    methods = self._extract_methods_for_node(actual_nested_def, source)
                    # Recursive call for deeper nesting
                    deeper_nested = self._extract_nested_classes_for_node(
                        actual_nested_def, source
                    )

                # Combine class variables with instance variables from all methods
                all_variables = class_variables.copy()
                instance_variables_seen = set()

                for method in methods:
                    for instance_var in method.instance_variables:
                        var_key = (
                            instance_var.signature.split("=")[0].strip(),
                            instance_var.signature,
                        )
                        if var_key not in instance_variables_seen:
                            instance_variables_seen.add(var_key)
                            all_variables.append(instance_var)

                # Sort all variables by line number
                all_variables.sort(key=lambda v: v.start_line)

                nested_classes.append(
                    PythonClassInfo(
                        start_line=start_line,
                        end_line=end_line,
                        signature="\n".join(sig_parts),
                        docstring=docstring,
                        vars=all_variables,
                        methods=methods,
                        nested_classes=deeper_nested,
                    )
                )

        return sorted(nested_classes, key=lambda c: c.start_line)
