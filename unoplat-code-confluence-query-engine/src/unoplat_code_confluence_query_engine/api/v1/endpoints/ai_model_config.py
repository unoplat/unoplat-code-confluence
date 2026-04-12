"""AI model configuration API endpoints."""

from datetime import datetime
import json
from typing import Any, Dict, Optional
from urllib.parse import urlparse

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse, Response
from loguru import logger
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from unoplat_code_confluence_query_engine.db.postgres.ai_model_config import (
    AiModelConfig,
)
from unoplat_code_confluence_query_engine.db.postgres.db import (
    get_db_session,
    get_startup_session,
)
from unoplat_code_confluence_query_engine.models.config.ai_model_config import (
    AiModelConfigIn,
    AiModelConfigOut,
)
from unoplat_code_confluence_query_engine.services.config.ai_model_config_service import (
    AiModelConfigService,
)
from unoplat_code_confluence_query_engine.services.config.codex_oauth_service import (
    CodexOAuthService,
)
from unoplat_code_confluence_query_engine.services.config.config_hot_reload import (
    update_app_agents,
)
from unoplat_code_confluence_query_engine.services.config.credentials_service import (
    CredentialsService,
)
from unoplat_code_confluence_query_engine.services.config.provider_catalog import (
    ProviderCatalog,
    ProviderSchema,
    ProviderSchemaPublic,
)
from unoplat_code_confluence_query_engine.services.temporal.build_id_generator import (
    compute_credential_hash,
    generate_build_id,
)
from unoplat_code_confluence_query_engine.services.temporal.temporal_worker_manager import (
    TemporalWorkerManager,
    get_worker_manager,
)

router = APIRouter(prefix="/v1", tags=["ai-model-config"])
callback_router = APIRouter(tags=["ai-model-config"])


class CodexOAuthAuthorizeResponse(BaseModel):
    """Response payload for OAuth authorize flow initialization."""

    flow_id: str
    authorization_url: str
    expires_at: int
    poll_interval_ms: int


class CodexOAuthAuthorizeRequest(BaseModel):
    """Optional payload for OAuth authorize URL generation."""

    frontend_origin: Optional[str] = None


class CodexOAuthFlowStatusResponse(BaseModel):
    """Polling response for OAuth flow state."""

    status: str
    error: Optional[str] = None


class CodexOAuthConnectionStatusResponse(BaseModel):
    """Current stored OAuth connection state for codex_openai."""

    connected: bool
    account_id: Optional[str] = None
    expires_at: Optional[int] = None
    configured_at: Optional[datetime] = None


class CodexOAuthDeleteResponse(BaseModel):
    """Response payload for OAuth disconnect endpoint."""

    deleted: bool
    message: str


def _oauth_success_html() -> str:
    return """
<!doctype html>
<html>
  <head><title>Authorization Successful</title></head>
  <body style="font-family: Arial, sans-serif; padding: 24px;">
    <h2>ChatGPT Authorization Successful</h2>
    <p>You can close this window and return to the app.</p>
    <script>setTimeout(() => window.close(), 800);</script>
  </body>
</html>
"""


def _oauth_error_html(message: str) -> str:
    safe_message = message.replace("<", "&lt;").replace(">", "&gt;")
    return f"""
<!doctype html>
<html>
  <head><title>Authorization Failed</title></head>
  <body style="font-family: Arial, sans-serif; padding: 24px;">
    <h2>ChatGPT Authorization Failed</h2>
    <p>{safe_message}</p>
    <p>You can close this window and retry from the app.</p>
  </body>
</html>
"""


def _normalize_frontend_origin(frontend_origin: Optional[str]) -> Optional[str]:
    if not frontend_origin:
        return None
    parsed = urlparse(frontend_origin.strip())
    if parsed.scheme not in {"http", "https"}:
        return None
    if not parsed.netloc:
        return None
    return f"{parsed.scheme}://{parsed.netloc}"


def _oauth_popup_result_html(
    *, frontend_origin: str, success: bool, message: str
) -> str:
    payload: dict[str, str] = {
        "type": "codex-oauth-callback",
        "status": "success" if success else "failed",
    }
    if not success:
        payload["error"] = message
    payload_json = json.dumps(payload)
    target_origin_json = json.dumps(frontend_origin)
    text_title = "ChatGPT Authorization Successful" if success else "ChatGPT Authorization Failed"
    text_body = (
        "Authorization complete. This window should close automatically."
        if success
        else message.replace("<", "&lt;").replace(">", "&gt;")
    )
    return f"""
<!doctype html>
<html>
  <head><title>{text_title}</title></head>
  <body style="font-family: Arial, sans-serif; padding: 24px;">
    <h2>{text_title}</h2>
    <p>{text_body}</p>
    <script>
      (() => {{
        const payload = {payload_json};
        const targetOrigin = {target_origin_json};
        if (window.opener && targetOrigin) {{
          window.opener.postMessage(payload, targetOrigin);
          window.close();
          return;
        }}
      }})();
    </script>
  </body>
</html>
"""


async def _get_worker_credential_hash(
    session: AsyncSession, config: AiModelConfig
) -> str | None:
    if config.provider_key == "codex_openai":
        credential = await CredentialsService.get_model_oauth_refresh_token(session)
    else:
        credential = await CredentialsService.get_model_credential(session)
    return compute_credential_hash(credential) if credential else None


async def _handle_worker_versioning(
    request: Request,
    session: AsyncSession,
    worker_manager: TemporalWorkerManager,
    old_build_id: str | None,
) -> None:
    """Handle Temporal worker versioning after config change.

    Starts the worker if not running, or restarts if build ID changed.

    Args:
        request: FastAPI request to access app state and settings
        session: Database session for loading config
        worker_manager: Temporal worker manager instance
        old_build_id: Build ID before config change (None if worker not running)
    """
    settings = request.app.state.settings

    if not settings.temporal_enabled:
        logger.debug("Temporal disabled, skipping worker versioning")
        return

    # Load the updated config to generate new build ID
    config = await session.get(AiModelConfig, 1)
    if not config:
        logger.warning("No AI model config found after upsert, cannot start worker")
        return

    # Build-id credential source is provider-aware:
    # - codex_openai: refresh token
    # - all others: model API key
    credential_hash = await _get_worker_credential_hash(session, config)

    new_build_id = generate_build_id(config, credential_hash)

    # Case 1: Worker not running - start it
    if not worker_manager.is_running:
        logger.info("Starting Temporal worker with build ID: {}", new_build_id)
        try:
            await worker_manager.start(settings=settings, config=config)
            request.app.state.temporal_worker_manager = worker_manager
            logger.info(
                "Temporal worker started successfully with build ID: {}",
                worker_manager.current_build_id,
            )
        except Exception as e:
            logger.error("Failed to start Temporal worker: {}", e)
        return

    # Case 2: Worker running, check if build ID changed
    if old_build_id == new_build_id:
        logger.debug(
            "Build ID unchanged ({}), no worker restart needed",
            new_build_id,
        )
        return

    # Case 3: Build ID changed - restart worker
    logger.info(
        "Build ID changed ({} -> {}), restarting Temporal worker",
        old_build_id,
        new_build_id,
    )

    try:
        await worker_manager.stop()
        await worker_manager.start(settings=settings, config=config)
        request.app.state.temporal_worker_manager = worker_manager
        logger.info(
            "Temporal worker restarted with new build ID: {}",
            worker_manager.current_build_id,
        )
    except Exception as e:
        logger.error("Failed to restart Temporal worker: {}", e)
        request.app.state.temporal_worker_manager = None    


@router.get("/model-config", response_model=AiModelConfigOut)
async def get_ai_model_config(
    request: Request, session: AsyncSession = Depends(get_db_session)
) -> AiModelConfigOut:
    """Get the current AI model configuration.

    Args:
        request: FastAPI request object to access app state
        session: Database session

    Returns:
        AiModelConfigOut with the current configuration

    Raises:
        HTTPException: 404 if no configuration exists, 500 for other errors
    """
    try:
        service = request.app.state.ai_model_config_service
        config = await service.get_config(session)

        if config is None:
            logger.info("AI model configuration not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="AI model configuration not found",
            )

        logger.info("Retrieved AI model config for provider: {}", config.provider_key)
        return config

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error retrieving AI model config: {}", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve AI model configuration",
        )


@router.put("/model-config", response_model=AiModelConfigOut)
async def upsert_ai_model_config(
    request: Request,
    config: AiModelConfigIn,
    x_model_api_key: str | None = Header(None, alias="X-Model-API-Key"),
) -> AiModelConfigOut:
    """Create or update AI model configuration.

    Uses two-phase commit to ensure credential durability:
    1. Config and credential are committed first (Phase 1)
    2. Worker versioning happens after commit (Phase 2, can fail independently)

    This ensures credential is persisted even if worker restart fails.

    Args:
        request: FastAPI request object to access app state
        config: AI model configuration input
        x_model_api_key: API key from X-Model-API-Key header

    Returns:
        AiModelConfigOut with the saved configuration

    Raises:
        HTTPException: If provider is unknown or validation fails
    """
    try:
        # Get current build ID before update (if worker is running)
        worker_manager = get_worker_manager()
        old_build_id = worker_manager.current_build_id

        # PHASE 1: Commit config and credential
        # Uses explicit session that commits at context exit
        async with get_startup_session() as session:
            service: AiModelConfigService = request.app.state.ai_model_config_service
            result = await service.upsert_config(config, x_model_api_key, session)
            logger.info(
                "AI model config upserted for provider: {}", config.provider_key
            )

            # update_app_agents rebuilds model cache - safe in same transaction
            await update_app_agents(request.app, session)

        # Transaction committed here - credential now visible to other sessions

        # PHASE 2: Worker versioning (after commit)
        # Worker restart failure does NOT rollback the config/credential
        async with get_startup_session() as session:
            await _handle_worker_versioning(
                request, session, worker_manager, old_build_id
            )

        return result

    except ValueError as e:
        logger.warning("Validation error upserting AI model config: {}", e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error("Error upserting AI model config: {}", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save AI model configuration",
        )


@router.delete("/model-config")
async def delete_ai_model_config(
    request: Request, session: AsyncSession = Depends(get_db_session)
) -> Dict[str, Any]:
    """Delete the current AI model configuration.

    Args:
        request: FastAPI request object to access app state
        session: Database session

    Returns:
        Dictionary with deletion status
    """
    try:
        service = request.app.state.ai_model_config_service
        deleted = await service.delete_config(session)

        if deleted:
            logger.info("AI model configuration deleted")
            return {
                "message": "AI model configuration deleted successfully",
                "deleted": True,
            }
        else:
            logger.info("No AI model configuration found to delete")
            return {"message": "No AI model configuration found", "deleted": False}

    except Exception as e:
        logger.error("Error deleting AI model config: {}", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete AI model configuration",
        )


@router.get("/providers", response_model=Dict[str, ProviderSchemaPublic])
async def list_providers() -> Dict[str, ProviderSchemaPublic]:
    """List all available AI model providers with full schemas.

    Returns:
        Mapping of provider_key to ProviderSchemaPublic
    """
    try:
        providers = ProviderCatalog.list_providers_map()
        logger.info("Retrieved {} available providers", len(providers))
        return providers

    except Exception as e:
        logger.error("Error listing providers: {}", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve provider list",
        )


@router.get("/providers/{provider_key}", response_model=ProviderSchema)
async def get_provider_schema(provider_key: str) -> ProviderSchema:
    """Get configuration schema for a specific provider.

    Args:
        provider_key: The provider identifier

    Returns:
        ProviderSchema with configuration details

    Raises:
        HTTPException: If provider is not found
    """
    try:
        schema = ProviderCatalog.get_provider(provider_key)
        if not schema:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Provider not found: {provider_key}",
            )

        logger.info("Retrieved schema for provider: {}", provider_key)
        return schema

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting provider schema for {}: {}", provider_key, e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve provider schema",
        )


@router.post(
    "/model-config/codex-openai/oauth/authorize",
    response_model=CodexOAuthAuthorizeResponse,
)
async def codex_oauth_authorize(
    request: Request,
    payload: CodexOAuthAuthorizeRequest | None = None,
) -> CodexOAuthAuthorizeResponse:
    """Start Codex OAuth PKCE flow and return authorization URL."""
    callback_ready = getattr(request.app.state, "codex_callback_server_ready", False)
    if not callback_ready:
        callback_port = request.app.state.settings.codex_openai_callback_port
        callback_hosts = request.app.state.settings.codex_openai_callback_hosts
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                f"Codex OAuth callback listener is unavailable on {callback_hosts}:{callback_port}. "
                "Ensure port is free and restart query-engine."
            ),
        )

    service: CodexOAuthService = request.app.state.codex_oauth_service
    raw_frontend_origin = payload.frontend_origin if payload else None
    frontend_origin = _normalize_frontend_origin(
        raw_frontend_origin
    )
    if raw_frontend_origin and not frontend_origin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid frontend_origin. Expected origin format like http://localhost:3000",
        )
    payload = await service.create_authorization_flow(frontend_origin=frontend_origin)
    return CodexOAuthAuthorizeResponse(**payload)


@router.get(
    "/model-config/codex-openai/oauth/flows/{flow_id}",
    response_model=CodexOAuthFlowStatusResponse,
)
async def codex_oauth_flow_status(
    request: Request, flow_id: str
) -> CodexOAuthFlowStatusResponse:
    """Poll OAuth flow status."""
    service: CodexOAuthService = request.app.state.codex_oauth_service
    payload = await service.get_flow_status(flow_id)
    return CodexOAuthFlowStatusResponse(
        status=payload["status"] or "failed",
        error=payload.get("error"),
    )


async def _process_codex_oauth_callback(
    request: Request,
    code: Optional[str] = Query(default=None),
    state: Optional[str] = Query(default=None),
    error: Optional[str] = Query(default=None),
    error_description: Optional[str] = Query(default=None),
) -> Response:
    service: CodexOAuthService = request.app.state.codex_oauth_service
    frontend_origin = await service.get_flow_frontend_origin(state)
    success = False
    message = "Authorization failed"

    worker_manager = get_worker_manager()
    old_build_id = worker_manager.current_build_id

    async with get_startup_session() as session:
        success, message = await service.complete_authorization_callback(
            session,
            state=state,
            code=code,
            error=error,
            error_description=error_description,
        )

    if success:
        async with get_startup_session() as session:
            await _handle_worker_versioning(
                request, session, worker_manager, old_build_id
            )
        if frontend_origin:
            return HTMLResponse(
                content=_oauth_popup_result_html(
                    frontend_origin=frontend_origin,
                    success=True,
                    message=message,
                ),
                status_code=200,
            )
        return HTMLResponse(content=_oauth_success_html(), status_code=200)
    if frontend_origin:
        return HTMLResponse(
            content=_oauth_popup_result_html(
                frontend_origin=frontend_origin,
                success=False,
                message=message,
            ),
            status_code=400,
        )
    return HTMLResponse(content=_oauth_error_html(message), status_code=400)


@router.get("/model-config/codex-openai/oauth/callback", response_class=HTMLResponse)
async def codex_oauth_callback(
    request: Request,
    code: Optional[str] = Query(default=None),
    state: Optional[str] = Query(default=None),
    error: Optional[str] = Query(default=None),
    error_description: Optional[str] = Query(default=None),
) -> Response:
    """OAuth callback endpoint for browser authorization flow."""
    return await _process_codex_oauth_callback(
        request=request,
        code=code,
        state=state,
        error=error,
        error_description=error_description,
    )


@callback_router.get("/auth/callback", response_class=HTMLResponse)
async def codex_oauth_callback_alias(
    request: Request,
    code: Optional[str] = Query(default=None),
    state: Optional[str] = Query(default=None),
    error: Optional[str] = Query(default=None),
    error_description: Optional[str] = Query(default=None),
) -> Response:
    """OpenCode-compatible callback alias path for Codex OAuth."""
    return await _process_codex_oauth_callback(
        request=request,
        code=code,
        state=state,
        error=error,
        error_description=error_description,
    )


@router.get(
    "/model-config/codex-openai/oauth/status",
    response_model=CodexOAuthConnectionStatusResponse,
)
async def codex_oauth_status(
    request: Request,
    session: AsyncSession = Depends(get_db_session),
) -> CodexOAuthConnectionStatusResponse:
    """Get persisted Codex OAuth connection status."""
    service: CodexOAuthService = request.app.state.codex_oauth_service
    status_payload = await service.get_oauth_status(session)
    return CodexOAuthConnectionStatusResponse(
        connected=status_payload.connected,
        account_id=status_payload.account_id,
        expires_at=status_payload.expires_at,
        configured_at=status_payload.configured_at,
    )


@router.delete(
    "/model-config/codex-openai/oauth",
    response_model=CodexOAuthDeleteResponse,
)
async def codex_oauth_delete(request: Request) -> CodexOAuthDeleteResponse:
    """Disconnect Codex OAuth credentials and refresh worker versioning."""
    service: CodexOAuthService = request.app.state.codex_oauth_service
    worker_manager = get_worker_manager()
    old_build_id = worker_manager.current_build_id

    async with get_startup_session() as session:
        deleted = await service.disconnect(session)

    async with get_startup_session() as session:
        await _handle_worker_versioning(request, session, worker_manager, old_build_id)

    message = (
        "Codex OAuth credentials deleted"
        if deleted
        else "No Codex OAuth credentials found"
    )
    return CodexOAuthDeleteResponse(deleted=deleted, message=message)
