"""Fast TypeScript package manager detector using ripgrep.

This detector mirrors the Python ripgrep detector but is configured for
TypeScript/JavaScript ecosystems (npm, pnpm, yarn, bun). It reuses the
ordered detection rules defined in ``rules.yaml`` and keeps the same
async interface so it can be swapped into the existing orchestration.
"""

from __future__ import annotations

import os
import asyncio
from collections.abc import Sequence
import json
from pathlib import Path
from typing import Optional, cast

from aiofile import async_open
from loguru import logger
from pydantic import ValidationError
from unoplat_code_confluence_commons.configuration_models import CodebaseConfig
from unoplat_code_confluence_commons.programming_language_metadata import (
    PackageManagerType,
    ProgrammingLanguage,
    ProgrammingLanguageMetadata,
    WorkspaceOrchestratorType,
)
import yaml

from src.code_confluence_flow_bridge.models.detection.shared.evidence import (
    ManagerDetectionResult,
)
from src.code_confluence_flow_bridge.models.detection.shared.inventory import (
    FileNode,
)
from src.code_confluence_flow_bridge.models.detection.shared.results import (
    DetectedCodebase,
)
from src.code_confluence_flow_bridge.models.detection.shared.rules import (
    LanguageRules,
)
from src.code_confluence_flow_bridge.models.detection.typescript.discovery import (
    TypeScriptRepositoryScan,
    WorkspaceDiscoveryContext,
    WorkspaceOrchestratorMetadata,
)
from src.code_confluence_flow_bridge.models.detection.typescript.rules import (
    PnpmWorkspaceConfig,
    WorkspacePackagesConfig,
)
from src.code_confluence_flow_bridge.parser.package_manager.shared.ordered_detection import (
    OrderedDetector,
)
from src.code_confluence_flow_bridge.parser.package_manager.shared.git_utils import (
    clone_repo_if_missing,
)
from src.code_confluence_flow_bridge.parser.package_manager.shared.ripgrep import (
    find_files,
    find_files_with_content,
)
from src.code_confluence_flow_bridge.parser.package_manager.typescript.detectors.monorepo_detection_adapter import (
    TypeScriptMonorepoDetectionAdapter,
)
from src.code_confluence_flow_bridge.parser.package_manager.typescript.detectors.ripgrep_utils import (
    parse_package_json_dependencies,
)
from src.code_confluence_flow_bridge.parser.package_manager.typescript.detectors.rules_loader import (
    load_typescript_language_rules,
)
from src.code_confluence_flow_bridge.parser.package_manager.typescript.detectors.standalone_detection_adapter import (
    TypeScriptStandaloneDetectionAdapter,
)
from src.code_confluence_flow_bridge.parser.package_manager.typescript.detectors.workspace_utils import (
    expand_workspace_globs_with_exclusions,
    group_files_by_directory,
    rebase_workspace_glob,
)


class TypeScriptRipgrepDetector:
    """Fast TypeScript package manager detector using ripgrep."""

    LANGUAGE_KEY = "typescript"

    def __init__(self, rules_path: Optional[str] = None) -> None:
        """Initialise detector with optional rules override."""
        if rules_path is None:
            rules_path = str(
                Path(__file__).resolve().parents[2] / "shared" / "rules.yaml"
            )

        self.rules_path: str = rules_path
        self.language_rules: Optional[LanguageRules] = None
        self.ordered_detector: Optional[OrderedDetector] = None
        self._initialized: bool = False
        self._typescript_dependency_dirs_cache: dict[str, set[str]] = {}
        self._tsconfig_dirs_cache: dict[str, set[str]] = {}

    async def initialize_rules(self) -> None:
        """Load detection rules for TypeScript from YAML."""
        if self._initialized:
            return

        self.language_rules = await self._load_rules()
        self.ordered_detector = OrderedDetector(self.language_rules)
        self._initialized = True
        logger.debug("TypeScript ripgrep detector rules initialised")

    # todo: duplicate code with python detector
    async def _load_rules(self) -> LanguageRules:
        """Load and parse TypeScript rules from YAML file."""
        return await load_typescript_language_rules(self.rules_path)

    async def detect_codebases(
        self, git_url: str, github_token: str
    ) -> list[CodebaseConfig]:
        """Detect all TypeScript codebases in a repository and return their configurations.

        Accepts either a remote GitHub URL (cloned on-demand) or a local filesystem path.
        Delegates to _scan_and_classify_codebases for the core detection algorithm, then
        wraps each detected directory into a CodebaseConfig.

        Example — monorepo with workspaces:
            git_url = "https://github.com/org/turbo-monorepo"
            # Returns [CodebaseConfig("apps/web", bun, INHERITED), CodebaseConfig("packages/ui", bun, INHERITED)]

        Example — standalone project:
            git_url = "/local/path/to/my-ts-app"
            # Returns [CodebaseConfig(".", npm, LOCAL)]
        """
        if not self._initialized:
            raise RuntimeError(
                "Detector not initialized. Call initialize_rules() first."
            )

        if os.path.exists(git_url):
            repo_path = git_url
        else:
            cloned_path: Path = await asyncio.to_thread(
                clone_repo_if_missing,
                git_url,
                github_token,
                depth=1,
            )
            repo_path = str(cloned_path)

        repository_scan, detections = await self._scan_and_classify_codebases(repo_path)

        configs: list[CodebaseConfig] = []
        for directory_path, detected in detections.items():
            config = await self._build_codebase_config(
                directory_path,
                detected,
                repository_scan,
                repo_path,
            )
            if config.programming_language_metadata.manifest_path is None:
                logger.debug(
                    "Skipping detected TypeScript codebase without manifest: dir={}, manager={}",
                    directory_path,
                    detected.manager_name,
                )
                continue
            configs.append(config)

        return configs

    async def _scan_and_classify_codebases(
        self, repo_path: str
    ) -> tuple[TypeScriptRepositoryScan, dict[str, DetectedCodebase]]:
        """Scan once, then route through monorepo or standalone detection adapters."""
        if not self.language_rules or not self.ordered_detector:
            raise RuntimeError("Detector not initialized")

        repository_scan = await self._scan_repository(repo_path)
        root_workspace_context = await self._discover_root_workspace_context(
            repo_path=repo_path,
            repository_scan=repository_scan,
        )
        if root_workspace_context is None:
            standalone_adapter = TypeScriptStandaloneDetectionAdapter(
                ordered_detector=self.ordered_detector,
                is_typescript_project=self._is_typescript_project,
                resolve_workspace_members_and_exclusions=(
                    self._resolve_workspace_members_and_exclusions
                ),
            )
            detections = await standalone_adapter.detect_codebases(
                repo_path,
                repository_scan,
            )
            return repository_scan, detections

        monorepo_adapter = TypeScriptMonorepoDetectionAdapter(
            ordered_detector=self.ordered_detector,
            is_typescript_project=self._is_typescript_project,
            resolve_workspace_members_and_exclusions=(
                self._resolve_workspace_members_and_exclusions
            ),
            detect_local_package_manager_override=(
                self._detect_local_package_manager_override
            ),
        )
        detections = await monorepo_adapter.detect_codebases(
            repo_path,
            repository_scan,
            root_workspace_context,
        )
        return repository_scan, detections

    async def _scan_repository(self, repo_path: str) -> TypeScriptRepositoryScan:
        """Run one ripgrep-backed inventory scan and reuse it across detector phases."""
        if self.language_rules is None:
            raise RuntimeError("Detector not initialized")

        file_patterns = self._collect_ripgrep_search_patterns()
        all_files = await find_files(
            patterns=file_patterns,
            search_path=repo_path,
            ignore_dirs=self.language_rules.ignores,
        )
        dirs_to_files = group_files_by_directory(all_files)
        inventory = tuple(
            FileNode(path=file_path, kind="file", size=None) for file_path in all_files
        )
        return TypeScriptRepositoryScan(
            inventory=inventory,
            inventory_paths=frozenset(node.path for node in inventory),
            dirs_to_files=dirs_to_files,
            known_dirs=tuple(dirs_to_files.keys()),
            manifest_dirs=tuple(
                sorted(
                    {
                        os.path.dirname(file_path) or "."
                        for file_path in all_files
                        if os.path.basename(file_path) == "package.json"
                    }
                )
            ),
        )

    async def _discover_root_workspace_context(
        self,
        repo_path: str,
        repository_scan: TypeScriptRepositoryScan,
    ) -> WorkspaceDiscoveryContext | None:
        """Check if the repo root declares workspaces and return the full ownership context.

        Returns None if the root directory has no workspace configuration. Otherwise
        resolves the package manager, expands workspace globs to member directories,
        and detects any Nx/Turbo orchestrator.

        Example — pnpm monorepo root:
            # Root has pnpm-workspace.yaml with packages: ["apps/*", "libs/*"]
            # Root also has nx.json
            # Returns: WorkspaceDiscoveryContext(
            #     root_dir=".", manager_name="pnpm",
            #     member_dirs=("apps/web", "libs/shared"),
            #     orchestrator=WorkspaceOrchestratorMetadata(NX, "nx.json"))

        Example — no workspace at root:
            # Root has package.json without workspaces field
            # Returns: None
        """
        root_files = repository_scan.dirs_to_files.get(".")
        if root_files is None:
            return None

        manager_name = await self._resolve_root_workspace_package_manager(
            repo_path=repo_path,
            files_in_dir=root_files,
        )
        if manager_name is None:
            return None

        (
            member_dirs,
            excluded_dirs,
        ) = await self._resolve_workspace_members_and_exclusions(
            directory_path=".",
            repo_path=repo_path,
            manager_name=manager_name,
            package_candidate_dirs=repository_scan.manifest_dirs,
        )
        if not member_dirs:
            return None

        orchestrator = self._detect_workspace_orchestrator(
            directory_path=".",
            files_in_dir=root_files,
        )
        logger.debug(
            "Authoritative root workspace discovered: manager={}, members={}, exclusions={}, orchestrator={}",
            manager_name,
            sorted(member_dirs),
            sorted(excluded_dirs),
            orchestrator.orchestrator.value if orchestrator is not None else None,
        )
        return WorkspaceDiscoveryContext(
            root_dir=".",
            manager_name=manager_name,
            member_dirs=tuple(sorted(member_dirs)),
            excluded_dirs=tuple(sorted(excluded_dirs)),
            orchestrator=orchestrator,
        )

    async def _resolve_root_workspace_package_manager(
        self, repo_path: str, files_in_dir: Sequence[str]
    ) -> str | None:
        """Determine which package manager owns the root-level workspace using a priority cascade.

        Returns the manager name string or None if the root has no workspace configuration.

        Precedence (highest to lowest):
        1. pnpm-workspace.yaml present → "pnpm"
        2. package.json.workspaces present + packageManager field → use declared (npm/yarn/bun)
        3. package.json.workspaces present + explicit lockfile signal → use lockfile manager
        4. package.json.workspaces present + no other signal → "npm" (workspaces implies npm)
        5. No workspace config at all → None

        Example — root has pnpm-workspace.yaml + package-lock.json:
            # Returns "pnpm" (pnpm-workspace.yaml always wins, lockfile ignored)

        Example — root has package.json with "workspaces" + "packageManager": "bun@1.3.9":
            # Returns "bun" (packageManager field takes priority over lockfile detection)

        Example — root has package.json with "workspaces" + yarn.lock but no packageManager field:
            # Returns "yarn" (explicit lockfile signal via OrderedDetector)

        Example — root has package.json with "workspaces" but no lockfile and no packageManager:
            # Returns "npm" (deterministic fallback)
        """
        file_names = {os.path.basename(path) for path in files_in_dir}
        if "pnpm-workspace.yaml" in file_names:
            logger.debug(
                "Root workspace manager resolved via authoritative pnpm-workspace.yaml"
            )
            return "pnpm"

        npm_like_globs = await self._read_workspace_globs(
            directory_path=".",
            repo_path=repo_path,
            manager_name="npm",
            workspace_field="workspaces",
        )
        if not npm_like_globs:
            return None

        declared_manager = await self._read_package_manager_field(".", repo_path)
        if declared_manager in {"npm", "yarn", "bun"}:
            logger.debug(
                "Root workspace manager resolved via packageManager field: {}",
                declared_manager,
            )
            return declared_manager

        ordered_detector = self.ordered_detector
        if ordered_detector is None:
            raise RuntimeError("Detector not initialized")

        explicit_signal = await ordered_detector.detect_explicit_manager_result(
            directory_path=".",
            available_files=files_in_dir,
            repo_path=repo_path,
        )
        if explicit_signal is not None and explicit_signal.manager_name in {
            "npm",
            "yarn",
            "bun",
        }:
            logger.debug(
                "Root workspace manager resolved via explicit local signal: manager={}, evidence_type={}, evidence_value={}",
                explicit_signal.manager_name,
                explicit_signal.evidence_type,
                explicit_signal.evidence_value,
            )
            return explicit_signal.manager_name

        logger.debug(
            "Root workspace manager falling back to npm because package.json.workspaces is authoritative and no stronger npm-like signal exists"
        )
        return "npm"

    def _detect_workspace_orchestrator(
        self, directory_path: str, files_in_dir: Sequence[str]
    ) -> WorkspaceOrchestratorMetadata | None:
        """Check for Nx or Turborepo config files and return orchestrator metadata.

        Nx takes priority when both Nx and Turbo configs coexist in the same directory.

        Example — directory has nx.json:
            # Returns WorkspaceOrchestratorMetadata(orchestrator=NX, config_path="nx.json")

        Example — directory at "tools/build" has turbo.json:
            # Returns WorkspaceOrchestratorMetadata(orchestrator=TURBO, config_path="tools/build/turbo.json")

        Example — directory has both nx.json and turbo.json:
            # Returns NX (Nx preferred when both present)

        Example — directory has neither:
            # Returns None
        """
        file_names = {os.path.basename(path) for path in files_in_dir}
        nx_config_name = self._first_present_file(
            file_names, ["nx.json", "workspace.json"]
        )
        turbo_config_name = self._first_present_file(
            file_names, ["turbo.json", "turbo.jsonc"]
        )

        if nx_config_name is not None and turbo_config_name is not None:
            logger.debug(
                "Both Nx and Turbo root configs detected at {}; preferring Nx for authoritative workspace metadata",
                directory_path,
            )

        selected_config_name = nx_config_name or turbo_config_name
        if selected_config_name is None:
            return None

        orchestrator = (
            WorkspaceOrchestratorType.NX
            if nx_config_name is not None
            else WorkspaceOrchestratorType.TURBO
        )
        if directory_path == ".":
            config_path = selected_config_name
        else:
            config_path = f"{directory_path}/{selected_config_name}"
        return WorkspaceOrchestratorMetadata(
            orchestrator=orchestrator,
            config_path=config_path,
        )

    @staticmethod
    def _first_present_file(file_names: set[str], candidates: list[str]) -> str | None:
        """Return the first candidate filename present in the directory."""
        for candidate in candidates:
            if candidate in file_names:
                return candidate
        return None

    async def _resolve_workspace_members_and_exclusions(
        self,
        directory_path: str,
        repo_path: str,
        manager_name: str,
        package_candidate_dirs: Sequence[str],
    ) -> tuple[set[str], set[str]]:
        """Read workspace globs from an aggregator's config and expand into (included, excluded) directory sets.

        Reads globs from pnpm-workspace.yaml (for pnpm) or package.json.workspaces (for npm/yarn/bun),
        rebases them to repo-relative form if the aggregator is not at the root, and expands
        against manifest-bearing package directories. Negated globs (e.g. "!packages/excluded")
        populate the excluded set.

        Example — root with "workspaces": ["packages/*", "!packages/internal"]:
            directory_path=".", manager_name="npm"
            package_candidate_dirs=["packages/ui", "packages/internal", "packages/core"]
            # Returns ({"packages/ui", "packages/core"}, {"packages/internal"})

        Example — manager has no workspace_field in rules.yaml:
            # Returns (set(), set())
        """
        ws_field = self._get_workspace_config_field_name(manager_name)
        if not ws_field:
            return set(), set()
        globs = await self._read_workspace_globs(
            directory_path, repo_path, manager_name, ws_field
        )
        if not globs:
            return set(), set()
        if directory_path != ".":
            globs = [
                rebase_workspace_glob(directory_path, glob_pattern)
                for glob_pattern in globs
            ]
        return expand_workspace_globs_with_exclusions(globs, package_candidate_dirs)

    def _get_workspace_config_field_name(self, manager_name: str) -> Optional[str]:
        """Look up the JSON field name used for workspace declarations in rules.yaml for the given manager.

        Example — for npm/yarn/bun, rules.yaml declares workspace_field: "workspaces":
            _get_workspace_config_field_name("bun")  # Returns "workspaces"

        Example — for a manager not in rules or with no workspace_field:
            _get_workspace_config_field_name("pip")  # Returns None
        """
        if not self.language_rules:
            return None
        for rule in self.language_rules.managers:
            if rule.manager == manager_name:
                return rule.workspace_field
        return None

    @staticmethod
    async def _read_package_json(
        directory_path: str, repo_path: str
    ) -> dict[str, object] | None:
        """Read and parse package.json from the given directory into a dict.

        Returns the parsed dict or None if the file is missing or contains invalid JSON.

        Example — directory_path="apps/web", repo_path="/home/user/repo":
            # Reads /home/user/repo/apps/web/package.json
            # Returns {"name": "@repo/web", "dependencies": {...}} or None
        """
        if directory_path == ".":
            pkg_path = os.path.join(repo_path, "package.json")
        else:
            pkg_path = os.path.join(repo_path, directory_path, "package.json")

        try:
            async with async_open(pkg_path, "r") as fh:
                content = await fh.read()
            raw: object = json.loads(content)
        except (FileNotFoundError, json.JSONDecodeError) as exc:
            logger.debug("Cannot read package.json from {}: {}", pkg_path, exc)
            return None

        if not isinstance(raw, dict):
            return None

        package_data: dict[str, object] = {}
        raw_package_data = cast(dict[object, object], raw)
        for key, value in raw_package_data.items():
            if isinstance(key, str):
                package_data[key] = value
        return package_data

    async def _read_workspace_globs(
        self,
        directory_path: str,
        repo_path: str,
        manager_name: str,
        workspace_field: str,
    ) -> list[str]:
        """Read workspace globs for the detected package manager.

        pnpm prefers `pnpm-workspace.yaml` with a top-level `packages` list.
        For compatibility, pnpm falls back to package.json when the YAML file
        is absent or does not declare any package patterns.

        package.json handling supports both array and object forms:
        - Array: ``"workspaces": ["apps/*", "packages/*"]``
        - Object: ``"workspaces": {"packages": ["apps/*", ...]}``
        """
        if manager_name == "pnpm":
            pnpm_globs = await self._read_pnpm_workspace_globs(
                directory_path, repo_path
            )
            if pnpm_globs:
                return pnpm_globs

        pkg = await self._read_package_json(directory_path, repo_path)
        if pkg is None:
            return []

        ws_value: object | None = pkg.get(workspace_field)
        if ws_value is None:
            return []

        globs: list[str] = []

        if isinstance(ws_value, list):
            workspace_items = cast(list[object], ws_value)
            for item in workspace_items:
                if isinstance(item, str):
                    globs.append(item)
            return globs

        if isinstance(ws_value, dict):
            try:
                workspace_config = WorkspacePackagesConfig.model_validate(ws_value)
            except ValidationError:
                return []
            return list(workspace_config.packages)

        return globs

    @staticmethod
    async def _read_pnpm_workspace_globs(
        directory_path: str, repo_path: str
    ) -> list[str]:
        """Read workspace package patterns from pnpm-workspace.yaml."""
        workspace_path = os.path.join(repo_path, directory_path, "pnpm-workspace.yaml")

        try:
            async with async_open(workspace_path, "r") as fh:
                content = await fh.read()
            raw: object = yaml.safe_load(content)
        except FileNotFoundError:
            return []
        except yaml.YAMLError as exc:
            logger.debug(
                "Cannot read pnpm-workspace.yaml from {}: {}", workspace_path, exc
            )
            return []

        try:
            workspace_config = PnpmWorkspaceConfig.model_validate(raw)
        except ValidationError:
            return []
        return list(workspace_config.packages)

    def _collect_ripgrep_search_patterns(self) -> list[str]:
        """Build the list of filename patterns to pass to ripgrep for bulk file discovery.

        Collects patterns from two sources:
        - Package manager signature files from rules.yaml (e.g. "package-lock.json", "bun.lockb")
        - Hardcoded TypeScript/monorepo config patterns (e.g. "tsconfig*.json", "nx.json", "turbo.json")

        Example output:
            ["package.json", "package-lock.json", "yarn.lock", "bun.lockb",
             "pnpm-lock.yaml", "tsconfig*.json", "pnpm-workspace.yaml",
             "turbo.json", "turbo.jsonc", "nx.json", "workspace.json", "project.json"]
        """
        if not self.language_rules:
            return []

        patterns: set[str] = set()

        # Extract patterns from package manager rules
        for manager_rule in self.language_rules.managers:
            for signature in manager_rule.signatures:
                if signature.file:
                    patterns.add(signature.file)
                if signature.glob:
                    patterns.add(signature.glob)

        # Add TypeScript-specific patterns for validation
        # These are needed by _has_tsconfig() to detect TypeScript projects
        patterns.add("tsconfig*.json")
        patterns.add("pnpm-workspace.yaml")
        patterns.add("turbo.json")
        patterns.add("turbo.jsonc")
        patterns.add("nx.json")
        patterns.add("workspace.json")
        patterns.add("project.json")

        return list(patterns)

    async def _has_typescript_dependency(
        self, directory_path: str, repo_path: str
    ) -> bool:
        """
        Check if directory contains package.json with typescript in dependencies.

        Uses ripgrep to find candidate package.json files containing "typescript"
        (with quotes), then parses JSON to verify typescript is in actual
        dependency sections (dependencies, devDependencies, peerDependencies,
        optionalDependencies). This avoids false positives from keywords,
        descriptions, or other fields.

        Args:
            directory_path: Directory to check (relative to repo root)
            repo_path: Absolute path to repository root

        Returns:
            True if package.json has typescript in dependency sections, False otherwise
        """
        try:
            candidate_dirs = await self._get_typescript_dependency_dirs(repo_path)

            if directory_path not in candidate_dirs:
                return False

            # Step 2: Parse JSON to verify typescript is in dependency sections
            if directory_path == ".":
                expected_package_json = "package.json"
            else:
                expected_package_json = os.path.join(directory_path, "package.json")
            package_json_abs_path = os.path.join(repo_path, expected_package_json)
            has_typescript = await parse_package_json_dependencies(
                package_json_abs_path
            )

            return has_typescript

        except (FileNotFoundError, json.JSONDecodeError) as e:
            # If file doesn't exist or is invalid JSON, not a valid TypeScript project
            logger.debug(
                "Error checking typescript dependency in {}: {}",
                directory_path,
                e,
            )
            return False

    async def _has_tsconfig(self, directory_path: str, repo_path: str) -> bool:
        """
        Check if directory contains TypeScript configuration files.

        Looks for tsconfig.json or variants like tsconfig.build.json,
        tsconfig.test.json, etc.

        Args:
            directory_path: Directory to check (relative to repo root)
            repo_path: Absolute path to repository root

        Returns:
            True if tsconfig files found in directory, False otherwise
        """
        tsconfig_dirs = await self._get_tsconfig_dirs(repo_path)
        return directory_path in tsconfig_dirs

    async def _is_typescript_project(self, directory_path: str, repo_path: str) -> bool:
        """
        Determine if directory is a TypeScript project using ordered checks.

        Evaluation order (first match wins):
        1. Has typescript in package.json dependencies (most definitive, checked first)
        2. Has tsconfig.json or variants (fallback for global TypeScript installs)

        Args:
            directory_path: Directory to check (relative to repo root)
            repo_path: Absolute path to repository root

        Returns:
            True if directory is TypeScript project, False if JavaScript-only
        """
        # Check 1: TypeScript dependency (fast and definitive)
        if await self._has_typescript_dependency(directory_path, repo_path):
            logger.debug("TypeScript detected via dependency in {}", directory_path)
            return True

        # Check 2: tsconfig file (fallback for global installs)
        if await self._has_tsconfig(directory_path, repo_path):
            logger.debug("TypeScript detected via tsconfig in {}", directory_path)
            return True

        # Not a TypeScript project
        logger.debug("JavaScript-only project detected in {}", directory_path)
        return False

    async def _read_project_name(
        self, directory_path: str, repo_path: str
    ) -> Optional[str]:
        """Read the "name" field from package.json in the given directory.

        Example — package.json has {"name": "@t3tools/web"}:
            # Returns "@t3tools/web"

        Example — package.json missing or has no name field:
            # Returns None
        """
        pkg = await self._read_package_json(directory_path, repo_path)
        if pkg is None:
            return None
        name: object = pkg.get("name")
        if isinstance(name, str):
            return name
        return None

    async def _read_package_manager_field(
        self, directory_path: str, repo_path: str
    ) -> Optional[str]:
        """Extract the manager name from the package.json "packageManager" field.

        Parses the value before the "@" version delimiter. Returns None if the field
        is absent, not a string, or specifies an unsupported manager.

        Example — package.json has "packageManager": "bun@1.3.9":
            # Returns "bun"

        Example — package.json has "packageManager": "pnpm@9.1.0":
            # Returns "pnpm"

        Example — package.json has no packageManager field:
            # Returns None
        """
        pkg = await self._read_package_json(directory_path, repo_path)
        if pkg is None:
            return None

        package_manager = pkg.get("packageManager")
        if not isinstance(package_manager, str):
            return None

        manager_name = package_manager.split("@", 1)[0].strip()
        if manager_name in {"bun", "npm", "pnpm", "yarn"}:
            logger.debug(
                "Declared packageManager field found: dir={}, package_manager={}",
                directory_path,
                package_manager,
            )
            return manager_name

        logger.debug(
            "Ignoring unsupported packageManager field: dir={}, package_manager={}",
            directory_path,
            package_manager,
        )
        return None

    async def _detect_local_package_manager_override(
        self, directory_path: str, files_in_dir: Sequence[str], repo_path: str
    ) -> ManagerDetectionResult | None:
        """Check if a workspace member declares its own package manager, overriding the parent.

        Uses a priority cascade to detect local ownership signals:
        1. packageManager field in package.json (e.g. "packageManager": "npm@10.9.0")
        2. pnpm-workspace.yaml present in the directory
        3. Explicit lockfile signal via OrderedDetector (ignores generic package.json fallback)

        Returns a ManagerDetectionResult if a local override is found, None if the member
        should inherit from its parent workspace.

        Example — packages/contracts has "packageManager": "npm@10.9.0" in a bun workspace:
            # Returns ManagerDetectionResult(manager_name="npm", evidence_type="package_manager_field")

        Example — packages/shared has no lockfile and no packageManager field:
            # Returns None (will inherit parent's manager)
        """
        ordered_detector = self.ordered_detector
        if ordered_detector is None:
            raise RuntimeError("Detector not initialized")

        file_names = {os.path.basename(path) for path in files_in_dir}

        declared_manager = await self._read_package_manager_field(
            directory_path, repo_path
        )
        if declared_manager is not None:
            detection_result = ManagerDetectionResult(
                manager_name=declared_manager,
                evidence_type="package_manager_field",
                evidence_value="packageManager",
            )
            logger.debug(
                "Workspace member local override declared via packageManager field: dir={}, manager={}, evidence_type={}, evidence_value={}",
                directory_path,
                detection_result.manager_name,
                detection_result.evidence_type,
                detection_result.evidence_value,
            )
            return detection_result

        if "pnpm-workspace.yaml" in file_names:
            detection_result = ManagerDetectionResult(
                manager_name="pnpm",
                evidence_type="file",
                evidence_value="pnpm-workspace.yaml",
            )
            logger.debug(
                "Workspace member local override detected via pnpm workspace manifest: dir={}, manager={}, evidence_type={}, evidence_value={}",
                directory_path,
                detection_result.manager_name,
                detection_result.evidence_type,
                detection_result.evidence_value,
            )
            return detection_result

        local_detection = await ordered_detector.detect_explicit_manager_result(
            directory_path, files_in_dir, repo_path
        )
        if local_detection is None:
            return None

        logger.debug(
            "Workspace member local override detected from local files: dir={}, manager={}, evidence_type={}, evidence_value={}",
            directory_path,
            local_detection.manager_name,
            local_detection.evidence_type,
            local_detection.evidence_value,
        )
        return local_detection

    async def _get_typescript_dependency_dirs(self, repo_path: str) -> set[str]:
        """Return (cached) set of directories whose package.json contains "typescript" in dependencies.

        On first call for a given repo_path, uses ripgrep to find all package.json files
        containing the string "typescript", extracts their parent directories, and caches
        the result. Subsequent calls for the same repo_path return the cached set.

        Example — repo has apps/web/package.json with devDependencies.typescript:
            # Returns {"apps/web", "packages/shared", ...}  (all dirs with TS in deps)
        """
        cached_dirs = self._typescript_dependency_dirs_cache.get(repo_path)
        if cached_dirs is not None:
            logger.debug(
                "Using cached TypeScript dependency directory set: repo={}, count={}",
                repo_path,
                len(cached_dirs),
            )
            return cached_dirs

        ignore_dirs = self.language_rules.ignores if self.language_rules else None
        candidates = await find_files_with_content(
            '"typescript"', "package.json", repo_path, ignore_dirs=ignore_dirs
        )
        candidate_dirs = {os.path.dirname(path) or "." for path in candidates}
        self._typescript_dependency_dirs_cache[repo_path] = candidate_dirs
        logger.debug(
            "Built TypeScript dependency directory cache: repo={}, count={}, dirs={}",
            repo_path,
            len(candidate_dirs),
            sorted(candidate_dirs),
        )
        return candidate_dirs

    async def _get_tsconfig_dirs(self, repo_path: str) -> set[str]:
        """Return (cached) set of directories that contain any tsconfig*.json file.

        On first call for a given repo_path, uses ripgrep to find all tsconfig*.json files
        (tsconfig.json, tsconfig.build.json, tsconfig.test.json, etc.), extracts their
        parent directories, and caches the result.

        Example — repo has apps/web/tsconfig.json and apps/web/tsconfig.build.json:
            # Returns {"apps/web", "packages/ui", ...}  (deduplicated by directory)
        """
        cached_dirs = self._tsconfig_dirs_cache.get(repo_path)
        if cached_dirs is not None:
            logger.debug(
                "Using cached tsconfig directory set: repo={}, count={}",
                repo_path,
                len(cached_dirs),
            )
            return cached_dirs

        ignore_dirs = self.language_rules.ignores if self.language_rules else None
        tsconfig_files = await find_files(
            ["tsconfig*.json"], repo_path, ignore_dirs=ignore_dirs
        )
        tsconfig_dirs = {os.path.dirname(path) or "." for path in tsconfig_files}
        self._tsconfig_dirs_cache[repo_path] = tsconfig_dirs
        logger.debug(
            "Built tsconfig directory cache: repo={}, count={}, dirs={}",
            repo_path,
            len(tsconfig_dirs),
            sorted(tsconfig_dirs),
        )
        return tsconfig_dirs

    async def _build_codebase_config(
        self,
        directory_path: str,
        detected: DetectedCodebase,
        repository_scan: TypeScriptRepositoryScan,
        repo_path: str,
    ) -> CodebaseConfig:
        """Assemble a CodebaseConfig from a DetectedCodebase by resolving manifest path and project name.

        Reads the "name" field from package.json, finds the manifest file in the ripgrep
        inventory, and packages everything into ProgrammingLanguageMetadata + CodebaseConfig.

        Example — detected = DetectedCodebase(manager_name="bun", provenance=INHERITED, workspace_root="."):
            directory_path = "apps/web"
            # Returns CodebaseConfig(
            #     codebase_folder="apps/web",
            #     programming_language_metadata=ProgrammingLanguageMetadata(
            #         language=TYPESCRIPT, package_manager=bun, manifest_path="apps/web/package.json",
            #         project_name="@repo/web", package_manager_provenance=INHERITED, workspace_root="."))
        """

        manifest_candidates = self._get_manifest_filenames_for_manager(
            detected.manager_name
        )
        manifest_path = self._find_manifest_in_inventory(
            directory_path,
            manifest_candidates,
            repository_scan,
        )

        package_manager_enum = (
            PackageManagerType(detected.manager_name) if detected.manager_name else None
        )

        project_name = await self._read_project_name(directory_path, repo_path)

        metadata = ProgrammingLanguageMetadata(
            language=ProgrammingLanguage.TYPESCRIPT,
            package_manager=package_manager_enum,
            manifest_path=manifest_path,
            language_version=None,
            project_name=project_name,
            package_manager_provenance=detected.provenance,
            workspace_root=detected.workspace_root,
            workspace_orchestrator=detected.workspace_orchestrator,
            workspace_orchestrator_config_path=detected.workspace_orchestrator_config_path,
        )

        return CodebaseConfig(
            codebase_folder=directory_path,
            root_packages=None,
            programming_language_metadata=metadata,
        )

    @staticmethod
    def _get_manifest_filenames_for_manager(manager: str) -> list[str]:
        """Return the candidate manifest filenames for the given package manager.

        Example — manager="bun":  # Returns ["package.json"]
        Example — manager="pnpm": # Returns ["package.json"]
        Example — manager="unknown": # Returns []
        """
        if manager in {"npm", "yarn", "pnpm", "bun"}:
            return ["package.json"]
        return []

    @staticmethod
    def _find_manifest_in_inventory(
        directory_path: str,
        manifest_candidates: list[str],
        repository_scan: TypeScriptRepositoryScan,
    ) -> str | None:
        """Search the ripgrep file inventory for a manifest file in the given directory.

        Returns the repo-relative path if found, None otherwise.

        Example — directory_path="apps/web", manifest_candidates=["package.json"],
                  inventory contains FileNode(path="apps/web/package.json"):
            # Returns "apps/web/package.json"

        Example — directory_path=".", manifest_candidates=["package.json"]:
            # Returns "package.json" (no directory prefix for root)
        """
        if not manifest_candidates:
            return None

        for candidate in manifest_candidates:
            if directory_path == ".":
                manifest_key = candidate
            else:
                manifest_key = os.path.join(directory_path, candidate)
            if manifest_key in repository_scan.inventory_paths:
                return manifest_key
        return None
