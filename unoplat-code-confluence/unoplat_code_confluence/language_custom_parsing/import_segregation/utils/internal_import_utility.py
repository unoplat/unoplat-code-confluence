from typing import List
from stdlib_list import stdlib_list

from unoplat_code_confluence.data_models.chapi_unoplat_import import ChapiUnoplatImport



class InternalImportUtility:
    
    def __init__(self, programming_language_version: str | None = None):
        self.stdlib_modules = set(stdlib_list(programming_language_version))
    
    
    
    def get_system_imports(self, imports: List[ChapiUnoplatImport]) -> List[ChapiUnoplatImport]:
        
        return [imp for imp in imports if imp.source in self.stdlib_modules]
