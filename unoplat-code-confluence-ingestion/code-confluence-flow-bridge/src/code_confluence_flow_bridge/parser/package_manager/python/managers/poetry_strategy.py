import os
from collections import defaultdict
from collections.abc import Mapping
from typing import cast

from temporalio import activity
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
from src.code_confluence_flow_bridge.parser.package_manager.python.manifests.requirements_loader import (
    RequirementsUtils,
)
from src.code_confluence_flow_bridge.parser.package_manager.python.manifests.setup_parser import (
    SetupParser,
)
from src.code_confluence_flow_bridge.parser.package_manager.shared.strategy import (
    PackageManagerStrategy,
)
from src.code_confluence_flow_bridge.utility.author_utils import normalize_authors


class PythonPoetryStrategy(PackageManagerStrategy):
    def process_metadata(
        self, local_workspace_path: str, metadata: ProgrammingLanguageMetadata
    ) -> UnoplatPackageManagerMetadata:
        """Process poetry specific metadata from pyproject.toml."""
        pyproject_path = os.path.join(local_workspace_path, "pyproject.toml")

        if not os.path.exists(pyproject_path):
            activity.logger.warning("pyproject.toml not found: %s", pyproject_path)
            return self._create_empty_metadata(metadata)

        try:
            with open(pyproject_path, "r", encoding="utf-8") as file_handle:
                pyproject_content = file_handle.read()
            pyproject_data = tomlkit.parse(pyproject_content)

            try:
                validator = validator_api.Validator()
                validator(pyproject_data)
            except ValidationError as exc:
                activity.logger.warning(
                    "pyproject.toml validation failed: %s (%s)",
                    str(exc),
                    pyproject_path,
                )

            pyproject_mapping = self._coerce_string_key_dict(pyproject_data)
            tool_data = self._coerce_string_key_dict(pyproject_mapping.get("tool"))
            poetry_data = self._coerce_string_key_dict(tool_data.get("poetry"))
            project_data = self._coerce_string_key_dict(
                pyproject_mapping.get("project")
            )

            if not poetry_data:
                return self._handle_fallback(local_workspace_path, metadata)

            dependencies = self._parse_all_dependency_groups(poetry_data)
            poetry_dependencies = self._coerce_string_key_dict(
                poetry_data.get("dependencies")
            )
            programming_language_version = (
                self._coerce_string(project_data.get("requires-python"))
                or self._coerce_string(poetry_dependencies.get("python"))
                or metadata.language_version
            )

            return UnoplatPackageManagerMetadata(
                dependencies=dependencies,
                package_name=self._coerce_string(poetry_data.get("name")),
                programming_language=metadata.language.value,
                package_manager=metadata.package_manager.value
                if metadata.package_manager
                else PackageManagerType.POETRY.value,
                programming_language_version=programming_language_version,
                project_version=self._coerce_string(poetry_data.get("version")),
                description=self._coerce_string(poetry_data.get("description")),
                authors=normalize_authors(
                    self._coerce_string_list_or_none(poetry_data.get("authors"))
                ),
                entry_points=self._get_entry_points(
                    self._coerce_script_mapping(poetry_data.get("scripts"))
                ),
                license=self._normalize_license(poetry_data.get("license")),
                homepage=self._coerce_string(poetry_data.get("homepage")),
                repository=self._coerce_string(poetry_data.get("repository")),
                documentation=self._coerce_string(poetry_data.get("documentation")),
                keywords=self._coerce_string_list(poetry_data.get("keywords")),
                maintainers=self._coerce_string_list(poetry_data.get("maintainers")),
                readme=self._coerce_string(poetry_data.get("readme")),
                manifest_path=metadata.manifest_path,
            )
        except Exception as exc:
            activity.logger.error(
                "Error parsing pyproject.toml: %s (%s)",
                str(exc),
                pyproject_path,
            )
            return self._create_empty_metadata(metadata)

    def _handle_fallback(
        self, local_workspace_path: str, metadata: ProgrammingLanguageMetadata
    ) -> UnoplatPackageManagerMetadata:
        """Handle fallback to requirements.txt when no poetry config is found."""
        package_manager_value = (
            metadata.package_manager.value if metadata.package_manager else "unknown"
        )
        activity.logger.warning(
            "No poetry configuration found, falling back to requirements: %s (%s)",
            local_workspace_path,
            package_manager_value,
        )
        fallback_dependencies = RequirementsUtils.parse_requirements_folder(
            local_workspace_path
        )
        grouped_dependencies: dict[str, dict[str, UnoplatProjectDependency]] = (
            defaultdict(dict)
        )

        for dependency_name, dependency in fallback_dependencies.items():
            grouped_dependencies["default"][dependency_name] = dependency

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
        self, poetry_data: dict[str, object]
    ) -> dict[str, dict[str, UnoplatProjectDependency]]:
        """Parse dependencies from main, legacy dev, and named groups."""
        grouped_dependencies: dict[str, dict[str, UnoplatProjectDependency]] = (
            defaultdict(dict)
        )
        group_includes: dict[str, list[str]] = {}

        main_dependencies = self._coerce_string_key_dict(
            poetry_data.get("dependencies")
        )
        grouped_dependencies["default"].update(
            self._parse_dependencies(main_dependencies)
        )

        dev_dependencies = self._coerce_string_key_dict(
            poetry_data.get("dev-dependencies")
        )
        if dev_dependencies:
            grouped_dependencies["dev"].update(
                self._parse_dependencies(dev_dependencies)
            )

        group_section = self._coerce_string_key_dict(poetry_data.get("group"))
        for group_name, raw_group_data in group_section.items():
            group_data = self._coerce_string_key_dict(raw_group_data)
            if not group_data:
                continue

            group_dependencies = self._coerce_string_key_dict(
                group_data.get("dependencies")
            )
            if group_dependencies:
                grouped_dependencies[group_name].update(
                    self._parse_dependencies(group_dependencies)
                )

            include_groups = self._extract_include_groups(group_data)
            if include_groups:
                group_includes[group_name] = include_groups

        for target_group, includes in group_includes.items():
            target_bucket = grouped_dependencies.setdefault(target_group, {})
            for included_group in includes:
                included_bucket = grouped_dependencies.get(included_group, {})
                for dependency_name, dependency in included_bucket.items():
                    if dependency_name not in target_bucket:
                        target_bucket[dependency_name] = dependency.model_copy(
                            deep=True
                        )

        return {group_name: deps for group_name, deps in grouped_dependencies.items()}

    def _extract_include_groups(self, group_data: dict[str, object]) -> list[str]:
        """Normalize include-groups declarations to a list."""
        include_groups = group_data.get("include-groups")
        if include_groups is None:
            include_groups = group_data.get("include_groups")

        if isinstance(include_groups, str) and include_groups:
            return [include_groups]
        return self._coerce_string_list(include_groups)

    def _parse_version_constraint(self, constraint: str) -> UnoplatVersion:
        """Parse version constraint using packaging library."""
        if not constraint or constraint == "*":
            return UnoplatVersion()

        try:
            return UnoplatVersion(specifier=constraint)
        except Exception as exc:
            activity.logger.warning(
                "Error parsing version constraint '%s': %s",
                constraint,
                str(exc),
            )
            return UnoplatVersion()

    def _create_empty_metadata(
        self, metadata: ProgrammingLanguageMetadata
    ) -> UnoplatPackageManagerMetadata:
        """Create empty metadata with basic information."""
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
        self, deps_dict: dict[str, object]
    ) -> dict[str, UnoplatProjectDependency]:
        dependencies: dict[str, UnoplatProjectDependency] = {}

        for name, constraint in deps_dict.items():
            if name == "python":
                continue

            version = UnoplatVersion()
            extras: list[str] | None = None
            source: str | None = None
            source_url: str | None = None
            source_reference: str | None = None
            subdirectory: str | None = None

            try:
                if isinstance(constraint, str):
                    version = self._parse_version_constraint(constraint)
                else:
                    constraint_data = self._coerce_string_key_dict(constraint)
                    if not constraint_data:
                        activity.logger.warning(
                            "Skipping invalid dependency specification for %s", name
                        )
                        continue

                    version_constraint = self._coerce_string(
                        constraint_data.get("version")
                    )
                    if version_constraint is not None:
                        version = self._parse_version_constraint(version_constraint)

                    extras = self._coerce_string_list_or_none(
                        constraint_data.get("extras")
                    )

                    git_source = self._coerce_string(constraint_data.get("git"))
                    path_source = self._coerce_string(constraint_data.get("path"))
                    url_source = self._coerce_string(constraint_data.get("url"))

                    if git_source is not None:
                        source = "git"
                        source_url = git_source
                        source_reference = self._first_present_string(
                            constraint_data.get("rev"),
                            constraint_data.get("branch"),
                            constraint_data.get("tag"),
                        )
                        subdirectory = self._coerce_string(
                            constraint_data.get("subdirectory")
                        )
                        version = UnoplatVersion()
                    elif path_source is not None:
                        source = "path"
                        source_url = path_source
                        version = UnoplatVersion()
                    elif url_source is not None:
                        source = "url"
                        source_url = url_source
                        version = UnoplatVersion()

                dependencies[name] = UnoplatProjectDependency(
                    version=version,
                    extras=extras,
                    source=source,
                    source_url=source_url,
                    source_reference=source_reference,
                    subdirectory=subdirectory,
                )
            except Exception as exc:
                activity.logger.warning(
                    "Error parsing dependency %s: %s", name, str(exc)
                )
                dependencies[name] = UnoplatProjectDependency(version=UnoplatVersion())

        return dependencies

    def _get_entry_points(self, scripts: dict[str, str]) -> dict[str, str]:
        """Get all entry points from Poetry scripts section."""
        return scripts if scripts else {}

    @staticmethod
    def _coerce_string_key_dict(value: object) -> dict[str, object]:
        if not isinstance(value, Mapping):
            return {}

        mapping_value = cast(Mapping[object, object], value)
        normalized: dict[str, object] = {}
        for key, item in mapping_value.items():
            if isinstance(key, str):
                normalized[key] = item
        return normalized

    @staticmethod
    def _coerce_string(value: object) -> str | None:
        return value if isinstance(value, str) else None

    @staticmethod
    def _coerce_string_list(value: object) -> list[str]:
        if not isinstance(value, list):
            return []

        list_value = cast(list[object], value)
        return [item for item in list_value if isinstance(item, str)]

    def _coerce_string_list_or_none(self, value: object) -> list[str] | None:
        values = self._coerce_string_list(value)
        return values or None

    def _coerce_script_mapping(self, value: object) -> dict[str, str]:
        script_mapping = self._coerce_string_key_dict(value)
        return {
            name: entry_point
            for name, entry_point in script_mapping.items()
            if isinstance(entry_point, str)
        }

    def _normalize_license(self, value: object) -> dict[str, object] | None:
        if value is None:
            return None
        if isinstance(value, str):
            return {"text": value}

        license_mapping = self._coerce_string_key_dict(value)
        return license_mapping or None

    def _first_present_string(self, *values: object) -> str | None:
        for value in values:
            normalized_value = self._coerce_string(value)
            if normalized_value is not None:
                return normalized_value
        return None
