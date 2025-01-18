# Standard Library
import os
import ast
from typing import Any, Dict, List, Optional, Union

# Third Party
from loguru import logger
from packaging.requirements import Requirement

# First Party
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_package_manager_metadata import UnoplatPackageManagerMetadata
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_project_dependency import UnoplatProjectDependency
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_version import UnoplatVersion


class SetupParser:
    """Parser for Python setup.py files to extract package metadata"""
    
    @staticmethod
    def _extract_constant_value(node: ast.AST) -> Optional[str]:
        """Extract string value from an AST Constant node"""
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        return None

    @staticmethod
    def _extract_list_values(node: ast.List) -> List[str]:
        """Extract string values from an AST List node"""
        return [
            elt.value for elt in node.elts 
            if isinstance(elt, ast.Constant) and isinstance(elt.value, str)
        ]

    @staticmethod
    def _extract_dict_values(node: ast.Dict) -> Dict[str, Any]:
        """Extract key-value pairs from an AST Dict node, including nested structures."""
        result = {}
        for key, value in zip(node.keys, node.values):
            if not isinstance(key, ast.Constant) or not isinstance(key.value, str):
                continue
                
            if isinstance(value, ast.Constant):
                if isinstance(value.value, str):
                    result[key.value] = value.value
            elif isinstance(value, ast.List):
                result[key.value] = SetupParser._extract_list_values(value)
            elif isinstance(value, ast.Dict):
                result[key.value] = SetupParser._extract_dict_values(value)
                
        return result

    @staticmethod
    def _extract_setup_args_from_ast(node: ast.AST) -> Optional[Dict[str, Any]]:
        """Extract setup() arguments from an AST node"""
        if not (isinstance(node, ast.Call) and 
                isinstance(node.func, ast.Name) and 
                node.func.id == 'setup'):
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
            console_scripts = entry_points.get('console_scripts', [])
            if isinstance(console_scripts, list):
                for script in console_scripts:
                    try:
                        name, path = [part.strip() for part in script.split('=', 1)]
                        result[name] = path
                    except ValueError:
                        logger.warning(f"Invalid entry point format: {script}")
            elif isinstance(console_scripts, dict):
                result.update(console_scripts)

        elif isinstance(entry_points, str):
            try:
                # Standard Library
                import configparser
                config = configparser.ConfigParser()
                if not entry_points.strip().startswith('['):
                    entry_points = '[console_scripts]\n' + entry_points
                config.read_string(entry_points)
                if 'console_scripts' in config:
                    result.update(dict(config['console_scripts']))
            except Exception as e:
                logger.warning(f"Failed to parse entry_points string: {str(e)}")

        elif isinstance(entry_points, list):
            for entry in entry_points:
                try:
                    name, path = [part.strip() for part in entry.split('=', 1)]
                    result[name] = path
                except ValueError:
                    logger.warning(f"Invalid entry point format: {entry}")

        return result

    @staticmethod
    def _update_metadata_from_setup_args(
        metadata: UnoplatPackageManagerMetadata, 
        setup_args: Dict[str, Any]
    ) -> UnoplatPackageManagerMetadata:
        """Update metadata instance with setup arguments"""
        if 'name' in setup_args:
            metadata.package_name = setup_args['name']

        if 'version' in setup_args:
            metadata.project_version = setup_args['version']
                
        if 'description' in setup_args:
            metadata.description = setup_args['description']
                
        if 'author' in setup_args:
            authors = [setup_args['author']]
            if 'author_email' in setup_args:
                authors[0] = f"{authors[0]} <{setup_args['author_email']}>"
            metadata.authors = authors
                
        if 'license' in setup_args:
            metadata.license = setup_args['license']
                
        if 'python_requires' in setup_args:
            version_str = setup_args['python_requires']
            
            metadata.programming_language_version = version_str
                
        if 'entry_points' in setup_args:
            metadata.entry_points = SetupParser._parse_entry_points(setup_args['entry_points'])
            
        # Process install_requires
        if 'install_requires' in setup_args:
            for req_str in setup_args['install_requires']:
                req = Requirement(req_str)
                version = UnoplatVersion()
                
                # Handle version specifiers
                if req.specifier:
                    min_ver: Optional[str] = None
                    max_ver: Optional[str] = None
                    current_ver: Optional[str] = None
                    
                    for spec in req.specifier:
                        spec_str = str(spec)
                        if spec.operator == "==":
                            current_ver = spec_str
                        elif spec.operator in (">=", ">"):
                            min_ver = spec_str
                        elif spec.operator in ("<=", "<"):
                            max_ver = spec_str
                            
                    version = UnoplatVersion(
                        minimum_version=min_ver,
                        maximum_version=max_ver,
                        current_version=current_ver
                    )
                
                dep = UnoplatProjectDependency(
                    version=version,
                    extras=list(req.extras) if req.extras else None,
                    environment_marker=str(req.marker) if req.marker else None
                )
                metadata.dependencies[req.name] = dep
        
        # Process extras_require
        if 'extras_require' in setup_args:
            for extra_name, req_list in setup_args['extras_require'].items():
                for req_str in req_list:
                    req = Requirement(req_str)
                    version = UnoplatVersion()
                    
                    # Handle version specifiers
                    if req.specifier:
                        min_ver: Optional[str] = None
                        max_ver: Optional[str] = None
                        current_ver: Optional[str] = None
                        
                        for spec in req.specifier:
                            spec_str = str(spec)
                            if spec.operator == "==":
                                current_ver = spec_str
                            elif spec.operator in (">=", ">"):
                                min_ver = spec_str
                            elif spec.operator in ("<=", "<"):
                                max_ver = spec_str
                                
                        version = UnoplatVersion(
                            minimum_version=min_ver,
                            maximum_version=max_ver,
                            current_version=current_ver
                        )
                    
                    dep = UnoplatProjectDependency(
                        version=version,
                        extras=[extra_name] + list(req.extras) if req.extras else [extra_name],
                        environment_marker=str(req.marker) if req.marker else None,
                        group=extra_name
                    )
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

            with open(setup_file_path, 'r', encoding='utf-8') as file:
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
                metadata = SetupParser._update_metadata_from_setup_args(metadata, setup_args)
                
            return metadata
            
        except Exception as e:
            logger.error(f"Error parsing setup.py: {str(e)}")
            return metadata
