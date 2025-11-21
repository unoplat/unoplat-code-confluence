"""
Ordered package manager detection without weights.

This module implements simple ordered detection logic where managers are
evaluated in sequence and the first match wins. No weight calculations
or complex tie-breaking logic needed.
"""

from __future__ import annotations

import os
import fnmatch
from typing import List, Optional

from src.code_confluence_flow_bridge.models.configuration.settings import (
    LanguageRules,
    ManagerRule,
    Signature,
)
from src.code_confluence_flow_bridge.parser.package_manager.detectors.ripgrep_utils import (
    search_absence_in_file,
    search_in_file,
)


class OrderedDetector:
    """Simple ordered detection: first match wins."""

    def __init__(self, language_rules: LanguageRules) -> None:
        """
        Initialize detector with language rules.

        Args:
            language_rules: Rules containing managers and their signatures
        """
        self.language_rules: LanguageRules = language_rules

    async def detect_manager(
        self, directory_path: str, available_files: List[str], repo_path: str
    ) -> Optional[str]:
        """
        Detect package manager using ordered rules evaluation.

        Args:
            directory_path: Path to directory being checked (relative to repo)
            available_files: List of files in the directory
            repo_path: Absolute path to repository root

        Returns:
            Package manager name if detected, None otherwise
        """
        # Convert to sets for O(1) lookup
        file_set: set[str] = set(os.path.basename(f) for f in available_files)

        # Evaluate managers in order (first match wins)
        for manager_rule in self.language_rules.managers:
            manager_detected: bool = await self._check_manager_signatures(
                manager_rule, directory_path, file_set, repo_path
            )
            if manager_detected:
                return manager_rule.manager

        return None

    async def _check_manager_signatures(
        self,
        manager_rule: ManagerRule,
        directory_path: str,
        available_files: set[str],
        repo_path: str,
    ) -> bool:
        """
        Check if any signature matches for this manager.

        Args:
            manager_rule: Manager rule to check
            directory_path: Directory being checked
            available_files: Set of filenames in directory
            repo_path: Repository root path

        Returns:
            True if any signature matches, False otherwise
        """
        for signature in manager_rule.signatures:
            signature_matches: bool = await self._check_signature(
                signature, directory_path, available_files, repo_path
            )
            if signature_matches:
                return True
        return False

    async def _check_signature(
        self,
        signature: Signature,
        directory_path: str,
        available_files: set[str],
        repo_path: str,
    ) -> bool:
        """
        Check if a single signature matches.

        Args:
            signature: Signature to check
            directory_path: Directory being checked
            available_files: Set of filenames in directory
            repo_path: Repository root path

        Returns:
            True if signature matches, False otherwise
        """
        # Handle file-based signatures
        if signature.file:
            return await self._check_file_signature(
                signature, directory_path, available_files, repo_path
            )

        # Handle glob-based signatures
        if signature.glob:
            return self._check_glob_signature(signature, available_files)

        return False

    async def _check_file_signature(
        self,
        signature: Signature,
        directory_path: str,
        available_files: set[str],
        repo_path: str,
    ) -> bool:
        """
        Check file-based signature with optional content matching.

        Args:
            signature: File signature to check
            directory_path: Directory being checked
            available_files: Set of filenames in directory
            repo_path: Repository root path

        Returns:
            True if file signature matches, False otherwise
        """
        if not signature.file or signature.file not in available_files:
            return False

        # Build full file path
        if directory_path == ".":
            file_path: str = os.path.join(repo_path, signature.file)
        else:
            file_path = os.path.join(repo_path, directory_path, signature.file)

        # Check if file exists
        if not os.path.exists(file_path):
            return False

        # Check positive content requirement
        if signature.contains:
            contains_found: bool = await search_in_file(file_path, signature.contains)
            if not contains_found:
                return False

        # Check negative content requirements (contains_absence)
        if signature.contains_absence:
            absence_satisfied: bool = await search_absence_in_file(
                file_path, signature.contains_absence
            )
            if not absence_satisfied:
                return False

        return True

    def _check_glob_signature(
        self, signature: Signature, available_files: set[str]
    ) -> bool:
        """
        Check glob-based signature.

        Args:
            signature: Glob signature to check
            available_files: Set of filenames in directory

        Returns:
            True if any file matches glob pattern, False otherwise
        """
        if not signature.glob:
            return False

        # Check if any file matches the glob pattern
        for filename in available_files:
            if fnmatch.fnmatch(filename, signature.glob):
                return True

        return False
