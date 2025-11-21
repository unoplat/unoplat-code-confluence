# Standard Library
import os


class PythonPackageNamingStrategy:
    """Python-specific package naming strategy."""

    def get_package_name(self, file_path: str, import_prefix: str) -> str:
        """Get package name for Python files.

        Args:
            file_path: Full path to the Python file
            workspace_path: Path to the workspace (not used)
            import_prefix: The prefix used for absolute imports

        Returns:
            str: Package name in dot notation (e.g., 'package.subpackage')

        Example:
            For file_path = '/path/to/unoplat-code-confluence/src/package/subpackage/file.py'
            and import_prefix = 'unoplat-code-confluence'
            Returns: 'src.package.subpackage'
        """
        # Find the position of import_prefix in the path
        prefix_pos = file_path.find(import_prefix)
        if prefix_pos == -1:
            raise ValueError(
                f"Import prefix '{import_prefix}' not found in path '{file_path}'"
            )

        # Get the path starting from the import prefix
        path_from_prefix = file_path[prefix_pos:]

        # Get the directory path without the file name
        dir_path = os.path.dirname(path_from_prefix)

        # Convert path separators to dots and return
        package_name = dir_path.replace(os.path.sep, ".")

        return package_name
