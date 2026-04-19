from __future__ import annotations

from pydantic_ai_backends import RuntimeConfig

from unoplat_code_confluence_query_engine.config.settings import EnvironmentSettings
from unoplat_code_confluence_query_engine.models.repository.repository_ruleset_metadata import (
    CodebaseMetadata,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_backend_paths import (
    resolve_repository_root,
    resolve_work_dir,
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
    work_dir = resolve_work_dir(metadata)

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
    repository_root = resolve_repository_root(metadata)
    return {repository_root: repository_root}


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
