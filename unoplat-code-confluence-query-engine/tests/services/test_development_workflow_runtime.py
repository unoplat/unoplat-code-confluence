from pydantic_ai_backends import RuntimeConfig

from unoplat_code_confluence_query_engine.config.settings import EnvironmentSettings
from unoplat_code_confluence_query_engine.models.repository.repository_ruleset_metadata import (
    CodebaseMetadata,
)
from unoplat_code_confluence_query_engine.services.temporal.development_workflow_runtime import (
    resolve_development_workflow_repository_mounts,
    resolve_development_workflow_repository_root,
    resolve_development_workflow_runtime,
    resolve_development_workflow_work_dir,
)
from unoplat_code_confluence_query_engine.services.temporal.service_registry import (
    ServiceRegistry,
)

PYTHON_IMAGE = (
    "ghcr.io/unoplat/unoplat-code-confluence/"
    "code-confluence-dev-workflow-python:0.1.0"
)
TYPESCRIPT_IMAGE = (
    "ghcr.io/unoplat/unoplat-code-confluence/"
    "code-confluence-dev-workflow-typescript:0.1.0"
)


def _build_settings() -> EnvironmentSettings:
    return EnvironmentSettings.model_construct(
        dev_workflow_python_image=PYTHON_IMAGE,
        dev_workflow_typescript_image=TYPESCRIPT_IMAGE,
        dev_workflow_idle_timeout_seconds=3600,
        dev_workflow_network_mode="bridge",
    )


def _build_metadata(
    *,
    language: str,
    package_manager: str,
    codebase_name: str = "apps/api",
    codebase_path: str = "/opt/unoplat/repositories/acme-repo/apps/api",
) -> CodebaseMetadata:
    return CodebaseMetadata(
        codebase_name=codebase_name,
        codebase_path=codebase_path,
        codebase_programming_language=language,
        codebase_package_manager=package_manager,
        codebase_package_manager_provenance="local",
        codebase_workspace_root=".",
        codebase_workspace_root_path=codebase_path,
    )


def test_resolve_python_runtime_uses_prebuilt_image_and_codebase_work_dir() -> None:
    metadata = _build_metadata(language="python", package_manager="poetry")

    runtime = resolve_development_workflow_runtime(metadata, _build_settings())

    assert runtime == RuntimeConfig(
        name="unoplat-python-poetry",
        description=(
            "Python development workflow runtime from a prebuilt sandbox image "
            "with poetry support"
        ),
        image=PYTHON_IMAGE,
        package_manager="pip",
        work_dir="/opt/unoplat/repositories/acme-repo/apps/api",
    )


def test_resolve_typescript_runtime_uses_prebuilt_image_and_codebase_work_dir() -> None:
    metadata = _build_metadata(language="typescript", package_manager="pnpm")

    runtime = resolve_development_workflow_runtime(metadata, _build_settings())

    assert runtime == RuntimeConfig(
        name="unoplat-typescript-pnpm",
        description=(
            "TypeScript development workflow runtime from a prebuilt sandbox image "
            "with pnpm support"
        ),
        image=TYPESCRIPT_IMAGE,
        package_manager="npm",
        work_dir="/opt/unoplat/repositories/acme-repo/apps/api",
    )


def test_resolve_default_runtime_falls_back_to_python_image() -> None:
    metadata = _build_metadata(language="go", package_manager="go modules")

    runtime = resolve_development_workflow_runtime(metadata, _build_settings())

    assert runtime == RuntimeConfig(
        name="unoplat-default",
        description="Fallback development workflow runtime from a prebuilt sandbox image",
        image=PYTHON_IMAGE,
        work_dir="/opt/unoplat/repositories/acme-repo/apps/api",
    )


def test_resolve_work_dir_requires_absolute_codebase_path() -> None:
    metadata = _build_metadata(
        language="python",
        package_manager="pip",
        codebase_path="apps/api",
    )

    try:
        resolve_development_workflow_work_dir(metadata)
    except ValueError as exc:
        assert "absolute codebase_path" in str(exc)
    else:
        raise AssertionError("Expected ValueError for non-absolute codebase_path")


def test_resolve_repository_root_and_mounts_use_active_repository_only() -> None:
    metadata = _build_metadata(language="python", package_manager="pip")

    assert resolve_development_workflow_repository_root(metadata) == (
        "/opt/unoplat/repositories/acme-repo"
    )
    assert resolve_development_workflow_repository_mounts(metadata) == {
        "/opt/unoplat/repositories/acme-repo": "/opt/unoplat/repositories/acme-repo"
    }


def test_resolve_repository_root_returns_codebase_path_when_codebase_is_repo_root() -> None:
    metadata = _build_metadata(
        language="python",
        package_manager="pip",
        codebase_name=".",
        codebase_path="/opt/unoplat/repositories/acme-repo",
    )

    assert resolve_development_workflow_repository_root(metadata) == (
        "/opt/unoplat/repositories/acme-repo"
    )


def test_service_registry_runtime_resolution_delegates_to_helper() -> None:
    metadata = _build_metadata(language="python", package_manager="uv")
    registry = ServiceRegistry()
    registry._settings = _build_settings()

    assert registry._resolve_runtime(metadata) == resolve_development_workflow_runtime(
        metadata,
        registry._settings,
    )


def test_service_registry_mount_resolution_delegates_to_helper() -> None:
    metadata = _build_metadata(language="python", package_manager="uv")

    assert ServiceRegistry._resolve_repository_mounts(metadata) == {
        "/opt/unoplat/repositories/acme-repo": "/opt/unoplat/repositories/acme-repo"
    }
