"""Fast TypeScript package manager detector using ripgrep.

This detector mirrors the Python ripgrep detector but is configured for
TypeScript/JavaScript ecosystems (npm, pnpm, yarn, bun). It reuses the
ordered detection rules defined in ``rules.yaml`` and keeps the same
async interface so it can be swapped into the existing orchestration.
"""

from __future__ import annotations

import os
import asyncio
from collections import defaultdict
import fnmatch
import json
from pathlib import Path, PurePosixPath
from typing import Dict, List, Optional, Tuple

from aiofile import async_open
from loguru import logger
from unoplat_code_confluence_commons.configuration_models import CodebaseConfig
from unoplat_code_confluence_commons.programming_language_metadata import (
    PackageManagerType,
    ProgrammingLanguage,
    ProgrammingLanguageMetadata,
)
import yaml

from src.code_confluence_flow_bridge.models.configuration.settings import (
    FileNode,
    LanguageRules,
    ManagerRule,
    Signature,
)
from src.code_confluence_flow_bridge.parser.package_manager.detectors.git_utils import (
    clone_repo_if_missing,
)
from src.code_confluence_flow_bridge.parser.package_manager.detectors.ordered_detection import (
    OrderedDetector,
)
from src.code_confluence_flow_bridge.parser.package_manager.detectors.ripgrep_utils import (
    find_files,
    find_files_with_content,
    parse_package_json_dependencies,
)


class TypeScriptRipgrepDetector:
    """Fast TypeScript package manager detector using ripgrep."""

    LANGUAGE_KEY = "typescript"

    def __init__(self, rules_path: Optional[str] = None) -> None:
        """Initialise detector with optional rules override."""
        if rules_path is None:
            rules_path = os.path.join(os.path.dirname(__file__), "rules.yaml")

        self.rules_path: str = rules_path
        self.language_rules: Optional[LanguageRules] = None
        self.ordered_detector: Optional[OrderedDetector] = None
        self._initialized: bool = False

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
        rules_file = Path(self.rules_path)
        if not rules_file.exists():
            raise FileNotFoundError(f"Rules file not found: {rules_file}")

        async with async_open(rules_file, "r") as fh:
            content = await fh.read()
            rules_data: Dict[str, object] = yaml.safe_load(content)  # type: ignore[assignment]

        ts_rules_raw: object = rules_data.get(self.LANGUAGE_KEY, {})
        ts_rules: Dict[str, object] = (
            ts_rules_raw if isinstance(ts_rules_raw, dict) else {}
        )  # type: ignore[assignment]
        managers: List[ManagerRule] = []

        managers_list: object = ts_rules.get("managers", [])
        for manager_entry_raw in (
            managers_list if isinstance(managers_list, list) else []
        ):  # pyright: ignore[reportUnknownVariableType]
            if not isinstance(manager_entry_raw, dict):
                continue
            manager_entry: Dict[str, object] = manager_entry_raw  # type: ignore[assignment]
            signatures: List[Signature] = []
            sigs_raw: object = manager_entry.get("signatures", [])
            for sig in sigs_raw if isinstance(sigs_raw, list) else []:  # pyright: ignore[reportUnknownVariableType]
                if isinstance(sig, str):
                    signatures.append(Signature(file=sig))
                elif isinstance(sig, dict):
                    sig_dict: Dict[str, object] = sig  # type: ignore[assignment]
                    signatures.append(Signature(**sig_dict))  # type: ignore[arg-type]

            manager_name_val: str = str(manager_entry.get("manager", ""))
            weight_val: int = int(manager_entry.get("weight", 1))  # type: ignore[arg-type]
            ws_field_val: object = manager_entry.get("workspace_field")
            ws_field_str: Optional[str] = (
                ws_field_val if isinstance(ws_field_val, str) else None
            )

            managers.append(
                ManagerRule(
                    manager=manager_name_val,
                    weight=weight_val,
                    signatures=signatures,
                    workspace_field=ws_field_str,
                )
            )

        ignores_raw: object = ts_rules.get("ignores", [])
        ignores: List[str] = ignores_raw if isinstance(ignores_raw, list) else []  # type: ignore[assignment]
        return LanguageRules(ignores=ignores, managers=managers)

    async def detect_codebases(
        self, git_url: str, github_token: str
    ) -> List[CodebaseConfig]:
        """Detect TypeScript codebases from a GitHub URL or local path."""
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

        inventory, detections = await self._fast_detect(repo_path)

        configs: List[CodebaseConfig] = []
        for directory_path, manager_name in detections.items():
            config = await self._build_codebase_config(
                directory_path, manager_name, inventory, repo_path
            )
            configs.append(config)

        return configs

    async def _resolve_workspace_members(
        self,
        directory_path: str,
        repo_path: str,
        manager_name: str,
        known_dirs: List[str],
    ) -> set[str]:
        """Resolve workspace member directories for a given aggregator.

        Reads the workspace_field from rules for the manager, parses
        workspace globs from package.json, prefixes them with the
        declaring directory, and expands against known_dirs.
        """
        ws_field = self._get_workspace_field(manager_name)
        if not ws_field:
            return set()
        globs = await self._read_workspace_globs(
            directory_path, repo_path, manager_name, ws_field
        )
        if not globs:
            return set()
        if directory_path != ".":
            globs = [
                self._rebase_workspace_glob(directory_path, glob_pattern)
                for glob_pattern in globs
            ]
        members, _excluded_dirs = self._expand_workspace_globs_with_exclusions(
            globs, known_dirs
        )
        return members

    async def _fast_detect(
        self, repo_path: str
    ) -> Tuple[List[FileNode], Dict[str, str]]:
        """Run ripgrep discovery and ordered detection.

        Workspace aggregator roots (directories whose package.json declares
        workspace globs that resolve to at least one known directory) are
        excluded from the output. Only the resolved workspace members are
        emitted, inheriting the aggregator's detected package manager.
        Non-workspace standalone projects continue to emit normally.
        """
        if not self.language_rules or not self.ordered_detector:
            raise RuntimeError("Detector not initialized")

        file_patterns = self._extract_file_patterns()
        all_files = await find_files(
            patterns=file_patterns,
            search_path=repo_path,
            ignore_dirs=self.language_rules.ignores,
        )

        inventory: List[FileNode] = [
            FileNode(path=file_path, kind="file", size=None) for file_path in all_files
        ]

        dirs_to_files: Dict[str, List[str]] = self._group_files_by_directory(all_files)
        known_dirs_list: List[str] = list(dirs_to_files.keys())

        detections: Dict[str, str] = {}
        done_dirs: set[str] = set()
        aggregator_manager_map: Dict[str, str] = {}  # aggregator_dir → manager
        workspace_member_dirs: set[str] = set()  # expanded member paths
        workspace_excluded_dirs: set[str] = set()  # explicit negated workspace paths

        sorted_dirs = sorted(dirs_to_files.keys(), key=lambda p: len(p.split("/")))

        for directory_path in sorted_dirs:
            if directory_path in workspace_excluded_dirs:
                logger.debug(
                    "Skipping excluded workspace directory: {}", directory_path
                )
                continue

            # --- Branch A: Explicit workspace member (checked FIRST) ---
            if directory_path in workspace_member_dirs:
                is_typescript = await self._is_typescript_project(
                    directory_path, repo_path
                )
                if not is_typescript:
                    continue

                inherited = self._find_aggregator_manager(
                    directory_path, aggregator_manager_map
                )
                if not inherited:
                    continue

                # Check if this member is itself a nested aggregator
                (
                    nested_members,
                    nested_excluded_dirs,
                ) = await self._resolve_workspace_glob_sets(
                    directory_path, repo_path, inherited, known_dirs_list
                )

                if nested_members:
                    # Nested aggregator — suppress, register its members
                    workspace_member_dirs.update(nested_members)
                    workspace_excluded_dirs.update(nested_excluded_dirs)
                    aggregator_manager_map[directory_path] = inherited
                    logger.debug(
                        "Nested workspace aggregator: {} (inherited {}), members: {}",
                        directory_path,
                        inherited,
                        sorted(nested_members),
                    )
                else:
                    # Leaf member — emit with inherited manager
                    detections[directory_path] = inherited
                    done_dirs.add(directory_path)
                    logger.debug(
                        "Workspace member detected: {} (inherited {})",
                        directory_path,
                        inherited,
                    )
                continue

            # --- Nested suppression (only for non-workspace-member dirs) ---
            if self._is_nested_under_done_dirs(directory_path, done_dirs):
                continue

            # --- Branch B: Normal detection ---
            files_in_dir = dirs_to_files[directory_path]
            detected_manager = await self.ordered_detector.detect_manager(
                directory_path, files_in_dir, repo_path
            )

            if detected_manager:
                is_typescript = await self._is_typescript_project(
                    directory_path, repo_path
                )

                if is_typescript:
                    # Check for workspace aggregator
                    (
                        resolved_members,
                        excluded_dirs,
                    ) = await self._resolve_workspace_glob_sets(
                        directory_path,
                        repo_path,
                        detected_manager,
                        known_dirs_list,
                    )

                    if resolved_members:
                        # Aggregator — DO NOT add to detections or done_dirs
                        workspace_member_dirs.update(resolved_members)
                        workspace_excluded_dirs.update(excluded_dirs)
                        aggregator_manager_map[directory_path] = detected_manager
                        logger.debug(
                            "Workspace aggregator: {} ({}), members: {}",
                            directory_path,
                            detected_manager,
                            sorted(resolved_members),
                        )
                    else:
                        # Standalone — normal emit
                        detections[directory_path] = detected_manager
                        done_dirs.add(directory_path)
                        logger.debug(
                            "TypeScript codebase detected: {} ({})",
                            directory_path,
                            detected_manager,
                        )
                else:
                    logger.debug(
                        "Skipping JavaScript-only directory: {}",
                        directory_path,
                    )

        return inventory, detections

    async def _resolve_workspace_glob_sets(
        self,
        directory_path: str,
        repo_path: str,
        manager_name: str,
        known_dirs: List[str],
    ) -> Tuple[set[str], set[str]]:
        """Resolve included and excluded workspace directories for an aggregator."""
        ws_field = self._get_workspace_field(manager_name)
        if not ws_field:
            return set(), set()
        globs = await self._read_workspace_globs(
            directory_path, repo_path, manager_name, ws_field
        )
        if not globs:
            return set(), set()
        if directory_path != ".":
            globs = [
                self._rebase_workspace_glob(directory_path, glob_pattern)
                for glob_pattern in globs
            ]
        return self._expand_workspace_globs_with_exclusions(globs, known_dirs)

    def _get_workspace_field(self, manager_name: str) -> Optional[str]:
        """Return the workspace_field declared in rules for the given manager."""
        if not self.language_rules:
            return None
        for rule in self.language_rules.managers:
            if rule.manager == manager_name:
                return rule.workspace_field
        return None

    @staticmethod
    async def _read_package_json(
        directory_path: str, repo_path: str
    ) -> Optional[Dict[str, object]]:
        """Read and parse package.json from the given directory.

        Returns the parsed dict or None if the file is missing / invalid.
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
        return raw  # type: ignore[return-value]

    async def _read_workspace_globs(
        self,
        directory_path: str,
        repo_path: str,
        manager_name: str,
        workspace_field: str,
    ) -> List[str]:
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

        globs: List[str] = []

        if isinstance(ws_value, list):
            for item in ws_value:  # pyright: ignore[reportUnknownVariableType]
                if isinstance(item, str):
                    globs.append(item)
            return globs

        if isinstance(ws_value, dict):
            pkgs: object | None = ws_value.get("packages")  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]
            if isinstance(pkgs, list):
                for item in pkgs:  # pyright: ignore[reportUnknownVariableType]
                    if isinstance(item, str):
                        globs.append(item)
            return globs

        return globs

    @staticmethod
    async def _read_pnpm_workspace_globs(
        directory_path: str, repo_path: str
    ) -> List[str]:
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

        if not isinstance(raw, dict):
            return []

        packages: object = raw.get("packages")
        if not isinstance(packages, list):
            return []

        globs: List[str] = []
        for item in packages:
            if isinstance(item, str):
                globs.append(item)
        return globs

    @staticmethod
    def _match_workspace_pattern(pattern: str, dir_path: str) -> bool:
        """Segment-aware glob match with ``fnmatch`` and ``**`` support.

        - ``*`` matches exactly one path segment (partial ok via fnmatch).
        - ``**`` matches zero or more segments (recursive wildcard).

        Examples:
            ``apps/*`` matches ``apps/web`` but not ``apps/web/deep``
            ``apps/*-web`` matches ``apps/next-web`` but not ``apps/web``
            ``packages/**`` matches ``packages/core`` and ``packages/core/utils``
        """
        pattern_parts = PurePosixPath(pattern).parts
        dir_parts = PurePosixPath(dir_path).parts
        return segment_match(pattern_parts, 0, dir_parts, 0)

    @classmethod
    def _expand_workspace_globs(
        cls, workspace_globs: List[str], known_dirs: List[str]
    ) -> set[str]:
        """Expand workspace glob patterns against known directories."""
        members, _excluded_dirs = cls._expand_workspace_globs_with_exclusions(
            workspace_globs, known_dirs
        )
        return members

    @classmethod
    def _expand_workspace_globs_with_exclusions(
        cls, workspace_globs: List[str], known_dirs: List[str]
    ) -> Tuple[set[str], set[str]]:
        """Expand workspace glob patterns, returning included and excluded dirs."""
        members: set[str] = set()
        excluded_dirs: set[str] = set()
        for glob_pattern in workspace_globs:
            is_exclusion = glob_pattern.startswith("!")
            pattern_body = glob_pattern[1:] if is_exclusion else glob_pattern
            normalized_pattern = cls._normalize_dir_path(pattern_body)
            matching_dirs: set[str] = set()
            for dir_path in known_dirs:
                normalized_dir = cls._normalize_dir_path(dir_path)
                if cls._match_workspace_pattern(normalized_pattern, normalized_dir):
                    matching_dirs.add(normalized_dir)
            if is_exclusion:
                members.difference_update(matching_dirs)
                excluded_dirs.update(matching_dirs)
            else:
                members.update(matching_dirs)
                excluded_dirs.difference_update(matching_dirs)
        return members, excluded_dirs

    @staticmethod
    def _find_aggregator_manager(
        directory_path: str, aggregator_manager_map: Dict[str, str]
    ) -> Optional[str]:
        """Find which aggregator owns this directory.

        Picks the deepest matching aggregator (most specific parent).
        """
        sorted_aggregators = sorted(
            aggregator_manager_map.keys(),
            key=lambda p: len(PurePosixPath(p).parts),
            reverse=True,
        )
        for agg_dir in sorted_aggregators:
            if agg_dir == "." or directory_path.startswith(agg_dir + "/"):
                return aggregator_manager_map[agg_dir]
        return None

    @staticmethod
    def _normalize_dir_path(raw_path: str) -> str:
        """Normalize a repo-relative path to a canonical POSIX form.

        Strips trailing ``/``, converts empty string to ``"."``, and
        normalizes via ``PurePosixPath``.
        """
        stripped = raw_path.rstrip("/")
        if not stripped:
            return "."
        return str(PurePosixPath(stripped))

    @classmethod
    def _rebase_workspace_glob(cls, directory_path: str, glob_pattern: str) -> str:
        """Rebase a workspace glob declared in a subdirectory to repo-relative form."""
        is_exclusion = glob_pattern.startswith("!")
        pattern_body = glob_pattern[1:] if is_exclusion else glob_pattern
        rebased_pattern = cls._normalize_dir_path(f"{directory_path}/{pattern_body}")
        if is_exclusion:
            return f"!{rebased_pattern}"
        return rebased_pattern

    def _extract_file_patterns(self) -> List[str]:
        """
        Collect unique file/glob patterns used in the rules.

        Includes both package manager signature files and TypeScript-specific
        files needed for validation (tsconfig*.json).
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

        return list(patterns)

    def _group_files_by_directory(self, file_paths: List[str]) -> Dict[str, List[str]]:
        """Group file paths by their parent directory."""
        dirs_to_files: Dict[str, List[str]] = defaultdict(list)
        for file_path in file_paths:
            directory = os.path.dirname(file_path) or "."
            dirs_to_files[directory].append(file_path)
        return dict(dirs_to_files)

    def _is_nested_under_done_dirs(
        self, directory_path: str, done_dirs: set[str]
    ) -> bool:
        """Check if the directory is under an already processed directory."""
        if "." in done_dirs and directory_path != ".":
            return True
        for done_dir in done_dirs:
            if (
                done_dir != "."
                and directory_path != done_dir
                and directory_path.startswith(done_dir + "/")
            ):
                return True
        return False

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
            # Step 1: Use ripgrep to find candidate package.json files
            # Search for "typescript" with quotes to reduce false positives
            candidates: List[str] = await find_files_with_content(
                '"typescript"', "package.json", repo_path
            )

            if not candidates:
                return False

            # Step 2: Filter candidates to current directory only
            # Build expected package.json path for this directory
            if directory_path == ".":
                expected_package_json = "package.json"
            else:
                expected_package_json = os.path.join(directory_path, "package.json")

            # Check if our directory's package.json is in candidates
            if expected_package_json not in candidates:
                return False

            # Step 3: Parse JSON to verify typescript is in dependency sections
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
        # Find all tsconfig*.json files in repository
        tsconfig_files: List[str] = await find_files(["tsconfig*.json"], repo_path)

        if not tsconfig_files:
            return False

        # Check if any tsconfig file is in the current directory
        for tsconfig_path in tsconfig_files:
            # Get directory of tsconfig file
            tsconfig_dir = os.path.dirname(tsconfig_path) or "."

            if tsconfig_dir == directory_path:
                return True

        return False

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
        """Read the ``name`` field from package.json in the given directory."""
        pkg = await self._read_package_json(directory_path, repo_path)
        if pkg is None:
            return None
        name: object = pkg.get("name")
        if isinstance(name, str):
            return name
        return None

    async def _build_codebase_config(
        self,
        directory_path: str,
        manager_name: str,
        inventory: List[FileNode],
        repo_path: str,
    ) -> CodebaseConfig:
        """Construct CodebaseConfig for the detected directory."""

        manifest_candidates = self._manifest_candidates_for_manager(manager_name)
        manifest_path = self._resolve_manifest_path(
            directory_path, manifest_candidates, inventory
        )

        package_manager_enum = (
            PackageManagerType(manager_name) if manager_name else None
        )

        project_name = await self._read_project_name(directory_path, repo_path)

        metadata = ProgrammingLanguageMetadata(
            language=ProgrammingLanguage.TYPESCRIPT,
            package_manager=package_manager_enum,
            manifest_path=manifest_path,
            language_version=None,
            project_name=project_name,
        )

        return CodebaseConfig(
            codebase_folder=directory_path,
            root_packages=None,
            programming_language_metadata=metadata,
        )

    @staticmethod
    def _manifest_candidates_for_manager(manager: str) -> List[str]:
        """Return manifest filenames to check based on package manager."""
        if manager in {"npm", "yarn", "pnpm", "bun"}:
            return ["package.json"]
        return []

    @staticmethod
    def _resolve_manifest_path(
        directory_path: str,
        manifest_candidates: List[str],
        inventory: List[FileNode],
    ) -> Optional[str]:
        """Resolve the manifest path relative to repository root if present."""
        if not manifest_candidates:
            return None

        inventory_paths = {node.path for node in inventory}
        for candidate in manifest_candidates:
            if directory_path == ".":
                manifest_key = candidate
            else:
                manifest_key = os.path.join(directory_path, candidate)
            if manifest_key in inventory_paths:
                return manifest_key
        return None


def segment_match(
    pattern_parts: tuple[str, ...],
    pi: int,
    dir_parts: tuple[str, ...],
    di: int,
) -> bool:
    """Recursive segment-aware glob matcher.

    Supports ``*`` (single-segment, with fnmatch partial matching) and
    ``**`` (zero-or-more segments).
    """
    while pi < len(pattern_parts) and di < len(dir_parts):
        pp = pattern_parts[pi]
        if pp == "**":
            # ** can match zero or more segments
            # Try matching zero segments (skip **)
            if segment_match(pattern_parts, pi + 1, dir_parts, di):
                return True
            # Try matching one segment and keep ** active
            return segment_match(pattern_parts, pi, dir_parts, di + 1)
        if not fnmatch.fnmatchcase(dir_parts[di], pp):
            return False
        pi += 1
        di += 1

    # Skip trailing ** patterns (they can match zero segments)
    while pi < len(pattern_parts) and pattern_parts[pi] == "**":
        pi += 1

    return pi == len(pattern_parts) and di == len(dir_parts)
