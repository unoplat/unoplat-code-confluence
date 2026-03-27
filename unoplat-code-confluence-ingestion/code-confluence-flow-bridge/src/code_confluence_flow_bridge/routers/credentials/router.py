"""Credential management API endpoints."""

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from unoplat_code_confluence_commons.credential_enums import (
    CredentialNamespace,
    ProviderKey,
    SecretKind,
)

from src.code_confluence_flow_bridge.processor.db.postgres.db import get_session
from src.code_confluence_flow_bridge.routers.credentials.service import (
    create_credential,
    delete_credential,
    extract_bearer_token,
    update_credential,
)

router = APIRouter(prefix="", tags=["Credentials"])


@router.post("/ingest-token", status_code=201)
async def ingest_token(
    authorization: str = Header(...),
    namespace: CredentialNamespace = Query(..., description="Credential namespace"),
    provider_key: ProviderKey = Query(..., description="Provider key"),
    secret_kind: SecretKind = Query(..., description="Secret kind"),
    url: str | None = Query(
        None, description="Base URL for enterprise/self-hosted instances"
    ),
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    token = extract_bearer_token(authorization)

    try:
        await create_credential(
            session=session,
            token=token,
            namespace=namespace,
            provider_key=provider_key,
            secret_kind=secret_kind,
            url=url,
        )
        return {"message": "Token ingested successfully."}
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Failed to process token: {}", str(exc))
        raise HTTPException(
            status_code=500, detail="Failed to process token: {}".format(str(exc))
        )


@router.put("/update-token", status_code=200)
async def update_token_endpoint(
    authorization: str = Header(...),
    namespace: CredentialNamespace = Query(..., description="Credential namespace"),
    provider_key: ProviderKey = Query(..., description="Provider key"),
    secret_kind: SecretKind = Query(..., description="Secret kind"),
    url: str | None = Query(
        None, description="Base URL for enterprise/self-hosted instances"
    ),
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    token = extract_bearer_token(authorization)

    try:
        await update_credential(
            session=session,
            token=token,
            namespace=namespace,
            provider_key=provider_key,
            secret_kind=secret_kind,
            url=url,
        )
        return {"message": "Token updated successfully."}
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Failed to update token: {}", str(exc))
        raise HTTPException(
            status_code=500, detail="Failed to update authentication token"
        )


@router.delete("/delete-token", status_code=200)
async def delete_token_endpoint(
    namespace: CredentialNamespace = Query(..., description="Credential namespace"),
    provider_key: ProviderKey = Query(..., description="Provider key"),
    secret_kind: SecretKind = Query(..., description="Secret kind"),
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    try:
        await delete_credential(
            session=session,
            namespace=namespace,
            provider_key=provider_key,
            secret_kind=secret_kind,
        )
        return {"message": "Token deleted successfully."}
    except HTTPException as http_ex:
        raise http_ex
    except Exception as exc:
        logger.error("Failed to delete token: {}", str(exc))
        raise HTTPException(
            status_code=500, detail="Failed to delete authentication token"
        )
