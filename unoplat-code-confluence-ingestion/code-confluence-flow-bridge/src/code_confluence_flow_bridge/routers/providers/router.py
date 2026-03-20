"""Repository provider discovery and user lookup endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from unoplat_code_confluence_commons.credential_enums import ProviderKey

from src.code_confluence_flow_bridge.models.github.github_repo import (
    PaginatedResponse,
    RepositoryProvidersResponse,
)
from src.code_confluence_flow_bridge.processor.db.postgres.db import get_session
from src.code_confluence_flow_bridge.routers.providers.service import (
    fetch_authenticated_user_details,
    fetch_paginated_repositories,
    list_repository_providers,
)

router = APIRouter(prefix="", tags=["Providers"])


@router.get("/repository-providers", response_model=RepositoryProvidersResponse)
async def get_repository_providers(
    session: AsyncSession = Depends(get_session),
) -> RepositoryProvidersResponse:
    """Get all configured repository providers from credentials table."""
    try:
        return await list_repository_providers(session)
    except Exception as exc:
        logger.error("Failed to fetch repository providers: {}", str(exc))
        raise HTTPException(
            status_code=500, detail="Failed to fetch repository providers"
        )


@router.get("/repos", response_model=PaginatedResponse)
async def get_repos(
    per_page: int = Query(30, ge=1, le=100, description="Items per page"),
    cursor: str | None = Query(None, description="Pagination cursor"),
    filterValues: str | None = Query(
        None, description="Optional JSON filter values to filter repositories"
    ),
    provider_key: ProviderKey = Query(..., description="Repository provider key"),
    session: AsyncSession = Depends(get_session),
) -> PaginatedResponse:
    try:
        return await fetch_paginated_repositories(
            session=session,
            provider_key=provider_key,
            per_page=per_page,
            cursor=cursor,
            filter_values=filterValues,
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("GraphQL Error: {}", str(exc))
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch repositories: {str(exc)}"
        )


@router.get("/user-details", status_code=200)
async def get_user_details(
    provider_key: ProviderKey = Query(..., description="Repository provider key"),
    session: AsyncSession = Depends(get_session),
) -> dict[str, str | None]:
    """Fetch authenticated GitHub user's name, avatar URL, and email."""
    return await fetch_authenticated_user_details(session, provider_key)
