import os
from unoplat_code_confluence.language_custom_parsing.qualified_name.qualified_name_strategy import QualifiedNameStrategy

class PythonQualifiedNameStrategy(QualifiedNameStrategy):
    def get_qualified_name(self, node_name: str, node_file_path: str, local_workspace_path: str, codebase_name: str) -> str:
        """Get qualified name for Python nodes.
        
        For Python, the qualified name follows the format:
        rootcodebasename.package.subpackage.classname
        where classname is the actual node_name rather than the filename
        
        Args:
            node_name: The actual name of the class/node
            node_file_path: Path to the node's file
            local_workspace_path: Base workspace path
            codebase_name: Name of the codebase
            
        Returns:
            str: Qualified name in format codebase_name.package.subpackage.node_name
        """
        # Get relative path and remove .py extension
        relative_path = os.path.relpath(node_file_path, local_workspace_path)
        path_without_ext = os.path.splitext(relative_path)[0]
        
        # Split the path into parts
        path_parts = path_without_ext.replace('/', '.').replace('\\', '.').split('.')
        
        # Replace the last part (filename) with the actual node name
        path_parts[-1] = node_name
        
        # Combine codebase name with the path
        qualified_name = f"{codebase_name}.{'.'.join(path_parts)}"
        
        return qualified_name 