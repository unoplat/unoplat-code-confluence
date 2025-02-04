# Standard Library
import os


class PythonQualifiedNameStrategy:
    def get_qualified_name(self, node_name: str, node_file_path: str, node_type: str, import_prefix: str) -> str:
        """Get qualified name for Python nodes.

        For Python, the qualified name follows the format:
        package.subpackage.classname
        where classname is the actual node_name rather than the filename

        Args:
            node_name: The actual name of the class/node
            node_file_path: Path to the node's file
            node_type: Type of the node (e.g., 'CLASS')
            import_prefix: The prefix used for absolute imports (e.g., 'unoplat-code-confluence')

        Returns:
            str: Qualified name in format package.subpackage.node_name
        """
        # Find the position of import_prefix in the path
        prefix_pos = node_file_path.find(import_prefix)
        if prefix_pos == -1:
            raise ValueError(f"Import prefix '{import_prefix}' not found in path '{node_file_path}'")

        # Get the path starting from the import prefix
        path_from_prefix = node_file_path[prefix_pos:]
        
        # Remove the .py extension
        path_without_ext = os.path.splitext(path_from_prefix)[0]

        # Split the path into parts and convert to package notation
        path_parts = path_without_ext.replace("/", ".").replace("\\", ".").split(".")

        # Replace the last part (filename) with the actual node name for CLASS types
        if node_type == "CLASS":
            path_parts[-1] = node_name

        # Join the path parts
        qualified_name = ".".join(path_parts)

        return qualified_name
