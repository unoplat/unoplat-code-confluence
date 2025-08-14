"""
Fast Python package manager detector using ripgrep.

This module provides a drop-in replacement for PythonCodebaseDetector that uses
ripgrep for fast file discovery and ordered evaluation for package manager detection.
Maintains the same public interface for seamless migration.
"""

from __future__ import annotations

import os
import asyncio
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from aiofile import async_open
from git import Repo
from unoplat_code_confluence_commons.configuration_models import CodebaseConfig
from unoplat_code_confluence_commons.programming_language_metadata import (
    PackageManagerType,
    ProgrammingLanguage,
    ProgrammingLanguageMetadata,
)
import yaml  # type: ignore

from src.code_confluence_flow_bridge.models.configuration.settings import (
    FileNode,
    LanguageRules,
    ManagerRule,
    Signature,
)
from src.code_confluence_flow_bridge.parser.package_manager.detectors.ordered_detection import (
    OrderedDetector,
)
from src.code_confluence_flow_bridge.parser.package_manager.detectors.ripgrep_utils import (
    find_files,
    find_python_mains,
)


# todo: check async/sync operations . it will be important to be performant when we enable batch ingestions or any other batch operations
class PythonRipgrepDetector:
    """Fast Python package manager detector using ripgrep and ordered evaluation.

    Maintains same interface as PythonCodebaseDetector for drop-in replacement.
    Uses ripgrep for fast file discovery and ordered evaluation without weights.
    """

    def __init__(self, rules_path: Optional[str] = None) -> None:
        """
        Initialize the detector.

        Args:
            rules_path: Path to rules yaml file. If None, uses rules.yaml.
        """
        if rules_path is None:
            # Use rules.yaml from same directory
            rules_path = os.path.join(os.path.dirname(__file__), "rules.yaml")

        self.rules_path: str = rules_path
        self.language_rules: Optional[LanguageRules] = None
        self.ordered_detector: Optional[OrderedDetector] = None
        self._initialized: bool = False

    async def initialize_rules(self) -> None:
        """
        Initialize rules and build ordered detector.
        Must be called after construction before using the detector.
        """
        if self._initialized:
            return

        self.language_rules = await self._load_rules()
        self.ordered_detector = OrderedDetector(self.language_rules)
        self._initialized = True

    async def _load_rules(self) -> LanguageRules:
        """Load and parse rules from YAML file."""
        if not Path(self.rules_path).exists():
            raise FileNotFoundError(f"Rules file not found: {self.rules_path}")

        async with async_open(self.rules_path, "r") as f:
            content: str = await f.read()
            rules_data: Dict = yaml.safe_load(content)

        # Extract Python rules
        python_rules: Dict = rules_data.get("python", {})
        managers: List[ManagerRule] = []

        for mgr_data in python_rules.get("managers", []):
            signatures: List[Signature] = []
            for sig_data in mgr_data.get("signatures", []):
                if isinstance(sig_data, str):
                    # Simple string signature
                    signatures.append(Signature(file=sig_data))
                elif isinstance(sig_data, dict):
                    # Complex signature with proper type handling
                    signatures.append(Signature(**sig_data))

            managers.append(
                ManagerRule(
                    manager=mgr_data["manager"],
                    weight=mgr_data.get("weight", 1),  # Still parsed but not used
                    signatures=signatures,
                    workspace_field=mgr_data.get("workspace_field"),
                )
            )

        return LanguageRules(ignores=python_rules.get("ignores", []), managers=managers)

    async def detect_codebases(
        self, git_url: str, github_token: str
    ) -> List[CodebaseConfig]:
        """
        Main detection method to detect Python codebases from a GitHub repository URL or local path.

        Maintains same interface as PythonCodebaseDetector for drop-in replacement.

        Args:
            git_url: GitHub repository URL (supports HTTPS and SSH formats) or local path
            github_token: GitHub personal access token for authentication

        Returns:
            List of CodebaseConfig objects for detected codebases
        """
        if not self._initialized:
            raise RuntimeError(
                "Detector not initialized. Call initialize_rules() first."
            )

        # Check if it's a local path or remote URL
        if os.path.exists(git_url):
            # Local path - use directly without cloning
            repo_path: str = git_url
        else:
            # Remote URL - clone repository
            repo_path = await asyncio.to_thread(self._clone_repository, git_url, github_token)

        # Fast detection using ripgrep with breadth-first processing
        inventory, detections = await self._fast_detect(repo_path)

        # Build codebase config objects
        codebase_configs: List[CodebaseConfig] = []
        for directory_path, manager_name in detections.items():
            codebase_config: CodebaseConfig = await self._build_codebase_config(
                directory_path, manager_name, inventory, repo_path
            )
            codebase_configs.append(codebase_config)

        return codebase_configs

    async def _fast_detect(
        self, repo_path: str
    ) -> Tuple[List[FileNode], Dict[str, str]]:
        """
        Fast detection using ripgrep for file discovery.

        Args:
            repo_path: Path to repository

        Returns:
            Tuple of (inventory, detections) where detections maps directory to manager
        """
        if not self.language_rules or not self.ordered_detector:
            raise RuntimeError("Detector not initialized")

        # Find all relevant files in one ripgrep call
        file_patterns: List[str] = self._extract_file_patterns()
        all_files: List[str] = await find_files(
            patterns=file_patterns,
            search_path=repo_path,
            ignore_dirs=self.language_rules.ignores,
        )

        # Build inventory
        inventory: List[FileNode] = [
            FileNode(path=file_path, kind="file", size=None) for file_path in all_files
        ]

        # Group files by directory
        dirs_to_files: Dict[str, List[str]] = self._group_files_by_directory(all_files)

        # Detect package managers using breadth-first processing with done_dirs
        detections: Dict[str, str] = {}
        done_dirs: set[str] = set()

        # Sort directories by path depth (breadth-first: shorter paths first)
        sorted_dirs: List[str] = sorted(
            dirs_to_files.keys(), key=lambda p: len(p.split("/"))
        )

        for directory_path in sorted_dirs:
            # Skip if this directory is nested under a done directory
            if self._is_nested_under_done_dirs(directory_path, done_dirs):
                continue

            files_in_dir: List[str] = dirs_to_files[directory_path]
            detected_manager: Optional[
                str
            ] = await self.ordered_detector.detect_manager(
                directory_path, files_in_dir, repo_path
            )

            if detected_manager:
                detections[directory_path] = detected_manager
                done_dirs.add(directory_path)

        return inventory, detections

    def _extract_file_patterns(self) -> List[str]:
        """Extract all file patterns from rules for ripgrep search."""
        if not self.language_rules:
            return []

        patterns: List[str] = []
        for manager_rule in self.language_rules.managers:
            for signature in manager_rule.signatures:
                if signature.file:
                    patterns.append(signature.file)
                if signature.glob:
                    patterns.append(signature.glob)

        return list(set(patterns))  # Remove duplicates

    def _group_files_by_directory(self, file_paths: List[str]) -> Dict[str, List[str]]:
        """Group files by their parent directory."""
        dirs_to_files: Dict[str, List[str]] = defaultdict(list)

        for file_path in file_paths:
            directory: str = os.path.dirname(file_path) or "."
            dirs_to_files[directory].append(file_path)

        return dict(dirs_to_files)

    def _is_nested_under_done_dirs(
        self, directory_path: str, done_dirs: set[str]
    ) -> bool:
        """Check if directory is nested under any done directory."""
        # Special case: if root directory "." is done, all other dirs are nested under it
        if "." in done_dirs and directory_path != ".":
            return True

        # Regular nested directory checking for non-root done_dirs
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
        repo_path: str,
    ) -> CodebaseConfig:
        """Build CodebaseConfig object for detected codebase."""
        # Find manifest path if exists
        manifest_path: Optional[str] = None
        if manager_name in ["poetry", "uv"]:
            manifest_candidate: str = (
                os.path.join(directory_path, "pyproject.toml")
                if directory_path != "."
                else "pyproject.toml"
            )
            if any(n.path == manifest_candidate for n in inventory):
                manifest_path = manifest_candidate

        # Detect root packages using ripgrep
        root_packages: Optional[List[str]] = await find_python_mains(
            repo_path, directory_path
        )

        # Build programming language metadata
        programming_language_metadata = ProgrammingLanguageMetadata(
            language=ProgrammingLanguage.PYTHON,
            package_manager=PackageManagerType(manager_name),
            language_version=None,
            manifest_path=manifest_path,
            project_name=None,
        )

        return CodebaseConfig(
            codebase_folder=directory_path,
            root_packages=root_packages,
            programming_language_metadata=programming_language_metadata,
        )

    # todo: stick to one format either ssh or https
    def _clone_repository(self, git_url: str, github_token: str) -> str:
        """
        Clone GitHub repository to local path.
        Uses same logic as existing detector for consistency.

        Args:
            git_url: GitHub repository URL
            github_token: GitHub personal access token for authentication

        Returns:
            Local path to cloned repository
        """
        # Extract repository name from URL (same logic as existing detector)
        if git_url.startswith("git@"):
            # Handle SSH format: git@github.com:org/repo.git
            repo_path: str = git_url.split("github.com:")[-1]
        else:
            # Handle HTTPS format: https://github.com/org/repo[.git]
            repo_path = git_url.split("github.com/")[-1]
        repo_path = repo_path.replace(".git", "")
        repo_name: str = repo_path.split("/")[-1]

        # Create local directory (same as existing detector)
        local_base_path: str = os.path.join(
            os.path.expanduser("~"), ".unoplat", "repositories"
        )
        os.makedirs(local_base_path, exist_ok=True)

        # Set local clone path
        local_repo_path: str = os.path.join(local_base_path, repo_name)

        # Clone repository if not already cloned
        if not os.path.exists(local_repo_path):
            # Add token to URL for HTTPS URLs
            if git_url.startswith("https://"):
                # Insert token into HTTPS URL
                clone_url: str = git_url.replace("https://", f"https://{github_token}@")
            else:
                clone_url = git_url

            Repo.clone_from(clone_url, local_repo_path, depth=1)

        return local_repo_path
