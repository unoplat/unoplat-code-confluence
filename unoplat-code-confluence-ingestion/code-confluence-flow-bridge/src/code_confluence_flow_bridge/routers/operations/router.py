"""Cross-repo operational query endpoints (workflow jobs, ingested repos)."""

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from unoplat_code_confluence_commons.base_models import (
    Repository,
    RepositoryWorkflowRun,
)
from unoplat_code_confluence_commons.workflow_models import JobStatus

from src.code_confluence_flow_bridge.models.github.github_repo import (
    IngestedRepositoriesListResponse,
    IngestedRepositoryResponse,
    ParentWorkflowJobListResponse,
    ParentWorkflowJobResponse,
)
from src.code_confluence_flow_bridge.processor.db.postgres.db import get_session
from src.code_confluence_flow_bridge.utility.workflow_helpers import (
    is_parent_workflow_cancellable,
)

router = APIRouter(prefix="", tags=["Operations"])


# ---------------------------------------------------------------------------
# GET /parent-workflow-jobs
# ---------------------------------------------------------------------------


@router.get(
    "/parent-workflow-jobs",
    response_model=ParentWorkflowJobListResponse,
    description="Get all parent workflow jobs data without pagination",
)
async def get_parent_workflow_jobs(
    session: AsyncSession = Depends(get_session),
) -> ParentWorkflowJobListResponse:
    """Get all parent workflow jobs data without pagination.

    Returns job information for all parent workflows (RepositoryWorkflowRun).
    Includes repository_name, repository_owner_name, repository_workflow_run_id, operation, status, started_at, completed_at.
    """
    try:
        # Query to get all parent workflow jobs (RepositoryWorkflowRun records)
        query = select(RepositoryWorkflowRun)
        result = await session.execute(query)
        workflow_runs = result.scalars().all()

        # Transform the database records to the response model format
        jobs = [
            ParentWorkflowJobResponse(
                repository_name=run.repository_name,
                repository_owner_name=run.repository_owner_name,
                repository_workflow_run_id=run.repository_workflow_run_id,
                operation=run.operation,
                status=JobStatus(run.status),
                started_at=run.started_at,
                completed_at=run.completed_at,
                feedback_issue_url=run.feedback_issue_url,
                is_cancellable=is_parent_workflow_cancellable(
                    run.operation,
                    run.status,
                ),
            )
            for run in workflow_runs
        ]

        return ParentWorkflowJobListResponse(jobs=jobs)
    except Exception as e:
        logger.error("Error retrieving parent workflow jobs: {}", str(e))
        raise HTTPException(
            status_code=500,
            detail="Error retrieving parent workflow jobs: {}".format(str(e)),
        )


# ---------------------------------------------------------------------------
# GET /get/ingestedRepositories
# ---------------------------------------------------------------------------


@router.get(
    "/get/ingestedRepositories",
    response_model=IngestedRepositoriesListResponse,
    description="Get all ingested repositories without pagination",
)
async def get_ingested_repositories(
    session: AsyncSession = Depends(get_session),
) -> IngestedRepositoriesListResponse:
    """Get all ingested repositories without pagination.

    Returns basic information for all repositories in the database.
    Includes repository_name and repository_owner_name only.
    """
    try:
        # Query to get all repositories
        query = select(Repository)
        result = await session.execute(query)
        repositories = result.scalars().all()

        # Transform the database records to the response model format
        repo_list = [
            IngestedRepositoryResponse(
                repository_name=repo.repository_name,
                repository_owner_name=repo.repository_owner_name,
                provider_key=repo.repository_provider,
            )
            for repo in repositories
        ]

        return IngestedRepositoriesListResponse(repositories=repo_list)
    except Exception as e:
        logger.error("Error retrieving ingested repositories: {}", str(e))
        raise HTTPException(
            status_code=500,
            detail="Error retrieving ingested repositories: {}".format(str(e)),
        )
