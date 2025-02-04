# Standard Library
import os


class PythonQualifiedNameStrategy:
    def get_qualified_name(self, node_name: str, node_file_path: str, local_workspace_path: str, node_type: str) -> str:
        """Get qualified name for Python nodes.

        For Python, the qualified name follows the format:
        package.subpackage.classname
        where classname is the actual node_name rather than the filename

        Args:
            node_name: The actual name of the class/node
            node_file_path: Path to the node's file
            local_workspace_path: Base workspace path

        Returns:
            str: Qualified name in format package.subpackage.node_name
        """
        # Get relative path and remove .py extension
        relative_path = os.path.relpath(node_file_path, local_workspace_path)
        path_without_ext = os.path.splitext(relative_path)[0]

        # Split the path into parts
        path_parts = path_without_ext.replace("/", ".").replace("\\", ".").split(".")

        # Replace the last part (filename) with the actual node name
        if node_type == "CLASS":
            path_parts.append(node_name)

        # Join the path parts without adding codebase_name since it's already in the path
        qualified_name = ".".join(path_parts)

        return qualified_name
