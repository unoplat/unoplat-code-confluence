"""Service for managing encrypted credentials via the shared credentials table."""

import os
from datetime import UTC, datetime
from typing import Optional

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
    async def execute_get_model_query(session: AsyncSession) -> Optional[Credentials]:
        result = await session.execute(
            select(Credentials)
            .where(Credentials.namespace == CredentialNamespace.MODEL)
            .where(Credentials.provider_key == ProviderKey.MODEL_PROVIDER_AUTH)
            .where(Credentials.secret_kind == SecretKind.MODEL_API_KEY)
        )
        return result.scalars().first()

    @staticmethod
    async def get_model_credential(session: AsyncSession) -> Optional[str]:
        """Get decrypted credential value by key.

        Args:
            session: Database session

        Returns:
            Decrypted credential value or None if not found
        """
        row = await CredentialsService.execute_get_model_query(session)

        if not row:
            logger.debug(f"No credential found for key: {CredentialNamespace.MODEL}")
            return None

        # Set TOKEN_ENCRYPTION_KEY environment variable for decrypt_token
        if not os.getenv("TOKEN_ENCRYPTION_KEY"):
            logger.error("TOKEN_ENCRYPTION_KEY environment variable not set")
            raise ValueError(
                "TOKEN_ENCRYPTION_KEY is required for credential decryption"
            )

        return decrypt_token(row.token_hash)

    @staticmethod
    async def upsert_model_credential(value: str, session: AsyncSession) -> None:
        """Update encrypted model credential.

        Args:
            value: The plaintext credential value to encrypt and store
            session: Database session
        """
        # Set TOKEN_ENCRYPTION_KEY environment variable for encrypt_token
        if not os.getenv("TOKEN_ENCRYPTION_KEY"):
            logger.error("TOKEN_ENCRYPTION_KEY environment variable not set")
            raise ValueError(
                "TOKEN_ENCRYPTION_KEY is required for credential encryption"
            )

        encrypted = encrypt_token(value)

        row = await CredentialsService.execute_get_model_query(session)

        if row:
            row.token_hash = encrypted
            row.updated_at = datetime.now(UTC)
            logger.debug("Updated model credential")
        else:
            row = Credentials(
                namespace=CredentialNamespace.MODEL,
                provider_key=ProviderKey.MODEL_PROVIDER_AUTH,
                secret_kind=SecretKind.MODEL_API_KEY,
                token_hash=encrypted,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            )
            session.add(row)
            logger.debug("Created new model credential")

    @staticmethod
    async def delete_model_credential(session: AsyncSession) -> bool:
        """Delete model credential.

        Args:
            session: Database session

        Returns:
            True if deleted, False if not found
        """
        row = await CredentialsService.execute_get_model_query(session)

        if row:
            await session.delete(row)
            logger.debug("Deleted model credential")
            return True

        logger.debug("No model credential found to delete")
        return False

    @staticmethod
    async def model_credential_exists(session: AsyncSession) -> bool:
        """Check if model credential exists.

        Args:
            session: Database session

        Returns:
            True if credential exists, False otherwise
        """
        row = await CredentialsService.execute_get_model_query(session)
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
