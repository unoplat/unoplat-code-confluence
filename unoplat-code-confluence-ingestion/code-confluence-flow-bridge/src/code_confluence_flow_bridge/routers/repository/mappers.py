"""Pure data-transformation helpers shared by repository endpoint handlers."""

from collections.abc import Mapping, Sequence
from typing import Dict, List, Optional, Tuple

from unoplat_code_confluence_commons.base_models import CodebaseWorkflowRun
from unoplat_code_confluence_commons.programming_language_metadata import (
    ProgrammingLanguageMetadata,
)
from unoplat_code_confluence_commons.workflow_models import ErrorReport, JobStatus

from src.code_confluence_flow_bridge.models.github.github_repo import (
    CodebaseStatus,
    CodebaseStatusList,
    IssueTracking,
    WorkflowRun,
    WorkflowStatus,
)


def build_programming_language_metadata(
    raw_metadata: Mapping[str, object],
) -> ProgrammingLanguageMetadata:
    """Build a ``ProgrammingLanguageMetadata`` from a raw dict stored in the DB.

    Uses ``.get()`` for all optional fields so callers with a superset
    (``get_codebase_metadata``) and a subset (``get_repository_data``) of keys
    both work correctly — ``ProgrammingLanguageMetadata`` defaults absent
    optional fields to ``None``.
    """
    return ProgrammingLanguageMetadata(
        language=raw_metadata["language"],  # type: ignore[arg-type]
        package_manager=raw_metadata.get("package_manager"),  # type: ignore[arg-type]
        language_version=raw_metadata.get("language_version"),  # type: ignore[arg-type]
        manifest_path=raw_metadata.get("manifest_path"),  # type: ignore[arg-type]
        project_name=raw_metadata.get("project_name"),  # type: ignore[arg-type]
    )


def build_repository_status_hierarchy(
    codebase_runs: Sequence[CodebaseWorkflowRun],
) -> Optional[CodebaseStatusList]:
    """Group ``CodebaseWorkflowRun`` rows into a nested status hierarchy.

    Returns ``None`` when *codebase_runs* is empty so the caller can
    assign directly to ``GithubRepoStatus.codebase_status_list``.
    """
    # Group codebase runs by codebase_folder
    codebase_data: Dict[str, List[Tuple[str, WorkflowRun]]] = {}
    for run in codebase_runs:
        codebase_folder = run.codebase_folder
        if codebase_folder not in codebase_data:
            codebase_data[codebase_folder] = []

        error_report = ErrorReport(**run.error_report) if run.error_report else None

        workflow_run = WorkflowRun(
            codebase_workflow_run_id=run.codebase_workflow_run_id,
            status=JobStatus(run.status),
            started_at=run.started_at,
            completed_at=run.completed_at,
            error_report=error_report,
            issue_tracking=IssueTracking(**run.issue_tracking)
            if run.issue_tracking
            else None,
        )

        codebase_data[codebase_folder].append((run.codebase_workflow_id, workflow_run))

    # Organize workflow runs by workflow ID within each codebase
    codebases: List[CodebaseStatus] = []
    for codebase_folder, runs in codebase_data.items():
        workflow_map: Dict[str, List[WorkflowRun]] = {}
        for workflow_id, wf_run in runs:
            if workflow_id not in workflow_map:
                workflow_map[workflow_id] = []
            workflow_map[workflow_id].append(wf_run)

        workflows: List[WorkflowStatus] = []
        for workflow_id, workflow_runs in workflow_map.items():
            workflows.append(
                WorkflowStatus(
                    codebase_workflow_id=workflow_id,
                    codebase_workflow_runs=workflow_runs,
                )
            )

        codebases.append(
            CodebaseStatus(codebase_folder=codebase_folder, workflows=workflows)
        )

    return CodebaseStatusList(codebases=codebases) if codebases else None
