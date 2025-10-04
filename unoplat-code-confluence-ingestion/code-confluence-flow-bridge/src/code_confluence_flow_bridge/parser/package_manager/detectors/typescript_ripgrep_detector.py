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
from pathlib import Path
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
    #todo: duplicate code with python detector
    async def _load_rules(self) -> LanguageRules:
        """Load and parse TypeScript rules from YAML file."""
        rules_file = Path(self.rules_path)
        if not rules_file.exists():
            raise FileNotFoundError(f"Rules file not found: {rules_file}")

        async with async_open(rules_file, "r") as fh:
            content = await fh.read()
            rules_data: Dict = yaml.safe_load(content)

        ts_rules: Dict = rules_data.get(self.LANGUAGE_KEY, {})
        managers: List[ManagerRule] = []

        for manager_entry in ts_rules.get("managers", []):
            signatures: List[Signature] = []
            for sig in manager_entry.get("signatures", []):
                if isinstance(sig, str):
                    signatures.append(Signature(file=sig))
                elif isinstance(sig, dict):
                    signatures.append(Signature(**sig))

            managers.append(
                ManagerRule(
                    manager=manager_entry["manager"],
                    weight=manager_entry.get("weight", 1),
                    signatures=signatures,
                    workspace_field=manager_entry.get("workspace_field"),
                )
            )

        ignores = ts_rules.get("ignores", [])
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
            repo_path = await asyncio.to_thread(
                clone_repo_if_missing,
                git_url,
                github_token,
                depth=1,
            )

        inventory, detections = await self._fast_detect(repo_path)

        configs: List[CodebaseConfig] = []
        for directory_path, manager_name in detections.items():
            config = await self._build_codebase_config(
                directory_path, manager_name, inventory
            )
            configs.append(config)

        return configs

    async def _fast_detect(
        self, repo_path: str
    ) -> Tuple[List[FileNode], Dict[str, str]]:
        """Run ripgrep discovery and ordered detection."""
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

        detections: Dict[str, str] = {}
        done_dirs: set[str] = set()

        sorted_dirs = sorted(dirs_to_files.keys(), key=lambda p: len(p.split("/")))

        for directory_path in sorted_dirs:
            if self._is_nested_under_done_dirs(directory_path, done_dirs):
                continue

            files_in_dir = dirs_to_files[directory_path]
            detected_manager = await self.ordered_detector.detect_manager(
                directory_path, files_in_dir, repo_path
            )

            if detected_manager:
                detections[directory_path] = detected_manager
                done_dirs.add(directory_path)

        return inventory, detections

    def _extract_file_patterns(self) -> List[str]:
        """Collect unique file/glob patterns used in the rules."""
        if not self.language_rules:
            return []

        patterns: set[str] = set()
        for manager_rule in self.language_rules.managers:
            for signature in manager_rule.signatures:
                if signature.file:
                    patterns.add(signature.file)
                if signature.glob:
                    patterns.add(signature.glob)

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

    async def _build_codebase_config(
        self,
        directory_path: str,
        manager_name: str,
        inventory: List[FileNode],
    ) -> CodebaseConfig:
        """Construct CodebaseConfig for the detected directory."""

        manifest_candidates = self._manifest_candidates_for_manager(manager_name)
        manifest_path = self._resolve_manifest_path(directory_path, manifest_candidates, inventory)

        package_manager_enum = (
            PackageManagerType(manager_name) if manager_name else None
        )

        metadata = ProgrammingLanguageMetadata(
            language=ProgrammingLanguage.TYPESCRIPT,
            package_manager=package_manager_enum,
            manifest_path=manifest_path,
            language_version=None,
            project_name=None,
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

    
