# Standard Library
# First Party
from src.code_confluence_flow_bridge.models.chapi.chapi_node import ChapiNode
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_import import ImportedName, UnoplatImport
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_import_type import ImportType
from src.code_confluence_flow_bridge.parser.python.utils.read_programming_file import ProgrammingFileReader
from src.code_confluence_flow_bridge.parser.tree_sitter.code_confluence_tree_sitter import CodeConfluenceTreeSitter

from typing import Dict, List, Tuple

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
        
        # Updated query to better handle different import types
        self.import_query = self.parser.language.query("""
            (import_statement 
                name: (dotted_name) @module_name
            )

            (import_from_statement
                module_name: (dotted_name) @from_module
                name: (dotted_name) @imported_name
            )

            (aliased_import
                name: (dotted_name) @original_name
                alias: (identifier) @alias_name
            )
        """)

    def _is_internal_import(self, module_path: str, source_directory: str) -> bool:
        """Check if an import is internal based on source directory."""
        return (
            module_path.startswith(f"{source_directory}.") or 
            module_path == source_directory
        )

    def _extract_module_path(self, node: Node) -> str:
        """Extract the module path from a Tree-sitter node."""
        return node.text.decode('utf-8').strip()

    def _process_from_import(self, module_node: Node, name_node: Node) -> Tuple[str, List[ImportedName]]:
        """Process a 'from' import statement."""
        source = self._extract_module_path(module_node)
        name_text = self._extract_module_path(name_node)
        
        imported_names = []
        if " as " in name_text:
            original, alias = name_text.split(" as ")
            imported_names.append(ImportedName(original_name=original.strip(), alias=alias.strip()))
        else:
            imported_names.append(ImportedName(original_name=name_text))
            
        return source, imported_names

    def _process_direct_import(self, module_node: Node) -> Tuple[str, List[ImportedName]]:
        """Process a direct import statement."""
        module_path = self._extract_module_path(module_node)
        
        if " as " in module_path:
            original, alias = module_path.split(" as ")
            return original.strip(), [ImportedName(original_name=original.strip(), alias=alias.strip())]
        else:
            return module_path, [ImportedName(original_name=module_path)]

    def process_imports(self, source_directory: str, class_metadata: ChapiNode) -> Dict[ImportType, List[UnoplatImport]]:
        """Process and categorize imports from a Python source file.

        Args:
            class_metadata: Metadata about the class/file being processed,
                          including file path and source directory information

        Returns:
            Dictionary mapping ImportType to list of UnoplatImport objects.
        """
        file_content: str = self.file_reader.read_file(class_metadata.file_path)
        
        
        sections: Dict[ImportType, List[UnoplatImport]] = {
            ImportType.INTERNAL: [],
            ImportType.STANDARD: [],
            ImportType.EXTERNAL: [],
            ImportType.LOCAL: []
        }
        
        tree = self.parser.parse(bytes(file_content, "utf8"))
        captures = self.import_query.captures(tree.root_node)
        
        current_module = None
        
        # Handle potential extra capture elements using extended unpacking
        for node, capture_name, *_ in captures:  # Added *_ to handle extra elements
            if capture_name == "module_name":
                source, imported_names = self._process_direct_import(node)
                import_type = ImportType.INTERNAL if self._is_internal_import(source, source_directory) else ImportType.STANDARD
                sections[import_type].append(
                    UnoplatImport(
                        Source=source,
                        UsageName=imported_names,
                        ImportType=import_type
                    )
                )
            elif capture_name == "from_module":
                current_module = node
            elif capture_name == "imported_name" and current_module:
                source, imported_names = self._process_from_import(current_module, node)
                import_type = ImportType.INTERNAL if self._is_internal_import(source, source_directory) else ImportType.EXTERNAL
                sections[import_type].append(
                    UnoplatImport(
                        Source=source,
                        UsageName=imported_names,
                        ImportType=import_type
                    )
                )
        
        return sections
