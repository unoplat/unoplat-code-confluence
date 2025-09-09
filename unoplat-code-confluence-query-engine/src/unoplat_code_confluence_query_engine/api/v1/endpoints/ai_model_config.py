"""AI model configuration API endpoints."""

from typing import Any, Dict, List

from fastapi import APIRouter, Header, HTTPException, Request, status
from loguru import logger

from unoplat_code_confluence_query_engine.models.ai_model_config import (
    AiModelConfigIn,
    AiModelConfigOut,
)
from unoplat_code_confluence_query_engine.services.ai_model_config_service import (
    AiModelConfigService,
)
from unoplat_code_confluence_query_engine.services.config_hot_reload import (
    update_app_agents,
)
from unoplat_code_confluence_query_engine.services.provider_catalog import (
    ProviderCatalog,
    ProviderSchema,
)

router = APIRouter(prefix="/v1", tags=["ai-model-config"])


@router.get("/config", response_model=AiModelConfigOut)
async def get_ai_model_config(request: Request) -> AiModelConfigOut:
    """Get the current AI model configuration.

    Args:
        request: FastAPI request object to access app state

    Returns:
        AiModelConfigOut with the current configuration

    Raises:
        HTTPException: 404 if no configuration exists, 500 for other errors
    """
    try:
        service = request.app.state.ai_model_config_service
        config = await service.get_config()

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


@router.put("/config", response_model=AiModelConfigOut)
async def upsert_ai_model_config(
    request: Request,
    config: AiModelConfigIn,
    x_model_api_key: str | None = Header(None, alias="X-Model-API-Key"),
) -> AiModelConfigOut:
    """Create or update AI model configuration.

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
        service: AiModelConfigService = request.app.state.ai_model_config_service
        result = await service.upsert_config(config, api_key=x_model_api_key)
        logger.info("AI model config upserted for provider: {}", config.provider_key)

        # Immediately refresh application agents so new config/credentials take effect
        try:
            before_keys = list(getattr(request.app.state, "agents", {}).keys())  # type: ignore[attr-defined]
        except Exception:
            before_keys = []
        logger.debug("Agents before refresh: {}", before_keys)

        await update_app_agents(request.app)

        after_keys = list(request.app.state.agents.keys())
        logger.info("Application agents refreshed after config upsert")
        logger.debug("Agents after refresh: {}", after_keys)

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


@router.delete("/config")
async def delete_ai_model_config(request: Request) -> Dict[str, Any]:
    """Delete the current AI model configuration.

    Args:
        request: FastAPI request object to access app state

    Returns:
        Dictionary with deletion status
    """
    try:
        service = request.app.state.ai_model_config_service
        deleted = await service.delete_config()

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


@router.get("/providers", response_model=List[ProviderSchema])
async def list_providers() -> List[ProviderSchema]:
    """List all available AI model providers with full schemas.

    Returns:
        List of ProviderSchema objects
    """
    try:
        providers = ProviderCatalog.list_providers()
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
