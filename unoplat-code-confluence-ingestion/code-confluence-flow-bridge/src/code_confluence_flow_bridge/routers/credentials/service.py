from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from unoplat_code_confluence_commons.base_models import Credentials, Flag
from unoplat_code_confluence_commons.credential_enums import (
    CredentialNamespace,
    ProviderKey,
    SecretKind,
)
from unoplat_code_confluence_commons.security import encrypt_token

TOKEN_SUBMITTED_FLAG_NAME = "isTokenSubmitted"


def extract_bearer_token(authorization: str) -> str:
    """Extract the bearer token from an Authorization header."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header")
    return authorization[7:].strip()


def build_credential_metadata(url: str | None) -> dict[str, str] | None:
    """Build credential metadata for provider-specific configuration."""
    return {"url": url} if url else None


async def get_credential(
    session: AsyncSession,
    namespace: CredentialNamespace,
    provider_key: ProviderKey,
    secret_kind: SecretKind,
) -> Credentials | None:
    """Fetch a stored credential by namespace/provider/secret kind."""
    result = await session.execute(
        select(Credentials)
        .where(Credentials.namespace == namespace)
        .where(Credentials.provider_key == provider_key)
        .where(Credentials.secret_kind == secret_kind)
    )
    return result.scalars().first()


async def set_token_submitted_flag(session: AsyncSession, status: bool) -> None:
    """Persist the token submission flag after credential mutations."""
    result = await session.execute(
        select(Flag).where(Flag.name == TOKEN_SUBMITTED_FLAG_NAME)
    )
    token_flag: Flag | None = result.scalar_one_or_none()

    if token_flag is None:
        token_flag = Flag(name=TOKEN_SUBMITTED_FLAG_NAME, status=status)
    else:
        token_flag.status = status

    session.add(token_flag)


async def create_credential(
    session: AsyncSession,
    token: str,
    namespace: CredentialNamespace,
    provider_key: ProviderKey,
    secret_kind: SecretKind,
    url: str | None,
) -> None:
    """Create a new stored credential and mark token submission as complete."""
    credential = await get_credential(session, namespace, provider_key, secret_kind)
    if credential is not None:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Credential for {namespace.value}/{provider_key.value}/{secret_kind.value} "
                "already exists. Use update-token to update it."
            ),
        )

    current_time = datetime.now(timezone.utc)
    session.add(
        Credentials(
            namespace=namespace,
            provider_key=provider_key,
            secret_kind=secret_kind,
            token_hash=encrypt_token(token),
            metadata_json=build_credential_metadata(url),
            created_at=current_time,
            updated_at=current_time,
        )
    )
    await set_token_submitted_flag(session, status=True)


async def update_credential(
    session: AsyncSession,
    token: str,
    namespace: CredentialNamespace,
    provider_key: ProviderKey,
    secret_kind: SecretKind,
    url: str | None,
) -> None:
    """Update an existing stored credential."""
    credential = await get_credential(session, namespace, provider_key, secret_kind)
    if credential is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"No credential found for {namespace.value}/{provider_key.value}/"
                f"{secret_kind.value}"
            ),
        )

    credential.token_hash = encrypt_token(token)
    credential.updated_at = datetime.now(timezone.utc)

    if url:
        credential.metadata_json = build_credential_metadata(url)

    session.add(credential)


async def delete_credential(
    session: AsyncSession,
    namespace: CredentialNamespace,
    provider_key: ProviderKey,
    secret_kind: SecretKind,
) -> None:
    """Delete a stored credential and mark token submission as absent."""
    credential = await get_credential(session, namespace, provider_key, secret_kind)
    if credential is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"No credential found for {namespace.value}/{provider_key.value}/"
                f"{secret_kind.value}"
            ),
        )

    await session.delete(credential)
    await set_token_submitted_flag(session, status=False)
