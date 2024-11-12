from loguru import logger
from unoplat_code_confluence.configuration.external_config import PackageManager, ProgrammingLanguageMetadata,PackageManagerType
from unoplat_code_confluence.data_models.unoplat_package_manager_metadata import UnoplatPackageManagerMetadata
from unoplat_code_confluence.data_models.unoplat_project_dependency import UnoplatProjectDependency
from unoplat_code_confluence.data_models.unoplat_version import UnoplatVersion
from unoplat_code_confluence.language_custom_parsing.python.package_manager.pip.setup_parser import SetupParser
from unoplat_code_confluence.language_custom_parsing.python.package_manager.utils.requirements_utils import RequirementsUtils
from typing import Dict, List, Optional
import os
import tomlkit
from unoplat_code_confluence.language_custom_parsing.python.package_manager.package_manager_strategy import PackageManagerStrategy


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
                logger.warning("No poetry configuration found in pyproject.toml, falling back to requirements")
                # Try parsing requirements folder using RequirementsUtils
                dependencies = RequirementsUtils.parse_requirements_folder(local_workspace_path)
                unoplatPackageManager: UnoplatPackageManagerMetadata =  UnoplatPackageManagerMetadata(
                    dependencies=dependencies,
                    programming_language=metadata.language.value,
                    package_manager=PackageManagerType.PIP.value
                )
                try:
                    unoplatPackageManager = SetupParser.parse_setup_file(local_workspace_path, unoplatPackageManager)
                except FileNotFoundError:
                    logger.warning("setup.py not found, skipping setup.py parsing")
                return unoplatPackageManager
                
                
            # Parse only main dependencies
            dependencies: List[UnoplatProjectDependency] = []
            main_deps = poetry_data.get("dependencies", {})
            dependencies.extend(self._parse_dependencies(main_deps))
            
            # Create metadata object with entry_points instead of entry_point
            return UnoplatPackageManagerMetadata(
                dependencies=dependencies,
                package_name=poetry_data.get("name"),
                programming_language=metadata.language.value,
                package_manager=metadata.package_manager,
                programming_language_version=self._parse_python_version(main_deps.get("python")),
                project_version=poetry_data.get("version"),
                description=poetry_data.get("description"),
                authors=poetry_data.get("authors"),
                entry_points=self._get_entry_points(poetry_data.get("scripts", {}))
            )
            
        except Exception as e:
            logger.error(f"Error parsing pyproject.toml: {str(e)}")
            return self._create_empty_metadata(metadata)
    
    def _create_empty_metadata(self, metadata: ProgrammingLanguageMetadata) -> UnoplatPackageManagerMetadata:
        """Create empty metadata with basic information"""
        return UnoplatPackageManagerMetadata(
            dependencies=[],
            programming_language=metadata.language.value,
            package_manager=metadata.package_manager
        )
    
    def _parse_version_constraint(self, constraint: str) -> UnoplatVersion:
        """Parse version constraint into UnoplatVersion format."""
        if not constraint or constraint == "*":
            return UnoplatVersion()
            
        # Handle comma-separated constraints (e.g., ">=1.0.0,<2.0.0")
        if "," in constraint:
            parts = [p.strip() for p in constraint.split(",")]
            min_ver = None
            max_ver = None
            current_ver = None
            
            for part in parts:
                if part.startswith(">=") or part.startswith(">"):
                    min_ver = part
                elif part.startswith("<=") or part.startswith("<"):
                    max_ver = part
                elif part.startswith("=="):
                    current_ver = part
                    
            return UnoplatVersion(
                minimum_version=min_ver,
                maximum_version=max_ver,
                current_version=current_ver
            )
        
        # Handle caret constraints (e.g., "^1.0.0")
        if constraint.startswith("^"):
            return UnoplatVersion(
                minimum_version=constraint
            )
        
        # Handle tilde constraints (e.g., "~1.0.0")
        if constraint.startswith("~"):
            return UnoplatVersion(
                minimum_version=constraint
            )
        
        # Handle comparison operators
        if constraint.startswith(">=") or constraint.startswith(">"):
            return UnoplatVersion(minimum_version=constraint)
        elif constraint.startswith("<=") or constraint.startswith("<"):
            return UnoplatVersion(maximum_version=constraint)
        elif constraint.startswith("=="):
            return UnoplatVersion(current_version=constraint)
        
        # Plain version string treated as exact version
        return UnoplatVersion(current_version=f"=={constraint}")
    
    def _parse_dependencies(self, deps_dict: Dict, group: Optional[str] = None) -> List[UnoplatProjectDependency]:
        dependencies = []
        
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
                
                dep = UnoplatProjectDependency(
                    name=name,
                    version=version,
                    group=group,
                    extras=extras,
                    source=source,
                    source_url=source_url,
                    source_reference=source_reference,
                    subdirectory=subdirectory
                )
                dependencies.append(dep)
                
            except Exception as e:
                logger.warning(f"Error parsing dependency {name}: {str(e)}")
                # Add dependency with empty version constraint
                dep = UnoplatProjectDependency(
                    name=name,
                    version=UnoplatVersion(),
                    group=group
                )
                dependencies.append(dep)
                
        return dependencies
    
    def _parse_python_version(self, version_constraint: Optional[str]) -> Dict[str, str]:
        """Parse Python version constraint into a standardized format."""
        if not version_constraint:
            return {}  # Return empty dict if no constraint
            
        if "," in version_constraint:
            parts = [p.strip() for p in version_constraint.split(",")]
            min_ver = None
            max_ver = None
            
            for part in parts:
                if part.startswith(">="):
                    min_ver = part
                elif part.startswith(">"):
                    min_ver = part
                elif part.startswith("<="):
                    max_ver = part
                elif part.startswith("<"):
                    max_ver = part
                elif part.startswith("^"):
                    min_ver = f">={part[1:]}"
                elif part.startswith("~"):
                    min_ver = f">={part[1:]}"
                    
            result = {}
            if min_ver:
                result["min"] = min_ver
            if max_ver:
                result["max"] = max_ver
            return result
        
        # Handle single constraints
        if version_constraint.startswith("^"):
            return {"min": f">={version_constraint[1:]}"}
        elif version_constraint.startswith("~"):
            return {"min": f">={version_constraint[1:]}"}
        elif version_constraint.startswith(">="):
            return {"min": version_constraint}
        elif version_constraint.startswith(">"):
            return {"min": version_constraint}
        elif version_constraint.startswith("<="):
            return {"max": version_constraint}
        elif version_constraint.startswith("<"):
            return {"max": version_constraint}
        else:
            # Exact version
            return {"min": f">={version_constraint}", "max": f"<={version_constraint}"}
    
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