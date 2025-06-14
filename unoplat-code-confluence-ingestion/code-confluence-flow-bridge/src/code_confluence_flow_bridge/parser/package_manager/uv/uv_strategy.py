# Standard Library
# First Party
from src.code_confluence_flow_bridge.models.code_confluence_parsing_models import (
    UnoplatPackageManagerMetadata,
    UnoplatProjectDependency,
    UnoplatVersion,
)
from src.code_confluence_flow_bridge.models.configuration.settings import ProgrammingLanguageMetadata
from src.code_confluence_flow_bridge.parser.package_manager.package_manager_strategy import PackageManagerStrategy
from src.code_confluence_flow_bridge.utility.author_utils import normalize_authors

from pathlib import Path
import tomllib
from typing import Dict, List, Optional
from urllib.parse import parse_qs, urlsplit

# Third Party
from loguru import logger


class UvStrategy(PackageManagerStrategy):
    def process_metadata(self, local_workspace_path: str, metadata: ProgrammingLanguageMetadata) -> UnoplatPackageManagerMetadata:
        """Process UV project metadata from pyproject.toml file.

        Parses a pyproject.toml file to extract package metadata and dependencies.
        Handles main dependencies, optional dependencies, git sources, and environment markers.

        Example pyproject.toml:
            [project]
            name = "my-package"
            version = "1.0.0"
            dependencies = [
                "requests>=2.25.0",
                "pandas[excel]>=1.2.0"
            ]

            [project.optional-dependencies]
            test = ["pytest>=6.0.0"]

            [tool.uv.sources]
            my-pkg = { git = "https://github.com/user/repo.git", tag = "v1.0.0" }

        Args:
            local_workspace_path: Path to the directory containing pyproject.toml
            metadata: Programming language metadata configuration

        Returns:
            UnoplatPackageManagerMetadata containing all parsed project information

        Raises:
            ValueError: If pyproject.toml exists but cannot be parsed
        """
        
        try:
            
            pyproject_path = Path(local_workspace_path) / "pyproject.toml"
            

            if not pyproject_path.exists():
                package_manager_value = metadata.package_manager.value if metadata.package_manager else "unknown"
                return UnoplatPackageManagerMetadata(
                    programming_language=metadata.language.value, 
                    package_manager=package_manager_value
                )
           
            with open(pyproject_path, "rb") as f:
                pyproject_data = tomllib.load(f)
        except Exception as e:
            raise ValueError(f"Failed to parse pyproject.toml: {str(e)}")

        # Extract project metadata
        project_data = pyproject_data.get("project", {})

        # Parse dependencies
        dependencies: Dict[str, UnoplatProjectDependency] = {}

        # Process main dependencies
        for dep in project_data.get("dependencies", []):
            try:
                name, version_str, extras = self._parse_dependency(dep)
                version = self._parse_version_constraint(version_str) if version_str else UnoplatVersion()

                dependencies[name] = UnoplatProjectDependency(
                    version=version,
                    extras=extras,  # Now properly handling extras
                )
            except Exception as e:
                logger.warning(f"Error processing dependency {dep}: {str(e)}")
                continue

        # Process optional dependencies (extras)
        optional_deps = project_data.get("optional-dependencies", {})
        for group_name, deps in optional_deps.items():
            for dep in deps:
                try:
                    name, version_str, extras = self._parse_dependency(dep)
                    version = self._parse_version_constraint(version_str) if version_str else UnoplatVersion()

                    if name not in dependencies:
                        dependencies[name] = UnoplatProjectDependency(
                            version=version,
                            group=group_name,
                            extras=extras,  # Include extras
                        )
                    else:
                        # Update existing dependency
                        existing_dep = dependencies[name]
                        if existing_dep.group != group_name:
                            existing_groups = [existing_dep.group] if existing_dep.group else []
                            existing_groups.append(group_name)
                            existing_dep.group = ",".join(existing_groups)
                        if extras:
                            existing_extras = existing_dep.extras or []
                            existing_dep.extras = list(set(existing_extras + extras))
                except Exception as e:
                    logger.warning(f"Error processing optional dependency {dep} in group {group_name}: {str(e)}")
                    continue

        # Process UV-specific sources
        uv_config = pyproject_data.get("tool", {}).get("uv", {})
        sources = uv_config.get("sources", {})
        for pkg_name, source_info in sources.items():
            if pkg_name in dependencies:
                try:
                    if "git" in source_info:
                        self._process_git_source(dependencies, pkg_name, source_info)
                    elif "index" in source_info:
                        dependencies[pkg_name].source = "index"
                        dependencies[pkg_name].source_url = self._get_index_url(pyproject_data, source_info["index"])
                except Exception as e:
                    logger.warning(f"Error processing source for {pkg_name}: {str(e)}")
                    continue

        # Process dependency metadata for environment markers
        dep_metadata = uv_config.get("dependency-metadata", [])
        for metadata_entry in dep_metadata:
            name = metadata_entry.get("name")
            if name in dependencies:
                try:
                    # Add environment markers if specified
                    if "requires-python" in metadata_entry:
                        dependencies[name].environment_marker = f"python_version {metadata_entry['requires-python']}"
                except Exception as e:
                    logger.warning(f"Error processing dependency metadata for {name}: {str(e)}")
                    continue

        package_manager_value = metadata.package_manager.value if metadata.package_manager else "unknown"
        return UnoplatPackageManagerMetadata(
            dependencies=dependencies,
            package_name=project_data.get("name"),
            programming_language=metadata.language.value,
            package_manager=package_manager_value,
            programming_language_version=project_data.get("requires-python"),
            project_version=project_data.get("version"),
            description=project_data.get("description"),
            authors=normalize_authors(project_data.get("authors", [])),
            license=project_data.get("license"),
            entry_points=self._parse_entry_points(project_data),
            homepage=project_data.get("homepage"),
            repository=project_data.get("repository"),
            documentation=project_data.get("documentation"),
            keywords=project_data.get("keywords", []),
            maintainers=project_data.get("maintainers", []),
            readme=project_data.get("readme"),
        )

    def _parse_dependency(self, dep_string: str) -> tuple[str, Optional[str], Optional[List[str]]]:
        """Parse a dependency string into name, version, and extras.

        Handles various dependency formats including:
        - Simple version specifiers: "requests>=2.25.0"
        - Multiple version specifiers: "requests>=2.25.0,<3.0.0"
        - Extras: "pandas[excel,csv]>=1.2.0"

        Examples:
            >>> _parse_dependency("requests>=2.25.0")
            ("requests", ">=2.25.0", None)
            >>> _parse_dependency("pandas[excel,csv]>=1.2.0")
            ("pandas", ">=1.2.0", ["excel", "csv"])
            >>> _parse_dependency("flask")
            ("flask", None, None)

        Args:
            dep_string: The dependency string to parse

        Returns:
            tuple containing:
            - str: Package name
            - Optional[str]: Version specifier if present
            - Optional[List[str]]: List of extras if present
        """
        try:
            # First split on version operators to get the package part
            package_part = dep_string
            version_part = None
            for operator in (">=", "==", "<=", "<", ">"):
                if operator in dep_string:
                    package_part, version_part = dep_string.split(operator, 1)
                    version_part = f"{operator}{version_part.strip()}"
                    break

            # Now handle extras in the package part
            extras = None
            name = package_part.strip()
            if "[" in name and "]" in name:
                name, extras_str = name.split("[", 1)
                extras_str = extras_str.split("]")[0]
                extras = [e.strip() for e in extras_str.split(",")]
                name = name.strip()

            return name, version_part, extras

        except Exception as e:
            logger.warning(f"Error parsing dependency '{dep_string}': {str(e)}")
            return dep_string.strip(), None, None

    def _parse_version_constraint(self, constraint: str) -> UnoplatVersion:
        """Parse version constraint into a specifier string.

        Handles various version constraint formats:
        - Simple constraints: "==1.0.0", ">=2.0.0"
        - Complex constraints: ">=1.0.0,<2.0.0"
        - Compatible release: "~=1.0.0"

        Examples:
            >>> _parse_version_constraint(">=1.0.0")
            UnoplatVersion(specifier=">=1.0.0")
            >>> _parse_version_constraint(">=1.0.0,<2.0.0")
            UnoplatVersion(specifier=">=1.0.0,<2.0.0")
            >>> _parse_version_constraint("==1.0.0")
            UnoplatVersion(specifier="==1.0.0")

        Args:
            constraint: Version constraint string

        Returns:
            UnoplatVersion with specifier field set
        """
        if not constraint or constraint == "*":
            return UnoplatVersion()

        try:
            # Simply store the raw version constraint as specifier
            return UnoplatVersion(specifier=constraint)

        except Exception as e:
            logger.warning(f"Error parsing version constraint '{constraint}': {str(e)}")
            return UnoplatVersion()

    def _get_index_url(self, pyproject_data: dict, index_name: str) -> Optional[str]:
        """Get the URL for a named custom package index from UV configuration.

        Example pyproject.toml:
            [[tool.uv.index]]
            name = "private-pypi"
            url = "https://pypi.internal.company.com/simple"

        Args:
            pyproject_data: Parsed pyproject.toml data
            index_name: Name of the index to look up

        Returns:
            URL string if index is found, None otherwise
        """
        uv_config = pyproject_data.get("tool", {}).get("uv", {})
        for index in uv_config.get("index", []):
            if index.get("name") == index_name:
                return index.get("url")
        return None

    def _parse_entry_points(self, project_data: dict) -> Dict[str, str]:
        """Parse entry points from project configuration.

        Handles both script entries and console_scripts entry points.

        Example pyproject.toml:
            [project.scripts]
            my-cli = "my_package.cli:main"

            [project.entry-points."console_scripts"]
            another-cli = "my_package.another:main"

        Args:
            project_data: Project section from pyproject.toml

        Returns:
            Dictionary mapping script names to their entry points
            Example: {"my-cli": "my_package.cli:main", "another-cli": "my_package.another:main"}
        """
        entry_points = {}

        # Parse scripts section
        scripts = project_data.get("scripts", {})
        entry_points.update(scripts)

        # Parse console_scripts entry points
        console_scripts = project_data.get("entry-points", {}).get("console_scripts", {})
        entry_points.update(console_scripts)

        return entry_points

    def _parse_vcs_url(self, url: str) -> tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
        """Parse VCS URL into components using urllib.parse.

        Handles various VCS URL formats:
        - Simple git URLs: "git+https://github.com/user/repo.git"
        - URLs with references: "git+https://github.com/user/repo.git@main"
        - URLs with extras: "git+https://github.com/user/repo.git#egg=package&subdirectory=src"

        Examples:
            >>> _parse_vcs_url("git+https://github.com/user/repo.git")
            ("https://github.com/user/repo", None, None, "repo")
            >>> _parse_vcs_url("git+https://github.com/user/repo.git@main#egg=mypackage")
            ("https://github.com/user/repo", "main", None, "mypackage")
            >>> _parse_vcs_url("git+https://github.com/user/repo.git#egg=pkg&subdirectory=src")
            ("https://github.com/user/repo", None, "src", "pkg")

        Args:
            url: VCS URL to parse

        Returns:
            tuple containing:
            - Optional[str]: Base URL without VCS prefix
            - Optional[str]: Reference (branch, tag, or commit)
            - Optional[str]: Subdirectory path if specified
            - Optional[str]: Package name from egg fragment or URL path
        """
        try:
            # Parse URL into components
            parsed = urlsplit(url)

            # Get base URL without VCS prefix
            if "+" in parsed.scheme:
                _, base_scheme = parsed.scheme.split("+", 1)
                base_url = f"{base_scheme}://{parsed.netloc}{parsed.path}"
            else:
                base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

            # Remove .git suffix if present
            if base_url.endswith(".git"):
                base_url = base_url[:-4]

            # Extract reference from path if present
            source_reference = None
            if "@" in parsed.path:
                path_parts = parsed.path.rsplit("@", 1)
                base_url = f"{parsed.scheme}://{parsed.netloc}{path_parts[0]}"
                source_reference = path_parts[1]

            # Parse fragment for egg and subdirectory
            name = None
            subdirectory = None
            if parsed.fragment:
                params = parse_qs(parsed.fragment)
                if "egg" in params:
                    # Get package name from egg fragment
                    egg = params["egg"][0]
                    # Remove any version specifier if present
                    name = egg.split("-")[0] if "-" in egg else egg
                if "subdirectory" in params:
                    subdirectory = params["subdirectory"][0]

            # If no name found in egg, try to get it from the path
            if not name:
                name = parsed.path.rstrip("/").split("/")[-1]
                if name.endswith(".git"):
                    name = name[:-4]

            return base_url, source_reference, subdirectory, name

        except Exception as e:
            logger.warning(f"Error parsing VCS URL '{url}': {str(e)}")
            return None, None, None, None

    def _process_git_source(self, dependencies: Dict[str, UnoplatProjectDependency], pkg_name: str, source_info: dict) -> None:
        """Process git source information for a dependency.

        Updates the dependency object with git source information including URL,
        reference (tag/branch/commit), and subdirectory if specified.

        Example source_info:
            {
                "git": "https://github.com/user/repo.git",
                "tag": "v1.0.0",
                "subdirectory": "python"
            }

        Args:
            dependencies: Dictionary of dependencies to update
            pkg_name: Name of the package to update
            source_info: Git source configuration from pyproject.toml

        Note:
            Modifies the dependency object in place with git source information
            If a tag is specified, also updates the version information
        """
        try:
            git_url = source_info["git"]
            source_url, source_reference, subdirectory, _ = self._parse_vcs_url(git_url)

            if source_url:
                dependencies[pkg_name].source = "git"
                dependencies[pkg_name].source_url = source_url

                # Use explicit tag/branch/rev if provided, otherwise use parsed reference
                if "tag" in source_info:
                    dependencies[pkg_name].source_reference = source_info["tag"]
                    # Update version if tag is specified
                    dependencies[pkg_name].version = self._parse_version_constraint(f"=={source_info['tag']}")
                elif "branch" in source_info:
                    dependencies[pkg_name].source_reference = source_info["branch"]
                elif "rev" in source_info:
                    dependencies[pkg_name].source_reference = source_info["rev"]
                elif source_reference:
                    dependencies[pkg_name].source_reference = source_reference

                # Use explicit subdirectory if provided, otherwise use parsed subdirectory
                if "subdirectory" in source_info:
                    dependencies[pkg_name].subdirectory = source_info["subdirectory"]
                elif subdirectory:
                    dependencies[pkg_name].subdirectory = subdirectory

        except Exception as e:
            logger.warning(f"Error processing git source for {pkg_name}: {str(e)}")
