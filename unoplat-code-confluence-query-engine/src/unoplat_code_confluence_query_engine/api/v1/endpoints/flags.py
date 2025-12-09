"""Feature flags API endpoints following the ingestion project pattern."""

from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, Request, status
from loguru import logger
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from unoplat_code_confluence_query_engine.db.postgres.db import get_db_session

router = APIRouter(prefix="/v1", tags=["flags"])


class FlagUpdateRequest(BaseModel):
    """Request model for updating flag status."""

    status: bool


@router.get("/flags", response_model=List[Dict[str, Any]])
async def get_all_flags(
    request: Request, session: AsyncSession = Depends(get_db_session)
) -> List[Dict[str, Any]]:
    """Get the status of all available flags.

    Args:
        request: FastAPI request object to access app state
        session: Database session

    Returns:
        List of flag information with name and status
    """
    try:
        service = request.app.state.flag_service
        flags = await service.list_all_flags(session)
        return [{"name": flag.name, "status": flag.status} for flag in flags]

    except Exception as e:
        logger.error("Error getting all flags: {}", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve flags",
        )


@router.get("/flags/{flag_name}", response_model=Dict[str, Any])
async def get_flag_status(
    request: Request, flag_name: str, session: AsyncSession = Depends(get_db_session)
) -> Dict[str, Any]:
    """Get the status of a specific flag by name.

    Args:
        request: FastAPI request object to access app state
        flag_name: The name of the flag to check
        session: Database session

    Returns:
        Flag information including name, status, and exists boolean

    Raises:
        HTTPException: 404 if flag not found
    """
    try:
        service = request.app.state.flag_service
        flag = await service.get_flag(flag_name, session)

        if flag is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Flag '{flag_name}' not found",
            )

        logger.info("Retrieved flag status for: {}", flag_name)
        return {"name": flag.name, "status": flag.status, "exists": True}

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting flag status for {}: {}", flag_name, e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get flag status for {flag_name}",
        )


@router.put("/flags/{flag_name}", response_model=Dict[str, Any])
async def set_flag_status(
    request: Request,
    flag_name: str,
    flag_request: FlagUpdateRequest,
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Set the status of a specific flag by name.

    This endpoint follows the upsert pattern from the ingestion project:
    - Creates the flag if it doesn't exist
    - Updates the flag status if it exists

    Args:
        request: FastAPI request object to access app state
        flag_name: The name of the flag to set
        flag_request: Request containing the status to set
        session: Database session

    Returns:
        Updated flag information with name and status
    """
    try:
        service = request.app.state.flag_service
        flag = await service.upsert_flag(flag_name, flag_request.status, session)

        logger.info("Set flag status for {}: status={}", flag_name, flag_request.status)
        return {"name": flag.name, "status": flag.status}

    except Exception as e:
        logger.error("Error setting flag status for {}: {}", flag_name, e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to set flag status for {flag_name}",
        )


@router.delete("/flags/{flag_name}")
async def delete_flag(
    request: Request, flag_name: str, session: AsyncSession = Depends(get_db_session)
) -> Dict[str, Any]:
    """Delete a specific flag by name.

    Args:
        request: FastAPI request object to access app state
        flag_name: The name of the flag to delete
        session: Database session

    Returns:
        Deletion status message

    Raises:
        HTTPException: 404 if flag not found
    """
    try:
        service = request.app.state.flag_service
        deleted = await service.delete_flag(flag_name, session)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Flag '{flag_name}' not found",
            )

        logger.info("Deleted flag: {}", flag_name)
        return {"message": f"Flag '{flag_name}' deleted successfully", "deleted": True}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting flag {flag_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete flag {flag_name}",
        )
