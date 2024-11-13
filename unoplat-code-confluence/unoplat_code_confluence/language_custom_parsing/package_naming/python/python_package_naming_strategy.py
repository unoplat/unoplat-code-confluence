from unoplat_code_confluence.language_custom_parsing.package_naming.package_naming_strategy import PackageNamingStrategy
from typing import Optional
import os

class PythonPackageNamingStrategy(PackageNamingStrategy):
    """Python-specific package naming strategy."""
    
    def get_package_name(self, file_path: str, workspace_path: str, codebase_name: Optional[str] = None) -> str:
        relative_path = os.path.relpath(file_path, workspace_path)
        package_name = os.path.dirname(relative_path).replace(os.path.sep, '.')
        if not codebase_name:
            return package_name if package_name else 'root'
        if not package_name:
            return codebase_name
        return f"{codebase_name}.{package_name}"