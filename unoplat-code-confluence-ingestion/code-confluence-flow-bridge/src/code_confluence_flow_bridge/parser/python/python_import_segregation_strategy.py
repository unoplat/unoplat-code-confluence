# Standard Library
# First Party
from src.code_confluence_flow_bridge.models.chapi.chapi_node import ChapiNode
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_import import (
    ImportedName,
    UnoplatImport,
)
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_import_type import (
    ImportType,
)
from src.code_confluence_flow_bridge.parser.python.utils.read_programming_file import (
    ProgrammingFileReader,
)
from src.code_confluence_flow_bridge.parser.tree_sitter.code_confluence_tree_sitter import (
    CodeConfluenceTreeSitter,
)

from typing import Dict, List, Optional

from tree_sitter import Node


class PythonImportSegregationStrategy:
    """Strategy for segregating Python imports into different categories based on their types.

    This class processes Python source files to extract and categorize imports based on their
    types using Tree-sitter parsing. It specifically identifies internal imports based on
    the source directory prefix.
    """

    def __init__(self, code_confluence_tree_sitter: CodeConfluenceTreeSitter):
        """Initialize the import segregation strategy with required components.
        
        Args:
            code_confluence_tree_sitter: Initialized Tree-sitter instance for Python
        """
        self.file_reader = ProgrammingFileReader()
        self.parser = code_confluence_tree_sitter.get_parser()
        
        
        

    def _is_internal_import(self, module_path: str, source_directory: str) -> bool:
        """Check if an import is internal based on source directory."""
        return (
            module_path.startswith(f"{source_directory}.") or 
            module_path == source_directory
        )

    def _extract_module_path(self, node: Node) -> str:
        """Extract the module path from a Tree-sitter node."""
        return node.text.decode('utf-8').strip()

    def _process_from_import_statement(
        self, node: Node, source_directory: str, code_bytes: bytes
    ) -> Optional[UnoplatImport]:
        """
        Process a from-import statement AST node using next_named_sibling to walk through imports.
        
        Args:
            node: The from-import statement node (dotted_name node captured as @module).
            source_directory: The source directory prefix for internal imports.
            code_bytes: The original source code bytes.
        
        Returns:
            A UnoplatImport object or None if parsing fails.
        """
        # Get the source from the dotted_name node (which is our @module capture)
        source: str = self._extract_module_path(node)
        
        usage_names: List[ImportedName] = []
        
        # Start with the first aliased_import after the 'import' keyword
        current = node.next_named_sibling
        
        # Walk through all aliased_imports using next_named_sibling
        while current:
            if current.type == "aliased_import":
                name_node = current.child(0)
                alias_node = current.child(2)
                
                if name_node:
                    name_text: str = name_node.text.decode("utf8").strip() #type: ignore
                    alias_text: Optional[str] = None
                    
                    if alias_node:
                        alias_text = alias_node.text.decode("utf8").strip() #type: ignore
                    
                    usage_names.append(
                        ImportedName(
                            original_name=name_text,
                            alias=alias_text
                        )
                    )
            elif current.type == "dotted_name":
                name_node = current.child(0)
                if name_node:
                    name_text: str = name_node.text.decode("utf8").strip() #type: ignore
                    usage_names.append(ImportedName(original_name=name_text))
            
            # Move to next sibling
            current = current.next_named_sibling
        
        if not usage_names:
            return None

        # Determine import type based on source prefix
        import_type = (
            ImportType.INTERNAL 
            if source.startswith(f"{source_directory}.") or source == source_directory
            else ImportType.EXTERNAL
        )
            
        return UnoplatImport(
            Source=source,
            UsageName=usage_names,
            ImportType=import_type
        )

    def process_imports(
        self, source_directory: str, class_metadata: ChapiNode
    ) -> Dict[ImportType, List[UnoplatImport]]:
        """Process and categorize imports from a Python source file.

        Args:
            source_directory: The source directory prefix for internal imports
            class_metadata: Metadata about the class/file being processed

        Returns:
            Dictionary mapping ImportType to list of UnoplatImport objects.
        """
        # Initialize sections dictionary
        sections: Dict[ImportType, List[UnoplatImport]] = {
            ImportType.INTERNAL: [],
            ImportType.STANDARD: [],
            ImportType.EXTERNAL: [],
            ImportType.LOCAL: []
        }

        # Read and parse the file
        file_content: str = self.file_reader.read_file(class_metadata.file_path) 
        code_bytes: bytes = file_content.encode("utf8")
        tree = self.parser.parse(code_bytes)

        # Define query to capture from-imports with the given source_directory
        # Escape dots in source_directory for the regex pattern
        escaped_prefix = source_directory.replace(".", "\\.")
        query = self.parser.language.query(
            f"""
            (
              import_from_statement
                 module_name: (dotted_name) @module
                 (#match? @module "^{escaped_prefix}")
            ) 
            """
        )

        # Get matches
        matches = query.matches(tree.root_node)

        # Process each match using next_named_sibling traversal
        for _, captures in matches:
            module_nodes = captures.get("module", [])
            for module_node in module_nodes:
                if result := self._process_from_import_statement(
                    module_node, source_directory, code_bytes
                ):
                    sections[result.import_type].append(result) #type:ignore

        return sections
