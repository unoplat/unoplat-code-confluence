from src.code_confluence_flow_bridge.parser.linters.linter_strategy import (
    LinterStrategy,
)

import os
from pathlib import Path
import re
import subprocess
from typing import Any, List, Optional

from loguru import logger
import tomlkit


class RuffStrategy(LinterStrategy):
    
    def _get_config_template_path(self) -> str:
        """Get path to Ruff config template, checking multiple locations."""
        # Check environment variable first
        if template_path := os.getenv("RUFF_CONFIG_TEMPLATE"):
            return template_path
            
        # Fall back to default locations in order:
        locations = [
            # 1. Config in current working directory
            Path.cwd() / "config" / "ruff_config_template.toml",
            # 2. Config in package directory
            Path(__file__).parent / "templates" / "ruff_config_template.toml",
            # 3. Config in /etc (for container deployments)
            Path("/etc/code-confluence/ruff_config_template.toml")
        ]
        
        for path  in locations:
            logger.info(f"checking config template path if it exists {str(path)}")
            if path.exists():
                logger.info(f"ruff config path that exists {str(path)}")
                return str(path)
                
        raise FileNotFoundError("Ruff config template not found in any standard location")
    
    def _convert_pep621_to_ruff_version(self, version_spec: str) -> str:
        """Convert PEP 621 Python version specifier to Ruff target version.
        
        Args:
            version_spec: Version specifier like '>=3.11' or '>=3.11,<4.0'
            
        Returns:
            Ruff target version like 'py311'
            
        Example:
            '>=3.11' -> 'py311'
            '>=3.11,<4.0' -> 'py311'
        """
        try:
            logger.info(f"Converting Python version '{version_spec}' to Ruff version")
            # Extract the minimum version using regex
            match = re.search(r'>=?\s*(\d+)\.(\d+)', version_spec)
            if match:
                major, minor = match.groups()
                return f"py{major}{minor:0>2}"  # Pad minor version with leading zero
            
            # If no >= found, look for exact version
            match = re.search(r'==?\s*(\d+)\.(\d+)', version_spec)
            if match:
                major, minor = match.groups()
                return f"py{major}{minor:0>2}"
                
            # Default to Python 3.9 if no valid version found
            logger.warning(f"Could not parse Python version from '{version_spec}', defaulting to py39")
            return "py39"
            
        except Exception as e:
            logger.error(f"Error converting Python version '{version_spec}': {e}")
            return "py39"

    def _create_ruff_config(self, local_workspace_path: str, programming_language_version: str) -> bool:
        """Create Ruff configuration file from template.
        
        Args:
            local_workspace_path: Path to workspace
            programming_language_version: Python version to target (PEP 621 format)
            
        Returns:
            bool: True if config was created successfully
        """
        try:
            # Load template
            template_path = self._get_config_template_path()
            with open(template_path, 'r', encoding='utf-8') as f:
                template = f.read()
            
            # Convert version format
            ruff_version = self._convert_pep621_to_ruff_version(programming_language_version)
            
            # Format template with values
            config_content = template.format(
                python_version=ruff_version,
                src_path=local_workspace_path
            )
            
            # Parse and write config
            config = tomlkit.parse(config_content)
            config_path = os.path.join(local_workspace_path, "ruff.toml")
            with open(config_path, 'w', encoding='utf-8') as f:
                tomlkit.dump(config, f)
            return True
            
        except Exception as e:
            logger.error(f"Error creating Ruff config: {e}")
            return False

    def _delete_ruff_sections(self, pyproject_path: str) -> bool:
        """
        Delete all Ruff-related sections from pyproject.toml
        
        Args:
            pyproject_path: Path to pyproject.toml file
            
        Returns:
            bool: True if file was modified, False otherwise
        """
        try:
            if not os.path.exists(pyproject_path):
                return False
                
            with open(pyproject_path, 'r', encoding='utf-8') as f:
                content = f.read()
                doc: dict[str, Any] = tomlkit.parse(content)
            
            modified = False
            
            # Check if tool section exists
            if isinstance(doc.get('tool', {}), dict):
                tool_section = doc['tool']
                
                # Find and remove all Ruff-related sections
                ruff_keys = [
                    key for key in tool_section.keys()
                    if isinstance(key, str) and key.startswith('ruff')
                ]
                
                for key in ruff_keys:
                    del tool_section[key]
                    modified = True
                
                # If tool section is empty after removing Ruff sections, remove it too
                if not tool_section and 'tool' in doc:
                    del doc['tool']
            
            if modified:
                with open(pyproject_path, 'w', encoding='utf-8') as f:
                    f.write(tomlkit.dumps(doc))
                logger.info(f"Deleted Ruff sections from {pyproject_path}")
                
            return modified
            
        except Exception as e:
            logger.error(f"Error handling pyproject.toml: {e}")
            return False
    
    def lint_codebase(self, local_workspace_path: str, dependencies: Optional[List[str]], programming_language_version: str) -> bool:
        """Run Ruff linter on Python codebase.

        Args:
            local_workspace_path (str): Path to Python codebase
            dependencies (List[str]): List of project dependencies
            programming_language_version (str): Python version specifier

        Returns:
            bool: True if linting violations were found, False otherwise
        """
        try:
            # First check and handle existing Ruff config
            pyproject_path = os.path.join(local_workspace_path, "pyproject.toml")
            logger.info(f"current linting path {pyproject_path}")
            self._delete_ruff_sections(pyproject_path)
            
            # Create our Ruff configuration
            if not self._create_ruff_config(local_workspace_path, programming_language_version):
                return False
            
            # Store current directory
            original_dir = os.getcwd()
            
            try:
                # Change to workspace directory
                os.chdir(local_workspace_path)
                
                # Now run Ruff with our configuration and fix option
                result: subprocess.CompletedProcess[str] = subprocess.run(
                    ["ruff", "check","--fix",".", "--unsafe-fixes"],
                    capture_output=True,
                    text=True,
                    check=False,  # Don't raise CalledProcessError on lint violations
                )
                
                if result.returncode == 0 and result.stdout:
                    logger.info(result.stdout)  # Validate JSON but we don't use it currently
                    return True

                return False
                
            finally:
                # Always restore original directory
                os.chdir(original_dir)

        except Exception as e:
            logger.error(f"Error running Ruff linter: {e}")
            return False
