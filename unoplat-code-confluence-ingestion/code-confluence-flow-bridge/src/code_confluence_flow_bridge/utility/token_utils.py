from typing import Any, Dict, Optional, Tuple

from fastapi import HTTPException
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from unoplat_code_confluence_commons.base_models import Credentials
from unoplat_code_confluence_commons.credential_enums import (
    CredentialNamespace,
    ProviderKey,
    SecretKind,
)
from unoplat_code_confluence_commons.security import decrypt_token


async def fetch_repository_provider_token(
    session: AsyncSession,
    namespace: CredentialNamespace,
    provider_key: ProviderKey,
) -> Tuple[str, Optional[Dict[str, Any]]]:
    """
    Fetch and decrypt repository provider token from database using enums.

    Args:
        session: Database session
        namespace: Credential namespace (e.g., REPOSITORY)
        provider_key: Provider key (e.g., GITHUB_OPEN, GITHUB_ENTERPRISE, GITLAB_CE)

    Returns:
        Tuple of (decrypted token, metadata_json dict or None)

    Raises:
        HTTPException: If no credentials found or decryption fails
    """
    try:
        result = await session.execute(
            select(Credentials)
            .where(Credentials.namespace == namespace)
            .where(Credentials.provider_key == provider_key)
            .where(Credentials.secret_kind == SecretKind.PAT)
        )
        credential: Optional[Credentials] = result.scalars().first()
    except Exception as db_error:
        logger.error("Database error while fetching credentials: {}", db_error)
        raise HTTPException(
            status_code=500, detail="Database error while fetching credentials"
        )

    if not credential:
        raise HTTPException(
            status_code=404,
            detail=f"No credentials found for {namespace.value}/{provider_key.value}",
        )

    try:
        decrypted_token = decrypt_token(credential.token_hash)
        return decrypted_token, credential.metadata_json
    except Exception as decrypt_error:
        logger.error("Failed to decrypt token: {}", decrypt_error)
        raise HTTPException(
            status_code=500,
            detail="Internal error during authentication token decryption",
        )
