"""API endpoint for Temporal-based agent execution.

This endpoint triggers Temporal workflows with trace_id from the API level,
providing distributed tracing and workflow state tracking via interceptors.
"""

from __future__ import annotations

from base64 import b64decode, b64encode
from collections.abc import Mapping
from pathlib import Path
import subprocess
from typing import TYPE_CHECKING, Literal, cast

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from ghapi.core import GhApi
from loguru import logger
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from temporalio.service import RPCError, RPCStatusCode
from unoplat_code_confluence_commons.credential_enums import ProviderKey
from unoplat_code_confluence_commons.pr_metadata_model import PrMetadata
from unoplat_code_confluence_commons.repo_models import (
    Repository,
    RepositoryAgentMdSnapshot,
    RepositoryWorkflowOperation,
    RepositoryWorkflowRun,
)
from unoplat_code_confluence_commons.workflow_models import JobStatus

from unoplat_code_confluence_query_engine.api.deps import trace_dependency
from unoplat_code_confluence_query_engine.db.postgres.ai_model_config import (
    AiModelConfig,
)
from unoplat_code_confluence_query_engine.db.postgres.db import get_startup_session
from unoplat_code_confluence_query_engine.services.config.credentials_service import (
    CredentialsService,
)
from unoplat_code_confluence_query_engine.services.github.git_ref_resolver import (
    resolve_repository_git_ref,
)
from unoplat_code_confluence_query_engine.services.github.github_api_helpers import (
    extract_http_error_status,
    is_http_not_found,
    resolve_github_host as _resolve_github_host_shared,
)
from unoplat_code_confluence_query_engine.services.repository.repository_metadata_service import (
    fetch_repository_metadata,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.constants import (
    APP_INTERFACES_ARTIFACT,
    BUSINESS_DOMAIN_REFERENCES_ARTIFACT,
    DEPENDENCY_OVERVIEW_ARTIFACT,
)
from unoplat_code_confluence_query_engine.services.temporal.temporal_worker_manager import (
    get_worker_manager,
)
from unoplat_code_confluence_query_engine.services.temporal.workflow_service import (
    TemporalWorkflowService,
)

if TYPE_CHECKING:
    from loguru import Logger
    from temporalio.client import Client

router = APIRouter(prefix="/v1", tags=["codebase-rules"])


class RepositoryWorkflowRunResponse(BaseModel):
    """Response returned when a repository Temporal workflow is launched."""

    repository_workflow_run_id: str
    trace_id: str


class RepositoryAgentRunCancelResponse(BaseModel):
    """Response returned when a repository agent workflow cancel is requested."""

    repository_workflow_run_id: str
    status: Literal["cancel_requested"]
    message: str


class RepositoryAgentMdPrRequest(BaseModel):
    """Request payload to manually create/update AGENTS.md PR."""

    owner_name: str = Field(..., min_length=1)
    repo_name: str = Field(..., min_length=1)
    repository_workflow_run_id: str = Field(..., min_length=1)

    model_config = ConfigDict(extra="forbid")


class RepositoryAgentMdPrResponse(BaseModel):
    """Response payload for manual AGENTS.md PR endpoint."""

    status: Literal["modified", "no_changes"]
    pr_url: str | None = None
    pr_number: int | None = None
    branch_name: str | None = None
    changed_files: list[str] = Field(default_factory=list)
    message: str


class RepositoryAgentMdPrStatusResponse(BaseModel):
    """Response payload for GET /repository-agent-md-pr status check."""

    exists: bool
    pr_metadata: RepositoryAgentMdPrResponse | None = None


TERMINAL_REPOSITORY_WORKFLOW_STATUSES: set[str] = {
    JobStatus.COMPLETED.value,
    JobStatus.FAILED.value,
    JobStatus.TIMED_OUT.value,
    JobStatus.ERROR.value,
    JobStatus.CANCELLED.value,
}

CANCELLABLE_REPOSITORY_WORKFLOW_OPERATIONS: set[RepositoryWorkflowOperation] = {
    RepositoryWorkflowOperation.AGENTS_GENERATION,
    RepositoryWorkflowOperation.AGENT_MD_UPDATE,
}

MANAGED_MARKDOWN_ARTIFACTS: tuple[str, ...] = (
    "AGENTS.md",
    DEPENDENCY_OVERVIEW_ARTIFACT,
    BUSINESS_DOMAIN_REFERENCES_ARTIFACT,
    APP_INTERFACES_ARTIFACT,
)


def _is_terminal_repository_workflow_status(status: str) -> bool:
    return status in TERMINAL_REPOSITORY_WORKFLOW_STATUSES


async def _cancel_temporal_workflow(
    *,
    temporal_client: Client,
    workflow_id: str,
) -> None:
    workflow_handle = temporal_client.get_workflow_handle(  # pyright: ignore[reportUnknownMemberType]
        workflow_id
    )
    await workflow_handle.cancel()


def _get_mapping_field(
    payload: Mapping[str, object],
    key: str,
) -> Mapping[str, object] | None:
    value = payload.get(key)
    if isinstance(value, Mapping):
        return cast(Mapping[str, object], value)
    return None


def _resolve_github_host(
    provider_key: ProviderKey,
    metadata: Mapping[str, object] | None,
) -> str:
    """Resolve GitHub API host, wrapping ValueError from shared helper as HTTPException."""
    try:
        return _resolve_github_host_shared(provider_key, metadata)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


def _get_codebase_file_rel_path(codebase_name: str, file_relative: str) -> str:
    """Compute repository-relative path for any file in a codebase."""
    clean = codebase_name.strip().strip("/")
    if clean in {"", "."}:
        return file_relative
    return f"{clean}/{file_relative}"


def _collect_changed_managed_markdown_files(codebase_root: Path) -> list[Path]:
    """Return existing managed markdown artifacts changed in the git working tree.

    The workflow now has direct artifact owners instead of section-updater run
    records. Publishing therefore discovers files from the fixed managed target
    set and lets git working-tree status decide which ones are candidates.
    """
    existing_targets = [
        artifact
        for artifact in MANAGED_MARKDOWN_ARTIFACTS
        if (codebase_root / artifact).is_file()
    ]
    if not existing_targets:
        return []

    try:
        status_result = subprocess.run(
            [
                "git",
                "-C",
                str(codebase_root),
                "status",
                "--porcelain",
                "--",
                *existing_targets,
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError) as status_error:
        logger.warning(
            "Unable to inspect git status for managed markdown in '{}': {}. "
            "Falling back to existing managed artifacts.",
            codebase_root,
            status_error,
        )
        return [codebase_root / artifact for artifact in existing_targets]

    if status_result.returncode != 0:
        logger.warning(
            "git status failed for managed markdown in '{}': {}. "
            "Falling back to existing managed artifacts.",
            codebase_root,
            status_result.stderr.strip(),
        )
        return [codebase_root / artifact for artifact in existing_targets]

    changed_artifacts = _parse_changed_artifacts_from_porcelain(
        status_result.stdout,
        set(existing_targets),
    )
    return [
        codebase_root / artifact
        for artifact in existing_targets
        if artifact in changed_artifacts
    ]


def _parse_changed_artifacts_from_porcelain(
    porcelain_output: str,
    expected_artifacts: set[str],
) -> set[str]:
    """Parse `git status --porcelain` output for known managed artifacts.

    Git porcelain output reports paths relative to the repository root, even when
    the status command is executed with ``git -C`` from a codebase subdirectory.
    Managed artifacts are direct children of the codebase root, so normalize each
    porcelain path to its filename before comparing against the expected artifact
    names and return those bare artifact names.
    """
    changed: set[str] = set()
    for raw_line in porcelain_output.splitlines():
        if len(raw_line) < 4:
            continue
        path_part = raw_line[3:].strip()
        if " -> " in path_part:
            path_part = path_part.rsplit(" -> ", 1)[1].strip()
        path_part = path_part.strip('"')
        artifact_name = Path(path_part).name
        if artifact_name in expected_artifacts:
            changed.add(artifact_name)
    return changed


def _decode_remote_content(encoded_content: str) -> str | None:
    normalized = encoded_content.replace("\n", "")
    try:
        decoded = b64decode(normalized)
        return decoded.decode("utf-8")
    except (ValueError, UnicodeDecodeError):
        return None


async def _persist_pr_metadata(
    owner_name: str,
    repo_name: str,
    repository_workflow_run_id: str,
    pr_metadata: PrMetadata,
) -> tuple[PrMetadata, bool]:
    """Persist PR metadata with row-level lock. Returns (metadata, already_existed).

    Uses SELECT ... FOR UPDATE to guard against concurrent publish requests.
    If pr_metadata is already non-null (another request won the race), returns
    the existing metadata with already_existed=True.
    """
    # Session 2 (short write transaction): acquire row lock only for the final
    # persistence step so we do not hold DB locks while performing network-bound
    # GitHub API calls.
    async with get_startup_session() as session:
        stmt = (
            select(RepositoryAgentMdSnapshot)
            .where(
                RepositoryAgentMdSnapshot.repository_owner_name == owner_name,
                RepositoryAgentMdSnapshot.repository_name == repo_name,
                RepositoryAgentMdSnapshot.repository_workflow_run_id
                == repository_workflow_run_id,
            )
            .with_for_update()
        )
        result = await session.execute(stmt)
        snapshot = result.scalar_one_or_none()
        if snapshot is None:
            # Defensive fallback: under normal workflow invariants the snapshot row
            # exists for this run and is not deleted during publish. If it is gone
            # (e.g. concurrent maintenance/deletion), treat as already handled to
            # preserve one-shot no-op behavior.
            return pr_metadata, True

        if snapshot.pr_metadata is not None:
            # Another request already persisted — return existing data
            existing = PrMetadata.model_validate(snapshot.pr_metadata)
            return existing, True

        snapshot.pr_metadata = pr_metadata.model_dump(mode="json")
        return pr_metadata, False


@router.get("/codebase-agent-rules")
async def start_repository_agent_run(
    request: Request,
    owner_name: str = Query(..., description="Repository owner name"),
    repo_name: str = Query(..., description="Repository name"),
    bound_logger: "Logger" = Depends(trace_dependency),
) -> RepositoryWorkflowRunResponse:
    """Start Temporal workflow with trace_id from API level.

    This endpoint:
    1. Generates trace_id from owner_name/repo_name via trace_dependency
    2. Fetches repository metadata from PostgreSQL
    3. Starts a Temporal RepositoryAgentWorkflow with trace_id
    4. Returns the workflow run ID for tracking

    The workflow state (RUNNING/COMPLETED/FAILED) is automatically tracked
    by Temporal interceptors and persisted to PostgreSQL.
    """
    # Get trace_id from request state (set by trace_dependency)
    trace_id: str = request.state.trace_id

    bound_logger.info(
        "[codebase_agent_rules] Starting workflow for {}/{} with trace_id={}",
        owner_name,
        repo_name,
        trace_id,
    )

    worker_manager = get_worker_manager()

    # Check provider/tool prerequisites first so errors are user-actionable.
    async with get_startup_session() as session:
        model_config = await session.get(AiModelConfig, 1)
        if not model_config:
            bound_logger.error("[codebase_agent_rules] AI model config not found")
            raise HTTPException(
                status_code=503,
                detail=(
                    "AI model config not found. Please configure a model first via "
                    "/v1/model-config endpoint."
                ),
            )

    # Check if Temporal worker is running after validating prerequisites.
    if not worker_manager.is_running:
        bound_logger.error("[codebase_agent_rules] Temporal worker not running")
        raise HTTPException(
            status_code=503,
            detail=(
                "Agent runtime is unavailable. Please verify model/tool configuration "
                "and retry."
            ),
        )

    # Fetch repository metadata
    try:
        ruleset_metadata = await fetch_repository_metadata(
            owner_name,
            repo_name,
        )
    except HTTPException:
        raise
    except Exception as metadata_error:
        bound_logger.error(
            "[codebase_agent_rules] Failed to fetch repository metadata for {}/{}: {}",
            owner_name,
            repo_name,
            metadata_error,
        )
        raise HTTPException(
            status_code=500, detail="Failed to fetch repository metadata"
        ) from metadata_error

    bound_logger.info(
        "[codebase_agent_rules] Fetched metadata: {} codebases",
        len(ruleset_metadata.codebase_metadata),
    )

    # Start the Temporal workflow
    try:
        workflow_service = TemporalWorkflowService(worker_manager.client)
        repository_workflow_run_id = await workflow_service.start_workflow(
            ruleset_metadata=ruleset_metadata,
            trace_id=trace_id,
        )
    except Exception as start_error:
        bound_logger.error(
            "[codebase_agent_rules] Failed to start workflow for {}/{}: {}",
            owner_name,
            repo_name,
            start_error,
        )
        raise HTTPException(
            status_code=500, detail="Failed to start Temporal workflow"
        ) from start_error

    bound_logger.info(
        "[codebase_agent_rules] Started workflow: run_id={}, trace_id={}",
        repository_workflow_run_id,
        trace_id,
    )

    return RepositoryWorkflowRunResponse(
        repository_workflow_run_id=repository_workflow_run_id,
        trace_id=trace_id,
    )


@router.post("/repository-agent-run/cancel")
async def cancel_repository_agent_run(
    owner_name: str = Query(..., description="Repository owner name"),
    repo_name: str = Query(..., description="Repository name"),
    repository_workflow_run_id: str = Query(
        ..., description="Repository workflow run ID"
    ),
    bound_logger: "Logger" = Depends(trace_dependency),
) -> RepositoryAgentRunCancelResponse:
    """Cancel an in-flight repository agent workflow.

    This endpoint supports cancellation only for agent workflows
    (AGENTS_GENERATION, AGENT_MD_UPDATE). INGESTION workflows are explicitly
    non-cancellable from this API.
    """
    worker_manager = get_worker_manager()

    if not worker_manager.is_running:
        bound_logger.error(
            "[codebase_agent_rules] Temporal worker not running for cancel request"
        )
        raise HTTPException(
            status_code=503,
            detail=(
                "Agent runtime is unavailable. Please verify model/tool configuration "
                "and retry."
            ),
        )

    async with get_startup_session() as session:
        workflow_run = await session.get(
            RepositoryWorkflowRun,
            (repo_name, owner_name, repository_workflow_run_id),
        )

        if workflow_run is None:
            raise HTTPException(
                status_code=404,
                detail=(
                    "Repository workflow run not found for "
                    f"{owner_name}/{repo_name} run_id={repository_workflow_run_id}"
                ),
            )

        if workflow_run.operation not in CANCELLABLE_REPOSITORY_WORKFLOW_OPERATIONS:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Cancellation is only supported for AGENTS_GENERATION and "
                    "AGENT_MD_UPDATE workflows"
                ),
            )

        if _is_terminal_repository_workflow_status(workflow_run.status):
            raise HTTPException(
                status_code=409,
                detail=(
                    f"Workflow run is already in terminal state ({workflow_run.status})"
                ),
            )

        workflow_id = workflow_run.repository_workflow_id

    try:
        await _cancel_temporal_workflow(
            temporal_client=worker_manager.client,
            workflow_id=workflow_id,
        )
    except RPCError as rpc_error:
        if rpc_error.status == RPCStatusCode.NOT_FOUND:
            raise HTTPException(
                status_code=404,
                detail=(
                    "Temporal workflow not found for "
                    f"workflow_id={workflow_id}; run may have already finished"
                ),
            ) from rpc_error

        if rpc_error.status in (
            RPCStatusCode.FAILED_PRECONDITION,
            RPCStatusCode.ABORTED,
        ):
            raise HTTPException(
                status_code=409,
                detail=(
                    "Workflow run is no longer cancellable because it is already "
                    "finishing or finished"
                ),
            ) from rpc_error

        bound_logger.error(
            "[codebase_agent_rules] Cancel failed for {}/{} run_id={} workflow_id={} status={} message={}",
            owner_name,
            repo_name,
            repository_workflow_run_id,
            workflow_id,
            rpc_error.status,
            rpc_error.message,
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to cancel repository agent workflow",
        ) from rpc_error
    except Exception as cancel_error:
        bound_logger.error(
            "[codebase_agent_rules] Unexpected cancel error for {}/{} run_id={} workflow_id={}: {}",
            owner_name,
            repo_name,
            repository_workflow_run_id,
            workflow_id,
            cancel_error,
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to cancel repository agent workflow",
        ) from cancel_error

    bound_logger.info(
        "[codebase_agent_rules] Cancel requested for {}/{} run_id={} workflow_id={}",
        owner_name,
        repo_name,
        repository_workflow_run_id,
        workflow_id,
    )
    return RepositoryAgentRunCancelResponse(
        repository_workflow_run_id=repository_workflow_run_id,
        status="cancel_requested",
        message=(
            "Cancel requested successfully. The workflow may take a short time "
            "to reach a terminal state."
        ),
    )


@router.get("/repository-agent-snapshot")
async def get_repository_agent_snapshot(
    owner_name: str = Query(..., description="Repository owner name"),
    repo_name: str = Query(..., description="Repository name"),
    repository_workflow_run_id: str = Query(
        ..., description="Repository workflow run ID to query"
    ),
) -> dict[str, object]:
    """Retrieve the agent snapshot output for a specific workflow run.

    Note: Workflow status is tracked by Temporal via RepositoryWorkflowRun,
    not in the snapshot. Use the Temporal API or RepositoryWorkflowRun table
    to query workflow status.

    Args:
        owner_name: Repository owner name
        repo_name: Repository name
        repository_workflow_run_id: The specific workflow run ID to query

    Returns:
        Dictionary with agent_md_output for the specified workflow run
    """
    try:
        async with get_startup_session() as session:
            stmt = select(RepositoryAgentMdSnapshot).where(
                RepositoryAgentMdSnapshot.repository_owner_name == owner_name,
                RepositoryAgentMdSnapshot.repository_name == repo_name,
                RepositoryAgentMdSnapshot.repository_workflow_run_id
                == repository_workflow_run_id,
            )
            result = await session.execute(stmt)
            snapshot = result.scalar_one_or_none()

            if snapshot is None:
                raise HTTPException(
                    status_code=404,
                    detail=(
                        f"No agent snapshot found for repository {owner_name}/{repo_name} "
                        f"with run_id={repository_workflow_run_id}"
                    ),
                )

            logger.info(
                "Retrieved agent snapshot for repository {}/{} run_id={}",
                owner_name,
                repo_name,
                repository_workflow_run_id,
            )
            return {
                "agent_md_output": snapshot.agent_md_output,
            }

    except HTTPException:
        raise
    except Exception as error:
        logger.error(
            "Error retrieving agent snapshot for {}/{} run_id={}: {}",
            owner_name,
            repo_name,
            repository_workflow_run_id,
            error,
        )
        raise HTTPException(status_code=500, detail="Internal server error") from error


@router.post("/repository-agent-md-pr")
async def create_repository_agent_md_pr(
    payload: RepositoryAgentMdPrRequest,
) -> RepositoryAgentMdPrResponse:
    """Publish a PR for codebase-local AGENTS.md outputs (one-shot per run).

    One-shot semantics: first successful publish for a run returns ``modified``.
    ALL subsequent calls for the same run return ``no_changes``.
    """
    owner_name = payload.owner_name
    repo_name = payload.repo_name
    repository_workflow_run_id = payload.repository_workflow_run_id

    # ── Session 1: read snapshot + repository + PAT credentials ──────────
    # Keep this read transaction separate from Session 2 persistence:
    # GitHub operations below are network-bound and can take time; we avoid
    # holding DB transaction/locks across those remote calls.
    async with get_startup_session() as session:
        repository = await session.get(Repository, (repo_name, owner_name))
        if repository is None:
            raise HTTPException(
                status_code=404,
                detail=f"Repository not found: {owner_name}/{repo_name}",
            )

        snapshot_stmt = select(RepositoryAgentMdSnapshot).where(
            RepositoryAgentMdSnapshot.repository_owner_name == owner_name,
            RepositoryAgentMdSnapshot.repository_name == repo_name,
            RepositoryAgentMdSnapshot.repository_workflow_run_id
            == repository_workflow_run_id,
        )
        snapshot_result = await session.execute(snapshot_stmt)
        snapshot = snapshot_result.scalar_one_or_none()
        if snapshot is None:
            raise HTTPException(
                status_code=404,
                detail=(
                    f"No snapshot found for {owner_name}/{repo_name} "
                    f"run_id={repository_workflow_run_id}"
                ),
            )

        # ONE-SHOT GUARD: if pr_metadata already persisted → return immediately
        if snapshot.pr_metadata is not None:
            existing = PrMetadata.model_validate(snapshot.pr_metadata)
            return RepositoryAgentMdPrResponse(
                status="no_changes",
                pr_url=existing.pr_url,
                pr_number=existing.pr_number,
                branch_name=existing.branch_name,
                changed_files=[],
                message="PR already published for this run",
            )

        provider_key = repository.repository_provider
        try:
            repository_pat = await CredentialsService.get_repository_pat(
                session, provider_key
            )
        except ValueError as decrypt_error:
            raise HTTPException(
                status_code=400,
                detail=str(decrypt_error),
            ) from decrypt_error
        if not repository_pat:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Repository PAT not configured for provider '{provider_key.value}'. "
                    "Please configure repository credentials first."
                ),
            )

        credential_metadata = (
            await CredentialsService.get_repository_credential_metadata(
                session,
                provider_key,
            )
        )

    # ── Collect files to publish ─────────────────────────────────────────
    snapshot_payload = cast(Mapping[str, object], snapshot.agent_md_output)

    codebases_payload = _get_mapping_field(snapshot_payload, "codebases")
    if not codebases_payload:
        no_codebases_meta = PrMetadata(
            status="no_changes",
            message="No codebase outputs found in snapshot",
        )
        persisted, already_existed = await _persist_pr_metadata(
            owner_name, repo_name, repository_workflow_run_id, no_codebases_meta
        )
        return _build_pr_response(persisted, already_existed)

    ruleset_metadata = await fetch_repository_metadata(owner_name, repo_name)
    codebase_path_map = {
        metadata.codebase_name: metadata.codebase_path
        for metadata in ruleset_metadata.codebase_metadata
    }

    files_to_publish: list[tuple[str, str]] = []
    seen_rel_paths: set[str] = set()

    for codebase_name in codebases_payload.keys():
        codebase_root = codebase_path_map.get(codebase_name)
        if not codebase_root:
            logger.warning(
                "Skipping codebase '{}' for PR: path not found", codebase_name
            )
            continue

        codebase_root_path = Path(codebase_root)
        changed_managed_files = _collect_changed_managed_markdown_files(
            codebase_root_path
        )
        if not changed_managed_files:
            logger.info(
                "Skipping codebase '{}': no managed markdown files changed",
                codebase_name,
            )
            continue

        for local_path in changed_managed_files:
            file_relative = str(local_path.relative_to(codebase_root_path))

            try:
                local_content = local_path.read_text(encoding="utf-8")
            except OSError as read_error:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to read managed artifact at {local_path}: {read_error}",
                ) from read_error

            rel_path = _get_codebase_file_rel_path(codebase_name, file_relative)

            # Deduplicate defensively across codebase payload entries.
            if rel_path in seen_rel_paths:
                continue
            seen_rel_paths.add(rel_path)

            files_to_publish.append((rel_path, local_content))

    if not files_to_publish:
        no_files_meta = PrMetadata(
            status="no_changes",
            message="No managed artifact files available to publish",
        )
        persisted, already_existed = await _persist_pr_metadata(
            owner_name, repo_name, repository_workflow_run_id, no_files_meta
        )
        return _build_pr_response(persisted, already_existed)

    # ── GitHub operations ────────────────────────────────────────────────
    github_host = _resolve_github_host(provider_key, credential_metadata)
    api = GhApi(
        owner=owner_name,
        repo=repo_name,
        token=repository_pat,
        gh_host=github_host,
    )

    branch_name = f"agents-md/{repository_workflow_run_id[:12]}"

    try:
        # Resolve default branch + head SHA via shared resolver
        try:
            git_ref = resolve_repository_git_ref(api, owner_name, repo_name)
        except ValueError as ref_error:
            raise HTTPException(
                status_code=502,
                detail=f"Failed to resolve repository git ref: {ref_error}",
            ) from ref_error
        default_branch = git_ref.default_branch
        base_sha = git_ref.head_commit_sha

        # Get or create feature branch
        try:
            api.git.get_ref(  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue]
                owner=owner_name,
                repo=repo_name,
                ref=f"heads/{branch_name}",
            )
        except Exception as get_ref_error:
            if is_http_not_found(get_ref_error):
                api.git.create_ref(  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue]
                    owner=owner_name,
                    repo=repo_name,
                    ref=f"refs/heads/{branch_name}",
                    sha=base_sha,
                )
            else:
                raise

        # Check for existing open PR BEFORE pushing files (zero mutations if PR exists)
        pulls = api.pulls.list(  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue, reportUnknownVariableType]
            owner=owner_name,
            repo=repo_name,
            state="open",
            head=f"{owner_name}:{branch_name}",
            base=default_branch,
            per_page=1,
            page=1,
        )
        pulls_list: list[object] = list(pulls) if isinstance(pulls, list) else []  # pyright: ignore[reportUnknownArgumentType]
        if pulls_list:
            first_pull = pulls_list[0]
            existing_pr_url: str | None = getattr(first_pull, "html_url", None)  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
            existing_pr_number: int | None = getattr(first_pull, "number", None)  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]

            if isinstance(existing_pr_url, str) and existing_pr_url:
                existing_pr_meta = PrMetadata(
                    status="no_changes",
                    pr_url=existing_pr_url,
                    pr_number=existing_pr_number if isinstance(existing_pr_number, int) else None,
                    branch_name=branch_name,
                    message="PR already exists for this branch",
                )
                persisted, already_existed = await _persist_pr_metadata(
                    owner_name,
                    repo_name,
                    repository_workflow_run_id,
                    existing_pr_meta,
                )
                return _build_pr_response(persisted, already_existed)

        # Push files (compare with remote, skip unchanged)
        changed_files: list[str] = []
        for rel_path, local_content in files_to_publish:
            existing_sha: str | None = None
            existing_content: str | None = None
            try:
                remote_content_response = api.repos.get_content(  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue, reportUnknownVariableType]
                    owner=owner_name,
                    repo=repo_name,
                    path=rel_path,
                    ref=branch_name,
                )
                remote_encoded: str = getattr(remote_content_response, "content", "") or ""  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
                remote_encoding: str = getattr(remote_content_response, "encoding", "") or ""  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
                existing_sha = getattr(remote_content_response, "sha", None)  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
                if not isinstance(existing_sha, str):
                    existing_sha = None
                if remote_encoding == "base64" and remote_encoded:
                    existing_content = _decode_remote_content(remote_encoded)
            except Exception as get_content_error:
                if is_http_not_found(get_content_error):
                    existing_sha = None
                    existing_content = None
                else:
                    raise

            if existing_content == local_content:
                continue

            content_b64 = b64encode(local_content.encode("utf-8")).decode("ascii")
            update_kwargs: dict[str, object] = {
                "owner": owner_name,
                "repo": repo_name,
                "path": rel_path,
                "message": f"Update {rel_path} from run {repository_workflow_run_id}",
                "content": content_b64,
                "branch": branch_name,
            }
            if existing_sha is not None:
                update_kwargs["sha"] = existing_sha

            api.repos.create_or_update_file_contents(  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue]
                **update_kwargs,
            )
            changed_files.append(rel_path)

        if not changed_files:
            no_diff_meta = PrMetadata(
                status="no_changes",
                branch_name=branch_name,
                message="No artifact changes detected against target branch",
            )
            persisted, already_existed = await _persist_pr_metadata(
                owner_name, repo_name, repository_workflow_run_id, no_diff_meta
            )
            return _build_pr_response(persisted, already_existed)

        # Create new PR
        pr_title = f"Update codebase artifacts (run {repository_workflow_run_id[:8]})"
        pr_body_lines = [
            "## Summary",
            f"- Codebase artifact update for run `{repository_workflow_run_id}`",
            f"- Updated files: {len(changed_files)}",
            "",
            "## Changed Files",
            *[f"- `{path}`" for path in changed_files],
        ]
        created_pr = api.pulls.create(  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue, reportUnknownVariableType]
            owner=owner_name,
            repo=repo_name,
            title=pr_title,
            head=branch_name,
            base=default_branch,
            body="\n".join(pr_body_lines),
        )
        created_pr_url: str | None = getattr(created_pr, "html_url", None)  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
        if not isinstance(created_pr_url, str) or not created_pr_url:
            raise HTTPException(
                status_code=502,
                detail="GitHub API response missing 'html_url' in pulls.create",
            )
        created_pr_number: int | None = getattr(created_pr, "number", None)  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
        if not isinstance(created_pr_number, int):
            created_pr_number = None

        # Persist modified result
        modified_meta = PrMetadata(
            status="modified",
            pr_url=created_pr_url,
            pr_number=created_pr_number,
            branch_name=branch_name,
            changed_files=changed_files,
            message="Created pull request for codebase artifact changes",
        )
        persisted, already_existed = await _persist_pr_metadata(
            owner_name, repo_name, repository_workflow_run_id, modified_meta
        )
        return _build_pr_response(persisted, already_existed)
    except HTTPException:
        raise
    except Exception as github_error:
        gh_status_code = extract_http_error_status(github_error)
        if gh_status_code in {401, 403}:
            raise HTTPException(
                status_code=gh_status_code,
                detail=f"GitHub permission/auth error: {github_error}",
            ) from github_error
        raise HTTPException(
            status_code=502,
            detail=f"GitHub API error while creating PR: {github_error}",
        ) from github_error


def _build_pr_response(
    persisted: PrMetadata,
    already_existed: bool,
) -> RepositoryAgentMdPrResponse:
    """Build API response from persist result, enforcing one-shot semantics."""
    if already_existed:
        return RepositoryAgentMdPrResponse(
            status="no_changes",
            pr_url=persisted.pr_url,
            pr_number=persisted.pr_number,
            branch_name=persisted.branch_name,
            changed_files=[],
            message="PR already published for this run",
        )
    return RepositoryAgentMdPrResponse(
        status=persisted.status,
        pr_url=persisted.pr_url,
        pr_number=persisted.pr_number,
        branch_name=persisted.branch_name,
        changed_files=list(persisted.changed_files),
        message=persisted.message,
    )


@router.get("/repository-agent-md-pr")
async def get_repository_agent_md_pr_status(
    owner_name: str = Query(..., description="Repository owner name"),
    repo_name: str = Query(..., description="Repository name"),
    repository_workflow_run_id: str = Query(
        ..., description="Repository workflow run ID"
    ),
) -> RepositoryAgentMdPrStatusResponse:
    """Return persisted PR metadata for a given workflow run, if any."""
    async with get_startup_session() as session:
        stmt = select(RepositoryAgentMdSnapshot.pr_metadata).where(
            RepositoryAgentMdSnapshot.repository_owner_name == owner_name,
            RepositoryAgentMdSnapshot.repository_name == repo_name,
            RepositoryAgentMdSnapshot.repository_workflow_run_id
            == repository_workflow_run_id,
        )
        result = await session.execute(stmt)
        raw = result.scalar_one_or_none()

    if raw is None:
        return RepositoryAgentMdPrStatusResponse(exists=False)

    validated = PrMetadata.model_validate(raw)
    return RepositoryAgentMdPrStatusResponse(
        exists=True,
        pr_metadata=RepositoryAgentMdPrResponse(
            status=validated.status,
            pr_url=validated.pr_url,
            pr_number=validated.pr_number,
            branch_name=validated.branch_name,
            changed_files=list(validated.changed_files),
            message=validated.message,
        ),
    )
