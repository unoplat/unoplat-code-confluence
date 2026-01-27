"""API endpoint for Temporal-based agent execution.

This endpoint triggers Temporal workflows with trace_id from the API level,
providing distributed tracing and workflow state tracking via interceptors.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from loguru import logger
from pydantic import BaseModel
from sqlalchemy import select
from unoplat_code_confluence_commons.credential_enums import ProviderKey
from unoplat_code_confluence_commons.repo_models import RepositoryAgentMdSnapshot

from unoplat_code_confluence_query_engine.api.deps import trace_dependency
from unoplat_code_confluence_query_engine.db.postgres.db import get_startup_session
from unoplat_code_confluence_query_engine.services.config.credentials_service import (
    CredentialsService,
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

router = APIRouter(prefix="/v1", tags=["codebase-rules"])


class RepositoryWorkflowRunResponse(BaseModel):
    """Response returned when a repository Temporal workflow is launched."""

    repository_workflow_run_id: str
    trace_id: str


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

    # Check if Temporal worker is running
    worker_manager = get_worker_manager()
    if not worker_manager.is_running:
        bound_logger.error("[codebase_agent_rules] Temporal worker not running")
        raise HTTPException(
            status_code=503,
            detail="Temporal worker is not running. Check server configuration.",
        )

    # Check if Exa tool is configured (required for agent workflows)
    async with get_startup_session() as session:
        exa_configured = await CredentialsService.tool_credential_exists(
            session, ProviderKey.EXA
        )
        if not exa_configured:
            bound_logger.error("[codebase_agent_rules] Exa tool not configured")
            raise HTTPException(
                status_code=503,
                detail=(
                    "Exa MCP tool is not configured. Please configure the Exa API key "
                    "via /v1/tool-config/exa endpoint first."
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
