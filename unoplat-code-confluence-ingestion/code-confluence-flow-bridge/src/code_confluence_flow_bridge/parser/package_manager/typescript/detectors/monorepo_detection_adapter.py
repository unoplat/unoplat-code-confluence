from __future__ import annotations

from collections.abc import Awaitable, Callable, Sequence

from loguru import logger
from unoplat_code_confluence_commons.programming_language_metadata import (
    PackageManagerProvenance,
)

from src.code_confluence_flow_bridge.models.detection.shared.evidence import (
    ManagerDetectionResult,
)
from src.code_confluence_flow_bridge.models.detection.shared.results import (
    DetectedCodebase,
)
from src.code_confluence_flow_bridge.models.detection.typescript.discovery import (
    TypeScriptRepositoryScan,
    WorkspaceDiscoveryContext,
    WorkspaceOrchestratorMetadata,
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
LocalOverrideDetector = Callable[
    [str, Sequence[str], str], Awaitable[ManagerDetectionResult | None]
]


class TypeScriptMonorepoDetectionAdapter:
    """Detect TypeScript codebases when authoritative root workspace context exists."""

    def __init__(
        self,
        ordered_detector: OrderedDetector,
        is_typescript_project: TypeScriptProjectCheck,
        resolve_workspace_members_and_exclusions: WorkspaceMembersResolver,
        detect_local_package_manager_override: LocalOverrideDetector,
    ) -> None:
        self._ordered_detector = ordered_detector
        self._is_typescript_project = is_typescript_project
        self._resolve_workspace_members_and_exclusions = (
            resolve_workspace_members_and_exclusions
        )
        self._detect_local_package_manager_override = (
            detect_local_package_manager_override
        )

    async def detect_codebases(
        self,
        repo_path: str,
        repository_scan: TypeScriptRepositoryScan,
        root_workspace_context: WorkspaceDiscoveryContext,
    ) -> dict[str, DetectedCodebase]:
        """Walk repository directories using authoritative workspace ownership first."""
        detections: dict[str, DetectedCodebase] = {}
        detected_standalone_dirs: set[str] = set()
        workspace_member_dirs: set[str] = set(root_workspace_context.member_dirs)
        workspace_excluded_dirs: set[str] = set(root_workspace_context.excluded_dirs)
        aggregator_to_manager: dict[str, str] = {
            root_workspace_context.root_dir: root_workspace_context.manager_name
        }
        aggregator_to_orchestrator: dict[str, WorkspaceOrchestratorMetadata | None] = {
            root_workspace_context.root_dir: root_workspace_context.orchestrator
        }

        for directory_path in sorted(
            repository_scan.known_dirs,
            key=lambda path: len(path.split("/")),
        ):
            if directory_path in workspace_excluded_dirs:
                logger.debug(
                    "Skipping excluded workspace directory: {}", directory_path
                )
                continue

            if directory_path == root_workspace_context.root_dir:
                logger.debug(
                    "Skipping authoritative root workspace owner: dir={}, manager={}",
                    root_workspace_context.root_dir,
                    root_workspace_context.manager_name,
                )
                continue

            if directory_path in workspace_member_dirs:
                is_typescript = await self._is_typescript_project(
                    directory_path, repo_path
                )
                if not is_typescript:
                    continue

                owner_result = find_nearest_workspace_owner(
                    directory_path, aggregator_to_manager
                )
                if owner_result is None:
                    continue

                inherited_manager, owner_dir = owner_result
                inherited_orchestrator = aggregator_to_orchestrator.get(owner_dir)
                files_in_dir = repository_scan.dirs_to_files[directory_path]
                local_detection = await self._detect_local_package_manager_override(
                    directory_path,
                    files_in_dir,
                    repo_path,
                )

                if local_detection is None:
                    effective_manager = inherited_manager
                    effective_provenance = PackageManagerProvenance.INHERITED
                    effective_workspace_root: str | None = owner_dir
                    effective_orchestrator = inherited_orchestrator
                else:
                    effective_manager = local_detection.manager_name
                    effective_provenance = PackageManagerProvenance.LOCAL
                    effective_workspace_root = None
                    effective_orchestrator = None

                (
                    nested_members,
                    nested_excluded_dirs,
                ) = await self._resolve_workspace_members_and_exclusions(
                    directory_path,
                    repo_path,
                    effective_manager,
                    repository_scan.manifest_dirs,
                )
                if nested_members:
                    workspace_member_dirs.update(nested_members)
                    workspace_excluded_dirs.update(nested_excluded_dirs)
                    aggregator_to_manager[directory_path] = effective_manager
                    aggregator_to_orchestrator[directory_path] = effective_orchestrator
                    logger.debug(
                        "Workspace aggregator discovered: dir={}, effective_manager={}, provenance={}, members={}",
                        directory_path,
                        effective_manager,
                        effective_provenance.value,
                        sorted(nested_members),
                    )
                    continue

                detections[directory_path] = DetectedCodebase(
                    manager_name=effective_manager,
                    provenance=effective_provenance,
                    workspace_root=effective_workspace_root,
                    workspace_orchestrator=(
                        effective_orchestrator.orchestrator
                        if effective_orchestrator is not None
                        else None
                    ),
                    workspace_orchestrator_config_path=(
                        effective_orchestrator.config_path
                        if effective_orchestrator is not None
                        else None
                    ),
                )
                detected_standalone_dirs.add(directory_path)
                logger.debug(
                    "Workspace member detected: dir={}, manager={}, provenance={}, workspace_root={}",
                    directory_path,
                    effective_manager,
                    effective_provenance.value,
                    effective_workspace_root,
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
                workspace_member_dirs.update(resolved_members)
                workspace_excluded_dirs.update(excluded_dirs)
                aggregator_to_manager[directory_path] = (
                    detected_manager_result.manager_name
                )
                aggregator_to_orchestrator[directory_path] = None
                logger.debug(
                    "Non-root local workspace aggregator discovered: dir={}, manager={}, evidence_type={}, evidence_value={}, members={}",
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
                "Standalone codebase detected outside root workspace ownership: dir={}, manager={}, evidence_type={}, evidence_value={}",
                directory_path,
                detected_manager_result.manager_name,
                detected_manager_result.evidence_type,
                detected_manager_result.evidence_value,
            )

        return detections
