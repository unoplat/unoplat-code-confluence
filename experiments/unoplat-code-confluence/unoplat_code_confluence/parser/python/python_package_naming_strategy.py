# Standard Library
import os


class PythonPackageNamingStrategy:
    """Python-specific package naming strategy."""
    
    def get_package_name(self, file_path: str, workspace_path: str) -> str:
        relative_path = os.path.relpath(file_path, workspace_path)
        package_name = os.path.dirname(relative_path).replace(os.path.sep, '.')
        
        return package_name