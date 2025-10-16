# Standard Library
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Third Party
from loguru import logger
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    ValidationInfo,
    field_validator,
    model_validator,
)
from unoplat_code_confluence_commons.base_models import ProgrammingLanguageMetadata


class PackageJsonNotFoundError(FileNotFoundError):
    """Raised when the supplied package.json cannot be found within the workspace."""


class PackageJsonParseError(ValueError):
    """Raised when package.json cannot be parsed or validated."""


class PackageJsonManifest(BaseModel):
    """Normalized snapshot of package.json content for downstream TypeScript strategies."""

    model_config = ConfigDict(populate_by_name=True)

    manifest_path: Optional[str] = Field(
        default=None, description="Manifest path relative to the workspace root."
    )

    name: Optional[str] = Field(default=None)
    version: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    keywords: List[str] = Field(default_factory=list)
    author: Optional[Any] = Field(default=None)
    contributors: List[Any] = Field(default_factory=list)
    maintainers: List[Any] = Field(default_factory=list)
    license: Optional[Any] = Field(default=None)
    repository: Optional[Any] = Field(default=None)
    bugs: Optional[Any] = Field(default=None)
    homepage: Optional[str] = Field(default=None)
    documentation: Optional[str] = Field(default=None)
    readme: Optional[Any] = Field(default=None)

    dependencies: Dict[str, Dict[str, str]] = Field(
        default_factory=dict,
        description="Dependency groups extracted from package.json (default/dev/peer/optional/bundled/override).",
    )
    scripts: Dict[str, str] = Field(default_factory=dict)
    bin: Dict[str, str] = Field(default_factory=dict)
    exports: Optional[Any] = Field(default=None)
    types: Optional[str] = Field(default=None)
    main: Optional[str] = Field(default=None)
    module: Optional[str] = Field(default=None)
    types_versions: Optional[Dict[str, Any]] = Field(
        default=None, alias="typesVersions"
    )
    engines: Optional[Dict[str, Any]] = Field(default=None)

    package_manager_field: Optional[str] = Field(default=None, alias="packageManager")
    workspaces: Optional[Any] = Field(default=None)

    @model_validator(mode="before")
    @classmethod
    def _build_from_raw(cls, data: Any, info: ValidationInfo) -> Dict[str, Any]:
        if not isinstance(data, dict):
            raise ValueError("package.json content must deserialize to an object")

        context = info.context or {}
        manifest_path = context.get("manifest_path")
        manifest_directory = context.get("manifest_directory")
        if manifest_directory is not None and not isinstance(manifest_directory, Path):
            manifest_directory = Path(manifest_directory)

        # Only set fields that require special handling
        # Pydantic will automatically map all other fields from data by name
        transformed: Dict[str, Any] = {
            "manifest_path": manifest_path,
            "dependencies": _build_dependency_sections(data),
            "scripts": _ensure_dict(data.get("scripts"), section_name="scripts"),
            "engines": _ensure_dict(data.get("engines"), section_name="engines"),
        }

        # Merge original data with transformed fields
        # Transformed fields take precedence over original data
        return {**data, **transformed}

    @field_validator("bin", mode="before")
    @classmethod
    def _normalize_bin(cls, value: Any, info: ValidationInfo) -> Dict[str, str]:
        if value is None:
            return {}
        if isinstance(value, dict):
            return {str(k): str(v) for k, v in value.items() if v is not None}
        if isinstance(value, str):
            package_name = getattr(info.data, "name", None)
            key = (
                package_name
                if isinstance(package_name, str) and package_name
                else "default"
            )
            return {key: value}
        logger.warning(
            "Unexpected bin section type", {"bin_type": type(value).__name__}
        )
        return {}

    @field_validator("keywords", mode="before")
    @classmethod
    def _normalize_keywords(cls, value: Any) -> List[str]:
        if value is None:
            return []
        if isinstance(value, list):
            return [str(item) for item in value]
        if isinstance(value, str):
            return [value]
        logger.warning(
            "Unexpected keywords type", {"keywords_type": type(value).__name__}
        )
        return []

    @field_validator("contributors", "maintainers", mode="before")
    @classmethod
    def _ensure_list(cls, value: Any) -> List[Any]:
        if value is None:
            return []
        if isinstance(value, list):
            return value
        return [value]


def load_package_json(
    local_workspace_path: str, metadata: ProgrammingLanguageMetadata
) -> PackageJsonManifest:
    """Load and normalize package.json according to metadata manifest hints."""

    manifest_path, manifest_relative = _resolve_manifest_path(
        local_workspace_path, metadata.manifest_path
    )
    manifest_text = _read_manifest_text(manifest_path)

    try:
        return PackageJsonManifest.model_validate_json(
            manifest_text,
            context={
                "manifest_path": manifest_relative,
                "manifest_directory": manifest_path.parent,
            },
        )
    except ValidationError as exc:
        logger.error(
            "Unable to parse package.json",
            {"path": str(manifest_path), "errors": exc.errors()},
        )
        raise PackageJsonParseError(str(exc)) from exc


def _resolve_manifest_path(
    local_workspace_path: str, manifest_hint: str
) -> Tuple[Path, str]:
    """Resolve manifest path to absolute path, ensuring it's within workspace.

    Args:
        local_workspace_path: Absolute path to workspace/codebase root
        manifest_hint: Relative path to manifest file (e.g., "package.json" or "frontend/package.json")

    Returns:
        Tuple of (absolute_path, relative_path)

    Raises:
        PackageJsonNotFoundError: If workspace doesn't exist, manifest is outside workspace, or file not found
    """
    workspace = Path(local_workspace_path).resolve()
    if not workspace.exists():
        raise PackageJsonNotFoundError(f"Workspace does not exist: {workspace}")

    # manifest_hint is guaranteed to be relative
    candidate_rel = Path(manifest_hint)
    candidate_abs = (workspace / candidate_rel).resolve()
    manifest_relative = str(candidate_rel)

    try:
        candidate_abs.relative_to(workspace)
    except ValueError as exc:
        logger.error(
            "Manifest resolved outside of workspace",
            {"workspace": str(workspace), "candidate": str(candidate_abs)},
        )
        raise PackageJsonNotFoundError(
            "manifest_path must reside within the workspace"
        ) from exc

    if not candidate_abs.exists():
        logger.error("package.json not found", {"path": str(candidate_abs)})
        raise PackageJsonNotFoundError(str(candidate_abs))

    return candidate_abs, manifest_relative

#todo: check afterwards to make this read  async
def _read_manifest_text(path: Path) -> str:
    with path.open("r", encoding="utf-8") as handle:
        data = handle.read()
    return data


def _ensure_dict(value: Any, *, section_name: str) -> Dict[str, Any]:
    if value is None:
        return {}
    if isinstance(value, dict):
        return value
    logger.warning(
        "Expected object section in package.json",
        {"section": section_name, "actual_type": type(value).__name__},
    )
    return {}


def _add_dependency_section(
    dependency_sections: Dict[str, Dict[str, str]], target_key: str, source_value: Any
) -> None:
    if isinstance(source_value, dict):
        dependency_sections[target_key].update(
            {str(k): str(v) for k, v in source_value.items()}
        )
    elif source_value is None:
        return
    elif isinstance(source_value, list) and target_key == "bundled":
        dependency_sections[target_key].update(
            {str(item): "true" for item in source_value}
        )
    else:
        logger.warning(
            "Unexpected dependency section type",
            {"section": target_key, "actual_type": type(source_value).__name__},
        )


def _build_dependency_sections(manifest: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
    dependency_sections: Dict[str, Dict[str, str]] = {
        "default": {},
        "dev": {},
        "peer": {},
        "optional": {},
        "bundled": {},
        "override": {},
    }

    _add_dependency_section(
        dependency_sections, "default", manifest.get("dependencies")
    )
    _add_dependency_section(dependency_sections, "dev", manifest.get("devDependencies"))
    _add_dependency_section(
        dependency_sections, "peer", manifest.get("peerDependencies")
    )
    _add_dependency_section(
        dependency_sections, "optional", manifest.get("optionalDependencies")
    )
    _add_dependency_section(
        dependency_sections,
        "bundled",
        manifest.get("bundledDependencies") or manifest.get("bundleDependencies"),
    )

    overrides = manifest.get("overrides")
    if isinstance(overrides, dict):
        dependency_sections["override"].update(
            {
                str(k): json.dumps(v) if isinstance(v, (dict, list)) else str(v)
                for k, v in overrides.items()
            }
        )
    elif overrides is not None:
        logger.warning(
            "Unexpected overrides type", {"actual_type": type(overrides).__name__}
        )

    return dependency_sections
