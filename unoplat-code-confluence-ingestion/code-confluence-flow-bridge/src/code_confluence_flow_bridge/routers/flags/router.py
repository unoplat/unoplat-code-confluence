"""Feature-flag endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from unoplat_code_confluence_commons.base_models import Flag

from src.code_confluence_flow_bridge.processor.db.postgres.db import get_session

router = APIRouter(prefix="", tags=["Flags"])


@router.get("/flags/{flag_name}", status_code=200)
async def get_flag_status(
    flag_name: str, session: AsyncSession = Depends(get_session)
) -> dict[str, str | bool]:
    """Get the status of a specific flag by name."""
    try:
        result = await session.execute(select(Flag).where(Flag.name == flag_name))
        flag: Flag | None = result.scalar_one_or_none()
        if flag is None:
            raise HTTPException(status_code=404, detail=f"Flag '{flag_name}' not found")
        return {"name": flag.name, "status": flag.status, "exists": True}
    except HTTPException as http_ex:
        raise http_ex
    except Exception as exc:
        logger.error("Failed to get flag status: {}", str(exc))
        raise HTTPException(
            status_code=500, detail="Failed to get flag status for {}".format(flag_name)
        )


@router.get("/flags", status_code=200)
async def get_all_flags(
    session: AsyncSession = Depends(get_session),
) -> list[dict[str, str | bool]]:
    """Get the status of all available flags."""
    try:
        result = await session.execute(select(Flag))
        flags = result.scalars().all()
        return [{"name": flag.name, "status": flag.status} for flag in flags]
    except Exception as exc:
        logger.error("Failed to get flags: {}", str(exc))
        raise HTTPException(status_code=500, detail="Failed to get flags")


@router.put("/flags/{flag_name}", status_code=200)
async def set_flag_status(
    flag_name: str, status: bool, session: AsyncSession = Depends(get_session)
) -> dict[str, str | bool]:
    """Set the status of a specific flag by name."""
    try:
        result = await session.execute(select(Flag).where(Flag.name == flag_name))
        flag: Flag | None = result.scalar_one_or_none()

        if flag is None:
            flag = Flag(name=flag_name, status=status)
        else:
            flag.status = status

        session.add(flag)
        return {"name": flag.name, "status": flag.status}
    except Exception as exc:
        logger.error("Failed to set flag status: {}", str(exc))
        raise HTTPException(
            status_code=500, detail="Failed to set flag status for {}".format(flag_name)
        )
