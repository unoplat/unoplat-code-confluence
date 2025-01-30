# Standard Library
from typing import Dict, List

# First Party
from unoplat_code_confluence.data_models.chapi.chapi_node import ChapiNode
from unoplat_code_confluence.data_models.chapi_forge.unoplat_import import ImportedName, UnoplatImport
from unoplat_code_confluence.data_models.chapi_forge.unoplat_import_type import ImportType
from unoplat_code_confluence.parser.python.utils.python_import_comment_parser import PythonImportCommentParser
from unoplat_code_confluence.parser.python.utils.read_programming_file import ProgrammingFileReader


class PythonImportSegregationStrategy:
    """Strategy for segregating Python imports into different categories based on their types.
    
    This class processes Python source files to extract and categorize imports based on their
    types (standard library, external, internal, local). It handles various import patterns
    including aliased imports and multiline imports.
    
    Attributes:
        file_reader: Reader for accessing Python source files
        comment_parser: Parser for extracting imports based on section comments
        
    Note:
        Current limitations:
        1. Does not preserve inline comments on imports
        2. Does not handle comments between imports
        3. Only preserves section comments (# Standard Library, # Third Party, etc.)
        
        For handling comments, it's recommended to use tools like isort for import formatting
        before processing with this strategy.
    """
    
    def __init__(self):
        """Initialize the import segregation strategy with required components."""
        self.file_reader = ProgrammingFileReader()
        self.comment_parser = PythonImportCommentParser()
        
    def process_imports(
        self, class_metadata: ChapiNode
    ) -> Dict[ImportType, List[UnoplatImport]]:
        """Process and categorize imports from a Python source file.
        
        Reads a Python source file and processes its imports, categorizing them into
        different types (standard library, external, internal, local) based on section
        comments. Handles various import patterns including:
        - Simple imports: import os
        - Aliased imports: import pandas as pd
        - From imports: from pathlib import Path
        - Multiple imports: from os import path, getcwd
        - Aliased from imports: from datetime import datetime as dt
        - Multiline imports: from sqlalchemy import (Column, Integer)
        
        Args:
            class_metadata: Metadata about the class/file being processed,
                          including file path
        
        Returns:
            Dictionary mapping ImportType to list of UnoplatImport objects.
            Each UnoplatImport contains:
            - Source: The module being imported from
            - UsageName: List of ImportedName objects containing:
                - original_name: The original name being imported
                - alias: Optional alias if the import uses 'as'
            - ImportType: The category of the import (STANDARD, EXTERNAL, etc.)
            
        Example:
            For input file content:
            ```python
            # Standard Library
            import os
            from datetime import datetime as dt
            
            # Third Party
            import pandas as pd
            
            # First Party
            from myproject.utils import helper
            ```
            
            Returns:
            {
                ImportType.STANDARD: [
                    UnoplatImport(Source="os", UsageName=[ImportedName(original_name="os")]),
                    UnoplatImport(Source="datetime", 
                                UsageName=[ImportedName(original_name="datetime", alias="dt")])
                ],
                ImportType.EXTERNAL: [
                    UnoplatImport(Source="pandas", 
                                UsageName=[ImportedName(original_name="pandas", alias="pd")])
                ],
                ImportType.INTERNAL: [
                    UnoplatImport(Source="myproject.utils", 
                                UsageName=[ImportedName(original_name="helper")])
                ]
            }
        """
        file_content: str = self.file_reader.read_file(class_metadata.file_path)
        
        # Parse imports based on comments
        import_sections: Dict[ImportType, List[str]] = self.comment_parser.parse_import_sections(
            file_content
        )
        
        # Convert each section to UnoplatImport format
        final_segregated_dict: Dict[ImportType, List[UnoplatImport]] = {}
        
        for section_type, imports in import_sections.items():
            if imports:
                imports_list = []
                for import_str in imports:
                    parts = import_str.split()
                    
                    if parts[0] == 'from':
                        # Handle 'from module import name1 as n1, name2 as n2, ...' case
                        source = parts[1]
                        # Join all parts after 'import' and split by commas
                        import_names = ' '.join(parts[3:]).split(',')
                        # Clean up any whitespace and handle aliases
                        imported_names = []
                        for name in import_names:
                            name_parts = name.strip().split(' as ')
                            if len(name_parts) > 1:
                                # If there's an alias
                                imported_names.append(
                                    ImportedName(
                                        original_name=name_parts[0].strip(),
                                        alias=name_parts[1].strip().rstrip(',')
                                    )
                                )
                            else:
                                # If no alias
                                imported_names.append(
                                    ImportedName(original_name=name_parts[0].strip())
                                )
                    else:
                        # Handle 'import module as m1, module2 as m2' case
                        imports_list.extend(self._process_simple_imports(parts, section_type))
                    
                    if parts[0] == 'from':
                        imports_list.append(
                            UnoplatImport(
                                Source=source,
                                UsageName=imported_names,
                                ImportType=section_type
                            )
                        )
                final_segregated_dict[section_type] = imports_list
        
        return final_segregated_dict

    def _process_simple_imports(self, parts: List[str], section_type: ImportType) -> List[UnoplatImport]:
        """Process simple imports like 'import module as alias, module2 as alias2'.
        
        Args:
            parts: List of parts from splitting the import string
            section_type: Type of import section (STANDARD, EXTERNAL, etc.)
            
        Returns:
            List of UnoplatImport objects
        """
        result: List[UnoplatImport] = []
        current_module: List[str] = []
        
        for part in parts[1:]:  # Skip 'import'
            if part == 'as':
                continue
            if part.endswith(','):
                # End of current module
                current_module.append(part.rstrip(','))
                if len(current_module) > 1:
                    # Has alias
                    result.append(
                        UnoplatImport(
                            Source=current_module[0],
                            UsageName=[
                                ImportedName(
                                    original_name=current_module[0],
                                    alias=current_module[1]
                                )
                            ],
                            ImportType=section_type
                        )
                    )
                else:
                    # No alias
                    result.append(
                        UnoplatImport(
                            Source=current_module[0],
                            UsageName=[
                                ImportedName(original_name=current_module[0])
                            ],
                            ImportType=section_type
                        )
                    )
                current_module = []
            else:
                current_module.append(part)
        
        # Handle last module
        if current_module:
            if len(current_module) > 1:
                # Has alias
                result.append(
                    UnoplatImport(
                        Source=current_module[0],
                        UsageName=[
                            ImportedName(
                                original_name=current_module[0],
                                alias=current_module[1]
                            )
                        ],
                        ImportType=section_type
                    )
                )
            else:
                # No alias
                result.append(
                    UnoplatImport(
                        Source=current_module[0],
                        UsageName=[
                            ImportedName(original_name=current_module[0])
                        ],
                        ImportType=section_type
                    )
                )
        
        return result
