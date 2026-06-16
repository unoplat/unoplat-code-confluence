"""API endpoint for Temporal-based agent execution.

This endpoint triggers Temporal workflows with trace_id from the API level,
providing distributed tracing and workflow state tracking via interceptors.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from loguru import logger
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import and_, select
from temporalio.service import RPCError, RPCStatusCode
from unoplat_code_confluence_commons.pr_metadata_model import PrMetadata
from unoplat_code_confluence_commons.repo_models import (
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
from unoplat_code_confluence_query_engine.services.github.agent_md_pr_service import (
    AgentMdPrAuthError,
    AgentMdPrConfigurationError,
    AgentMdPrGithubError,
    AgentMdPrInternalError,
    AgentMdPrNotFoundError,
    publish_agent_md_pr,
)
from unoplat_code_confluence_query_engine.services.repository.idempotency_service import (
    get_active_agent_workflow_run,
)
from unoplat_code_confluence_query_engine.services.repository.repository_metadata_service import (
    fetch_repository_metadata,
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
        active_run = await get_active_agent_workflow_run(
            session=session,
            repository_name=repo_name,
            repository_owner_name=owner_name,
        )
        if active_run:
            bound_logger.info(
                "[codebase_agent_rules] Active agent workflow already exists for {}/{}: run_id={}",
                owner_name,
                repo_name,
                active_run.repository_workflow_run_id,
            )
            return RepositoryWorkflowRunResponse(
                repository_workflow_run_id=active_run.repository_workflow_run_id,
                trace_id=trace_id,
            )

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
    repository_workflow_run_id: str | None = Query(
        None,
        description=(
            "Repository workflow run ID to query. If omitted, returns the latest "
            "COMPLETED agent snapshot for the repository."
        ),
    ),
) -> dict[str, object]:
    """Retrieve an agent snapshot output for a repository workflow run.

    When ``repository_workflow_run_id`` is provided, the endpoint returns that
    exact snapshot. When it is omitted, the endpoint returns the latest completed
    agent snapshot for the repository according to ``RepositoryWorkflowRun``.

    Args:
        owner_name: Repository owner name
        repo_name: Repository name
        repository_workflow_run_id: Optional specific workflow run ID to query

    Returns:
        Dictionary with the resolved repository_workflow_run_id and agent_md_output.
    """
    try:
        async with get_startup_session() as session:
            if repository_workflow_run_id is not None:
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
            else:
                stmt = (
                    select(RepositoryAgentMdSnapshot)
                    .join(
                        RepositoryWorkflowRun,
                        and_(
                            RepositoryWorkflowRun.repository_owner_name
                            == RepositoryAgentMdSnapshot.repository_owner_name,
                            RepositoryWorkflowRun.repository_name
                            == RepositoryAgentMdSnapshot.repository_name,
                            RepositoryWorkflowRun.repository_workflow_run_id
                            == RepositoryAgentMdSnapshot.repository_workflow_run_id,
                        ),
                    )
                    .where(
                        RepositoryAgentMdSnapshot.repository_owner_name == owner_name,
                        RepositoryAgentMdSnapshot.repository_name == repo_name,
                        RepositoryWorkflowRun.status == JobStatus.COMPLETED.value,
                        RepositoryWorkflowRun.operation.in_(
                            (
                                RepositoryWorkflowOperation.AGENTS_GENERATION,
                                RepositoryWorkflowOperation.AGENT_MD_UPDATE,
                            )
                        ),
                    )
                    .order_by(
                        RepositoryWorkflowRun.completed_at.desc().nulls_last(),
                        RepositoryWorkflowRun.started_at.desc(),
                        RepositoryWorkflowRun.repository_workflow_run_id.desc(),
                    )
                    .limit(1)
                )
                result = await session.execute(stmt)
                snapshot = result.scalar_one_or_none()

                if snapshot is None:
                    raise HTTPException(
                        status_code=404,
                        detail=(
                            "No completed agent snapshot found for repository "
                            f"{owner_name}/{repo_name}"
                        ),
                    )

            logger.info(
                "Retrieved agent snapshot for repository {}/{} run_id={}",
                owner_name,
                repo_name,
                snapshot.repository_workflow_run_id,
            )
            return {
                "repository_workflow_run_id": snapshot.repository_workflow_run_id,
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


# TODO(not urgent): concurrent-publish race. This manual endpoint and the
# in-workflow auto-publish activity both call publish_agent_md_pr with the same
# repository_workflow_run_id. The one-shot guard (pr_metadata IS NULL check) and
# the _persist_pr_metadata arbitration both sit AFTER the GitHub side effect, so
# two callers can pass the guard, both run publish_agent_md_artifacts on the same
# agents-md/<run_id> branch, and the loser surfaces a false 502 from pulls.create
# (422 "PR already exists") even though a valid PR was created. The frontend
# "Publish PR" button gates on an eventually-consistent GET status (30s stale),
# so it does not close the window. Fix server-side: serialize the publish per
# run_id (e.g. pg advisory lock on the run_id, or row lock before the GitHub
# call), not in the UI. Low severity: GitHub head->base uniqueness prevents a
# duplicate PR; only harm is a misleading error on the losing caller.
@router.post("/repository-agent-md-pr")
async def create_repository_agent_md_pr(
    payload: RepositoryAgentMdPrRequest,
) -> RepositoryAgentMdPrResponse:
    """Publish a PR for codebase-local AGENTS.md outputs (one-shot per run).

    One-shot semantics: first successful publish for a run returns ``modified``.
    ALL subsequent calls for the same run return ``no_changes``.

    Manual fallback/retry path for the automatic in-workflow publish.
    """
    try:
        persisted, already_existed = await publish_agent_md_pr(
            owner_name=payload.owner_name,
            repo_name=payload.repo_name,
            repository_workflow_run_id=payload.repository_workflow_run_id,
        )
    except AgentMdPrNotFoundError as not_found_error:
        raise HTTPException(
            status_code=404, detail=str(not_found_error)
        ) from not_found_error
    except AgentMdPrConfigurationError as config_error:
        raise HTTPException(status_code=400, detail=str(config_error)) from config_error
    except AgentMdPrAuthError as auth_error:
        raise HTTPException(
            status_code=auth_error.status_code, detail=str(auth_error)
        ) from auth_error
    except AgentMdPrInternalError as internal_error:
        raise HTTPException(
            status_code=500, detail=str(internal_error)
        ) from internal_error
    except AgentMdPrGithubError as github_error:
        raise HTTPException(status_code=502, detail=str(github_error)) from github_error
    return _build_pr_response(persisted, already_existed)


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
