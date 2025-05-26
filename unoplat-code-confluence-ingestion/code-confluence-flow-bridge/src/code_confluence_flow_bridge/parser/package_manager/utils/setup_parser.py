# Standard Library
# First Party
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_package_manager_metadata import UnoplatPackageManagerMetadata
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_project_dependency import UnoplatProjectDependency
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_version import UnoplatVersion

import os
import ast
import configparser
from typing import Any, Dict, List, Optional, Union

from packaging.requirements import Requirement

# Third Party
from temporalio import activity


class SetupParser:
    """Parser for Python setup.py files to extract package metadata"""

    SetupDictValue = Union[str, List[str], Dict[str, Any]]

    @staticmethod
    def _extract_constant_value(node: ast.AST) -> Optional[str]:
        """Extract string value from an AST Constant node"""
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        return None

    @staticmethod
    def _extract_list_values(node: ast.List) -> List[str]:
        """Extract string values from an AST List node"""
        return [elt.value for elt in node.elts if isinstance(elt, ast.Constant) and isinstance(elt.value, str)]

    @staticmethod
    def _extract_dict_values(node: ast.Dict) -> Dict[str, "SetupParser.SetupDictValue"]:
        """
        Extract key-value pairs from an AST Dict node iteratively
        (i.e., without recursion), handling:
          - string constants
          - lists of strings
          - nested dictionaries
        """

        # The dictionary for the top-level node
        result: Dict[str, "SetupParser.SetupDictValue"] = {}

        # Stack items are (dict_node, target_dict), where:
        # - dict_node is the AST Dict to parse
        # - target_dict is the Python dict we will fill at that level
        stack = [(node, result)]

        while stack:
            current_ast_dict, current_output_dict = stack.pop()

            for key_node, value_node in zip(current_ast_dict.keys, current_ast_dict.values):
                # Only handle string keys
                if not (isinstance(key_node, ast.Constant) and isinstance(key_node.value, str)):
                    continue
                key_str = key_node.value

                if isinstance(value_node, ast.Constant) and isinstance(value_node.value, str):
                    # A simple string
                    current_output_dict[key_str] = value_node.value

                elif isinstance(value_node, ast.List):
                    # A list of strings
                    current_output_dict[key_str] = SetupParser._extract_list_values(value_node)

                elif isinstance(value_node, ast.Dict):
                    # Nested dictionary: create a sub-dict in the current dictionary
                    sub_dict: Dict[str, "SetupParser.SetupDictValue"] = {}
                    current_output_dict[key_str] = sub_dict
                    # Push it on the stack to parse
                    stack.append((value_node, sub_dict))

                # You can add more branches here for other node types if you need them

        return result

    @staticmethod
    def _extract_setup_args_from_ast(node: ast.AST) -> Optional[Dict[str, Any]]:
        """Extract setup() arguments from an AST node"""
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "setup"):
            return None

        args_dict: Dict[str, Any] = {}

        for keyword in node.keywords:
            if keyword.arg is None:  # Skip if no argument name
                continue

            if isinstance(keyword.value, ast.Constant):
                value = SetupParser._extract_constant_value(keyword.value)
                if value is not None:
                    args_dict[keyword.arg] = value
            elif isinstance(keyword.value, ast.List):
                args_dict[keyword.arg] = SetupParser._extract_list_values(keyword.value)
            elif isinstance(keyword.value, ast.Dict):
                # Handle nested dictionary structures
                args_dict[keyword.arg] = SetupParser._extract_dict_values(keyword.value)

        return args_dict

    @staticmethod
    def _parse_entry_points(entry_points: Union[Dict, str, List]) -> Dict[str, str]:
        """Parse entry_points data into a standardized dictionary format"""
        result = {}

        if isinstance(entry_points, dict):
            console_scripts = entry_points.get("console_scripts", [])
            if isinstance(console_scripts, list):
                for script in console_scripts:
                    try:
                        name, path = [part.strip() for part in script.split("=", 1)]
                        result[name] = path
                    except ValueError:
                        activity.logger.warning("Invalid entry point format", {"script": script})
            elif isinstance(console_scripts, dict):
                result.update(console_scripts)

        elif isinstance(entry_points, str):
            try:
                

                config = configparser.ConfigParser()
                if not entry_points.strip().startswith("["):
                    entry_points = "[console_scripts]\n" + entry_points
                config.read_string(entry_points)
                if "console_scripts" in config:
                    result.update(dict(config["console_scripts"]))
            except Exception as e:
                activity.logger.warning("Failed to parse entry_points string", {"error": str(e), "entry_points": entry_points})

        elif isinstance(entry_points, list):
            for entry in entry_points:
                try:
                    name, path = [part.strip() for part in entry.split("=", 1)]
                    result[name] = path
                except ValueError:
                    activity.logger.warning("Invalid entry point format", {"entry": entry})

        return result

    @staticmethod
    def _update_metadata_from_setup_args(metadata: UnoplatPackageManagerMetadata, setup_args: Dict[str, Any]) -> UnoplatPackageManagerMetadata:
        """Update metadata instance with setup arguments"""
        if "name" in setup_args:
            metadata.package_name = setup_args["name"]

        if "version" in setup_args:
            metadata.project_version = setup_args["version"]

        if "description" in setup_args:
            metadata.description = setup_args["description"]

        if "author" in setup_args:
            authors = [setup_args["author"]]
            if "author_email" in setup_args:
                authors[0] = f"{authors[0]} <{setup_args['author_email']}>"
            metadata.authors = authors

        if "license" in setup_args:
            # Convert string license to dict format to match UnoplatPackageManagerMetadata expectations
            license_value = setup_args["license"]
            if isinstance(license_value, str):
                metadata.license = {"text": license_value}
            else:
                metadata.license = license_value

        if "python_requires" in setup_args:
            version_str = setup_args["python_requires"]

            metadata.programming_language_version = version_str

        if "entry_points" in setup_args:
            metadata.entry_points = SetupParser._parse_entry_points(setup_args["entry_points"])

        # Process install_requires
        if "install_requires" in setup_args:
            for req_str in setup_args["install_requires"]:
                req = Requirement(req_str)
                version = UnoplatVersion()

                # Handle version specifiers
                if req.specifier:
                    version = UnoplatVersion(specifier=str(req.specifier))

                dep = UnoplatProjectDependency(version=version, extras=list(req.extras) if req.extras else None, environment_marker=str(req.marker) if req.marker else None)
                metadata.dependencies[req.name] = dep

        # Process extras_require
        if "extras_require" in setup_args:
            for extra_name, req_list in setup_args["extras_require"].items():
                for req_str in req_list:
                    req = Requirement(req_str)
                    version = UnoplatVersion()

                    # Handle version specifiers
                    if req.specifier:
                        version = UnoplatVersion(specifier=str(req.specifier))

                    dep = UnoplatProjectDependency(version=version, extras=[extra_name] + list(req.extras) if req.extras else [extra_name], environment_marker=str(req.marker) if req.marker else None, group=extra_name)
                    if req.name not in metadata.dependencies:
                        metadata.dependencies[req.name] = dep
                    else:
                        existing_dep = metadata.dependencies[req.name]
                        if existing_dep.extras:
                            existing_dep.extras.append(extra_name)
                        else:
                            existing_dep.extras = [extra_name]

        return metadata

    @staticmethod
    def parse_setup_file(root_dir: str, metadata: UnoplatPackageManagerMetadata) -> UnoplatPackageManagerMetadata:
        """Parse a setup.py file and update the UnoplatPackageManagerMetadata instance

        Args:
            root_dir: Path to the directory containing setup.py
            metadata: Existing UnoplatPackageManagerMetadata instance to update

        Returns:
            Updated UnoplatPackageManagerMetadata instance
        """
        try:
            setup_file_path = os.path.join(root_dir, "setup.py")

            if not os.path.exists(setup_file_path):
                raise FileNotFoundError(f"setup.py not found at {setup_file_path}")

            with open(setup_file_path, "r", encoding="utf-8") as file:
                setup_content = file.read()

            # Parse the AST
            tree = ast.parse(setup_content)

            # Find the setup() call
            setup_args = None
            for node in ast.walk(tree):
                args = SetupParser._extract_setup_args_from_ast(node)
                if args:
                    setup_args = args
                    break

            if setup_args:
                # Log when python_requires is found
                if "python_requires" in setup_args:
                    activity.logger.info("Found python_requires in setup.py", {"version": setup_args["python_requires"], "path": setup_file_path})
                metadata = SetupParser._update_metadata_from_setup_args(metadata, setup_args)

            return metadata

        except Exception as e:
            activity.logger.error("Error parsing setup.py", {"error": str(e), "path": setup_file_path})
            return metadata
