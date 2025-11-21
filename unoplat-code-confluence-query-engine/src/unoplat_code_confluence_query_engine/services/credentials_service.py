"""Service for managing encrypted credentials via the shared credentials table."""

import os
from datetime import datetime
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
            row.updated_at = datetime.now()
            logger.debug("Updated model credential")
        else:
            row = Credentials(
                namespace=CredentialNamespace.MODEL,
                provider_key=ProviderKey.MODEL_PROVIDER_AUTH,
                secret_kind=SecretKind.MODEL_API_KEY,
                token_hash=encrypted,
                created_at=datetime.now(),
                updated_at=datetime.now(),
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
