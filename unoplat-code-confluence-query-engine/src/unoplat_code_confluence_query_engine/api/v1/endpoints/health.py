"""Health probe endpoints for liveness and readiness checks."""

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from loguru import logger
from sqlalchemy import text

from unoplat_code_confluence_query_engine.db.postgres.db import get_startup_session

router = APIRouter(tags=["health"])


@router.get("/health")
async def liveness() -> dict[str, str]:
    """Report that the process is up and serving requests.

    Liveness must stay dependency-free so a transient datastore outage never
    triggers a restart of an otherwise-healthy process.

    Returns:
        Status payload indicating the service is alive.
    """
    return {"status": "ok"}


@router.get("/ready")
async def readiness() -> JSONResponse:
    """Report whether the service can serve traffic by verifying the database.

    Returns:
        200 with a passing check map when PostgreSQL round-trips successfully,
        503 with a failing check map otherwise.
    """
    try:
        async with get_startup_session() as session:
            await session.execute(text("SELECT 1"))
    except Exception as e:
        logger.error("Readiness check failed: {}", e)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "not_ready", "checks": {"database": "fail"}},
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": "ready", "checks": {"database": "ok"}},
    )
