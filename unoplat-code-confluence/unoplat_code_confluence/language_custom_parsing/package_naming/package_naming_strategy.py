from abc import ABC, abstractmethod
import os
from typing import Optional

class UnsupportedLanguageError(Exception):
    """Exception raised when an unsupported programming language is encountered."""
    pass

class PackageNamingStrategy(ABC):
    """Interface for language-specific package naming strategies."""
    
    @abstractmethod
    def get_package_name(self, file_path: str, workspace_path: str, node_name: Optional[str] = None) -> str:
        """
        Determine the package name for a given file path and workspace.
        
        Args:
            file_path: Path to the source file
            workspace_path: Root path of the workspace/project
            node_name: Optional node name for languages that might need it
            
        Returns:
            str: The determined package name
            
        Raises:
            UnsupportedLanguageError: If the programming language is not supported
        """
        pass



class DefaultPackageNamingStrategy(PackageNamingStrategy):
    """Default package naming strategy for unsupported languages."""
    
    def get_package_name(self, file_path: str, workspace_path: str, node_name: Optional[str] = None) -> str:
        raise UnsupportedLanguageError("This programming language is not supported") 