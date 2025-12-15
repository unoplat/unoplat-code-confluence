"""AI model configuration API endpoints."""

from typing import Any, Dict

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from loguru import logger
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

    # Load current credential and compute hash for build ID
    credential = await CredentialsService.get_model_credential(session)
    credential_hash = compute_credential_hash(credential) if credential else None

    new_build_id = generate_build_id(config, credential_hash)

    # Case 1: Worker not running - start it
    if not worker_manager.is_running:
        logger.info(f"Starting Temporal worker with build ID: {new_build_id}")
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
            logger.info("AI model config upserted for provider: {}", config.provider_key)

            # update_app_agents rebuilds model cache - safe in same transaction
            await update_app_agents(request.app, session)

        # Transaction committed here - credential now visible to other sessions

        # PHASE 2: Worker versioning (after commit)
        # Worker restart failure does NOT rollback the config/credential
        async with get_startup_session() as session:
            await _handle_worker_versioning(request, session, worker_manager, old_build_id)

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
        logger.error(f"Error getting provider schema for {provider_key}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve provider schema",
        )
