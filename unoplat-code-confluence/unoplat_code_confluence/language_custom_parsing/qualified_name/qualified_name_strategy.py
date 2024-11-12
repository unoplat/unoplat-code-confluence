from abc import ABC, abstractmethod

class QualifiedNameStrategy(ABC):
    @abstractmethod
    def get_qualified_name(self, node_name: str, node_file_path: str, local_workspace_path: str, codebase_name: str) -> str:
        """Get qualified name for the node based on its relative path to workspace.
        
        Args:
            node_file_path: Path to the node's file
            local_workspace_path: Base workspace path
            codebase_name: Name of the codebase
            
        Returns:
            str: Qualified name based on language-specific rules
        """
        pass 