from typing import Dict, List
from unoplat_code_confluence.data_models.unoplat_import import ImportedName, UnoplatImport
from unoplat_code_confluence.data_models.chapi_unoplat_node import ChapiUnoplatNode
from unoplat_code_confluence.data_models.unoplat_project_dependency import UnoplatProjectDependency
from unoplat_code_confluence.language_custom_parsing.import_segregation.import_segregation_strategy import ImportSegregationStrategy
from unoplat_code_confluence.language_custom_parsing.import_segregation.utils.read_programming_file import ProgrammingFileReader
import ast
from collections import defaultdict
from unoplat_code_confluence.data_models.chapi_unoplat_import import ChapiUnoplatImport

class PythonImportSegregationStrategy(ImportSegregationStrategy):
    
    def __init__(self):
        self.file_reader = ProgrammingFileReader()
    
    
    def process_metadata(self, local_workspace_path: str, class_metadata: ChapiUnoplatNode, dependencies: set[str]) -> Dict[str,Dict[str,UnoplatImport]]:
        
        file_content: str = self.file_reader.read_file(local_workspace_path)
        imports: List[ChapiUnoplatImport] = self.parse_imports(file_content)
        
    
    
    def parse_imports(self, code: str) -> List[ChapiUnoplatImport]:
        tree = ast.parse(code)
        imports_dict: Dict[str, List[ImportedName]] = defaultdict(list)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                # Handle 'import module' statements
                for item in node.names:
                    module_name:str = item.name
                    alias_name:str = item.asname or module_name
                    imported_name: ImportedName = ImportedName(original_name=module_name, alias=alias_name)
                    imports_dict[module_name].append(imported_name)
            elif isinstance(node, ast.ImportFrom):
                # Handle 'from module import name(s)' statements
                module_name:str = node.module or ''
                for item in node.names:
                    original_name:str = item.name
                    alias_name:str = item.asname or original_name
                    imported_name: ImportedName = ImportedName(original_name=original_name, alias=alias_name)
                    imports_dict[module_name].append(imported_name)
        
        # Convert the dictionary to a list of Import objects
        imports: List[ChapiUnoplatImport] = []
        for source, imported_names in imports_dict.items():
            usage_name: List[str] = [item.alias for item in imported_names]
            imp: ChapiUnoplatImport = ChapiUnoplatImport(Source=source, UsageName=usage_name)
            imports.append(imp)    
        
        return imports    
        