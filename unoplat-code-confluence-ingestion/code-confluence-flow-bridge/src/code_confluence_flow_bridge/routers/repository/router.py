"""Repository-scoped API endpoints (status, data, metadata, delete, refresh)."""

import asyncio
from typing import Any, Dict, Optional, cast

from fastapi import APIRouter, Depends, HTTPException, Query
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import QueryableAttribute, selectinload
from sqlmodel import select
from temporalio.client import Client, WorkflowHandle
from unoplat_code_confluence_commons.base_models import (
    CodebaseWorkflowRun,
    Repository,
    RepositoryWorkflowRun,
)
from unoplat_code_confluence_commons.configuration_models import CodebaseConfig
from unoplat_code_confluence_commons.credential_enums import (
    CredentialNamespace,
    ProviderKey,
)
from unoplat_code_confluence_commons.relational_models import (
    UnoplatCodeConfluenceGitRepository,
)
from unoplat_code_confluence_commons.workflow_models import ErrorReport, JobStatus

from src.code_confluence_flow_bridge.logging.trace_utils import trace_id_var
from src.code_confluence_flow_bridge.models.code_confluence_parsing_models.unoplat_git_repository import (
    UnoplatGitRepository,
)
from src.code_confluence_flow_bridge.models.github.github_repo import (
    CodebaseMetadataListResponse,
    CodebaseMetadataResponse,
    GitHubRepoResponseConfiguration,
    GithubRepoStatus,
    IngestedRepositoryResponse,
    IssueTracking,
    RefreshRepositoryResponse,
    RepositoryRefreshRequest,
    RepositoryRequestConfiguration,
)
from src.code_confluence_flow_bridge.processor.db.postgres.db import get_session
from src.code_confluence_flow_bridge.processor.repo_workflow import RepoWorkflow
from src.code_confluence_flow_bridge.routers.repository.mappers import (
    build_programming_language_metadata,
    build_repository_status_hierarchy,
)
from src.code_confluence_flow_bridge.utility.deps import trace_dependency
from src.code_confluence_flow_bridge.utility.detection import (
    CodebaseDetector,
    detect_codebases_multi_language,
)
from src.code_confluence_flow_bridge.utility.provider_urls import (
    build_repository_git_url,
)
from src.code_confluence_flow_bridge.utility.runtime_deps import (
    get_codebase_detectors,
    get_temporal_client_dep,
)
from src.code_confluence_flow_bridge.utility.token_utils import (
    fetch_repository_provider_token,
)
from src.code_confluence_flow_bridge.utility.workflow_helpers import (
    monitor_workflow,
    start_workflow,
)

router = APIRouter(prefix="", tags=["Repository"])


# ---------------------------------------------------------------------------
# GET /repository-status
# ---------------------------------------------------------------------------


@router.get(
    "/repository-status",
    response_model=GithubRepoStatus,
)
async def get_repository_status(
    repository_name: str = Query(..., description="The name of the repository"),
    repository_owner_name: str = Query(
        ..., description="The name of the repository owner"
    ),
    workflow_run_id: str = Query(
        ..., description="The workflow run ID to fetch status for"
    ),
    session: AsyncSession = Depends(get_session),
) -> GithubRepoStatus:
    """
    Get the current status of a repository workflow run and its associated codebase runs.
    """
    try:
        # Build base query for repository workflow run
        stmt = select(RepositoryWorkflowRun).where(
            RepositoryWorkflowRun.repository_name == repository_name,
            RepositoryWorkflowRun.repository_owner_name == repository_owner_name,
            RepositoryWorkflowRun.repository_workflow_run_id == workflow_run_id,
        )

        parent_run = (await session.execute(stmt)).scalar_one_or_none()
        if not parent_run:
            error_msg = "Workflow run {} not found for {}/{}".format(
                workflow_run_id, repository_name, repository_owner_name
            )
            raise HTTPException(status_code=404, detail=error_msg)

        # Fetch all codebase workflow runs associated with this parent run
        cb_stmt = select(CodebaseWorkflowRun).where(
            CodebaseWorkflowRun.repository_name == repository_name,
            CodebaseWorkflowRun.repository_owner_name == repository_owner_name,
            CodebaseWorkflowRun.repository_workflow_run_id
            == parent_run.repository_workflow_run_id,
        )
        codebase_runs = (await session.execute(cb_stmt)).scalars().all()

        codebase_status_list = build_repository_status_hierarchy(codebase_runs)

        # Create parent repository status object
        return GithubRepoStatus(
            repository_name=parent_run.repository_name,
            repository_owner_name=parent_run.repository_owner_name,
            repository_workflow_run_id=parent_run.repository_workflow_run_id,
            repository_workflow_id=parent_run.repository_workflow_id,
            issue_tracking=IssueTracking(**parent_run.issue_tracking)
            if parent_run.issue_tracking
            else None,
            status=JobStatus(parent_run.status),
            started_at=parent_run.started_at,
            completed_at=parent_run.completed_at,
            error_report=ErrorReport(**parent_run.error_report)
            if parent_run.error_report
            else None,
            codebase_status_list=codebase_status_list,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error retrieving repository status: {}", str(e))
        raise HTTPException(
            status_code=500,
            detail="Error retrieving repository status: {}".format(str(e)),
        )


# ---------------------------------------------------------------------------
# GET /repository-data
# ---------------------------------------------------------------------------


@router.get(
    "/repository-data",
    response_model=GitHubRepoResponseConfiguration,
)
async def get_repository_data(
    repository_name: str = Query(..., description="The name of the repository"),
    repository_owner_name: str = Query(
        ..., description="The name of the repository owner"
    ),
    session: AsyncSession = Depends(get_session),
) -> GitHubRepoResponseConfiguration:
    # fetch repository record with its codebase configs
    db_obj: Repository | None = await session.get(
        Repository,
        (repository_name, repository_owner_name),
        options=[selectinload(cast(QueryableAttribute[Any], Repository.configs))],
    )
    if not db_obj:
        raise HTTPException(
            status_code=404,
            detail="Repository data not found for {}/{}".format(
                repository_name, repository_owner_name
            ),
        )

    # Map database CodebaseConfig entries to Pydantic models
    try:
        codebases = [
            CodebaseConfig(
                codebase_folder=config.codebase_folder,
                root_packages=config.root_packages,
                programming_language_metadata=build_programming_language_metadata(
                    config.programming_language_metadata
                ),
            )
            for config in db_obj.configs
        ]

        return GitHubRepoResponseConfiguration(
            repository_name=db_obj.repository_name,
            repository_owner_name=db_obj.repository_owner_name,
            repository_metadata=codebases,
        )
    except Exception as e:
        logger.error("Error mapping repository data: {}", str(e))
        raise HTTPException(
            status_code=500,
            detail="Error processing repository data for {}/{}".format(
                repository_name, repository_owner_name
            ),
        )


# ---------------------------------------------------------------------------
# GET /codebase-metadata
# ---------------------------------------------------------------------------


@router.get(
    "/codebase-metadata",
    response_model=CodebaseMetadataListResponse,
)
async def get_codebase_metadata(
    repository_name: str = Query(..., description="The name of the repository"),
    repository_owner_name: str = Query(
        ..., description="The name of the repository owner"
    ),
    session: AsyncSession = Depends(get_session),
) -> CodebaseMetadataListResponse:
    """
    Get codebase folders and their metadata for a specific repository.

    Returns a list of all codebases configured for the repository with their
    folder paths and programming language metadata.
    """
    # Fetch repository with codebase configs
    db_obj: Repository | None = await session.get(
        Repository,
        (repository_name, repository_owner_name),
        options=[selectinload(cast(QueryableAttribute[Any], Repository.configs))],
    )

    if not db_obj:
        raise HTTPException(
            status_code=404,
            detail="Repository not found: {}/{}".format(
                repository_owner_name, repository_name
            ),
        )

    try:
        # Map database CodebaseConfig entries to response models
        codebase_metadata = [
            CodebaseMetadataResponse(
                codebase_folder=config.codebase_folder,
                programming_language_metadata=build_programming_language_metadata(
                    config.programming_language_metadata
                ),
            )
            for config in db_obj.configs
        ]

        return CodebaseMetadataListResponse(
            repository_name=db_obj.repository_name,
            repository_owner_name=db_obj.repository_owner_name,
            codebases=codebase_metadata,
        )
    except Exception as e:
        logger.error("Error mapping codebase metadata: {}", str(e))
        raise HTTPException(
            status_code=500,
            detail="Error processing codebase metadata for {}/{}".format(
                repository_owner_name, repository_name
            ),
        )


# ---------------------------------------------------------------------------
# DELETE /delete-repository
# ---------------------------------------------------------------------------


@router.delete("/delete-repository", status_code=200)
async def delete_repository(
    repo_info: IngestedRepositoryResponse, session: AsyncSession = Depends(get_session)
) -> Dict[str, Any]:
    """Delete a repository from PostgreSQL relational tables.

    This endpoint removes a repository and all its associated data including:
    - Repository record and cascaded relations in PostgreSQL (base tables)
    - Code Confluence relational tables (git repo, codebases, files, metadata)

    Args:
        repo_info: IngestedRepositoryResponse containing repository_name and repository_owner_name
        session: Database session

    Returns:
        Success message with deletion statistics

    Raises:
        HTTPException: 404 if repository not found, 500 on error
    """
    repository_name = repo_info.repository_name
    repository_owner_name = repo_info.repository_owner_name

    try:
        # First check if repository exists in PostgreSQL
        db_obj: Repository | None = await session.get(
            Repository, (repository_name, repository_owner_name)
        )
        if not db_obj:
            raise HTTPException(
                status_code=404,
                detail="Repository not found: {}/{}".format(
                    repository_owner_name, repository_name
                ),
            )

        qualified_name = "{}_{}".format(repository_owner_name, repository_name)
        relational_repo = await session.get(
            UnoplatCodeConfluenceGitRepository, qualified_name
        )

        # Delete from PostgreSQL - cascade will handle related tables
        await session.delete(db_obj)
        relational_status = "not_found"
        if relational_repo:
            await session.delete(relational_repo)
            relational_status = "deleted"
        await session.commit()

        logger.info(
            "Deleted repository from PostgreSQL: {}/{}",
            repository_owner_name,
            repository_name,
        )
        if relational_status == "deleted":
            logger.info(
                "Deleted repository from Code Confluence relational tables: {}",
                qualified_name,
            )
        else:
            logger.warning(
                "Repository not found in Code Confluence relational tables: {}",
                qualified_name,
            )

        return {
            "message": "Successfully deleted repository {}/{}".format(
                repository_owner_name, repository_name
            ),
            "repository_name": repository_name,
            "repository_owner_name": repository_owner_name,
            "repository_qualified_name": qualified_name,
            "relational_deletion_status": relational_status,
        }

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error("Error deleting repository: {}", str(e))
        raise HTTPException(
            status_code=500, detail="Error deleting repository: {}".format(str(e))
        )


# ---------------------------------------------------------------------------
# POST /refresh-repository
# ---------------------------------------------------------------------------


@router.post(
    "/refresh-repository", response_model=RefreshRepositoryResponse, status_code=201
)
async def refresh_repository(
    refresh_request: RepositoryRefreshRequest,
    session: AsyncSession = Depends(get_session),
    request_logger: "Logger" = Depends(trace_dependency),  # type: ignore
    temporal_client: Client = Depends(get_temporal_client_dep),
    detectors: dict[str, CodebaseDetector] = Depends(get_codebase_detectors),
) -> RefreshRepositoryResponse:
    """
    Refresh a repository by re-detecting codebases and re-ingesting.

    This endpoint:
    1. Re-detects codebases using configured detectors
    2. Starts a new Temporal workflow for ingestion

    Args:
        repo_request: Repository request configuration with provider_key
        session: Database session
        request_logger: Logger with trace ID

    Returns:
        RefreshRepositoryResponse with workflow IDs
    """
    repository_name: str = refresh_request.repository_name
    repository_owner_name: str = refresh_request.repository_owner_name
    provider_key: ProviderKey = refresh_request.provider_key

    try:
        # 1. Get repository info from database to determine if it's local or remote
        db_repo: Repository | None = await session.get(
            Repository, (repository_name, repository_owner_name)
        )
        if not db_repo:
            raise HTTPException(
                status_code=404,
                detail="Repository not found in database: {}/{}".format(
                    repository_name, repository_owner_name
                ),
            )

        # Use provider from DB if refresh payload somehow differs
        if db_repo.repository_provider != provider_key:
            request_logger.warning(
                "Provider key mismatch for {}/{}: request={}, db={}",
                repository_owner_name,
                repository_name,
                provider_key,
                db_repo.repository_provider,
            )
            provider_key = db_repo.repository_provider

        # 2. Fetch repository provider token from database using provider_key
        provider_token, metadata = await fetch_repository_provider_token(
            session, CredentialNamespace.REPOSITORY, provider_key
        )

        # 3. Use repository URL from request or build for provider
        repository_url = refresh_request.repository_git_url or build_repository_git_url(
            repository_owner_name=repository_owner_name,
            repository_name=repository_name,
            provider_key=provider_key,
            metadata=metadata,
        )
        request_logger.info("Refreshing repository: {}", repository_url)

        repo_request = RepositoryRequestConfiguration(
            repository_name=repository_name,
            repository_owner_name=repository_owner_name,
            repository_git_url=repository_url,
            provider_key=provider_key,
        )

        # 4. Detect codebases using multi-language detector registry
        try:
            # Use multi-language detection helper
            detected_codebases = await detect_codebases_multi_language(
                git_url=repository_url,
                github_token=provider_token,
                detectors=detectors,
                request_logger=request_logger,
            )

            request_logger.info(
                "Detected {} codebases for {}/{}",
                len(detected_codebases),
                repository_owner_name,
                repository_name,
            )
        except Exception as e:
            request_logger.error("Codebase detection failed: {}", str(e))
            raise HTTPException(
                status_code=500, detail=f"Failed to detect codebases: {str(e)}"
            )

        # 6. Update repository request with detected codebases
        repo_request.repository_metadata = detected_codebases

        # 7. Start Temporal workflow
        trace_id: Optional[str] = trace_id_var.get()
        if not trace_id:
            raise HTTPException(500, "trace_id not set by dependency")

        workflow_handle: WorkflowHandle[
            RepoWorkflow, UnoplatGitRepository
        ] = await start_workflow(
            temporal_client=temporal_client,
            repo_request=repo_request,
            github_token=provider_token,
            workflow_id=f"refresh-{provider_key.value}-{repository_owner_name}-{repository_name}-{trace_id}",
            trace_id=trace_id,
        )

        # 8. Schedule background monitoring
        asyncio.create_task(monitor_workflow(workflow_handle))

        request_logger.info(
            f"Started refresh workflow for {repository_owner_name}/{repository_name}. "
            f"Workflow ID: {workflow_handle.id}, RunID: {workflow_handle.result_run_id}"
        )

        return RefreshRepositoryResponse(
            repository_name=repository_name,
            repository_owner_name=repository_owner_name,
            workflow_id=workflow_handle.id or "",
            run_id=workflow_handle.result_run_id or "",
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        request_logger.error("Error refreshing repository: {}", str(e))
        raise HTTPException(
            status_code=500, detail=f"Error refreshing repository: {str(e)}"
        )
