"""Service for AI model configuration database operations."""

from datetime import datetime
from typing import Optional

from loguru import logger
from sqlalchemy.exc import SQLAlchemyError

from unoplat_code_confluence_query_engine.db.postgres.ai_model_config import (
    AiModelConfig,
)
from unoplat_code_confluence_query_engine.db.postgres.db import get_session
from unoplat_code_confluence_query_engine.models.ai_model_config import (
    AiModelConfigIn,
    AiModelConfigOut,
    ProviderKind,
)
from unoplat_code_confluence_query_engine.services.credentials_service import (
    CredentialsService,
)
from unoplat_code_confluence_query_engine.services.provider_catalog import (
    ProviderCatalog,
)


class AiModelConfigService:
    """Service for managing AI model configuration (single-record approach)."""
    
    def __init__(self) -> None:
        self.credentials_service = CredentialsService()
    
    async def get_config(self) -> Optional[AiModelConfigOut]:
        """Get the current AI model configuration.
        
        Returns:
            AiModelConfigOut if configuration exists, None otherwise
        """
        try:
            async with get_session() as session:
                config = await session.get(AiModelConfig, 1)
                
                if not config:
                    return None
                
                # Check for stored credentials
                has_api_key = await self.credentials_service.credential_exists(
                    "model_api_key", session=session
                )
                
                return AiModelConfigOut(
                    provider_key=config.provider_key,
                    model_name=config.model_name,
                    provider_name=(config.extra_config or {}).get("provider_name"),
                    provider_kind=ProviderKind(config.provider_kind) if config.provider_kind else None,
                    base_url=config.base_url,
                    profile_key=config.profile_key,
                    extra_config=config.extra_config,
                    temperature=config.temperature,
                    top_p=config.top_p,
                    max_tokens=config.max_tokens,
                    has_api_key=has_api_key,
                    created_at=config.created_at,
                    updated_at=config.updated_at
                )
                
        except SQLAlchemyError as e:
            logger.error("Database error getting AI model config: {}", e)
            raise
        except Exception as e:
            logger.error("Unexpected error getting AI model config: {}", e)
            raise
    
    async def upsert_config(self, config_in: AiModelConfigIn, api_key: str | None = None) -> AiModelConfigOut:
        """Create or update AI model configuration.
        
        Args:
            config_in: Input configuration data
            api_key: API key from header (unified for all providers)
            
        Returns:
            AiModelConfigOut with the saved configuration
            
        Raises:
            ValueError: If provider_key is unknown
        """
        # Validate provider exists in catalog
        provider_schema = ProviderCatalog.get_provider(config_in.provider_key)
        if not provider_schema:
            raise ValueError(f"Unknown provider: {config_in.provider_key}")
        
        # Infer provider_kind if not provided
        provider_kind = config_in.provider_kind or ProviderCatalog.get_provider_kind(config_in.provider_key)
        if not provider_kind:
            raise ValueError(f"Could not determine provider kind for: {config_in.provider_key}")
        
        try:
            async with get_session() as session:
                # Check if config exists
                existing_config = await session.get(AiModelConfig, 1)
                
                current_time = datetime.utcnow()
                
                if existing_config:
                    # Compute changed fields for debug visibility
                    changed_fields = []
                    if existing_config.provider_key != config_in.provider_key:
                        changed_fields.append("provider_key")
                    if existing_config.model_name != config_in.model_name:
                        changed_fields.append("model_name")
                    if existing_config.provider_kind != provider_kind:
                        changed_fields.append("provider_kind")
                    if existing_config.base_url != config_in.base_url:
                        changed_fields.append("base_url")
                    if existing_config.profile_key != config_in.profile_key:
                        changed_fields.append("profile_key")
                    if existing_config.extra_config != config_in.extra_config:
                        changed_fields.append("extra_config")
                    # Track provider_name change even if embedded in extra_config
                    prev_provider_name = (existing_config.extra_config or {}).get("provider_name")
                    if config_in.provider_name is not None and prev_provider_name != config_in.provider_name:
                        changed_fields.append("provider_name")
                    if existing_config.temperature != config_in.temperature:
                        changed_fields.append("temperature")
                    if existing_config.top_p != config_in.top_p:
                        changed_fields.append("top_p")
                    if existing_config.max_tokens != config_in.max_tokens:
                        changed_fields.append("max_tokens")
                    logger.debug(
                        "Upserting AI config; fields changing: {}",
                        changed_fields,
                    )
                    # Update existing config
                    existing_config.provider_key = config_in.provider_key
                    existing_config.model_name = config_in.model_name
                    existing_config.provider_kind = provider_kind
                    existing_config.base_url = config_in.base_url
                    existing_config.profile_key = config_in.profile_key
                    # Merge extra_config with provider_name if supplied at top level
                    merged_extra = dict(existing_config.extra_config or {})
                    # Start from input extra_config if provided
                    if config_in.extra_config:
                        merged_extra.update(config_in.extra_config)
                    if config_in.provider_name is not None:
                        merged_extra["provider_name"] = config_in.provider_name
                    existing_config.extra_config = merged_extra
                    existing_config.temperature = config_in.temperature
                    existing_config.top_p = config_in.top_p
                    existing_config.max_tokens = config_in.max_tokens
                    existing_config.updated_at = current_time
                    
                    saved_config = existing_config
                    logger.info("Updated AI model config for provider: {}", config_in.provider_key)
                else:
                    # Create new config
                    # Merge extra_config with provider_name if provided
                    merged_extra = dict(config_in.extra_config or {})
                    if config_in.provider_name is not None:
                        merged_extra["provider_name"] = config_in.provider_name

                    new_config = AiModelConfig(
                        id=1,  # Always use id=1 for single-record approach
                        provider_key=config_in.provider_key,
                        model_name=config_in.model_name,
                        provider_kind=provider_kind,
                        base_url=config_in.base_url,
                        profile_key=config_in.profile_key,
                        extra_config=merged_extra,
                        temperature=config_in.temperature,
                        top_p=config_in.top_p,
                        max_tokens=config_in.max_tokens,
                        created_at=current_time,
                        updated_at=current_time
                    )
                    session.add(new_config)
                    saved_config = new_config
                    logger.info("Created AI model config for provider: {}", config_in.provider_key)
                
                # Context manager handles commit/rollback automatically
                # Store credentials if provided
                if api_key is not None:
                    await self.credentials_service.upsert_credential(
                        "model_api_key", api_key, session=session
                    )
                
                # Check for stored credentials for response
                has_api_key = await self.credentials_service.credential_exists(
                    "model_api_key", session=session
                )
                logger.debug(
                    "Upsert complete (pre-commit context exit): has_api_key={}",
                    has_api_key,
                )
                
                return AiModelConfigOut(
                    provider_key=saved_config.provider_key,
                    model_name=saved_config.model_name,
                    provider_name=(saved_config.extra_config or {}).get("provider_name"),
                    provider_kind=ProviderKind(saved_config.provider_kind) if saved_config.provider_kind else None,
                    base_url=saved_config.base_url,
                    profile_key=saved_config.profile_key,
                    extra_config=saved_config.extra_config,
                    temperature=saved_config.temperature,
                    top_p=saved_config.top_p,
                    max_tokens=saved_config.max_tokens,
                    has_api_key=has_api_key,
                    created_at=saved_config.created_at,
                    updated_at=saved_config.updated_at
                )
                
        except SQLAlchemyError as e:
            logger.error("Database error upserting AI model config: {}", e)
            raise
        except Exception as e:
            logger.error("Unexpected error upserting AI model config: {}", e)
            raise
    
    async def delete_config(self) -> bool:
        """Delete the current AI model configuration.
        
        Returns:
            True if configuration was deleted, False if no configuration existed
        """
        try:
            async with get_session() as session:
                config = await session.get(AiModelConfig, 1)
                # Context manager handles commit/rollback automatically
                if config:
                    await session.delete(config)
                    # Also delete stored credentials
                    await self.credentials_service.delete_credential("model_api_key", session=session)
                    logger.info("Deleted AI model configuration and credentials")
                    return True
                else:
                    logger.info("No AI model configuration to delete")
                    return False
                    
        except SQLAlchemyError as e:
            logger.error("Database error deleting AI model config: {}", e)
            raise
        except Exception as e:
            logger.error("Unexpected error deleting AI model config: {}", e)
            raise
    
    async def config_exists(self) -> bool:
        """Check if AI model configuration exists.
        
        Returns:
            True if configuration exists, False otherwise
        """
        try:
            async with get_session() as session:
                return (await session.get(AiModelConfig, 1)) is not None
                
        except SQLAlchemyError as e:
            logger.error("Database error checking AI model config existence: {}", e)
            raise
        except Exception as e:
            logger.error("Unexpected error checking AI model config existence: {}", e)
            raise
