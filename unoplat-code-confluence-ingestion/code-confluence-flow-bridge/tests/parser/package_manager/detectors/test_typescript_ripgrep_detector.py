from pathlib import Path

import pytest
from src.code_confluence_flow_bridge.parser.package_manager.typescript.detectors.ripgrep_detector import (
    TypeScriptRipgrepDetector,
)
from unoplat_code_confluence_commons.programming_language_metadata import (
    PackageManagerProvenance,
    PackageManagerType,
    WorkspaceOrchestratorType,
)

from tests.parser.package_manager.detectors.typescript_detector_test_support import (
    APOLLO_SERVER_GIT_URL,
    BUN_RUNTIME_GIT_URL,
    EXPECTED_APOLLO_SERVER_CODEBASE_FOLDERS,
    EXPECTED_APOLLO_SERVER_PACKAGE_MANAGER_PROVENANCE,
    EXPECTED_APOLLO_SERVER_PROJECT_NAMES,
    EXPECTED_APOLLO_SERVER_WORKSPACE_ROOTS,
    EXPECTED_BUN_RUNTIME_CODEBASE_FOLDERS,
    EXPECTED_BUN_RUNTIME_PACKAGE_MANAGER,
    EXPECTED_BUN_RUNTIME_PACKAGE_MANAGER_PROVENANCE,
    EXPECTED_BUN_RUNTIME_PROJECT_NAMES,
    EXPECTED_BUN_RUNTIME_WORKSPACE_ROOTS,
    EXPECTED_HOPPSCOTCH_CODEBASE_FOLDERS,
    EXPECTED_HOPPSCOTCH_PACKAGE_MANAGER_PROVENANCE,
    EXPECTED_HOPPSCOTCH_PROJECT_NAMES,
    EXPECTED_HOPPSCOTCH_WORKSPACE_ROOTS,
    EXPECTED_NX_REACT_TEMPLATE_CODEBASE_FOLDERS,
    EXPECTED_NX_REACT_TEMPLATE_PROJECT_NAMES,
    EXPECTED_NX_REACT_TEMPLATE_WORKSPACE_ROOTS,
    EXPECTED_PRINTDESK_CODEBASE_FOLDERS,
    EXPECTED_PRINTDESK_PROJECT_NAMES,
    EXPECTED_PRINTDESK_WORKSPACE_ROOTS,
    EXPECTED_SOCKETIO_CODEBASE_FOLDERS,
    EXPECTED_SOCKETIO_PACKAGE_MANAGER,
    EXPECTED_SOCKETIO_PACKAGE_MANAGER_PROVENANCE,
    EXPECTED_SOCKETIO_PROJECT_NAMES,
    EXPECTED_SOCKETIO_WORKSPACE_ROOTS,
    EXPECTED_T3CODE_CODEBASE_FOLDERS,
    EXPECTED_T3CODE_PROJECT_NAMES,
    EXPECTED_T3CODE_WORKSPACE_ROOTS,
    HOPPSCOTCH_GIT_URL,
    NX_REACT_TEMPLATE_GIT_URL,
    PNPM_WORKSPACE_FIXTURE_DIR,
    PRINTDESK_GIT_URL,
    SOCKETIO_GIT_URL,
    STANDALONE_FIXTURE_DIR,
    T3CODE_GIT_URL,
    format_detected_codebases,
    map_codebases_by_folder,
    write_package_json,
)


@pytest.mark.network
@pytest.mark.asyncio
async def test_detect_codebases_t3code_turbo_monorepo_returns_workspace_members_only() -> (
    None
):
    detector = TypeScriptRipgrepDetector()
    await detector.initialize_rules()

    detected_codebases = await detector.detect_codebases(T3CODE_GIT_URL, "")
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

    codebases_by_folder = map_codebases_by_folder(detected_codebases)

    # All workspace members must inherit the aggregator's package manager (bun)
    for folder in sorted(EXPECTED_T3CODE_CODEBASE_FOLDERS):
        codebase = codebases_by_folder[folder]
        metadata = codebase.programming_language_metadata
        assert metadata.package_manager == PackageManagerType("bun"), (
            f"Codebase {folder} should inherit bun.\n"
            f"Actual metadata: {format_detected_codebases(detected_codebases)}"
        )
        assert (
            metadata.package_manager_provenance == PackageManagerProvenance.INHERITED
        ), (
            f"Codebase {folder} should be inherited from the root workspace owner.\n"
            f"Actual metadata: {format_detected_codebases(detected_codebases)}"
        )
        assert metadata.workspace_root == EXPECTED_T3CODE_WORKSPACE_ROOTS[folder], (
            f"Codebase {folder} workspace_root mismatch; expected '.'.\n"
            f"Actual metadata: {format_detected_codebases(detected_codebases)}"
        )
        assert metadata.workspace_orchestrator == WorkspaceOrchestratorType.TURBO, (
            f"Codebase {folder} should inherit turbo orchestrator metadata from the root workspace.\n"
            f"Actual metadata: {format_detected_codebases(detected_codebases)}"
        )
        assert metadata.workspace_orchestrator_config_path == "turbo.json", (
            f"Codebase {folder} should point workflow generation at the root turbo config.\n"
            f"Actual metadata: {format_detected_codebases(detected_codebases)}"
        )
        # manifest_path must be set for each workspace member
        assert metadata.manifest_path is not None, (
            f"Codebase {folder} should have manifest_path set.\n"
            f"Actual metadata: {format_detected_codebases(detected_codebases)}"
        )
        assert metadata.manifest_path.endswith("package.json"), (
            f"Codebase {folder} manifest_path should end with package.json.\n"
            f"Actual metadata: {format_detected_codebases(detected_codebases)}"
        )
        expected_name = EXPECTED_T3CODE_PROJECT_NAMES[folder]
        assert metadata.project_name == expected_name, (
            f"Codebase {folder} should have project_name={expected_name!r}.\n"
            f"Actual metadata: {format_detected_codebases(detected_codebases)}"
        )


@pytest.mark.network
@pytest.mark.asyncio
async def test_detect_codebases_nx_react_template_monorepo_returns_workspace_members_only() -> (
    None
):
    detector = TypeScriptRipgrepDetector()
    await detector.initialize_rules()

    detected_codebases = await detector.detect_codebases(NX_REACT_TEMPLATE_GIT_URL, "")
    detected_folders = {codebase.codebase_folder for codebase in detected_codebases}

    # Root aggregator must NOT appear in detections
    assert "." not in detected_folders, (
        "Workspace aggregator root '.' should not be emitted.\n"
        f"Actual codebases: {format_detected_codebases(detected_codebases)}"
    )

    assert detected_folders == EXPECTED_NX_REACT_TEMPLATE_CODEBASE_FOLDERS, (
        "Unexpected detected TypeScript codebases for the nrwl/react-template Nx fixture.\n"
        f"Expected folders: {sorted(EXPECTED_NX_REACT_TEMPLATE_CODEBASE_FOLDERS)}\n"
        f"Actual codebases: {format_detected_codebases(detected_codebases)}"
    )

    codebases_by_folder = map_codebases_by_folder(detected_codebases)

    # All workspace members must inherit the root's package manager (npm)
    for folder in sorted(EXPECTED_NX_REACT_TEMPLATE_CODEBASE_FOLDERS):
        codebase = codebases_by_folder[folder]
        metadata = codebase.programming_language_metadata
        assert metadata.package_manager == PackageManagerType("npm"), (
            f"Codebase {folder} should inherit npm.\n"
            f"Actual metadata: {format_detected_codebases(detected_codebases)}"
        )
        assert (
            metadata.package_manager_provenance == PackageManagerProvenance.INHERITED
        ), (
            f"Codebase {folder} should be inherited from the root workspace owner.\n"
            f"Actual metadata: {format_detected_codebases(detected_codebases)}"
        )
        assert (
            metadata.workspace_root
            == EXPECTED_NX_REACT_TEMPLATE_WORKSPACE_ROOTS[folder]
        ), (
            f"Codebase {folder} workspace_root mismatch; expected '.'.\n"
            f"Actual metadata: {format_detected_codebases(detected_codebases)}"
        )
        assert metadata.workspace_orchestrator == WorkspaceOrchestratorType.NX, (
            f"Codebase {folder} should inherit NX orchestrator metadata from the root workspace.\n"
            f"Actual metadata: {format_detected_codebases(detected_codebases)}"
        )
        assert metadata.workspace_orchestrator_config_path == "nx.json", (
            f"Codebase {folder} should point workflow generation at the root nx.json config.\n"
            f"Actual metadata: {format_detected_codebases(detected_codebases)}"
        )
        # manifest_path must be set for each workspace member
        assert metadata.manifest_path is not None, (
            f"Codebase {folder} should have manifest_path set.\n"
            f"Actual metadata: {format_detected_codebases(detected_codebases)}"
        )
        assert metadata.manifest_path.endswith("package.json"), (
            f"Codebase {folder} manifest_path should end with package.json.\n"
            f"Actual metadata: {format_detected_codebases(detected_codebases)}"
        )
        expected_name = EXPECTED_NX_REACT_TEMPLATE_PROJECT_NAMES[folder]
        assert metadata.project_name == expected_name, (
            f"Codebase {folder} should have project_name={expected_name!r}.\n"
            f"Actual metadata: {format_detected_codebases(detected_codebases)}"
        )


@pytest.mark.network
@pytest.mark.asyncio
async def test_detect_codebases_hoppscotch_pnpm_workspace_returns_workspace_members_only() -> (
    None
):
    """hoppscotch/hoppscotch is a pure pnpm workspace (no Turbo/Nx) with packages/** glob."""
    detector = TypeScriptRipgrepDetector()
    await detector.initialize_rules()

    detected_codebases = await detector.detect_codebases(HOPPSCOTCH_GIT_URL, "")
    detected_folders = {codebase.codebase_folder for codebase in detected_codebases}

    # Root aggregator must NOT appear in detections
    assert "." not in detected_folders, (
        "Workspace aggregator root '.' should not be emitted.\n"
        f"Actual codebases: {format_detected_codebases(detected_codebases)}"
    )

    # Rust-only directory must NOT appear
    assert "packages/hoppscotch-relay" not in detected_folders, (
        "Rust crate 'packages/hoppscotch-relay' should not be emitted (no TypeScript).\n"
        f"Actual codebases: {format_detected_codebases(detected_codebases)}"
    )

    assert detected_folders == EXPECTED_HOPPSCOTCH_CODEBASE_FOLDERS, (
        "Unexpected detected TypeScript codebases for the hoppscotch pnpm workspace fixture.\n"
        f"Expected folders: {sorted(EXPECTED_HOPPSCOTCH_CODEBASE_FOLDERS)}\n"
        f"Actual codebases: {format_detected_codebases(detected_codebases)}"
    )

    codebases_by_folder = map_codebases_by_folder(detected_codebases)

    # All workspace members must inherit pnpm from the root workspace owner
    for folder in sorted(EXPECTED_HOPPSCOTCH_CODEBASE_FOLDERS):
        codebase = codebases_by_folder[folder]
        metadata = codebase.programming_language_metadata
        assert metadata.package_manager == PackageManagerType("pnpm"), (
            f"Codebase {folder} should inherit pnpm.\n"
            f"Actual metadata: {format_detected_codebases(detected_codebases)}"
        )
        assert (
            metadata.package_manager_provenance
            == EXPECTED_HOPPSCOTCH_PACKAGE_MANAGER_PROVENANCE[folder]
        ), (
            f"Codebase {folder} should have the expected package manager provenance.\n"
            f"Actual metadata: {format_detected_codebases(detected_codebases)}"
        )
        assert metadata.workspace_root == EXPECTED_HOPPSCOTCH_WORKSPACE_ROOTS[folder], (
            f"Codebase {folder} workspace_root mismatch; expected '.'.\n"
            f"Actual metadata: {format_detected_codebases(detected_codebases)}"
        )
        assert metadata.workspace_orchestrator is None, (
            f"Codebase {folder} should have no orchestrator (pure pnpm workspace).\n"
            f"Actual metadata: {format_detected_codebases(detected_codebases)}"
        )
        assert metadata.workspace_orchestrator_config_path is None, (
            f"Codebase {folder} should have no orchestrator config path.\n"
            f"Actual metadata: {format_detected_codebases(detected_codebases)}"
        )
        assert metadata.manifest_path is not None, (
            f"Codebase {folder} should have manifest_path set.\n"
            f"Actual metadata: {format_detected_codebases(detected_codebases)}"
        )
        assert metadata.manifest_path.endswith("package.json"), (
            f"Codebase {folder} manifest_path should end with package.json.\n"
            f"Actual metadata: {format_detected_codebases(detected_codebases)}"
        )
        expected_name = EXPECTED_HOPPSCOTCH_PROJECT_NAMES[folder]
        assert metadata.project_name == expected_name, (
            f"Codebase {folder} should have project_name={expected_name!r}.\n"
            f"Actual metadata: {format_detected_codebases(detected_codebases)}"
        )


@pytest.mark.asyncio
async def test_detect_codebases_standalone_ts_project_returns_root() -> None:
    """A standalone TS project (no workspaces) should emit '.' as the codebase folder."""
    assert STANDALONE_FIXTURE_DIR.exists(), (
        f"Standalone fixture not found: {STANDALONE_FIXTURE_DIR}"
    )

    detector = TypeScriptRipgrepDetector()
    await detector.initialize_rules()

    detected_codebases = await detector.detect_codebases(
        str(STANDALONE_FIXTURE_DIR), ""
    )
    detected_folders = {codebase.codebase_folder for codebase in detected_codebases}

    assert detected_folders == {"."}, (
        "Standalone TS project should emit exactly {'.'}.\n"
        f"Actual codebases: {format_detected_codebases(detected_codebases)}"
    )

    root_codebase = detected_codebases[0]
    assert (
        root_codebase.programming_language_metadata.package_manager
        == PackageManagerType("bun")
    )
    assert root_codebase.programming_language_metadata.manifest_path == "package.json"
    assert (
        root_codebase.programming_language_metadata.project_name == "standalone-ts-app"
    )
    assert root_codebase.programming_language_metadata.workspace_orchestrator is None
    assert (
        root_codebase.programming_language_metadata.workspace_orchestrator_config_path
        is None
    )


@pytest.mark.asyncio
async def test_nested_workspace_aggregator_is_suppressed(tmp_path: Path) -> None:
    """Nested aggregators should be suppressed; only leaf members emitted."""
    # Root: workspaces: ["packages/*"], bun.lock, tsconfig
    root_pkg = {
        "name": "root-monorepo",
        "workspaces": ["packages/*"],
        "devDependencies": {"typescript": "^5.0.0"},
    }
    write_package_json(tmp_path / "package.json", root_pkg)
    (tmp_path / "bun.lock").write_text("")
    (tmp_path / "tsconfig.json").write_text('{"compilerOptions": {}}')

    # packages/platform: nested aggregator with workspaces: ["plugins/*"]
    platform_dir = tmp_path / "packages" / "platform"
    platform_dir.mkdir(parents=True)
    platform_pkg = {
        "name": "platform",
        "workspaces": ["plugins/*", "!plugins/e2e/*"],
        "devDependencies": {"typescript": "^5.0.0"},
    }
    write_package_json(platform_dir / "package.json", platform_pkg)
    (platform_dir / "tsconfig.json").write_text('{"compilerOptions": {}}')

    # packages/platform/plugins/foo: leaf member
    foo_dir = platform_dir / "plugins" / "foo"
    foo_dir.mkdir(parents=True)
    foo_pkg = {"name": "@platform/foo", "devDependencies": {"typescript": "^5.0.0"}}
    write_package_json(foo_dir / "package.json", foo_pkg)
    (foo_dir / "tsconfig.json").write_text('{"compilerOptions": {}}')

    # packages/platform/plugins/e2e/bar: excluded by nested negated workspace glob
    e2e_dir = platform_dir / "plugins" / "e2e" / "bar"
    e2e_dir.mkdir(parents=True)
    e2e_pkg = {"name": "@platform/e2e-bar", "devDependencies": {"typescript": "^5.0.0"}}
    write_package_json(e2e_dir / "package.json", e2e_pkg)
    (e2e_dir / "tsconfig.json").write_text('{"compilerOptions": {}}')

    detector = TypeScriptRipgrepDetector()
    await detector.initialize_rules()

    detected_codebases = await detector.detect_codebases(str(tmp_path), "")
    detected_folders = {c.codebase_folder for c in detected_codebases}

    assert detected_folders == {"packages/platform/plugins/foo"}, (
        "Only the nested leaf member should be emitted.\n"
        f"Actual: {format_detected_codebases(detected_codebases)}"
    )

    foo_codebase = detected_codebases[0]
    assert (
        foo_codebase.programming_language_metadata.package_manager
        == PackageManagerType("bun")
    )
    assert (
        foo_codebase.programming_language_metadata.package_manager_provenance
        == PackageManagerProvenance.INHERITED
    )
    assert (
        foo_codebase.programming_language_metadata.workspace_root == "packages/platform"
    )
    assert foo_codebase.programming_language_metadata.workspace_orchestrator is None
    assert foo_codebase.programming_language_metadata.project_name == "@platform/foo"


@pytest.mark.asyncio
async def test_workspace_glob_members_ignore_config_only_child_directories(
    tmp_path: Path,
) -> None:
    root_pkg = {
        "name": "workspace-root",
        "private": True,
        "workspaces": ["packages/**"],
        "devDependencies": {"typescript": "^5.0.0"},
    }
    write_package_json(tmp_path / "package.json", root_pkg)
    (tmp_path / "package-lock.json").write_text("{}")
    (tmp_path / "tsconfig.json").write_text('{"compilerOptions": {}}')

    app_dir = tmp_path / "packages" / "app"
    app_dir.mkdir(parents=True)
    app_pkg = {"name": "@repo/app", "devDependencies": {"typescript": "^5.0.0"}}
    write_package_json(app_dir / "package.json", app_pkg)
    (app_dir / "tsconfig.json").write_text('{"compilerOptions": {}}')

    src_dir = app_dir / "src"
    src_dir.mkdir()
    (src_dir / "tsconfig.json").write_text('{"compilerOptions": {}}')

    detector = TypeScriptRipgrepDetector()
    await detector.initialize_rules()

    detected_codebases = await detector.detect_codebases(str(tmp_path), "")
    assert {codebase.codebase_folder for codebase in detected_codebases} == {
        "packages/app"
    }, format_detected_codebases(detected_codebases)

    metadata = detected_codebases[0].programming_language_metadata
    assert metadata.package_manager == PackageManagerType("npm")
    assert metadata.package_manager_provenance == PackageManagerProvenance.INHERITED
    assert metadata.workspace_root == "."
    assert metadata.manifest_path == "packages/app/package.json"
    assert metadata.project_name == "@repo/app"


@pytest.mark.asyncio
async def test_detect_codebases_pnpm_workspace_yaml_returns_workspace_members_only() -> (
    None
):
    assert PNPM_WORKSPACE_FIXTURE_DIR.exists(), (
        f"pnpm workspace fixture not found: {PNPM_WORKSPACE_FIXTURE_DIR}"
    )

    detector = TypeScriptRipgrepDetector()
    await detector.initialize_rules()

    detected_codebases = await detector.detect_codebases(
        str(PNPM_WORKSPACE_FIXTURE_DIR), ""
    )
    detected_folders = {codebase.codebase_folder for codebase in detected_codebases}

    assert detected_folders == {"packages/app"}, (
        "pnpm-workspace.yaml members should be emitted while the root aggregator is suppressed.\n"
        f"Actual codebases: {format_detected_codebases(detected_codebases)}"
    )

    app_codebase = detected_codebases[0]
    assert (
        app_codebase.programming_language_metadata.package_manager
        == PackageManagerType("pnpm")
    )
    assert (
        app_codebase.programming_language_metadata.package_manager_provenance
        == PackageManagerProvenance.INHERITED
    )
    assert app_codebase.programming_language_metadata.workspace_root == "."
    assert app_codebase.programming_language_metadata.workspace_orchestrator is None
    assert (
        app_codebase.programming_language_metadata.manifest_path
        == "packages/app/package.json"
    )
    assert app_codebase.programming_language_metadata.project_name == "@pnpm/app"


@pytest.mark.asyncio
async def test_workspace_member_prefers_explicit_local_package_manager_override(
    tmp_path: Path,
) -> None:
    root_pkg = {
        "name": "mixed-manager-root",
        "private": True,
        "packageManager": "bun@1.3.9",
        "workspaces": ["packages/*"],
        "devDependencies": {"typescript": "^5.0.0"},
    }
    write_package_json(tmp_path / "package.json", root_pkg)
    (tmp_path / "bun.lock").write_text("")
    (tmp_path / "tsconfig.json").write_text('{"compilerOptions": {}}')

    inherited_dir = tmp_path / "packages" / "shared"
    inherited_dir.mkdir(parents=True)
    inherited_pkg = {
        "name": "@repo/shared",
        "devDependencies": {"typescript": "^5.0.0"},
    }
    write_package_json(inherited_dir / "package.json", inherited_pkg)
    (inherited_dir / "tsconfig.json").write_text('{"compilerOptions": {}}')

    local_override_dir = tmp_path / "packages" / "contracts"
    local_override_dir.mkdir(parents=True)
    local_override_pkg = {
        "name": "@repo/contracts",
        "packageManager": "npm@10.9.0",
        "devDependencies": {"typescript": "^5.0.0"},
    }
    write_package_json(local_override_dir / "package.json", local_override_pkg)
    (local_override_dir / "tsconfig.json").write_text('{"compilerOptions": {}}')

    detector = TypeScriptRipgrepDetector()
    await detector.initialize_rules()

    detected_codebases = await detector.detect_codebases(str(tmp_path), "")
    codebases_by_folder = map_codebases_by_folder(detected_codebases)

    assert set(codebases_by_folder) == {"packages/contracts", "packages/shared"}, (
        "Expected one inherited child and one explicit local override.\n"
        f"Actual codebases: {format_detected_codebases(detected_codebases)}"
    )

    inherited_metadata = codebases_by_folder[
        "packages/shared"
    ].programming_language_metadata
    assert inherited_metadata.package_manager == PackageManagerType("bun"), (
        "packages/shared should inherit bun from the root workspace.\n"
        f"Actual codebases: {format_detected_codebases(detected_codebases)}"
    )
    assert (
        inherited_metadata.package_manager_provenance
        == PackageManagerProvenance.INHERITED
    )
    assert inherited_metadata.workspace_root == "."

    local_override_metadata = codebases_by_folder[
        "packages/contracts"
    ].programming_language_metadata
    assert local_override_metadata.package_manager == PackageManagerType("npm"), (
        "packages/contracts should prefer its explicit local packageManager field.\n"
        f"Actual codebases: {format_detected_codebases(detected_codebases)}"
    )
    assert (
        local_override_metadata.package_manager_provenance
        == PackageManagerProvenance.LOCAL
    )
    assert local_override_metadata.workspace_root is None
    assert local_override_metadata.workspace_orchestrator is None


@pytest.mark.asyncio
async def test_detect_codebases_nx_workspace_emits_authoritative_orchestrator_metadata(
    tmp_path: Path,
) -> None:
    root_pkg = {
        "name": "nx-root",
        "private": True,
        "workspaces": ["apps/*"],
        "devDependencies": {"typescript": "^5.0.0"},
    }
    write_package_json(tmp_path / "package.json", root_pkg)
    (tmp_path / "package-lock.json").write_text("{}")
    (tmp_path / "nx.json").write_text('{"workspaceLayout": {"appsDir": "apps"}}')
    (tmp_path / "tsconfig.json").write_text('{"compilerOptions": {}}')

    app_dir = tmp_path / "apps" / "web"
    app_dir.mkdir(parents=True)
    app_pkg = {
        "name": "@repo/web",
        "devDependencies": {"typescript": "^5.0.0"},
    }
    write_package_json(app_dir / "package.json", app_pkg)
    (app_dir / "project.json").write_text('{"name": "web"}')
    (app_dir / "tsconfig.json").write_text('{"compilerOptions": {}}')

    detector = TypeScriptRipgrepDetector()
    await detector.initialize_rules()

    detected_codebases = await detector.detect_codebases(str(tmp_path), "")
    assert {codebase.codebase_folder for codebase in detected_codebases} == {
        "apps/web"
    }, format_detected_codebases(detected_codebases)

    metadata = detected_codebases[0].programming_language_metadata
    assert metadata.package_manager == PackageManagerType("npm")
    assert metadata.package_manager_provenance == PackageManagerProvenance.INHERITED
    assert metadata.workspace_root == "."
    assert metadata.workspace_orchestrator == WorkspaceOrchestratorType.NX
    assert metadata.workspace_orchestrator_config_path == "nx.json"


@pytest.mark.network
@pytest.mark.asyncio
async def test_detect_codebases_bun_runtime_pure_workspace_returns_workspace_and_standalone_members() -> (
    None
):
    """oven-sh/bun is a pure Bun workspace (no Turbo/Nx) with explicit ./prefixed paths.

    Only packages/bun-types and packages/@types/bun are declared workspace members.
    packages/@types/bun is filtered (no TypeScript markers), leaving packages/bun-types
    as the sole INHERITED member.  The remaining detected codebases are standalone
    projects scattered across the repo, each with LOCAL provenance.

    Exercises:
    - Lockfile-only Bun detection (no packageManager field in root package.json)
    - Explicit ./prefixed workspace paths (not globs) with normalize_dir_path stripping
    - Selective TypeScript filtering of workspace members
    - Mixed INHERITED / LOCAL provenance in the same repo
    """
    detector = TypeScriptRipgrepDetector()
    await detector.initialize_rules()

    detected_codebases = await detector.detect_codebases(BUN_RUNTIME_GIT_URL, "")
    detected_folders = {codebase.codebase_folder for codebase in detected_codebases}

    # Root aggregator must NOT appear in detections
    assert "." not in detected_folders, (
        "Workspace aggregator root '.' should not be emitted.\n"
        f"Actual codebases: {format_detected_codebases(detected_codebases)}"
    )

    # packages/@types/bun is a declared workspace member but has no TypeScript markers
    assert "packages/@types/bun" not in detected_folders, (
        "packages/@types/bun has no tsconfig.json and no typescript dependency, "
        "should not be detected as a TypeScript codebase.\n"
        f"Actual codebases: {format_detected_codebases(detected_codebases)}"
    )

    assert detected_folders == EXPECTED_BUN_RUNTIME_CODEBASE_FOLDERS, (
        "Unexpected detected TypeScript codebases for the oven-sh/bun pure workspace.\n"
        f"Expected folders: {sorted(EXPECTED_BUN_RUNTIME_CODEBASE_FOLDERS)}\n"
        f"Actual codebases: {format_detected_codebases(detected_codebases)}"
    )

    codebases_by_folder = map_codebases_by_folder(detected_codebases)

    for folder in sorted(EXPECTED_BUN_RUNTIME_CODEBASE_FOLDERS):
        codebase = codebases_by_folder[folder]
        metadata = codebase.programming_language_metadata
        assert metadata.package_manager == EXPECTED_BUN_RUNTIME_PACKAGE_MANAGER[folder], (
            f"Codebase {folder} package_manager mismatch.\n"
            f"Actual metadata: {format_detected_codebases(detected_codebases)}"
        )
        assert (
            metadata.package_manager_provenance
            == EXPECTED_BUN_RUNTIME_PACKAGE_MANAGER_PROVENANCE[folder]
        ), (
            f"Codebase {folder} provenance mismatch.\n"
            f"Actual metadata: {format_detected_codebases(detected_codebases)}"
        )
        assert (
            metadata.workspace_root == EXPECTED_BUN_RUNTIME_WORKSPACE_ROOTS[folder]
        ), (
            f"Codebase {folder} workspace_root mismatch.\n"
            f"Actual metadata: {format_detected_codebases(detected_codebases)}"
        )
        # Pure Bun workspace has no orchestrator
        assert metadata.workspace_orchestrator is None, (
            f"Codebase {folder} should have no orchestrator (pure Bun workspace).\n"
            f"Actual metadata: {format_detected_codebases(detected_codebases)}"
        )
        assert metadata.workspace_orchestrator_config_path is None, (
            f"Codebase {folder} should have no orchestrator config path.\n"
            f"Actual metadata: {format_detected_codebases(detected_codebases)}"
        )
        assert metadata.manifest_path is not None, (
            f"Codebase {folder} should have manifest_path set.\n"
            f"Actual metadata: {format_detected_codebases(detected_codebases)}"
        )
        assert metadata.manifest_path.endswith("package.json"), (
            f"Codebase {folder} manifest_path should end with package.json.\n"
            f"Actual metadata: {format_detected_codebases(detected_codebases)}"
        )
        expected_name = EXPECTED_BUN_RUNTIME_PROJECT_NAMES[folder]
        assert metadata.project_name == expected_name, (
            f"Codebase {folder} should have project_name={expected_name!r}.\n"
            f"Actual metadata: {format_detected_codebases(detected_codebases)}"
        )


@pytest.mark.network
@pytest.mark.asyncio
async def test_detect_codebases_printdesk_bun_object_form_workspace_returns_workspace_members_only() -> (
    None
):
    """declanlscott/printdesk uses object-form workspaces with catalog: protocol (Bun-specific).

    Root package.json declares workspaces as an object:
      {"packages": ["packages/**"], "catalog": {"zod": "...", ...}}
    which is parsed via WorkspacePackagesConfig.model_validate().

    Exercises:
    - Object-form workspace declaration (dict with "packages" key)
    - Bun catalog: dependency protocol in member package.json files
    - packages/** double-star glob matching at various nesting depths
    - Filtering of non-TypeScript nested packages (wailsjs/runtime)
    - Lockfile-only Bun detection (no packageManager field)
    """
    detector = TypeScriptRipgrepDetector()
    await detector.initialize_rules()

    detected_codebases = await detector.detect_codebases(PRINTDESK_GIT_URL, "")
    detected_folders = {codebase.codebase_folder for codebase in detected_codebases}

    # Root aggregator must NOT appear in detections
    assert "." not in detected_folders, (
        "Workspace aggregator root '.' should not be emitted.\n"
        f"Actual codebases: {format_detected_codebases(detected_codebases)}"
    )

    # wailsjs/runtime is matched by packages/** glob but is JS-only
    assert (
        "packages/clients/edge-proxy/frontend/wailsjs/runtime" not in detected_folders
    ), (
        "wailsjs/runtime is JavaScript-only, should not be detected.\n"
        f"Actual codebases: {format_detected_codebases(detected_codebases)}"
    )

    assert detected_folders == EXPECTED_PRINTDESK_CODEBASE_FOLDERS, (
        "Unexpected detected TypeScript codebases for the printdesk Bun workspace.\n"
        f"Expected folders: {sorted(EXPECTED_PRINTDESK_CODEBASE_FOLDERS)}\n"
        f"Actual codebases: {format_detected_codebases(detected_codebases)}"
    )

    codebases_by_folder = map_codebases_by_folder(detected_codebases)

    for folder in sorted(EXPECTED_PRINTDESK_CODEBASE_FOLDERS):
        codebase = codebases_by_folder[folder]
        metadata = codebase.programming_language_metadata
        assert metadata.package_manager == PackageManagerType("bun"), (
            f"Codebase {folder} should inherit bun (detected via bun.lock).\n"
            f"Actual metadata: {format_detected_codebases(detected_codebases)}"
        )
        assert (
            metadata.package_manager_provenance == PackageManagerProvenance.INHERITED
        ), (
            f"Codebase {folder} should be inherited from the root workspace owner.\n"
            f"Actual metadata: {format_detected_codebases(detected_codebases)}"
        )
        assert metadata.workspace_root == EXPECTED_PRINTDESK_WORKSPACE_ROOTS[folder], (
            f"Codebase {folder} workspace_root mismatch; expected '.'.\n"
            f"Actual metadata: {format_detected_codebases(detected_codebases)}"
        )
        # No orchestrator (pure Bun workspace with object-form)
        assert metadata.workspace_orchestrator is None, (
            f"Codebase {folder} should have no orchestrator.\n"
            f"Actual metadata: {format_detected_codebases(detected_codebases)}"
        )
        assert metadata.workspace_orchestrator_config_path is None, (
            f"Codebase {folder} should have no orchestrator config path.\n"
            f"Actual metadata: {format_detected_codebases(detected_codebases)}"
        )
        assert metadata.manifest_path is not None, (
            f"Codebase {folder} should have manifest_path set.\n"
            f"Actual metadata: {format_detected_codebases(detected_codebases)}"
        )
        assert metadata.manifest_path.endswith("package.json"), (
            f"Codebase {folder} manifest_path should end with package.json.\n"
            f"Actual metadata: {format_detected_codebases(detected_codebases)}"
        )
        expected_name = EXPECTED_PRINTDESK_PROJECT_NAMES[folder]
        assert metadata.project_name == expected_name, (
            f"Codebase {folder} should have project_name={expected_name!r}.\n"
            f"Actual metadata: {format_detected_codebases(detected_codebases)}"
        )


@pytest.mark.network
@pytest.mark.asyncio
async def test_detect_codebases_apollo_server_npm_workspace_glob_returns_workspace_members_only() -> (
    None
):
    """apollographql/apollo-server is a pure npm workspace (no Turbo/Nx) with packages/* glob.

    The root declares ``"workspaces": ["packages/*"]`` with ``package-lock.json``
    (no ``packageManager`` field).  Five of the six workspace packages have TypeScript
    markers; ``usage-reporting-protobuf`` is filtered.  A standalone ``smoke-test/``
    directory is also discovered outside the workspace with LOCAL provenance.

    Exercises:
    - Lockfile-only npm detection (no packageManager field in root package.json)
    - Glob-based workspace expansion (packages/*)
    - Filtering of non-TypeScript workspace members (usage-reporting-protobuf)
    - Mixed INHERITED (workspace) and LOCAL (standalone) provenance in the same repo
    """
    detector = TypeScriptRipgrepDetector()
    await detector.initialize_rules()

    detected_codebases = await detector.detect_codebases(APOLLO_SERVER_GIT_URL, "")
    detected_folders = {codebase.codebase_folder for codebase in detected_codebases}

    # Root aggregator must NOT appear in detections
    assert "." not in detected_folders, (
        "Workspace aggregator root '.' should not be emitted.\n"
        f"Actual codebases: {format_detected_codebases(detected_codebases)}"
    )

    # Non-TypeScript package must NOT appear
    assert "packages/usage-reporting-protobuf" not in detected_folders, (
        "packages/usage-reporting-protobuf has no tsconfig.json and no typescript dependency, "
        "should not be detected as a TypeScript codebase.\n"
        f"Actual codebases: {format_detected_codebases(detected_codebases)}"
    )

    assert detected_folders == EXPECTED_APOLLO_SERVER_CODEBASE_FOLDERS, (
        "Unexpected detected TypeScript codebases for the apollo-server npm workspace.\n"
        f"Expected folders: {sorted(EXPECTED_APOLLO_SERVER_CODEBASE_FOLDERS)}\n"
        f"Actual codebases: {format_detected_codebases(detected_codebases)}"
    )

    codebases_by_folder = map_codebases_by_folder(detected_codebases)

    for folder in sorted(EXPECTED_APOLLO_SERVER_CODEBASE_FOLDERS):
        codebase = codebases_by_folder[folder]
        metadata = codebase.programming_language_metadata
        assert metadata.package_manager == PackageManagerType("npm"), (
            f"Codebase {folder} package_manager mismatch.\n"
            f"Actual metadata: {format_detected_codebases(detected_codebases)}"
        )
        assert (
            metadata.package_manager_provenance
            == EXPECTED_APOLLO_SERVER_PACKAGE_MANAGER_PROVENANCE[folder]
        ), (
            f"Codebase {folder} provenance mismatch.\n"
            f"Actual metadata: {format_detected_codebases(detected_codebases)}"
        )
        assert (
            metadata.workspace_root
            == EXPECTED_APOLLO_SERVER_WORKSPACE_ROOTS[folder]
        ), (
            f"Codebase {folder} workspace_root mismatch.\n"
            f"Actual metadata: {format_detected_codebases(detected_codebases)}"
        )
        assert metadata.workspace_orchestrator is None, (
            f"Codebase {folder} should have no orchestrator (pure npm workspace).\n"
            f"Actual metadata: {format_detected_codebases(detected_codebases)}"
        )
        assert metadata.workspace_orchestrator_config_path is None, (
            f"Codebase {folder} should have no orchestrator config path.\n"
            f"Actual metadata: {format_detected_codebases(detected_codebases)}"
        )
        assert metadata.manifest_path is not None, (
            f"Codebase {folder} should have manifest_path set.\n"
            f"Actual metadata: {format_detected_codebases(detected_codebases)}"
        )
        assert metadata.manifest_path.endswith("package.json"), (
            f"Codebase {folder} manifest_path should end with package.json.\n"
            f"Actual metadata: {format_detected_codebases(detected_codebases)}"
        )
        expected_name = EXPECTED_APOLLO_SERVER_PROJECT_NAMES[folder]
        assert metadata.project_name == expected_name, (
            f"Codebase {folder} should have project_name={expected_name!r}.\n"
            f"Actual metadata: {format_detected_codebases(detected_codebases)}"
        )


@pytest.mark.network
@pytest.mark.asyncio
async def test_detect_codebases_socketio_npm_workspace_explicit_paths_returns_workspace_members_only() -> (
    None
):
    """socketio/socket.io is a pure npm workspace (no Turbo/Nx) with explicit workspace paths.

    Root package.json declares workspaces as an array of 12 explicit paths (not globs):
      ["packages/socket.io-component-emitter", "packages/engine.io-parser", ...]

    Only 10 of the 11 TypeScript workspace members are detected as INHERITED;
    ``socket.io-cluster-adapter`` has its own ``package-lock.json`` and is detected
    as LOCAL.  The repo also contains 13 standalone TypeScript example projects
    scattered across ``examples/`` with LOCAL provenance.

    Exercises:
    - Lockfile-only npm detection (no packageManager field in root package.json)
    - Explicit-path workspace resolution (not glob-based)
    - Filtering of non-TypeScript workspace members (socket.io-component-emitter)
    - Mixed INHERITED / LOCAL provenance in workspace members and standalone examples
    - Yarn detection for ReactNativeExample (has yarn.lock)
    """
    detector = TypeScriptRipgrepDetector()
    await detector.initialize_rules()

    detected_codebases = await detector.detect_codebases(SOCKETIO_GIT_URL, "")
    detected_folders = {codebase.codebase_folder for codebase in detected_codebases}

    # Root aggregator must NOT appear in detections
    assert "." not in detected_folders, (
        "Workspace aggregator root '.' should not be emitted.\n"
        f"Actual codebases: {format_detected_codebases(detected_codebases)}"
    )

    # Non-TypeScript package must NOT appear
    assert "packages/socket.io-component-emitter" not in detected_folders, (
        "packages/socket.io-component-emitter has no tsconfig.json and no typescript dependency, "
        "should not be detected as a TypeScript codebase.\n"
        f"Actual codebases: {format_detected_codebases(detected_codebases)}"
    )

    assert detected_folders == EXPECTED_SOCKETIO_CODEBASE_FOLDERS, (
        "Unexpected detected TypeScript codebases for the socket.io npm workspace.\n"
        f"Expected folders: {sorted(EXPECTED_SOCKETIO_CODEBASE_FOLDERS)}\n"
        f"Actual codebases: {format_detected_codebases(detected_codebases)}"
    )

    codebases_by_folder = map_codebases_by_folder(detected_codebases)

    for folder in sorted(EXPECTED_SOCKETIO_CODEBASE_FOLDERS):
        codebase = codebases_by_folder[folder]
        metadata = codebase.programming_language_metadata
        assert metadata.package_manager == EXPECTED_SOCKETIO_PACKAGE_MANAGER[folder], (
            f"Codebase {folder} package_manager mismatch.\n"
            f"Actual metadata: {format_detected_codebases(detected_codebases)}"
        )
        assert (
            metadata.package_manager_provenance
            == EXPECTED_SOCKETIO_PACKAGE_MANAGER_PROVENANCE[folder]
        ), (
            f"Codebase {folder} provenance mismatch.\n"
            f"Actual metadata: {format_detected_codebases(detected_codebases)}"
        )
        assert metadata.workspace_root == EXPECTED_SOCKETIO_WORKSPACE_ROOTS[folder], (
            f"Codebase {folder} workspace_root mismatch.\n"
            f"Actual metadata: {format_detected_codebases(detected_codebases)}"
        )
        assert metadata.workspace_orchestrator is None, (
            f"Codebase {folder} should have no orchestrator (pure npm workspace).\n"
            f"Actual metadata: {format_detected_codebases(detected_codebases)}"
        )
        assert metadata.workspace_orchestrator_config_path is None, (
            f"Codebase {folder} should have no orchestrator config path.\n"
            f"Actual metadata: {format_detected_codebases(detected_codebases)}"
        )
        assert metadata.manifest_path is not None, (
            f"Codebase {folder} should have manifest_path set.\n"
            f"Actual metadata: {format_detected_codebases(detected_codebases)}"
        )
        assert metadata.manifest_path.endswith("package.json"), (
            f"Codebase {folder} manifest_path should end with package.json.\n"
            f"Actual metadata: {format_detected_codebases(detected_codebases)}"
        )
        expected_name = EXPECTED_SOCKETIO_PROJECT_NAMES[folder]
        assert metadata.project_name == expected_name, (
            f"Codebase {folder} should have project_name={expected_name!r}.\n"
            f"Actual metadata: {format_detected_codebases(detected_codebases)}"
        )
