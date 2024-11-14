from typing import List, Dict
from stdlib_list import stdlib_list

from unoplat_code_confluence.data_models.chapi_unoplat_import import ChapiUnoplatImport
from unoplat_code_confluence.data_models.unoplat_import_type import ImportType



class PythonSystemImportUtility:
    
    def __init__(self, programming_language_version: str | None = None):
        self.stdlib_modules = set(stdlib_list(programming_language_version))
    
    
    
    def get_system_imports(self, imports_dict: Dict[str, ChapiUnoplatImport]) -> Dict[str, ChapiUnoplatImport]:
        system_imports: Dict[str, ChapiUnoplatImport] = {}
        for source, imp in imports_dict.items():
            if source in self.stdlib_modules:
                imp.import_type = ImportType.SYSTEM
                system_imports[source] = imp
        return system_imports
