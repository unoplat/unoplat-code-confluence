import json
from pathlib import Path, PurePosixPath

import pytest
from src.code_confluence_flow_bridge.parser.package_manager.detectors.typescript_ripgrep_detector import (
    TypeScriptRipgrepDetector,
    segment_match,
)
from unoplat_code_confluence_commons.configuration_models import CodebaseConfig
from unoplat_code_confluence_commons.programming_language_metadata import (
    PackageManagerType,
)

T3CODE_FIXTURE_DIR = (
    Path(__file__).resolve().parents[3] / "test_data" / "turbo_monorepo" / "t3code"
)
EXPECTED_T3CODE_CODEBASE_FOLDERS = {
    "apps/desktop",
    "apps/marketing",
    "apps/server",
    "apps/web",
    "packages/contracts",
    "packages/shared",
    "scripts",
}
EXPECTED_T3CODE_PROJECT_NAMES: dict[str, str] = {
    "apps/desktop": "@t3tools/desktop",
    "apps/marketing": "@t3tools/marketing",
    "apps/server": "t3",
    "apps/web": "@t3tools/web",
    "packages/contracts": "@t3tools/contracts",
    "packages/shared": "@t3tools/shared",
    "scripts": "@t3tools/scripts",
}

STANDALONE_FIXTURE_DIR = (
    Path(__file__).resolve().parents[3] / "test_data" / "standalone_ts_project"
)


def format_detected_codebases(detected_codebases: list[CodebaseConfig]) -> list[str]:
    formatted_codebases: list[str] = []
    for codebase in detected_codebases:
        metadata = codebase.programming_language_metadata
        formatted_codebases.append(
            (
                f"{codebase.codebase_folder} | "
                f"package_manager={metadata.package_manager} | "
                f"manifest_path={metadata.manifest_path} | "
                f"project_name={metadata.project_name}"
            )
        )
    return sorted(formatted_codebases)


@pytest.mark.asyncio
async def test_detect_codebases_t3code_turbo_monorepo_returns_workspace_members_only() -> (
    None
):
    detector = TypeScriptRipgrepDetector()
    await detector.initialize_rules()

    assert T3CODE_FIXTURE_DIR.exists(), (
        f"Turbo monorepo fixture not found: {T3CODE_FIXTURE_DIR}"
    )

    detected_codebases = await detector.detect_codebases(str(T3CODE_FIXTURE_DIR), "")
    detected_folders = {codebase.codebase_folder for codebase in detected_codebases}

    # Root aggregator must NOT appear in detections
    assert "." not in detected_folders, (
        "Workspace aggregator root '.' should not be emitted.\n"
        f"Actual codebases: {format_detected_codebases(detected_codebases)}"
    )

    assert detected_folders == EXPECTED_T3CODE_CODEBASE_FOLDERS, (
        "Unexpected detected TypeScript codebases for the t3code Turbo fixture.\n"
        f"Expected folders: {sorted(EXPECTED_T3CODE_CODEBASE_FOLDERS)}\n"
        f"Actual codebases: {format_detected_codebases(detected_codebases)}"
    )

    # All workspace members must inherit the aggregator's package manager (bun)
    for codebase in detected_codebases:
        assert codebase.programming_language_metadata.package_manager == PackageManagerType("bun"), (
            f"Codebase {codebase.codebase_folder} should inherit bun, "
            f"got {codebase.programming_language_metadata.package_manager}"
        )
        # manifest_path must be set for each workspace member
        assert codebase.programming_language_metadata.manifest_path is not None, (
            f"Codebase {codebase.codebase_folder} should have manifest_path set"
        )
        assert codebase.programming_language_metadata.manifest_path.endswith("package.json"), (
            f"Codebase {codebase.codebase_folder} manifest_path should end with package.json, "
            f"got {codebase.programming_language_metadata.manifest_path}"
        )
        expected_name = EXPECTED_T3CODE_PROJECT_NAMES[codebase.codebase_folder]
        assert codebase.programming_language_metadata.project_name == expected_name, (
            f"Codebase {codebase.codebase_folder} should have project_name={expected_name!r}, "
            f"got {codebase.programming_language_metadata.project_name!r}"
        )


@pytest.mark.asyncio
async def test_detect_codebases_standalone_ts_project_returns_root() -> None:
    """A standalone TS project (no workspaces) should emit '.' as the codebase folder."""
    assert STANDALONE_FIXTURE_DIR.exists(), (
        f"Standalone fixture not found: {STANDALONE_FIXTURE_DIR}"
    )

    detector = TypeScriptRipgrepDetector()
    await detector.initialize_rules()

    detected_codebases = await detector.detect_codebases(str(STANDALONE_FIXTURE_DIR), "")
    detected_folders = {codebase.codebase_folder for codebase in detected_codebases}

    assert detected_folders == {"."}, (
        "Standalone TS project should emit exactly {'.'}.\n"
        f"Actual codebases: {format_detected_codebases(detected_codebases)}"
    )

    root_codebase = detected_codebases[0]
    assert root_codebase.programming_language_metadata.package_manager == PackageManagerType("bun")
    assert root_codebase.programming_language_metadata.manifest_path == "package.json"
    assert root_codebase.programming_language_metadata.project_name == "standalone-ts-app"


@pytest.mark.asyncio
async def test_nested_workspace_aggregator_suppressed(tmp_path: Path) -> None:
    """Nested aggregators should be suppressed; only leaf members emitted."""
    # Root: workspaces: ["packages/*"], bun.lock, tsconfig
    root_pkg = {
        "name": "root-monorepo",
        "workspaces": ["packages/*"],
        "devDependencies": {"typescript": "^5.0.0"},
    }
    (tmp_path / "package.json").write_text(json.dumps(root_pkg))
    (tmp_path / "bun.lock").write_text("")
    (tmp_path / "tsconfig.json").write_text('{"compilerOptions": {}}')

    # packages/platform: nested aggregator with workspaces: ["plugins/*"]
    platform_dir = tmp_path / "packages" / "platform"
    platform_dir.mkdir(parents=True)
    platform_pkg = {
        "name": "platform",
        "workspaces": ["plugins/*"],
        "devDependencies": {"typescript": "^5.0.0"},
    }
    (platform_dir / "package.json").write_text(json.dumps(platform_pkg))
    (platform_dir / "tsconfig.json").write_text('{"compilerOptions": {}}')

    # packages/platform/plugins/foo: leaf member
    foo_dir = platform_dir / "plugins" / "foo"
    foo_dir.mkdir(parents=True)
    foo_pkg = {"name": "@platform/foo", "devDependencies": {"typescript": "^5.0.0"}}
    (foo_dir / "package.json").write_text(json.dumps(foo_pkg))
    (foo_dir / "tsconfig.json").write_text('{"compilerOptions": {}}')

    detector = TypeScriptRipgrepDetector()
    await detector.initialize_rules()

    detected_codebases = await detector.detect_codebases(str(tmp_path), "")
    detected_folders = {c.codebase_folder for c in detected_codebases}

    assert detected_folders == {"packages/platform/plugins/foo"}, (
        "Only the nested leaf member should be emitted.\n"
        f"Actual: {format_detected_codebases(detected_codebases)}"
    )

    foo_codebase = detected_codebases[0]
    assert foo_codebase.programming_language_metadata.package_manager == PackageManagerType("bun")
    assert foo_codebase.programming_language_metadata.project_name == "@platform/foo"


def _match(pattern: str, dir_path: str) -> bool:
    """Helper to call segment_match with PurePosixPath parts."""
    return segment_match(PurePosixPath(pattern).parts, 0, PurePosixPath(dir_path).parts, 0)


def test_segment_aware_glob_matching() -> None:
    """Verify segment-aware glob matching with fnmatch and ** support."""
    # Basic single-segment wildcard
    assert _match("apps/*", "apps/web") is True
    assert _match("apps/*", "apps/web/deep") is False

    # Partial segment match via fnmatch
    assert _match("apps/*-web", "apps/next-web") is True
    assert _match("apps/*-web", "apps/web") is False

    # ** recursive wildcard
    assert _match("packages/**", "packages/core") is True
    assert _match("packages/**", "packages/core/utils") is True

    # Exact match
    assert _match("scripts", "scripts") is True
    assert _match("scripts", "other") is False

    # No match
    assert _match("apps/*", "packages/foo") is False
