from __future__ import annotations

from collections.abc import Awaitable, Callable, Sequence

from loguru import logger
from unoplat_code_confluence_commons.programming_language_metadata import (
    PackageManagerProvenance,
)

from src.code_confluence_flow_bridge.models.detection.shared.results import (
    DetectedCodebase,
)
from src.code_confluence_flow_bridge.models.detection.typescript.discovery import (
    TypeScriptRepositoryScan,
)
from src.code_confluence_flow_bridge.parser.package_manager.shared.ordered_detection import (
    OrderedDetector,
)
from src.code_confluence_flow_bridge.parser.package_manager.typescript.detectors.workspace_utils import (
    find_nearest_workspace_owner,
    is_child_of_detected_codebase,
)

TypeScriptProjectCheck = Callable[[str, str], Awaitable[bool]]
WorkspaceMembersResolver = Callable[
    [str, str, str, Sequence[str]], Awaitable[tuple[set[str], set[str]]]
]


class TypeScriptStandaloneDetectionAdapter:
    """Detect standalone or locally-owned TypeScript codebases without root context."""

    def __init__(
        self,
        ordered_detector: OrderedDetector,
        is_typescript_project: TypeScriptProjectCheck,
        resolve_workspace_members_and_exclusions: WorkspaceMembersResolver,
    ) -> None:
        self._ordered_detector = ordered_detector
        self._is_typescript_project = is_typescript_project
        self._resolve_workspace_members_and_exclusions = (
            resolve_workspace_members_and_exclusions
        )

    async def detect_codebases(
        self,
        repo_path: str,
        repository_scan: TypeScriptRepositoryScan,
    ) -> dict[str, DetectedCodebase]:
        """Walk repository directories and emit standalone or nested local detections."""
        detections: dict[str, DetectedCodebase] = {}
        detected_standalone_dirs: set[str] = set()
        nested_aggregator_to_manager: dict[str, str] = {}
        nested_workspace_member_dirs: set[str] = set()
        nested_workspace_excluded_dirs: set[str] = set()

        for directory_path in sorted(
            repository_scan.known_dirs,
            key=lambda path: len(path.split("/")),
        ):
            if directory_path in nested_workspace_excluded_dirs:
                logger.debug(
                    "Skipping excluded nested workspace directory: {}", directory_path
                )
                continue

            if directory_path in nested_workspace_member_dirs:
                is_typescript = await self._is_typescript_project(
                    directory_path, repo_path
                )
                if not is_typescript:
                    continue

                aggregator_result = find_nearest_workspace_owner(
                    directory_path, nested_aggregator_to_manager
                )
                if aggregator_result is None:
                    continue

                inherited_manager, aggregator_dir = aggregator_result
                (
                    nested_members,
                    nested_excluded_dirs,
                ) = await self._resolve_workspace_members_and_exclusions(
                    directory_path,
                    repo_path,
                    inherited_manager,
                    repository_scan.manifest_dirs,
                )
                if nested_members:
                    nested_workspace_member_dirs.update(nested_members)
                    nested_workspace_excluded_dirs.update(nested_excluded_dirs)
                    nested_aggregator_to_manager[directory_path] = inherited_manager
                    logger.debug(
                        "Nested standalone workspace aggregator discovered: dir={}, manager={}, members={}",
                        directory_path,
                        inherited_manager,
                        sorted(nested_members),
                    )
                    continue

                detections[directory_path] = DetectedCodebase(
                    manager_name=inherited_manager,
                    provenance=PackageManagerProvenance.INHERITED,
                    workspace_root=aggregator_dir,
                    workspace_orchestrator=None,
                    workspace_orchestrator_config_path=None,
                )
                detected_standalone_dirs.add(directory_path)
                logger.debug(
                    "Nested standalone workspace member detected: dir={}, manager={}, workspace_root={}",
                    directory_path,
                    inherited_manager,
                    aggregator_dir,
                )
                continue

            if is_child_of_detected_codebase(directory_path, detected_standalone_dirs):
                continue

            files_in_dir = repository_scan.dirs_to_files[directory_path]
            detected_manager_result = (
                await self._ordered_detector.detect_manager_result(
                    directory_path,
                    files_in_dir,
                    repo_path,
                )
            )
            if detected_manager_result is None:
                continue

            is_typescript = await self._is_typescript_project(directory_path, repo_path)
            if not is_typescript:
                logger.debug("Skipping JavaScript-only directory: {}", directory_path)
                continue

            (
                resolved_members,
                excluded_dirs,
            ) = await self._resolve_workspace_members_and_exclusions(
                directory_path,
                repo_path,
                detected_manager_result.manager_name,
                repository_scan.manifest_dirs,
            )
            if resolved_members:
                nested_workspace_member_dirs.update(resolved_members)
                nested_workspace_excluded_dirs.update(excluded_dirs)
                nested_aggregator_to_manager[directory_path] = (
                    detected_manager_result.manager_name
                )
                logger.debug(
                    "Standalone directory discovered as workspace aggregator: dir={}, manager={}, evidence_type={}, evidence_value={}, members={}",
                    directory_path,
                    detected_manager_result.manager_name,
                    detected_manager_result.evidence_type,
                    detected_manager_result.evidence_value,
                    sorted(resolved_members),
                )
                continue

            detections[directory_path] = DetectedCodebase(
                manager_name=detected_manager_result.manager_name,
                provenance=PackageManagerProvenance.LOCAL,
                workspace_root=None,
                workspace_orchestrator=None,
                workspace_orchestrator_config_path=None,
            )
            detected_standalone_dirs.add(directory_path)
            logger.debug(
                "TypeScript standalone codebase detected: dir={}, manager={}, evidence_type={}, evidence_value={}",
                directory_path,
                detected_manager_result.manager_name,
                detected_manager_result.evidence_type,
                detected_manager_result.evidence_value,
            )

        return detections
