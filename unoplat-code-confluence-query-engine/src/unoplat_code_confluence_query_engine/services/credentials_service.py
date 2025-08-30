"""Service for managing encrypted credentials via the shared credentials table."""

import os
from datetime import datetime
from typing import Optional

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from unoplat_code_confluence_commons.credentials import Credentials
from unoplat_code_confluence_commons.security import decrypt_token, encrypt_token

from unoplat_code_confluence_query_engine.db.postgres.db import get_session


class CredentialsService:
    """Read/write encrypted credentials via the shared credentials table."""

    @staticmethod
    async def get_credential(credential_key: str, session: Optional[AsyncSession] = None) -> Optional[str]:
        """Get decrypted credential value by key.
        
        Args:
            credential_key: The key identifying the credential (e.g., 'model_api_key', 'github_pat')
            
        Returns:
            Decrypted credential value or None if not found
        """
        if session is None:
            async with get_session() as s:
                result = await s.execute(
                    select(Credentials).where(Credentials.credential_key == credential_key)
                )
                row = result.scalars().first()
        else:
            result = await session.execute(
                select(Credentials).where(Credentials.credential_key == credential_key)
            )
            row = result.scalars().first()

        if not row:
            logger.debug(f"No credential found for key: {credential_key}")
            return None

        # Set TOKEN_ENCRYPTION_KEY environment variable for decrypt_token
        if not os.getenv("TOKEN_ENCRYPTION_KEY"):
            logger.error("TOKEN_ENCRYPTION_KEY environment variable not set")
            raise ValueError("TOKEN_ENCRYPTION_KEY is required for credential decryption")

        return decrypt_token(row.token_hash)

    @staticmethod
    async def upsert_credential(credential_key: str, value: str, session: Optional[AsyncSession] = None) -> None:
        """Upsert encrypted credential.
        
        Args:
            credential_key: The key identifying the credential
            value: The plaintext credential value to encrypt and store
        """
        # Set TOKEN_ENCRYPTION_KEY environment variable for encrypt_token
        if not os.getenv("TOKEN_ENCRYPTION_KEY"):
            logger.error("TOKEN_ENCRYPTION_KEY environment variable not set")
            raise ValueError("TOKEN_ENCRYPTION_KEY is required for credential encryption")

        encrypted = encrypt_token(value)

        if session is None:
            async with get_session() as s:
                result = await s.execute(
                    select(Credentials).where(Credentials.credential_key == credential_key)
                )
                row = result.scalars().first()

                if row:
                    row.token_hash = encrypted
                    row.updated_at = datetime.utcnow()
                    logger.debug(f"Updated credential for key: {credential_key}")
                else:
                    row = Credentials(
                        credential_key=credential_key,
                        token_hash=encrypted,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow(),
                    )
                    s.add(row)
                    logger.debug(f"Created new credential for key: {credential_key}")
                # Session commit handled by get_session() context manager
        else:
            result = await session.execute(
                select(Credentials).where(Credentials.credential_key == credential_key)
            )
            row = result.scalars().first()

            if row:
                row.token_hash = encrypted
                row.updated_at = datetime.utcnow()
                logger.debug(f"Updated credential for key: {credential_key}")
            else:
                row = Credentials(
                    credential_key=credential_key,
                    token_hash=encrypted,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
                session.add(row)
                logger.debug(f"Created new credential for key: {credential_key}")

    @staticmethod
    async def delete_credential(credential_key: str, session: Optional[AsyncSession] = None) -> bool:
        """Delete a credential by key.
        
        Args:
            credential_key: The key identifying the credential to delete
            
        Returns:
            True if deleted, False if not found
        """
        if session is None:
            async with get_session() as s:
                result = await s.execute(
                    select(Credentials).where(Credentials.credential_key == credential_key)
                )
                row = result.scalars().first()

                if row:
                    await s.delete(row)
                    logger.debug(f"Deleted credential for key: {credential_key}")
                    return True

                logger.debug(f"No credential found to delete for key: {credential_key}")
                return False
        else:
            result = await session.execute(
                select(Credentials).where(Credentials.credential_key == credential_key)
            )
            row = result.scalars().first()

            if row:
                await session.delete(row)
                logger.debug(f"Deleted credential for key: {credential_key}")
                return True

            logger.debug(f"No credential found to delete for key: {credential_key}")
            return False

    @staticmethod
    async def credential_exists(credential_key: str, session: Optional[AsyncSession] = None) -> bool:
        """Check if a credential exists.
        
        Args:
            credential_key: The key identifying the credential
            
        Returns:
            True if credential exists, False otherwise
        """
        if session is None:
            async with get_session() as s:
                result = await s.execute(
                    select(Credentials).where(Credentials.credential_key == credential_key)
                )
                return result.scalars().first() is not None
        else:
            result = await session.execute(
                select(Credentials).where(Credentials.credential_key == credential_key)
            )
            return result.scalars().first() is not None
