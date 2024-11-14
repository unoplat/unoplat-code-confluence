from typing import Dict, List
from unoplat_code_confluence.data_models.unoplat_import import ImportedName
from unoplat_code_confluence.data_models.chapi_unoplat_node import ChapiUnoplatNode
from unoplat_code_confluence.data_models.unoplat_import_type import ImportType
from unoplat_code_confluence.language_custom_parsing.import_segregation.python.python_external_Imports_segregation import PythonExternalImportsSegregation

import ast
from collections import defaultdict
from unoplat_code_confluence.data_models.chapi_unoplat_import import ChapiUnoplatImport
from unoplat_code_confluence.parser.python.utils.python_system_import_utility import PythonSystemImportUtility
from unoplat_code_confluence.parser.python.utils.read_programming_file import ProgrammingFileReader

class PythonImportSegregationStrategy:
    
    def __init__(self, dependencies: set[str], programming_language_version: str | None = None):
        self.file_reader = ProgrammingFileReader()
        self.system_import_utility = PythonSystemImportUtility(programming_language_version)
        self.external_dependencies = dependencies
        self.external_imports_segregation = PythonExternalImportsSegregation(dependencies)
        
    def process_metadata(self, local_workspace_path: str, class_metadata: ChapiUnoplatNode) -> Dict[str,Dict[str,ChapiUnoplatImport]]:
        file_content: str = self.file_reader.read_file(local_workspace_path)
        # Get imports as dictionary with source as key
        imports_dict: Dict[str, ChapiUnoplatImport] = self.consolidate_imports(file_content)
        
        # Get system imports as dictionary
        system_imports: Dict[str, ChapiUnoplatImport] = self.system_import_utility.get_system_imports(imports_dict)
        
        # Remove system imports from original dict to pass remaining to external segregation
        remaining_imports_external_internal = {
            source: imp for source, imp in imports_dict.items() 
            if source not in system_imports
        }
        
        # Convert remaining dict back to list for external segregation
        external_imports: Dict[str,ChapiUnoplatImport] = self.external_imports_segregation.segregate_external_imports(remaining_imports_external_internal)
        
        #now we have done system and external so remaining are internal custom classes lets filter for that
        internal_custom_imports = {
            source: imp for source , imp in remaining_imports_external_internal.items()
            if source not in external_imports
        }
        
        
        
        #modify internal imports to absolute paths
        
        final_segregated_dict: Dict[str,Dict[str,ChapiUnoplatImport]] = {}
        final_segregated_dict[ImportType.SYSTEM] = system_imports
        final_segregated_dict[ImportType.EXTERNAL] = external_imports
        final_segregated_dict[ImportType.INTERNAL] = internal_custom_imports
        
        return final_segregated_dict
        
    def _process_import_item(self, module_name: str, item: ast.alias, imports_dict: Dict[str, List[ImportedName]]) -> None:
        original_name: str = item.name
        alias_name: str = item.asname or original_name
        imported_name: ImportedName = ImportedName(original_name=original_name, alias=alias_name)
        imports_dict[module_name].append(imported_name)

    def consolidate_imports(self, code: str) -> Dict[str, ChapiUnoplatImport]:
        tree = ast.parse(code)
        imports_dict: Dict[str, List[ImportedName]] = defaultdict(list)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                # Handle 'import module' statements
                for item in node.names:
                    self._process_import_item(item.name, item, imports_dict)
            elif isinstance(node, ast.ImportFrom):
                # Handle 'from module import name(s)' statements
                module_name: str = node.module or ''
                for item in node.names:
                    self._process_import_item(module_name, item, imports_dict)
        
        # Convert the dictionary to a list of Import objects
        imports: Dict[str, ChapiUnoplatImport] = {}
        for source, imported_names in imports_dict.items():
            usage_name: List[str] = [item.original_name if item.alias is None else item.alias for item in imported_names]
            imports[source] = ChapiUnoplatImport(Source=source, UsageName=usage_name)
        return imports    
        