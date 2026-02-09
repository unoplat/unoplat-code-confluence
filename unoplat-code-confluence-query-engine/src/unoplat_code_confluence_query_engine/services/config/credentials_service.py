"""Service for managing encrypted credentials via the shared credentials table."""

import os
from datetime import UTC, datetime
from typing import Any, Optional

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from unoplat_code_confluence_commons.credential_enums import (
    CredentialNamespace,
    ProviderKey,
    SecretKind,
)
from unoplat_code_confluence_commons.credentials import Credentials
from unoplat_code_confluence_commons.security import decrypt_token, encrypt_token


class CredentialsService:
    """Read/write encrypted credentials via the shared credentials table."""

    @staticmethod
    async def execute_get_model_secret_query(
        session: AsyncSession, secret_kind: SecretKind
    ) -> Optional[Credentials]:
        result = await session.execute(
            select(Credentials)
            .where(Credentials.namespace == CredentialNamespace.MODEL)
            .where(Credentials.provider_key == ProviderKey.MODEL_PROVIDER_AUTH)
            .where(Credentials.secret_kind == secret_kind)
        )
        return result.scalars().first()

    @staticmethod
    async def execute_get_model_query(session: AsyncSession) -> Optional[Credentials]:
        """Backward-compatible getter for model API key row."""
        return await CredentialsService.execute_get_model_secret_query(
            session, SecretKind.MODEL_API_KEY
        )

    @staticmethod
    async def get_model_secret(
        session: AsyncSession, secret_kind: SecretKind
    ) -> Optional[str]:
        """Get decrypted model secret value for a given secret kind.

        Args:
            session: Database session
            secret_kind: Secret type under MODEL/model_provider_auth

        Returns:
            Decrypted credential value or None if not found
        """
        row = await CredentialsService.execute_get_model_secret_query(
            session, secret_kind
        )

        if not row:
            logger.debug(
                "No model credential found for secret kind: {}", secret_kind.value
            )
            return None

        if not os.getenv("TOKEN_ENCRYPTION_KEY"):
            logger.error("TOKEN_ENCRYPTION_KEY environment variable not set")
            raise ValueError(
                "TOKEN_ENCRYPTION_KEY is required for credential decryption"
            )

        return decrypt_token(row.token_hash)

    @staticmethod
    async def get_model_credential(session: AsyncSession) -> Optional[str]:
        """Get decrypted model API key value."""
        return await CredentialsService.get_model_secret(session, SecretKind.MODEL_API_KEY)

    @staticmethod
    async def upsert_model_secret(
        value: str,
        session: AsyncSession,
        secret_kind: SecretKind,
        metadata_json: Optional[dict[str, Any]] = None,
    ) -> None:
        """Create or update encrypted model secret.

        Args:
            value: The plaintext secret value to encrypt and store
            session: Database session
            secret_kind: Secret type under MODEL/model_provider_auth
            metadata_json: Optional metadata payload to persist
        """
        if not os.getenv("TOKEN_ENCRYPTION_KEY"):
            logger.error("TOKEN_ENCRYPTION_KEY environment variable not set")
            raise ValueError(
                "TOKEN_ENCRYPTION_KEY is required for credential encryption"
            )

        encrypted = encrypt_token(value)

        row = await CredentialsService.execute_get_model_secret_query(
            session, secret_kind
        )

        if row:
            row.token_hash = encrypted
            row.updated_at = datetime.now(UTC)
            row.metadata_json = metadata_json
            logger.debug(
                "Updated model credential for secret kind: {}", secret_kind.value
            )
        else:
            row = Credentials(
                namespace=CredentialNamespace.MODEL,
                provider_key=ProviderKey.MODEL_PROVIDER_AUTH,
                secret_kind=secret_kind,
                token_hash=encrypted,
                metadata_json=metadata_json,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            )
            session.add(row)
            logger.debug(
                "Created new model credential for secret kind: {}", secret_kind.value
            )

    @staticmethod
    async def upsert_model_credential(value: str, session: AsyncSession) -> None:
        """Update encrypted model API key."""
        await CredentialsService.upsert_model_secret(
            value=value,
            session=session,
            secret_kind=SecretKind.MODEL_API_KEY,
            metadata_json=None,
        )

    @staticmethod
    async def delete_model_secret(
        session: AsyncSession, secret_kind: SecretKind
    ) -> bool:
        """Delete model credential for a specific secret kind.

        Args:
            session: Database session
            secret_kind: Secret type under MODEL/model_provider_auth

        Returns:
            True if deleted, False if not found
        """
        row = await CredentialsService.execute_get_model_secret_query(
            session, secret_kind
        )

        if row:
            await session.delete(row)
            logger.debug(
                "Deleted model credential for secret kind: {}", secret_kind.value
            )
            return True

        logger.debug(
            "No model credential found to delete for secret kind: {}",
            secret_kind.value,
        )
        return False

    @staticmethod
    async def delete_model_credential(session: AsyncSession) -> bool:
        """Delete model API key credential."""
        return await CredentialsService.delete_model_secret(
            session, SecretKind.MODEL_API_KEY
        )

    @staticmethod
    async def model_credential_exists(session: AsyncSession) -> bool:
        """Check if model API key exists."""
        row = await CredentialsService.execute_get_model_secret_query(
            session, SecretKind.MODEL_API_KEY
        )
        return row is not None

    @staticmethod
    async def get_model_oauth_access_metadata(
        session: AsyncSession,
    ) -> Optional[dict[str, Any]]:
        """Get metadata for model OAuth access token row."""
        row = await CredentialsService.execute_get_model_secret_query(
            session, SecretKind.OAUTH_ACCESS_TOKEN
        )
        if not row:
            return None
        metadata = row.metadata_json
        return metadata if isinstance(metadata, dict) else None

    @staticmethod
    async def get_model_oauth_access_token(session: AsyncSession) -> Optional[str]:
        """Get decrypted model OAuth access token."""
        return await CredentialsService.get_model_secret(
            session, SecretKind.OAUTH_ACCESS_TOKEN
        )

    @staticmethod
    async def get_model_oauth_refresh_token(session: AsyncSession) -> Optional[str]:
        """Get decrypted model OAuth refresh token."""
        return await CredentialsService.get_model_secret(
            session, SecretKind.OAUTH_REFRESH_TOKEN
        )

    @staticmethod
    async def upsert_model_oauth_credentials(
        session: AsyncSession,
        *,
        access_token: str,
        refresh_token: str,
        id_token: Optional[str],
        expires_at: int,
        account_id: Optional[str],
    ) -> None:
        """Persist model OAuth credentials under MODEL/model_provider_auth."""
        metadata: dict[str, Any] = {"expires_at": expires_at}
        if account_id:
            metadata["account_id"] = account_id

        await CredentialsService.upsert_model_secret(
            value=access_token,
            session=session,
            secret_kind=SecretKind.OAUTH_ACCESS_TOKEN,
            metadata_json=metadata,
        )
        await CredentialsService.upsert_model_secret(
            value=refresh_token,
            session=session,
            secret_kind=SecretKind.OAUTH_REFRESH_TOKEN,
            metadata_json=None,
        )
        if id_token:
            await CredentialsService.upsert_model_secret(
                value=id_token,
                session=session,
                secret_kind=SecretKind.OAUTH_ID_TOKEN,
                metadata_json=None,
            )

    @staticmethod
    async def delete_model_oauth_credentials(session: AsyncSession) -> bool:
        """Delete all model OAuth credential rows."""
        deleted_access = await CredentialsService.delete_model_secret(
            session, SecretKind.OAUTH_ACCESS_TOKEN
        )
        deleted_refresh = await CredentialsService.delete_model_secret(
            session, SecretKind.OAUTH_REFRESH_TOKEN
        )
        deleted_id = await CredentialsService.delete_model_secret(
            session, SecretKind.OAUTH_ID_TOKEN
        )
        return deleted_access or deleted_refresh or deleted_id

    @staticmethod
    async def model_oauth_connected(session: AsyncSession) -> bool:
        """Connected when refresh token exists for model OAuth."""
        row = await CredentialsService.execute_get_model_secret_query(
            session, SecretKind.OAUTH_REFRESH_TOKEN
        )
        return row is not None

    # ─── Tool Credential Methods ───────────────────────────────────────────────

    @staticmethod
    async def execute_get_tool_query(
        session: AsyncSession, provider_key: ProviderKey
    ) -> Optional[Credentials]:
        """Execute query to get tool credential by provider key.

        Args:
            session: Database session
            provider_key: The tool provider key (e.g., ProviderKey.EXA)

        Returns:
            Credentials row if found, None otherwise
        """
        result = await session.execute(
            select(Credentials)
            .where(Credentials.namespace == CredentialNamespace.TOOL)
            .where(Credentials.provider_key == provider_key)
            .where(Credentials.secret_kind == SecretKind.TOOL_API_KEY)
        )
        return result.scalars().first()

    @staticmethod
    async def get_tool_credential(
        session: AsyncSession, provider_key: ProviderKey
    ) -> Optional[str]:
        """Get decrypted tool credential value.

        Args:
            session: Database session
            provider_key: The tool provider key (e.g., ProviderKey.EXA)

        Returns:
            Decrypted credential value or None if not found
        """
        row = await CredentialsService.execute_get_tool_query(session, provider_key)

        if not row:
            logger.debug(
                "No tool credential found for provider: {}", provider_key.value
            )
            return None

        if not os.getenv("TOKEN_ENCRYPTION_KEY"):
            logger.error("TOKEN_ENCRYPTION_KEY environment variable not set")
            raise ValueError(
                "TOKEN_ENCRYPTION_KEY is required for credential decryption"
            )

        return decrypt_token(row.token_hash)

    @staticmethod
    async def tool_credential_exists(
        session: AsyncSession, provider_key: ProviderKey
    ) -> bool:
        """Check if tool credential exists.

        Args:
            session: Database session
            provider_key: The tool provider key (e.g., ProviderKey.EXA)

        Returns:
            True if credential exists, False otherwise
        """
        row = await CredentialsService.execute_get_tool_query(session, provider_key)
        return row is not None

    @staticmethod
    async def upsert_tool_credential(
        value: str, provider_key: ProviderKey, session: AsyncSession
    ) -> None:
        """Create or update encrypted tool credential.

        Args:
            value: The plaintext credential value to encrypt and store
            provider_key: The tool provider key (e.g., ProviderKey.EXA)
            session: Database session
        """
        if not os.getenv("TOKEN_ENCRYPTION_KEY"):
            logger.error("TOKEN_ENCRYPTION_KEY environment variable not set")
            raise ValueError(
                "TOKEN_ENCRYPTION_KEY is required for credential encryption"
            )

        encrypted = encrypt_token(value)

        row = await CredentialsService.execute_get_tool_query(session, provider_key)
        if row:
            row.token_hash = encrypted
            row.updated_at = datetime.now(UTC)
            logger.debug("Updated tool credential for provider: {}", provider_key.value)
        else:
            row = Credentials(
                namespace=CredentialNamespace.TOOL,
                provider_key=provider_key,
                secret_kind=SecretKind.TOOL_API_KEY,
                token_hash=encrypted,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            )
            session.add(row)
            logger.debug("Created new tool credential for provider: {}", provider_key.value)

    @staticmethod
    async def delete_tool_credential(
        session: AsyncSession, provider_key: ProviderKey
    ) -> bool:
        """Delete tool credential for provider.

        Args:
            session: Database session
            provider_key: The tool provider key (e.g., ProviderKey.EXA)

        Returns:
            True if deleted, False if not found
        """
        row = await CredentialsService.execute_get_tool_query(session, provider_key)
        if not row:
            return False
        await session.delete(row)
        logger.debug("Deleted tool credential for provider: {}", provider_key.value)
        return True
