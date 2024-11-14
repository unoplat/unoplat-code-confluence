from typing import Dict, List
from unoplat_code_confluence.data_models.chapi_unoplat_import import ChapiUnoplatImport
from unoplat_code_confluence.data_models.unoplat_import_type import ImportType


class PythonExternalImportsSegregation:
    
    def __init__(self,dependencies: set[str]):
        self.external_dependencies = dependencies
        
    def segregate_external_imports(self, imports: Dict[str,ChapiUnoplatImport]) -> Dict[str,ChapiUnoplatImport]:
        external_imports:Dict[str,ChapiUnoplatImport] = {}
        
        for source,import_item in imports.items():
            if import_item.source:
                # Get the root package name (first part before any dots)
                root_package = import_item.source.split('.')[0]
                
                # Check if the root package is in external dependencies
                if root_package in self.external_dependencies:
                    import_item.import_type = ImportType.EXTERNAL
                    external_imports[source]=(import_item)
        
        return external_imports
    
    