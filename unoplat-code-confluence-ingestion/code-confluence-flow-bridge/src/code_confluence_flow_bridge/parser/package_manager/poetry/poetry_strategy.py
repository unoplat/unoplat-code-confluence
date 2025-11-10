# Standard Library
import os
from collections import defaultdict
from typing import Dict, List

from temporalio import activity

# Third Party
import tomlkit
from unoplat_code_confluence_commons.programming_language_metadata import (
    PackageManagerType,
    ProgrammingLanguageMetadata,
)
from validate_pyproject import api as validator_api
from validate_pyproject.errors import ValidationError

from src.code_confluence_flow_bridge.models.code_confluence_parsing_models import (
    UnoplatPackageManagerMetadata,
    UnoplatProjectDependency,
    UnoplatVersion,
)
from src.code_confluence_flow_bridge.parser.package_manager.package_manager_strategy import (
    PackageManagerStrategy,
)
from src.code_confluence_flow_bridge.parser.package_manager.utils.requirements_utils import (
    RequirementsUtils,
)
from src.code_confluence_flow_bridge.parser.package_manager.utils.setup_parser import (
    SetupParser,
)
from src.code_confluence_flow_bridge.utility.author_utils import normalize_authors


class PythonPoetryStrategy(PackageManagerStrategy):
    def process_metadata(
        self, local_workspace_path: str, metadata: ProgrammingLanguageMetadata
    ) -> UnoplatPackageManagerMetadata:
        """Process poetry specific metadata from pyproject.toml"""
        pyproject_path = os.path.join(local_workspace_path, "pyproject.toml")

        if not os.path.exists(pyproject_path):
            activity.logger.warning(
                "pyproject.toml not found", {"path": pyproject_path}
            )
            return self._create_empty_metadata(metadata)

        try:
            with open(pyproject_path, "r") as f:
                pyproject_content = f.read()
                pyproject_data = tomlkit.parse(pyproject_content)

            # Validate PEP 621 compliance
            try:
                validator = validator_api.Validator()
                validator(pyproject_data)
            except ValidationError as e:
                activity.logger.warning(
                    "pyproject.toml validation failed",
                    {"error": e.message, "path": pyproject_path},
                )
                # Continue processing even if validation fails, but log the warning

            poetry_data = pyproject_data.get("tool", {}).get("poetry", {})
            project_data = pyproject_data.get("project", {})

            if not poetry_data:
                return self._handle_fallback(local_workspace_path, metadata)

            # Parse dependencies from all groups into grouped structure
            dependencies = self._parse_all_dependency_groups(poetry_data)

            # Get Python version requirement - check PEP 621 first, then Poetry
            programming_language_version = (
                project_data.get("requires-python")  # PEP 621 format
                or poetry_data.get("dependencies", {}).get("python")  # Poetry format
                or metadata.language_version  # Fallback
            )

            # Create metadata object with all available fields
            return UnoplatPackageManagerMetadata(
                dependencies=dependencies,
                package_name=poetry_data.get("name"),
                programming_language=metadata.language.value,
                package_manager=metadata.package_manager.value
                if metadata.package_manager
                else PackageManagerType.POETRY.value,
                programming_language_version=programming_language_version,
                project_version=poetry_data.get("version"),
                description=poetry_data.get("description"),
                authors=normalize_authors(poetry_data.get("authors")),
                entry_points=self._get_entry_points(poetry_data.get("scripts", {})),
                license=poetry_data.get("license"),
                homepage=poetry_data.get("homepage"),
                repository=poetry_data.get("repository"),
                documentation=poetry_data.get("documentation"),
                keywords=poetry_data.get("keywords", []),
                maintainers=poetry_data.get("maintainers", []),
                readme=poetry_data.get("readme"),
                manifest_path=metadata.manifest_path,
            )

        except Exception as e:
            activity.logger.error(
                "Error parsing pyproject.toml",
                {"error": str(e), "path": pyproject_path},
            )
            return self._create_empty_metadata(metadata)

    def _handle_fallback(
        self, local_workspace_path: str, metadata: ProgrammingLanguageMetadata
    ) -> UnoplatPackageManagerMetadata:
        """Handle fallback to requirements.txt when no poetry config is found"""
        package_manager_value = (
            metadata.package_manager.value if metadata.package_manager else "unknown"
        )
        activity.logger.warning(
            "No poetry configuration found, falling back to requirements",
            {"path": local_workspace_path, "package_manager": package_manager_value},
        )
        fallback_dependencies = RequirementsUtils.parse_requirements_folder(
            local_workspace_path
        )
        grouped_dependencies: Dict[str, Dict[str, UnoplatProjectDependency]] = (
            defaultdict(dict)
        )

        for dep_name, dependency in fallback_dependencies.items():
            grouped_dependencies["default"][dep_name] = dependency

        grouped_dependencies.setdefault("default", {})

        package_manager = UnoplatPackageManagerMetadata(
            dependencies=dict(grouped_dependencies),
            programming_language=metadata.language.value,
            package_manager=PackageManagerType.PIP.value,
            manifest_path=metadata.manifest_path,
        )
        try:
            return SetupParser.parse_setup_file(local_workspace_path, package_manager)
        except FileNotFoundError:
            activity.logger.warning("setup.py not found, skipping setup.py parsing")
            return package_manager

    def _parse_all_dependency_groups(
        self, poetry_data: Dict
    ) -> Dict[str, Dict[str, UnoplatProjectDependency]]:
        """Parse dependencies from main, legacy dev, and named groups."""

        grouped_dependencies: Dict[str, Dict[str, UnoplatProjectDependency]] = (
            defaultdict(dict)
        )
        group_includes: Dict[str, List[str]] = {}

        # Main dependencies map to the default group
        main_deps = poetry_data.get("dependencies", {})
        grouped_dependencies["default"].update(self._parse_dependencies(main_deps))

        # Legacy dev-dependencies block
        dev_deps = poetry_data.get("dev-dependencies", {})
        if dev_deps:
            grouped_dependencies["dev"].update(self._parse_dependencies(dev_deps))

        # Poetry 1.2+ dependency groups
        for group_name, group_data in poetry_data.get("group", {}).items():
            if not isinstance(group_data, dict):
                continue

            group_dependencies = group_data.get("dependencies", {})
            if group_dependencies:
                grouped_dependencies[group_name].update(
                    self._parse_dependencies(group_dependencies)
                )

            include_groups = self._extract_include_groups(group_data)
            if include_groups:
                group_includes[group_name] = include_groups

        # Apply include-groups by merging referenced group contents
        for target_group, includes in group_includes.items():
            target_bucket = grouped_dependencies.setdefault(target_group, {})
            for included_group in includes:
                included_bucket = grouped_dependencies.get(included_group, {})
                for dep_name, dependency in included_bucket.items():
                    if dep_name not in target_bucket:
                        target_bucket[dep_name] = dependency.model_copy(deep=True)

        return {group: deps for group, deps in grouped_dependencies.items()}

    def _extract_include_groups(self, group_data: Dict) -> List[str]:
        """Normalize include-groups declarations to a list."""

        include_groups = group_data.get("include-groups")
        if include_groups is None:
            include_groups = group_data.get("include_groups")

        if isinstance(include_groups, list):
            return [g for g in include_groups if isinstance(g, str) and g]

        if isinstance(include_groups, str) and include_groups:
            return [include_groups]

        return []

    def _parse_version_constraint(self, constraint: str) -> UnoplatVersion:
        """Parse version constraint using packaging library"""
        if not constraint or constraint == "*":
            return UnoplatVersion()

        try:
            # Simply store the raw version constraint as specifier
            return UnoplatVersion(specifier=constraint)

        except Exception as e:
            activity.logger.warning(
                "Error parsing version constraint '{}': {}", constraint, str(e)
            )
            return UnoplatVersion()

    def _create_empty_metadata(
        self, metadata: ProgrammingLanguageMetadata
    ) -> UnoplatPackageManagerMetadata:
        """Create empty metadata with basic information"""
        return UnoplatPackageManagerMetadata(
            dependencies={"default": {}},
            programming_language=metadata.language.value,
            package_manager=metadata.package_manager.value
            if metadata.package_manager
            else PackageManagerType.POETRY.value,
            programming_language_version=metadata.language_version,
            manifest_path=metadata.manifest_path,
        )

    def _parse_dependencies(
        self, deps_dict: Dict
    ) -> Dict[str, UnoplatProjectDependency]:
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
                        source_reference = (
                            constraint.get("rev")
                            or constraint.get("branch")
                            or constraint.get("tag")
                        )
                        subdirectory = constraint.get("subdirectory")
                        version = (
                            UnoplatVersion()
                        )  # Git dependencies don't have version constraints

                    # Handle path dependencies
                    elif "path" in constraint:
                        source = "path"
                        source_url = constraint["path"]
                        version = (
                            UnoplatVersion()
                        )  # Path dependencies don't have version constraints

                    # Handle url dependencies
                    elif "url" in constraint:
                        source = "url"
                        source_url = constraint["url"]
                        version = (
                            UnoplatVersion()
                        )  # URL dependencies don't have version constraints
                else:
                    activity.logger.warning(
                        "Skipping invalid dependency specification for {}", name
                    )
                    continue

                tuple_dependency = UnoplatProjectDependency(
                    version=version,
                    extras=extras,
                    source=source,
                    source_url=source_url,
                    source_reference=source_reference,
                    subdirectory=subdirectory,
                )
                dependencies[name] = tuple_dependency

            except Exception as e:
                activity.logger.warning(
                    "Error parsing dependency",
                    {"dependency": name, "error": str(e), "group": group},
                )
                # Add dependency with empty version constraint
                tuple_dependency = UnoplatProjectDependency(version=UnoplatVersion())
                dependencies[name] = tuple_dependency

        return dependencies

    def _get_entry_points(self, scripts: Dict[str, str]) -> Dict[str, str]:
        """Get all entry points from Poetry scripts section."""
        return scripts if scripts else {}
