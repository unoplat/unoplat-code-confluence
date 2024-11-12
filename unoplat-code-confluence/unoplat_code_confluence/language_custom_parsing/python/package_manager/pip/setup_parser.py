import ast
from typing import Optional, Dict, List
import re
from unoplat_code_confluence.data_models.unoplat_package_manager_metadata import UnoplatPackageManagerMetadata
import os
class SetupParser:
    """Parser for Python setup.py files to extract package metadata"""
    
    @staticmethod
    def _extract_setup_args_from_ast(node: ast.AST) -> Optional[Dict]:
        """
        Extract setup() arguments from an AST node
        """
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'setup':
            args_dict = {}
            for keyword in node.keywords:
                if isinstance(keyword.value, ast.Str):
                    args_dict[keyword.arg] = keyword.value.s
                elif isinstance(keyword.value, ast.List):
                    args_dict[keyword.arg] = [
                        elt.s for elt in keyword.value.elts 
                        if isinstance(elt, ast.Str)
                    ]
                elif isinstance(keyword.value, ast.Dict):
                    args_dict[keyword.arg] = {
                        key.s: value.s
                        for key, value in zip(keyword.value.keys, keyword.value.values)
                        if isinstance(key, ast.Str) and isinstance(value, ast.Str)
                    }
            return args_dict
        return None

    @staticmethod
    def _parse_python_version(python_requires: str) -> Dict[str, str]:
        """
        Parse Python version requirements into a structured format
        """
        version_info = {"min": None, "max": None}
        
        if not python_requires:
            return version_info
            
        # Handle >= format
        if '>=' in python_requires:
            version_info['min'] = python_requires.split('>=')[1].strip()
        
        # Handle <= format
        if '<=' in python_requires:
            version_info['max'] = python_requires.split('<=')[1].strip()
            
        return version_info

    @staticmethod
    def _parse_entry_points(entry_points_dict: Dict) -> Dict[str, str]:
        """
        Parse entry_points dictionary into the required format
        """
        result = {}
        if not entry_points_dict:
            return result
            
        # Handle console_scripts specifically
        console_scripts = entry_points_dict.get('console_scripts', {})
        if isinstance(console_scripts, list):
            for script in console_scripts:
                name, path = script.split('=')
                result[name.strip()] = path.strip()
        elif isinstance(console_scripts, dict):
            result.update(console_scripts)
            
        return result

    @staticmethod
    def parse_setup_file(root_dir: str, metadata: UnoplatPackageManagerMetadata) -> UnoplatPackageManagerMetadata:
        """
        Parse a setup.py file and update the UnoplatPackageManagerMetadata instance
        
        Args:
            file_path: Path to the setup.py file
            metadata: Existing UnoplatPackageManagerMetadata instance to update
            
        Returns:
            Updated UnoplatPackageManagerMetadata instance
        """
        try:
            req_file_path = os.path.join(root_dir, "requirements.txt")
        
            if os.path.exists(req_file_path):
                with open(req_file_path, 'r', encoding='utf-8') as file:
                    setup_content = file.read()
            else:
                raise FileNotFoundError(f"Requirements file not found at {req_file_path}")
                    
            # Parse the AST
            tree = ast.parse(setup_content)
            
            # Find the setup() call
            setup_args = None
            for node in ast.walk(tree):
                args = SetupParser._extract_setup_args_from_ast(node)
                if args:
                    setup_args = args
                    break
                    
            if not setup_args:
                return metadata
                
            # Update metadata fields
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
                metadata.programming_language_version = SetupParser._parse_python_version(
                    setup_args['python_requires']
                )
                
            if 'entry_points' in setup_args:
                metadata.entry_points = SetupParser._parse_entry_points(setup_args['entry_points'])
                
            return metadata
            
        except Exception as e:
            # Log error but don't fail - return original metadata
            print(f"Error parsing setup.py: {str(e)}")
            return metadata
