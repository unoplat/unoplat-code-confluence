# Standard Library
import os
import logging

logger = logging.getLogger(__name__)


class PythonQualifiedNameStrategy:
    def get_qualified_name(
        self,
        node_name: str,
        node_file_path: str,
        node_type: str,
        import_prefix: str
    ) -> str:
        """Get qualified name for Python nodes.

        For Python, the qualified name follows the format:
        package.subpackage.filename.classname
        where classname is the actual node_name

        Args:
            node_name: The actual name of the class/node
            node_file_path: Path to the node's file
            node_type: Type of the node (e.g., 'CLASS')
            import_prefix: The prefix used for absolute imports (e.g., 'unoplat-code-confluence')

        Returns:
            str: Qualified name in format package.subpackage.filename.node_name for CLASS types,
                 or package.subpackage.filename for other types
        """
        logger.debug(
            "Getting qualified name for node: name=%r, file_path=%r, type=%r, import_prefix=%r",
            node_name, node_file_path, node_type, import_prefix
        )

        # Find the position of import_prefix in the path
        prefix_pos = node_file_path.find(import_prefix)
        if prefix_pos == -1:
            logger.error(
                "Import prefix '%s' not found in path '%s'", import_prefix, node_file_path
            )
            raise ValueError(f"Import prefix '{import_prefix}' not found in path '{node_file_path}'")

        # Get the path starting from the import prefix
        path_from_prefix = node_file_path[prefix_pos:]
        logger.debug("Path from prefix: %r", path_from_prefix)
        
        # Remove the .py extension
        path_without_ext = os.path.splitext(path_from_prefix)[0]
        logger.debug("Path without extension: %r", path_without_ext)

        # Split the path into parts and convert to package notation
        path_parts = path_without_ext.replace("/", ".").replace("\\", ".").split(".")
        logger.debug("Path parts: %r", path_parts)

        # For CLASS types, append the node name instead of replacing the filename
        if node_type == "CLASS":
            qualified_name = ".".join(path_parts) + "." + node_name
            logger.debug("Qualified name for CLASS: %r", qualified_name)
        else:
            # Join the path parts
            qualified_name = ".".join(path_parts)
            logger.debug("Qualified name for non-CLASS: %r", qualified_name)

        return qualified_name
