from __future__ import annotations

from pathlib import PurePosixPath

from pydantic_ai_backends import RuntimeConfig

from unoplat_code_confluence_query_engine.config.settings import EnvironmentSettings
from unoplat_code_confluence_query_engine.models.repository.repository_ruleset_metadata import (
    CodebaseMetadata,
)


def resolve_development_workflow_runtime(
    metadata: CodebaseMetadata,
    settings: EnvironmentSettings,
) -> RuntimeConfig:
    """Resolve a deterministic Docker runtime for development-workflow runs.

    The runtime is selected from codebase metadata only, keeping the behavior
    Temporal-safe and reproducible for repeated tool calls within a workflow run.
    Runtime images are prebuilt and selected through settings so the worker does
    not need to mutate PATH or install toolchains during sandbox startup.
    """
    language = metadata.codebase_programming_language
    package_manager = metadata.codebase_package_manager
    work_dir = resolve_development_workflow_work_dir(metadata)

    if language == "python":
        return _build_python_runtime(package_manager, settings.dev_workflow_python_image, work_dir)
    if language in {"typescript", "javascript"}:
        return _build_typescript_runtime(
            package_manager,
            settings.dev_workflow_typescript_image,
            work_dir,
        )
    return _build_default_runtime(settings.dev_workflow_python_image, work_dir)


def resolve_development_workflow_repository_mounts(
    metadata: CodebaseMetadata,
) -> dict[str, str]:
    """Mount only the active repository into the sandbox at the same absolute path."""
    repository_root = resolve_development_workflow_repository_root(metadata)
    return {repository_root: repository_root}


def resolve_development_workflow_repository_root(metadata: CodebaseMetadata) -> str:
    """Derive the repository root from absolute codebase metadata.

    ``codebase_path`` is expected to be the absolute filesystem path to the
    current codebase root, while ``codebase_name`` is expected to be the path
    relative to the repository root. We use that relationship to walk back to
    the repository root so only the active repository is mounted into the
    sandbox.
    """
    codebase_path = PurePosixPath(resolve_development_workflow_work_dir(metadata))
    codebase_parts = _normalize_codebase_name_parts(metadata.codebase_name)

    if not codebase_parts:
        return str(codebase_path)

    if len(codebase_path.parts) <= len(codebase_parts):
        raise ValueError(
            "Cannot derive repository root because codebase_path is shallower "
            f"than codebase_name: {metadata.codebase_path!r} vs {metadata.codebase_name!r}"
        )

    repository_root = PurePosixPath(*codebase_path.parts[: -len(codebase_parts)])
    expected_codebase_path = repository_root.joinpath(*codebase_parts)
    if expected_codebase_path != codebase_path:
        raise ValueError(
            "Codebase metadata is inconsistent: codebase_path does not end with "
            f"codebase_name ({metadata.codebase_path!r} vs {metadata.codebase_name!r})"
        )

    return str(repository_root)


def resolve_development_workflow_work_dir(metadata: CodebaseMetadata) -> str:
    """Return the absolute working directory for sandboxed tool execution."""
    codebase_path = metadata.codebase_path.strip()
    path = PurePosixPath(codebase_path)
    if not codebase_path or not path.is_absolute():
        raise ValueError(
            f"Development workflow sandbox requires an absolute codebase_path, got: {metadata.codebase_path!r}"
        )
    return str(path)


def _build_python_runtime(
    package_manager: str,
    image: str,
    work_dir: str,
) -> RuntimeConfig:
    runtime_name = package_manager if package_manager in {"pip", "uv", "poetry"} else "default"

    return RuntimeConfig(
        name=f"unoplat-python-{runtime_name}",
        description=(
            "Python development workflow runtime from a prebuilt sandbox image"
            if package_manager in {"pip", "uv", "unknown"}
            else (
                "Python development workflow runtime from a prebuilt sandbox image "
                f"with {package_manager} support"
            )
        ),
        image=image,
        package_manager="pip",
        work_dir=work_dir,
    )


def _build_typescript_runtime(
    package_manager: str,
    image: str,
    work_dir: str,
) -> RuntimeConfig:
    runtime_name = package_manager if package_manager in {"npm", "pnpm", "yarn", "bun"} else "default"
    description = (
        "TypeScript development workflow runtime from a prebuilt sandbox image"
        if package_manager in {"npm", "unknown"}
        else (
            "TypeScript development workflow runtime from a prebuilt sandbox image "
            f"with {package_manager} support"
        )
    )

    return RuntimeConfig(
        name=f"unoplat-typescript-{runtime_name}",
        description=description,
        image=image,
        package_manager="npm",
        work_dir=work_dir,
    )


def _build_default_runtime(image: str, work_dir: str) -> RuntimeConfig:
    return RuntimeConfig(
        name="unoplat-default",
        description="Fallback development workflow runtime from a prebuilt sandbox image",
        image=image,
        work_dir=work_dir,
    )


def _normalize_codebase_name_parts(codebase_name: str) -> tuple[str, ...]:
    raw = codebase_name.strip()
    if raw in {"", "."}:
        return ()

    path = PurePosixPath(raw)
    parts = path.parts
    if any(part == ".." for part in parts):
        raise ValueError(f"codebase_name must not traverse upward: {codebase_name!r}")

    return tuple(part for part in parts if part not in {"", ".", "/"})
