# Standard Library
import os
from typing import Dict, Optional

# Third Party
import tomlkit
from loguru import logger
from packaging.specifiers import SpecifierSet

from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_package_manager_metadata import UnoplatPackageManagerMetadata
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_project_dependency import UnoplatProjectDependency
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_version import UnoplatVersion
from src.code_confluence_flow_bridge.models.configuration.settings import PackageManagerType, ProgrammingLanguageMetadata
from src.code_confluence_flow_bridge.parser.package_manager.package_manager_strategy import PackageManagerStrategy
from src.code_confluence_flow_bridge.parser.package_manager.utils.requirements_utils import RequirementsUtils
from src.code_confluence_flow_bridge.parser.package_manager.utils.setup_parser import SetupParser


class PythonPoetryStrategy(PackageManagerStrategy):
    def process_metadata(self, local_workspace_path: str, metadata: ProgrammingLanguageMetadata) -> UnoplatPackageManagerMetadata:
        """Process poetry specific metadata from pyproject.toml"""
        pyproject_path = os.path.join(local_workspace_path, "pyproject.toml")
        
        if not os.path.exists(pyproject_path):
            logger.warning(f"pyproject.toml not found at {pyproject_path}")
            return self._create_empty_metadata(metadata)
            
        try:
            with open(pyproject_path, "r") as f:
                pyproject_data = tomlkit.parse(f.read())
            
            poetry_data = pyproject_data.get("tool", {}).get("poetry", {})
            if not poetry_data:
                return self._handle_fallback(local_workspace_path, metadata)
                
            # Parse dependencies from all groups
            dependencies = self._parse_all_dependency_groups(poetry_data)
            
            # Parse Python version
            programming_language_version = self._parse_python_version(
                poetry_data.get("dependencies", {}).get("python")
            ) or metadata.language_version
            
            # Create metadata object with all available fields
            return UnoplatPackageManagerMetadata(
                dependencies=dependencies,
                package_name=poetry_data.get("name"),
                programming_language=metadata.language.value,
                package_manager=metadata.package_manager,
                programming_language_version=programming_language_version,
                project_version=poetry_data.get("version"),
                description=poetry_data.get("description"),
                authors=poetry_data.get("authors"),
                entry_points=self._get_entry_points(poetry_data.get("scripts", {})),
                license=poetry_data.get("license"),
                homepage=poetry_data.get("homepage"),
                repository=poetry_data.get("repository"),
                documentation=poetry_data.get("documentation"),
                keywords=poetry_data.get("keywords", []),
                maintainers=poetry_data.get("maintainers", []),
                readme=poetry_data.get("readme"),
             
            )
            
        except Exception as e:
            logger.error(f"Error parsing pyproject.toml: {str(e)}")
            return self._create_empty_metadata(metadata)

    def _handle_fallback(self, local_workspace_path: str, metadata: ProgrammingLanguageMetadata) -> UnoplatPackageManagerMetadata:
        """Handle fallback to requirements.txt when no poetry config is found"""
        logger.warning("No poetry configuration found in pyproject.toml, falling back to requirements")
        dependencies = RequirementsUtils.parse_requirements_folder(local_workspace_path)
        package_manager = UnoplatPackageManagerMetadata(
            dependencies=dependencies,
            programming_language=metadata.language.value,
            package_manager=PackageManagerType.PIP.value
        )
        try:
            return SetupParser.parse_setup_file(local_workspace_path, package_manager)
        except FileNotFoundError:
            logger.warning("setup.py not found, skipping setup.py parsing")
            return package_manager

    def _parse_all_dependency_groups(self, poetry_data: Dict) -> Dict[str, UnoplatProjectDependency]:
        """Parse dependencies from all groups including main, dev, and custom groups"""
        all_dependencies = {}
        
        # Parse main dependencies
        main_deps = poetry_data.get("dependencies", {})
        all_dependencies.update(self._parse_dependencies(main_deps))
        
        # Parse dev dependencies (legacy format)
        dev_deps = poetry_data.get("dev-dependencies", {})
        if dev_deps:
            all_dependencies.update(self._parse_dependencies(dev_deps, group="dev"))
            
        # Parse group dependencies (Poetry 1.2+ format)
        groups = poetry_data.get("group", {})
        for group_name, group_data in groups.items():
            if isinstance(group_data, dict) and "dependencies" in group_data:
                group_deps = self._parse_dependencies(
                    group_data["dependencies"], 
                    group=group_name
                )
                all_dependencies.update(group_deps)
                
        return all_dependencies

    def _parse_version_constraint(self, constraint: str) -> UnoplatVersion:
        """Parse version constraint using packaging library"""
        if not constraint or constraint == "*":
            return UnoplatVersion()
            
        try:
            # Use packaging's SpecifierSet to parse the constraint
            spec_set = SpecifierSet(constraint)
            
            # Convert to UnoplatVersion format
            min_ver = None
            max_ver = None
            current_ver = None
            
            for spec in spec_set:
                if spec.operator in (">=", ">"):
                    min_ver = str(spec)
                elif spec.operator in ("<=", "<"):
                    max_ver = str(spec)
                elif spec.operator == "==":
                    current_ver = str(spec)
                elif spec.operator == "~=":
                    # Handle compatible release operator
                    min_ver = str(spec)
                elif spec.operator == "!=":
                    # Skip not equal constraints for now
                    continue
                    
            return UnoplatVersion(
                minimum_version=min_ver,
                maximum_version=max_ver,
                current_version=current_ver
            )
            
        except Exception as e:
            logger.warning(f"Error parsing version constraint '{constraint}': {str(e)}")
            return UnoplatVersion()


    def _create_empty_metadata(self, metadata: ProgrammingLanguageMetadata) -> UnoplatPackageManagerMetadata:
        """Create empty metadata with basic information"""
        return UnoplatPackageManagerMetadata(
            dependencies={},
            programming_language=metadata.language.value,
            package_manager=metadata.package_manager
        )
    
    def _parse_dependencies(self, deps_dict: Dict, group: Optional[str] = None) -> Dict[str, UnoplatProjectDependency]:
        dependencies = {}
        
        for name, constraint in deps_dict.items():
            if name == "python":  # Skip python version constraint
                continue
                
            # Initialize dependency fields
            version = UnoplatVersion()
            extras = None
            source = None
            source_url = None
            source_reference = None
            subdirectory = None
            
            try:
                # Parse different dependency specification formats
                if isinstance(constraint, str):
                    # Handle version constraints
                    version = self._parse_version_constraint(constraint)
                    
                elif isinstance(constraint, dict):
                    # Complex dependency specification
                    if "version" in constraint:
                        version = self._parse_version_constraint(constraint["version"])
                    extras = constraint.get("extras")
                    
                    # Handle git dependencies
                    if "git" in constraint:
                        source = "git"
                        source_url = constraint["git"]
                        source_reference = constraint.get("rev") or constraint.get("branch") or constraint.get("tag")
                        subdirectory = constraint.get("subdirectory")
                        version = UnoplatVersion()  # Git dependencies don't have version constraints
                        
                    # Handle path dependencies
                    elif "path" in constraint:
                        source = "path"
                        source_url = constraint["path"]
                        version = UnoplatVersion()  # Path dependencies don't have version constraints
                        
                    # Handle url dependencies
                    elif "url" in constraint:
                        source = "url"
                        source_url = constraint["url"]
                        version = UnoplatVersion()  # URL dependencies don't have version constraints
                else:
                    logger.warning(f"Skipping invalid dependency specification for {name}")
                    continue
                
                tuple_dependency = UnoplatProjectDependency(
                    version=version,
                    extras=extras,
                    source=source,
                    source_url=source_url,
                    source_reference=source_reference,
                    subdirectory=subdirectory
                )
                dependencies[name] = tuple_dependency
                
            except Exception as e:
                logger.warning(f"Error parsing dependency {name}: {str(e)}")
                # Add dependency with empty version constraint
                tuple_dependency = UnoplatProjectDependency(
                    version=UnoplatVersion()
                )
                dependencies[name] = tuple_dependency
                
        return dependencies
    
    def _parse_python_version(self, version_constraint: Optional[str]) -> str:
        """
        Parse Python version constraint into a single string.
        
        Args:
            version_constraint: Version constraint string from pyproject.toml
            
        Returns:
            str: Formatted version string or empty string if no constraint
        """
        if not version_constraint:
            return ""  # Return empty string if no constraint
            
        # Remove any whitespace but preserve all version constraint symbols
        version_constraint = version_constraint.strip()
        
        # Return the version constraint exactly as specified
        return version_constraint
    
    def _get_entry_points(self, scripts: Dict[str, str]) -> Dict[str, str]:
        """Get all entry points from Poetry scripts section.
        
        Returns all scripts defined in pyproject.toml as a dictionary mapping
        script names to their entry points.
        
        Handles various script definitions:
        1. Module format:
            [tool.poetry.scripts]
            cli = "package_name.module:function"
        
        2. Command format:
            [tool.poetry.scripts]
            serve = "uvicorn main:app --reload"
        
        Args:
            scripts (Dict[str, str]): Dictionary of scripts from pyproject.toml
        
        Returns:
            Dict[str, str]: Dictionary mapping script names to their entry points
        
        Example from pyproject.toml:
            [tool.poetry.scripts]
            unoplat-code-confluence = "unoplat_code_confluence.__main__:main"
            serve = "uvicorn api:app --reload"
            
            Returns:
            {
                "unoplat-code-confluence": "unoplat_code_confluence.__main__:main",
                "serve": "uvicorn api:app --reload"
            }
        """
        return scripts if scripts else {}