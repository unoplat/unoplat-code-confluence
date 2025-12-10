"""Service for AI model configuration database operations."""

from datetime import datetime
from typing import Optional

from loguru import logger
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from unoplat_code_confluence_query_engine.db.postgres.ai_model_config import (
    AiModelConfig,
)
from unoplat_code_confluence_query_engine.models.config.ai_model_config import (
    AiModelConfigIn,
    AiModelConfigOut,
    ProviderKind,
)
from unoplat_code_confluence_query_engine.services.config.credentials_service import (
    CredentialsService,
)
from unoplat_code_confluence_query_engine.services.config.provider_catalog import (
    ProviderCatalog,
)


class AiModelConfigService:
    """Service for managing AI model configuration (single-record approach)."""

    def __init__(self) -> None:
        self.credentials_service = CredentialsService()

    async def get_config(self, session: AsyncSession) -> Optional[AiModelConfigOut]:
        """Get the current AI model configuration.

        Args:
            session: Database session

        Returns:
            AiModelConfigOut if configuration exists, None otherwise
        """
        try:
            config = await session.get(AiModelConfig, 1)

            if not config:
                return None

            # Check for stored credentials
            has_api_key = await self.credentials_service.model_credential_exists(
                session
            )

            return AiModelConfigOut(
                provider_key=config.provider_key,
                model_name=config.model_name,
                provider_name=(config.extra_config or {}).get("provider_name"),
                provider_kind=ProviderKind(config.provider_kind)
                if config.provider_kind
                else None,
                base_url=config.base_url,
                profile_key=config.profile_key,
                extra_config=config.extra_config,
                temperature=config.temperature,
                top_p=config.top_p,
                max_tokens=config.max_tokens,
                has_api_key=has_api_key,
                created_at=config.created_at,
                updated_at=config.updated_at,
            )

        except SQLAlchemyError as e:
            logger.error("Database error getting AI model config: {}", e)
            raise
        except Exception as e:
            logger.error("Unexpected error getting AI model config: {}", e)
            raise

    async def upsert_config(
        self, config_in: AiModelConfigIn, api_key: str | None, session: AsyncSession
    ) -> AiModelConfigOut:
        """Create or update AI model configuration.

        Args:
            config_in: Input configuration data
            api_key: API key from header (unified for all providers)
            session: Database session

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
        provider_kind = config_in.provider_kind or ProviderCatalog.get_provider_kind(
            config_in.provider_key
        )
        if not provider_kind:
            raise ValueError(
                f"Could not determine provider kind for: {config_in.provider_key}"
            )

        try:
            # Check if config exists
            existing_config = await session.get(AiModelConfig, 1)

            current_time = datetime.utcnow()

            if existing_config:
                # Update existing config
                existing_config.provider_key = config_in.provider_key
                existing_config.model_name = config_in.model_name
                existing_config.provider_kind = provider_kind
                existing_config.base_url = config_in.base_url
                existing_config.profile_key = config_in.profile_key
                # Build a fresh extra_config and FILTER unsupported keys for the provider.
                # This ensures stale keys (e.g., provider_name from a previous provider) do not persist.
                provider_schema_fields = ProviderCatalog.get_provider(
                    config_in.provider_key
                ).fields  # type: ignore[union-attr]
                allowed_keys = {f.key for f in provider_schema_fields}
                # Start from input extra_config only (no merge with existing)
                incoming_extra = dict(config_in.extra_config or {})
                # Never persist credentials in DB even if sent accidentally
                incoming_extra.pop("model_api_key", None)
                # Apply top-level provider_name only if supported by the provider schema
                if (
                    config_in.provider_name is not None
                    and "provider_name" in allowed_keys
                ):
                    incoming_extra["provider_name"] = config_in.provider_name
                # Filter extras to provider-supported keys
                filtered_extra = {
                    k: v for k, v in incoming_extra.items() if k in allowed_keys
                }
                existing_config.extra_config = filtered_extra
                existing_config.temperature = config_in.temperature
                existing_config.top_p = config_in.top_p
                existing_config.max_tokens = config_in.max_tokens
                existing_config.updated_at = current_time

                saved_config = existing_config
                logger.info(
                    "Updated AI model config for provider: {}",
                    config_in.provider_key,
                )
            else:
                # Create new config
                # Build fresh extra_config and filter keys to provider schema
                provider_schema_fields = ProviderCatalog.get_provider(
                    config_in.provider_key
                ).fields  # type: ignore[union-attr]
                allowed_keys = {f.key for f in provider_schema_fields}
                incoming_extra = dict(config_in.extra_config or {})
                incoming_extra.pop("model_api_key", None)
                if (
                    config_in.provider_name is not None
                    and "provider_name" in allowed_keys
                ):
                    incoming_extra["provider_name"] = config_in.provider_name
                merged_extra = {
                    k: v for k, v in incoming_extra.items() if k in allowed_keys
                }

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
                    updated_at=current_time,
                )
                session.add(new_config)
                saved_config = new_config
                logger.info(
                    "Created AI model config for provider: {}",
                    config_in.provider_key,
                )

            # Store credentials if provided
            if api_key is not None:
                await self.credentials_service.upsert_model_credential(api_key, session)

            # Check for stored credentials for response
            has_api_key = await self.credentials_service.model_credential_exists(
                session
            )
            logger.debug(
                "Upsert complete (pre-commit context exit): has_api_key={}",
                has_api_key,
            )

            return AiModelConfigOut(
                provider_key=saved_config.provider_key,
                model_name=saved_config.model_name,
                provider_name=(saved_config.extra_config or {}).get("provider_name"),
                provider_kind=ProviderKind(saved_config.provider_kind)
                if saved_config.provider_kind
                else None,
                base_url=saved_config.base_url,
                profile_key=saved_config.profile_key,
                extra_config=saved_config.extra_config,
                temperature=saved_config.temperature,
                top_p=saved_config.top_p,
                max_tokens=saved_config.max_tokens,
                has_api_key=has_api_key,
                created_at=saved_config.created_at,
                updated_at=saved_config.updated_at,
            )

        except SQLAlchemyError as e:
            logger.error("Database error upserting AI model config: {}", e)
            raise
        except Exception as e:
            logger.error("Unexpected error upserting AI model config: {}", e)
            raise

    async def delete_config(self, session: AsyncSession) -> bool:
        """Delete the current AI model configuration.

        Args:
            session: Database session

        Returns:
            True if configuration was deleted, False if no configuration existed
        """
        try:
            config = await session.get(AiModelConfig, 1)
            if config:
                await session.delete(config)
                # Also delete stored credentials
                await self.credentials_service.delete_model_credential(session)
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

    async def config_exists(self, session: AsyncSession) -> bool:
        """Check if AI model configuration exists.

        Args:
            session: Database session

        Returns:
            True if configuration exists, False otherwise
        """
        try:
            return (await session.get(AiModelConfig, 1)) is not None

        except SQLAlchemyError as e:
            logger.error(f"Database error checking AI model config existence: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error checking AI model config existence: {e}")
            raise
