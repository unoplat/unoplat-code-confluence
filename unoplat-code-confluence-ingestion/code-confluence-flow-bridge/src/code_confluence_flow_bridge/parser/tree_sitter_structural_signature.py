"""
Tree-sitter structural signature extractor for code parsing.

This module provides language-agnostic structural signature extraction using tree-sitter
with configurable queries for different programming languages.
"""

from src.code_confluence_flow_bridge.models.code_confluence_parsing_models.class_info import ClassInfo
from src.code_confluence_flow_bridge.models.code_confluence_parsing_models.function_info import FunctionInfo
from src.code_confluence_flow_bridge.models.code_confluence_parsing_models.structural_signature import StructuralSignature

# Model imports
from src.code_confluence_flow_bridge.models.code_confluence_parsing_models.variable_info import VariableInfo

# Local imports
from src.code_confluence_flow_bridge.parser.language_configs import LanguageConfig, get_config

from pathlib import Path
from typing import Dict, List, Optional, Tuple

import tree_sitter
from tree_sitter_language_pack import get_language, get_parser

# ---------------------------------------------------------------------------
# Multi-level caches: language ► parser ► compiled query
# ---------------------------------------------------------------------------
_LANGUAGE_CACHE: Dict[str, tree_sitter.Language] = {}
_PARSER_CACHE: Dict[str, tree_sitter.Parser] = {}
_QUERY_CACHE: Dict[str, Dict[str, tree_sitter.Query]] = {}


class TreeSitterStructuralSignatureExtractor:
    """Extracts structural signatures from source code using tree-sitter queries."""
    
    def __init__(self, language_name: str = "python"):
        """Initialize parser & queries with multi-level caching and lazy compilation."""
        self.config: LanguageConfig = get_config(language_name)
        self.language_name: str = language_name
        self.language: tree_sitter.Language = self._get_language(language_name)
        self.parser: tree_sitter.Parser = self._get_parser(language_name)
        self.queries: Dict[str, tree_sitter.Query] = self._get_compiled_queries()
    
    @staticmethod
    def _get_language(language_name: str) -> tree_sitter.Language:
        """Fetch a tree-sitter Language with caching."""
        if language_name not in _LANGUAGE_CACHE:
            _LANGUAGE_CACHE[language_name] = get_language(language_name)  # type: ignore[arg-type]
        return _LANGUAGE_CACHE[language_name]

    @staticmethod
    def _get_parser(language_name: str) -> tree_sitter.Parser:
        """Fetch a tree-sitter Parser with caching."""
        if language_name not in _PARSER_CACHE:
            _PARSER_CACHE[language_name] = get_parser(language_name)  # type: ignore[arg-type]
        return _PARSER_CACHE[language_name]

    def _get_compiled_queries(self) -> Dict[str, tree_sitter.Query]:
        """Compile and cache queries for the current language on-demand."""
        if self.language_name not in _QUERY_CACHE:
            query_strings: Dict[str, str] = self._create_queries()
            _QUERY_CACHE[self.language_name] = {
                name: self.language.query(qstr) for name, qstr in query_strings.items()
            }
        return _QUERY_CACHE[self.language_name]

    def _create_queries(self) -> Dict[str, str]:
        """Return raw query strings keyed by a descriptive name."""
        base_dir: Path = self.config.query_dir

        query_file_map: Dict[str, str] = {
            "module_docstring": "module_docstring.scm",
            "global_variables": "global_variables.scm",
            "module_functions": "module_functions.scm",
            "module_classes": "module_classes.scm",
            "class_variables": "class_variables.scm",
            "class_methods": "class_methods.scm",
            "nested_functions": "nested_functions.scm",
            "function_calls": "function_calls.scm",
        }

        query_strings: Dict[str, str] = {}
        for key, filename in query_file_map.items():
            file_path = base_dir / filename
            if not file_path.exists():
                # The `function_calls` query is optional to allow gradual rollout
                if key == "function_calls":
                    continue
                raise FileNotFoundError(f"Query file not found: {file_path}")
            query_strings[key] = file_path.read_text()

        return query_strings
    
    def extract_structural_signature(self, file_path: str) -> StructuralSignature:
        """Extract structural signature from a source code file."""
        # Read the file content as bytes for correct offset handling
        with open(file_path, 'rb') as f:
            source_bytes = f.read()
            
        # Parse the source code (tree-sitter expects bytes)
        tree: tree_sitter.Tree = self.parser.parse(source_bytes)
        root_node: tree_sitter.Node = tree.root_node
        
        # Extract components
        module_docstring: Optional[str] = self._extract_module_docstring(root_node, source_bytes)
        global_variables: List[VariableInfo] = self._extract_global_variables(root_node, source_bytes)
        functions: List[FunctionInfo] = self._extract_functions(root_node, source_bytes)
        classes: List[ClassInfo] = self._extract_classes(root_node, source_bytes)
        
        return StructuralSignature(
            module_docstring=module_docstring,
            global_variables=global_variables,
            functions=functions,
            classes=classes
        )
    
    def _extract_module_docstring(self, root_node: tree_sitter.Node, source: bytes) -> Optional[str]:
        """Extract module-level docstring."""
        captures: Dict[str, List[tree_sitter.Node]] = self.queries['module_docstring'].captures(root_node)
        
        cap_name = self.config.cap("module")
        if cap_name in captures and captures[cap_name]:
            node: tree_sitter.Node = captures[cap_name][0]
            docstring: str = source[node.start_byte:node.end_byte].decode('utf-8')
            return self._clean_string_literal(docstring)
        
        return None
    
    def _extract_global_variables(self, root_node: tree_sitter.Node, source: bytes) -> List[VariableInfo]:
        """Extract module-level variable declarations."""
        captures = self.queries['global_variables'].captures(root_node)
        
        variables: List[VariableInfo] = []
        seen_assignments: set = set()
        
        var_stmt_cap = self.config.cap("var_statement")
        
        if var_stmt_cap in captures:
            for node in captures[var_stmt_cap]:
                if self._is_at_module_level(node):
                    start_line = node.start_point[0] + 1
                    end_line = node.end_point[0] + 1
                    signature = source[node.start_byte:node.end_byte].decode('utf-8').strip()
                    
                    if (start_line, signature) not in seen_assignments:
                        seen_assignments.add((start_line, signature))
                        variables.append(VariableInfo(
                            start_line=start_line,
                            end_line=end_line,
                            signature=signature
                        ))
        
        return variables
    
    def _extract_functions(self, root_node: tree_sitter.Node, source: bytes) -> List[FunctionInfo]:
        """Extract module-level function definitions using matches."""
        matches: List[tuple] = self.queries['module_functions'].matches(root_node)
        
        functions: List[FunctionInfo] = []
        seen: set = set()
        
        for match_id, captures in matches:
            func_node: Optional[tree_sitter.Node] = None
            # Capture names used in query files
            func_with_decor_cap: str = self.config.cap("func_with_decorators")
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
                signature: str = source[func_node.start_byte:func_node.end_byte].decode('utf-8')
                signature_lines: List[str] = signature.split('\n')
                sig_parts: List[str] = []
                for line in signature_lines:
                    sig_parts.append(line)
                    if line.rstrip().endswith(':'):
                        break
                
                # Extract docstring if present (@docstring capture in query)
                docstring: Optional[str] = None
                func_doc_cap: str = self.config.cap("function")  # maps to "docstring"
                if func_doc_cap in captures:
                    docstring_node: tree_sitter.Node = captures[func_doc_cap][0]
                    docstring = self._clean_string_literal(
                        source[docstring_node.start_byte:docstring_node.end_byte].decode('utf-8')
                    )
                
                # Extract nested functions
                actual_func_def = captures.get(function_node_cap, [None])[0]
                nested_functions: List[FunctionInfo] = []
                if actual_func_def:
                    nested_functions = self._extract_nested_functions_for_node(actual_func_def, source)
                
                # Extract function calls
                function_calls: List[str] = []
                if actual_func_def:
                    function_calls = self._extract_function_calls_for_node(actual_func_def, source)
                
                func_sig: str = '\n'.join(sig_parts)
                key: tuple = (start_line, func_sig)
                if key not in seen:
                    seen.add(key)
                    functions.append(FunctionInfo(
                        start_line=start_line,
                        end_line=end_line,
                        signature=func_sig,
                        docstring=docstring,
                        function_calls=function_calls,
                        nested_functions=nested_functions
                    ))
        
        return sorted(functions, key=lambda f: f.start_line)
    
    def _extract_classes(self, root_node: tree_sitter.Node, source: bytes) -> List[ClassInfo]:
        """Extract class definitions with their methods and variables using matches."""
        matches = self.queries['module_classes'].matches(root_node)
        
        classes = []
        
        for match_id, captures in matches:
            class_node: Optional[tree_sitter.Node] = None
            class_with_decor_cap = self.config.cap("class_with_decorators")
            class_def_cap = self.config.cap("class_def")

            if class_with_decor_cap in captures:
                class_node = captures[class_with_decor_cap][0]
            elif class_def_cap in captures:
                class_node = captures[class_def_cap][0]
            
            if class_node:
                start_line = class_node.start_point[0] + 1
                end_line = class_node.end_point[0] + 1
                
                # Extract signature
                signature = source[class_node.start_byte:class_node.end_byte].decode('utf-8')
                signature_lines = signature.split('\n')
                sig_parts = []
                for line in signature_lines:
                    sig_parts.append(line)
                    if line.rstrip().endswith(':'):
                        break
                
                # Extract docstring if present
                docstring = None
                class_doc_cap = self.config.cap("class")
                if class_doc_cap in captures:
                    docstring_node = captures[class_doc_cap][0]
                    docstring = self._clean_string_literal(
                        source[docstring_node.start_byte:docstring_node.end_byte].decode('utf-8')
                    )
                
                # Get the actual class_definition node for extracting variables and methods
                actual_class_def = captures[class_def_cap][0] if class_def_cap in captures else None
                
                # Extract class variables and methods
                class_variables = []
                methods = []
                
                if actual_class_def:
                    class_variables = self._extract_class_variables_for_node(actual_class_def, source)
                    methods = self._extract_methods_for_node(actual_class_def, source)
                
                classes.append(ClassInfo(
                    start_line=start_line,
                    end_line=end_line,
                    signature='\n'.join(sig_parts),
                    docstring=docstring,
                    class_variables=class_variables,
                    methods=methods,
                    nested_classes=[]  # TODO: Implement nested class extraction
                ))
        
        return sorted(classes, key=lambda c: c.start_line)
    
    def _extract_class_variables_for_node(self, class_node: tree_sitter.Node, source: bytes) -> List[VariableInfo]:
        """Extract class variables for a specific class node."""
        captures = self.queries['class_variables'].captures(class_node)
        
        variables = []
        seen = set()
        
        var_stmt_cap = self.config.cap("var_statement")

        if var_stmt_cap in captures:
            for node in captures[var_stmt_cap]:
                if self._is_class_level_variable(node, class_node):
                    start_line = node.start_point[0] + 1
                    end_line = node.end_point[0] + 1
                    signature = source[node.start_byte:node.end_byte].decode('utf-8').strip()
                    
                    key = (start_line, signature)
                    if key not in seen:
                        seen.add(key)
                        variables.append(VariableInfo(
                            start_line=start_line,
                            end_line=end_line,
                            signature=signature
                        ))
        
        return variables
    
    def _extract_methods_for_node(self, class_node: tree_sitter.Node, source: bytes) -> List[FunctionInfo]:
        """Extract methods for a specific class node using matches."""
        matches = self.queries['class_methods'].matches(class_node)
        
        methods = []
        
        for match_id, captures in matches:
            method_node: Optional[tree_sitter.Node] = None
            method_with_decor_cap = self.config.cap("method_with_decorators")
            method_def_cap = self.config.cap("method_def")

            if method_with_decor_cap in captures:
                method_node = captures[method_with_decor_cap][0]
            elif method_def_cap in captures:
                method_node = captures[method_def_cap][0]
            
            if method_node:
                start_line = method_node.start_point[0] + 1
                end_line = method_node.end_point[0] + 1
                
                # Extract signature
                signature = source[method_node.start_byte:method_node.end_byte].decode('utf-8')
                signature_lines = signature.split('\n')
                sig_parts = []
                for line in signature_lines:
                    sig_parts.append(line)
                    if line.rstrip().endswith(':'):
                        break
                
                # Extract docstring if present
                docstring = None
                method_doc_cap = self.config.cap("method")
                if method_doc_cap in captures:
                    docstring_node = captures[method_doc_cap][0]
                    docstring = self._clean_string_literal(
                        source[docstring_node.start_byte:docstring_node.end_byte].decode('utf-8')
                    )
                
                # Extract nested functions for this method
                actual_method_def = captures.get(method_def_cap, [None])[0]
                nested_functions = []
                if actual_method_def:
                    nested_functions = self._extract_nested_functions_for_node(actual_method_def, source)
                
                # Extract function calls inside this method
                function_calls: List[str] = []
                if actual_method_def:
                    function_calls = self._extract_function_calls_for_node(actual_method_def, source)
                
                methods.append(FunctionInfo(
                    start_line=start_line,
                    end_line=end_line,
                    signature='\n'.join(sig_parts),
                    docstring=docstring,
                    function_calls=function_calls,
                    nested_functions=nested_functions
                ))
        
        return sorted(methods, key=lambda m: m.start_line)
    
    def _extract_nested_functions_for_node(self, parent_func_node: tree_sitter.Node, source: bytes) -> List[FunctionInfo]:
        """Extract immediate nested functions within a specific function node.
        
        This method only extracts functions that are direct children of the parent
        function, not grandchildren or deeper descendants. Each extracted function
        is recursively processed to find its own nested functions.
        """
        matches: List[tuple] = self.queries['nested_functions'].matches(parent_func_node)
        
        nested_functions: List[FunctionInfo] = []
        
        for match_id, captures in matches:
            nested_func_node: Optional[tree_sitter.Node] = None
            nested_with_decor_cap = self.config.cap("nested_func_with_decorators")
            nested_def_cap = self.config.cap("nested_func_def")

            if nested_with_decor_cap in captures:
                nested_func_node = captures[nested_with_decor_cap][0]
            elif nested_def_cap in captures:
                nested_func_node = captures[nested_def_cap][0]
            
            if nested_func_node:
                # Filter out grandchildren and deeper descendants
                if not self._is_immediate_child_function(nested_func_node, parent_func_node):
                    continue
                    
                start_line: int = nested_func_node.start_point[0] + 1
                end_line: int = nested_func_node.end_point[0] + 1
                
                # Extract signature
                signature: str = source[nested_func_node.start_byte:nested_func_node.end_byte].decode('utf-8')
                signature_lines: List[str] = signature.split('\n')
                sig_parts: List[str] = []
                for line in signature_lines:
                    sig_parts.append(line)
                    if line.rstrip().endswith(':'):
                        break
                
                # Extract docstring if present
                docstring: Optional[str] = None
                nested_doc_cap = self.config.cap("nested_function")
                if nested_doc_cap in captures:
                    docstring_node: tree_sitter.Node = captures[nested_doc_cap][0]
                    docstring = self._clean_string_literal(
                        source[docstring_node.start_byte:docstring_node.end_byte].decode('utf-8')
                    )
                
                # Recursively extract nested functions within this nested function
                actual_nested_def: Optional[tree_sitter.Node] = captures.get(nested_def_cap, [None])[0]
                deeper_nested_functions: List[FunctionInfo] = []
                if actual_nested_def:
                    deeper_nested_functions = self._extract_nested_functions_for_node(actual_nested_def, source)
                
                nested_functions.append(FunctionInfo(
                    start_line=start_line,
                    end_line=end_line,
                    signature='\n'.join(sig_parts),
                    docstring=docstring,
                    function_calls=self._extract_function_calls_for_node(nested_func_node, source),
                    nested_functions=deeper_nested_functions
                ))
        
        return sorted(nested_functions, key=lambda f: f.start_line)
    
    def _is_at_module_level(self, node: tree_sitter.Node) -> bool:
        """Check if a node is at top-level scope using language config."""
        parent = node.parent
        while parent:
            if parent.type in self.config.container_nodes:
                return False
            parent = parent.parent
        return True
    
    def _is_class_level_variable(self, node: tree_sitter.Node, class_node: tree_sitter.Node) -> bool:
        """Check if a variable is at class level (not inside a method) using language config."""
        parent = node.parent
        while parent and parent != class_node:
            if parent.type in self.config.method_nodes:
                return False
            parent = parent.parent
        return True
    
    def _clean_string_literal(self, string_literal: str) -> str:
        """Delegate string cleaning to language config."""
        return self.config.clean_doc(string_literal)
    
    def _is_immediate_child_function(self, child_node: tree_sitter.Node, parent_func_node: tree_sitter.Node) -> bool:
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
        while current and current.type in self.config.block_nodes:
            current = current.parent
        
        # Check if we reached the parent function directly
        return current == parent_func_node

    # -------------------------------------------------------------------
    # Function-call extraction helpers
    # -------------------------------------------------------------------
    
    def _get_nested_function_ranges(self, func_node: tree_sitter.Node) -> List[Tuple[int, int]]:
        """Get byte ranges of immediate nested functions within a function node.
        
        Only returns ranges for functions that are direct children of the given
        function node, not grandchildren or deeper descendants.
        
        Returns:
            List of (start_byte, end_byte) tuples for each immediate child function.
        """
        if "nested_functions" not in self.queries:
            return []
            
        # Get all nested function nodes
        matches = self.queries['nested_functions'].matches(func_node)
        nested_ranges = []
        
        for match_id, captures in matches:
            # Look for the nested function node (with or without decorators)
            nested_func_node = None
            nested_with_decor_cap = self.config.cap("nested_func_with_decorators")
            nested_def_cap = self.config.cap("nested_func_def")
            
            if nested_with_decor_cap in captures:
                nested_func_node = captures[nested_with_decor_cap][0]
            elif nested_def_cap in captures:
                nested_func_node = captures[nested_def_cap][0]
                
            if nested_func_node:
                # Only include immediate children to match _extract_nested_functions_for_node behavior
                if not self._is_immediate_child_function(nested_func_node, func_node):
                    continue
                nested_ranges.append((nested_func_node.start_byte, nested_func_node.end_byte))
                
        return nested_ranges

    def _extract_function_calls_for_node(self, func_node: tree_sitter.Node, source: bytes, start_line: Optional[int] = None, end_line: Optional[int] = None) -> List[str]:
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
        captures = self.queries["function_calls"].captures(func_node)
        
        cap_name: str = self.config.cap("function_call")

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
                start <= call_start < end 
                for start, end in nested_ranges
            )
            if not is_within_nested:
                direct_call_nodes.append(call_node)
        
        # Sort by start byte to preserve lexical order
        direct_call_nodes_sorted = sorted(direct_call_nodes, key=lambda n: n.start_byte)
        
        # Extract and return the call text
        return [source[n.start_byte:n.end_byte].decode('utf-8').strip() for n in direct_call_nodes_sorted] 