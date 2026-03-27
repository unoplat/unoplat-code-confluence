"""
Ordered package manager detection without weights.

This module implements simple ordered detection logic where managers are
evaluated in sequence and the first match wins. No weight calculations
or complex tie-breaking logic needed.
"""

from __future__ import annotations

import os
from collections.abc import Sequence
import fnmatch

from loguru import logger

from src.code_confluence_flow_bridge.models.detection.shared.evidence import (
    ManagerDetectionResult,
)
from src.code_confluence_flow_bridge.models.detection.shared.rules import (
    LanguageRules,
    ManagerRule,
    Signature,
)
from src.code_confluence_flow_bridge.parser.package_manager.shared.ripgrep import (
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
        self, directory_path: str, available_files: Sequence[str], repo_path: str
    ) -> str | None:
        """
        Detect package manager using ordered rules evaluation.

        Args:
            directory_path: Path to directory being checked (relative to repo)
            available_files: List of files in the directory
            repo_path: Absolute path to repository root

        Returns:
            Package manager name if detected, None otherwise
        """
        detection_result = await self.detect_manager_result(
            directory_path, available_files, repo_path
        )
        if detection_result is None:
            return None
        return detection_result.manager_name

    async def detect_manager_result(
        self, directory_path: str, available_files: Sequence[str], repo_path: str
    ) -> ManagerDetectionResult | None:
        """Detect package manager and return matched-signature evidence."""
        file_set: set[str] = set(os.path.basename(f) for f in available_files)

        logger.debug(
            "Ordered manager detection start: dir={}, files={}",
            directory_path,
            sorted(file_set),
        )

        for manager_rule in self.language_rules.managers:
            detection_result: (
                ManagerDetectionResult | None
            ) = await self._check_manager_signatures(
                manager_rule, directory_path, file_set, repo_path
            )
            if detection_result is not None:
                logger.debug(
                    "Ordered manager detection matched: dir={}, manager={}, reason={}",
                    directory_path,
                    detection_result.manager_name,
                    f"{detection_result.evidence_type}:{detection_result.evidence_value}",
                )
                return detection_result

        logger.debug("Ordered manager detection found no match: dir={}", directory_path)
        return None

    async def detect_explicit_manager_result(
        self, directory_path: str, available_files: Sequence[str], repo_path: str
    ) -> ManagerDetectionResult | None:
        """Detect a manager using only explicit local ownership signals."""
        detection_result = await self.detect_manager_result(
            directory_path, available_files, repo_path
        )
        if detection_result is None:
            return None
        if self._is_generic_manifest_fallback(detection_result):
            logger.debug(
                "Ignoring generic manifest fallback for explicit ownership detection: dir={}, manager={}, reason={}",
                directory_path,
                detection_result.manager_name,
                f"{detection_result.evidence_type}:{detection_result.evidence_value}",
            )
            return None
        return detection_result

    @staticmethod
    def _is_generic_manifest_fallback(
        detection_result: ManagerDetectionResult,
    ) -> bool:
        return (
            detection_result.evidence_type == "file"
            and detection_result.evidence_value == "package.json"
        )

    async def _check_manager_signatures(
        self,
        manager_rule: ManagerRule,
        directory_path: str,
        available_files: set[str],
        repo_path: str,
    ) -> ManagerDetectionResult | None:
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
                evidence_type = "file" if signature.file is not None else "glob"
                evidence_value = signature.file or signature.glob
                if evidence_value is None:
                    raise ValueError(
                        "Manager detection signature must define file or glob"
                    )
                detection_result = ManagerDetectionResult(
                    manager_name=manager_rule.manager,
                    evidence_type=evidence_type,
                    evidence_value=evidence_value,
                )
                logger.debug(
                    "Ordered manager signature matched: dir={}, manager={}, evidence_type={}, evidence_value={}",
                    directory_path,
                    detection_result.manager_name,
                    detection_result.evidence_type,
                    detection_result.evidence_value,
                )
                return detection_result
        return None

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
