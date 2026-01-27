"""Tool/MCP configuration API endpoints for query-engine."""

from datetime import datetime
from enum import Enum
from typing import Optional

from fastapi import APIRouter, Header, HTTPException, Request
from loguru import logger
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from unoplat_code_confluence_commons.credential_enums import ProviderKey
from unoplat_code_confluence_query_engine.db.postgres.ai_model_config import (
    AiModelConfig,
)
from unoplat_code_confluence_query_engine.db.postgres.db import get_startup_session
from unoplat_code_confluence_query_engine.services.config.credentials_service import (
    CredentialsService,
)
from unoplat_code_confluence_query_engine.services.temporal.temporal_worker_manager import (
    TemporalWorkerManager,
    get_worker_manager,
)

router = APIRouter(prefix="/v1/tool-config", tags=["tool-config"])


class ToolProvider(str, Enum):
    """Supported tool/MCP providers."""

    EXA = "exa"


class ToolConfigStatus(str, Enum):
    """Status of tool configuration."""

    CONFIGURED = "configured"
    NOT_CONFIGURED = "not_configured"


class ToolConfigResponse(BaseModel):
    """Response for tool configuration status (never returns secrets)."""

    provider: ToolProvider
    status: ToolConfigStatus
    configured_at: Optional[datetime] = None


class ToolConfigListResponse(BaseModel):
    """Response listing all tool configurations."""

    tools: list[ToolConfigResponse] = Field(default_factory=list)


class ToolConfigDeleteResponse(BaseModel):
    """Response for successful tool configuration deletion."""

    message: str


def get_provider_key(provider: ToolProvider) -> ProviderKey:
    if provider == ToolProvider.EXA:
        return ProviderKey.EXA
    raise ValueError(f"Unsupported tool provider: {provider}")


async def _get_tool_credential(
    session: AsyncSession, provider_key: ProviderKey
) -> Optional[object]:
    return await CredentialsService.execute_get_tool_query(session, provider_key)


async def _restart_worker_for_tool_config(
    request: Request, worker_manager: TemporalWorkerManager
) -> None:
    settings = request.app.state.settings
    if not settings.temporal_enabled:
        logger.debug("Temporal disabled, skipping worker restart for tool config")
        return

    async with get_startup_session() as session:
        model_config = await session.get(AiModelConfig, 1)

    if not model_config:
        logger.warning(
            "No AI model config found; skipping worker restart for tool config update"
        )
        return

    try:
        if worker_manager.is_running:
            await worker_manager.stop()
        await worker_manager.start(settings=settings, config=model_config)
        request.app.state.temporal_worker_manager = worker_manager
        logger.info("Temporal worker restarted after tool config update")
    except Exception as e:
        logger.error("Failed to restart Temporal worker after tool config update: {}", e)


@router.put("/{provider}", response_model=ToolConfigResponse)
async def upsert_tool_config(
    provider: ToolProvider,
    request: Request,
    authorization: str = Header(..., description="Bearer token containing the API key"),
) -> ToolConfigResponse:
    """Create or update tool configuration."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header")
    api_key = authorization[7:].strip()
    if not api_key:
        raise HTTPException(status_code=400, detail="API key cannot be empty")

    provider_key = get_provider_key(provider)
    async with get_startup_session() as session:
        await CredentialsService.upsert_tool_credential(api_key, provider_key, session)
        credential = await _get_tool_credential(session, provider_key)

    worker_manager = get_worker_manager()
    await _restart_worker_for_tool_config(request, worker_manager)

    return ToolConfigResponse(
        provider=provider,
        status=ToolConfigStatus.CONFIGURED,
        configured_at=credential.updated_at if credential else None,
    )


@router.get("/{provider}", response_model=ToolConfigResponse)
async def get_tool_config(provider: ToolProvider) -> ToolConfigResponse:
    """Get configuration status for a specific tool provider."""
    provider_key = get_provider_key(provider)
    async with get_startup_session() as session:
        credential = await _get_tool_credential(session, provider_key)

    if credential:
        return ToolConfigResponse(
            provider=provider,
            status=ToolConfigStatus.CONFIGURED,
            configured_at=credential.updated_at,
        )
    return ToolConfigResponse(
        provider=provider,
        status=ToolConfigStatus.NOT_CONFIGURED,
        configured_at=None,
    )


@router.get("", response_model=ToolConfigListResponse)
async def list_tool_configs() -> ToolConfigListResponse:
    """List configuration status for all supported tool providers."""
    tools: list[ToolConfigResponse] = []
    async with get_startup_session() as session:
        for provider in ToolProvider:
            provider_key = get_provider_key(provider)
            credential = await _get_tool_credential(session, provider_key)
            if credential:
                tools.append(
                    ToolConfigResponse(
                        provider=provider,
                        status=ToolConfigStatus.CONFIGURED,
                        configured_at=credential.updated_at,
                    )
                )
            else:
                tools.append(
                    ToolConfigResponse(
                        provider=provider,
                        status=ToolConfigStatus.NOT_CONFIGURED,
                        configured_at=None,
                    )
                )

    return ToolConfigListResponse(tools=tools)


@router.delete("/{provider}", response_model=ToolConfigDeleteResponse)
async def delete_tool_config(
    provider: ToolProvider, request: Request
) -> ToolConfigDeleteResponse:
    """Delete tool configuration for a specific provider."""
    provider_key = get_provider_key(provider)
    async with get_startup_session() as session:
        deleted = await CredentialsService.delete_tool_credential(session, provider_key)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=f"No configuration found for tool provider: {provider.value}",
        )

    worker_manager = get_worker_manager()
    await _restart_worker_for_tool_config(request, worker_manager)

    return ToolConfigDeleteResponse(
        message=f"Tool configuration for {provider.value} deleted successfully"
    )
