from fastapi import APIRouter, HTTPException, Query, Request
from loguru import logger
from pydantic import BaseModel
from sqlalchemy import select
from unoplat_code_confluence_commons.repo_models import RepositoryAgentMdSnapshot

from unoplat_code_confluence_query_engine.db.postgres.db import get_session
from unoplat_code_confluence_query_engine.db.repository_metadata_service import (
    fetch_repository_metadata,
)
from unoplat_code_confluence_query_engine.services.agent_execution_service import (
    AgentExecutionService,
)

router = APIRouter(prefix="/v1", tags=["codebase-rules"])


class RepositoryWorkflowRunResponse(BaseModel):
    """Response returned when a repository workflow is launched."""

    repository_workflow_run_id: str


@router.get("/codebase-agent-rules")
async def start_repository_agent_run(
    request: Request,
    owner_name: str = Query(..., description="Repository owner name"),
    repo_name: str = Query(..., description="Repository name"),
) -> RepositoryWorkflowRunResponse:
    """Kick off the repository workflow and return its run identifier."""

    try:
        ruleset_metadata = await fetch_repository_metadata(
            owner_name,
            repo_name,
            request.app.state.neo4j_manager,
        )
    except HTTPException:
        raise
    except Exception as metadata_error:  # noqa: BLE001
        logger.error(
            "Failed to fetch repository metadata for {}/{}: {}",
            owner_name,
            repo_name,
            metadata_error,
        )
        raise HTTPException(
            status_code=500, detail="Failed to fetch repository metadata"
        )

    execution_service = AgentExecutionService()

    try:
        workflow_run_id = await execution_service.start_repository_workflow(
            ruleset_metadata=ruleset_metadata,
            request=request,
        )
    except Exception as start_error:  # noqa: BLE001
        logger.error(
            "Failed to start repository workflow for {}/{}: {}",
            owner_name,
            repo_name,
            start_error,
        )
        raise HTTPException(
            status_code=500, detail="Failed to start repository workflow"
        )

    logger.info(
        "Started repository workflow {} for {}/{}",
        workflow_run_id,
        owner_name,
        repo_name,
    )

    return RepositoryWorkflowRunResponse(repository_workflow_run_id=workflow_run_id)


@router.get("/repository-agent-snapshot")
async def get_repository_agent_snapshot(
    owner_name: str = Query(..., description="Repository owner name"),
    repo_name: str = Query(..., description="Repository name"),
) -> dict[str, object]:
    """Retrieve the latest agent snapshot (status plus aggregated payload)."""

    try:
        async with get_session() as session:
            stmt = select(RepositoryAgentMdSnapshot).where(
                RepositoryAgentMdSnapshot.repository_owner_name == owner_name,
                RepositoryAgentMdSnapshot.repository_name == repo_name,
            )
            result = await session.execute(stmt)
            snapshot = result.scalar_one_or_none()

            if snapshot is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"No agent snapshot found for repository {owner_name}/{repo_name}",
                )

            logger.info(
                "Retrieved agent snapshot for repository {}/{}",
                owner_name,
                repo_name,
            )
            return {
                "status": snapshot.status.value,
                "agent_md_output": snapshot.agent_md_output,
            }

    except HTTPException:
        raise
    except Exception as error:  # noqa: BLE001
        logger.error(
            "Error retrieving agent snapshot for {}/{}: {}",
            owner_name,
            repo_name,
            error,
        )
        raise HTTPException(status_code=500, detail="Internal server error")
