import ast
from typing import Optional, Dict
import os
from loguru import logger
from unoplat_code_confluence.data_models.unoplat_package_manager_metadata import UnoplatPackageManagerMetadata

class SetupParser:
    """Parser for Python setup.py files to extract package metadata"""
    
    @staticmethod
    def _extract_setup_args_from_ast(node: ast.AST) -> Optional[Dict]:
        """Extract setup() arguments from an AST node"""
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
                    
            if not setup_args:
                return metadata
                
            # Update metadata fields
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
                version_info = {}
                if '>=' in version_str:
                    version_info['min'] = version_str
                if '<=' in version_str:
                    version_info['max'] = version_str
                metadata.programming_language_version = version_info
                
            if 'entry_points' in setup_args:
                console_scripts = setup_args['entry_points'].get('console_scripts', {})
                if isinstance(console_scripts, list):
                    metadata.entry_points = {
                        name.strip(): path.strip()
                        for script in console_scripts
                        for name, path in [script.split('=', 1)]
                    }
                elif isinstance(console_scripts, dict):
                    metadata.entry_points = console_scripts
                
            return metadata
            
        except Exception as e:
            logger.error(f"Error parsing setup.py: {str(e)}")
            return metadata
