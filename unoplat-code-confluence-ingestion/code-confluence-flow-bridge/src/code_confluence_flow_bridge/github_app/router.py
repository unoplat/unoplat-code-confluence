"""FastAPI router exposing GitHub App onboarding endpoints."""

from __future__ import annotations

from datetime import datetime, timezone

# Standard Library
import hashlib
import hmac
import json
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

# Third Party
import httpx
from loguru import logger
from pydantic import AnyHttpUrl
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio.scoping import async_scoped_session

from src.code_confluence_flow_bridge.github_app.models import (
    ManifestConversionResponse,
    ManifestGenerationRequest,
    ManifestGenerationResponse,
)
from src.code_confluence_flow_bridge.github_app.service import (
    build_absolute_url,
    build_registration_url,
    cleanup_expired_manifest_requests,
    delete_manifest_record,
    fetch_credential,
    generate_state_token,
    get_manifest_record,
    load_manifest_template,
    persist_manifest_record,
    prepare_manifest,
    store_credential,
)
from src.code_confluence_flow_bridge.models.configuration.settings import (
    EnvironmentSettings,
)

# Local
from src.code_confluence_flow_bridge.processor.db.postgres.db import get_session

router = APIRouter(prefix="/integrations/github", tags=["GitHub App"])

GITHUB_MANIFEST_CONVERSION_ENDPOINT = (
    "https://api.github.com/app-manifests/{code}/conversions"
)


def _resolve_env_settings(request: Request) -> EnvironmentSettings:
    """Retrieve the cached environment configuration from the FastAPI app."""
    env_settings: EnvironmentSettings = request.app.state.code_confluence_env
    if not isinstance(env_settings, EnvironmentSettings):
        raise RuntimeError(
            "Environment settings have not been initialised on the FastAPI app."
        )
    return env_settings


@router.post(
    "/app-manifest",
    response_model=ManifestGenerationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_manifest(
    payload: ManifestGenerationRequest,
    request: Request,
    session: async_scoped_session = Depends(get_session),  # pyright:ignore
) -> ManifestGenerationResponse:
    """Generate a manifest JSON payload and registration URL for the operator."""
    env_settings = _resolve_env_settings(request)

    # Resolve owner defaults
    owner_login: Optional[str] = payload.owner or env_settings.github_app_owner
    owner_type = payload.owner_type or env_settings.github_app_owner_type
    if owner_type == "organization" and not owner_login:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization owner must be provided when owner_type is 'organization'.",
        )

    await cleanup_expired_manifest_requests(session)

    base_manifest = load_manifest_template(env_settings)
    redirect_url = build_absolute_url(
        str(payload.service_base_url), env_settings.github_app_redirect_path
    )

    service_webhook_url = build_absolute_url(
        str(payload.service_base_url), env_settings.github_app_webhook_path
    )
    webhook_delivery_url = (
        str(payload.webhook_proxy_url)
        if payload.webhook_proxy_url
        else service_webhook_url
    )
    post_install_redirect_url = (
        str(payload.post_install_redirect_url)
        if payload.post_install_redirect_url
        else None
    )

    manifest = prepare_manifest(
        base_manifest=base_manifest,
        env=env_settings,
        request_payload=payload,
        redirect_url=redirect_url,
        webhook_delivery_url=webhook_delivery_url,
        post_install_redirect_url=post_install_redirect_url,
    )

    state = generate_state_token()
    try:
        registration_url = build_registration_url(owner_type, owner_login, state)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    record = await persist_manifest_record(
        session=session,
        state=state,
        manifest=manifest,
        owner=owner_login,
        owner_type=owner_type,
        registration_url=registration_url,
        env=env_settings,
        requested_by=payload.requested_by,
    )

    logger.info(
        "Generated GitHub App manifest request (state={}, owner={}, owner_type={}, proxy_webhook={})",
        state,
        owner_login,
        owner_type,
        bool(payload.webhook_proxy_url),
    )

    return ManifestGenerationResponse(
        state=state,
        manifest=manifest,
        registration_url=AnyHttpUrl(registration_url),
        owner=owner_login,
        owner_type=owner_type,
        expires_at=record.expires_at,
    )


@router.get(
    "/app-manifest/callback",
    response_model=ManifestConversionResponse,
    status_code=status.HTTP_200_OK,
)
async def manifest_callback(
    code: str,
    state: str,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> ManifestConversionResponse:
    """Exchange the GitHub-provided code for app credentials and persist them."""
    await cleanup_expired_manifest_requests(session)
    record = await get_manifest_record(session, state)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unknown or expired manifest state.",
        )

    if record.expires_at and record.expires_at < datetime.now(timezone.utc):
        await delete_manifest_record(session, record)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Manifest state has expired. Please restart the onboarding flow.",
        )

    conversion_url = GITHUB_MANIFEST_CONVERSION_ENDPOINT.format(code=code)
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                conversion_url,
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "User-Agent": "unoplat-code-confluence",
                },
            )
        except httpx.HTTPError as exc:
            logger.error("Failed to call GitHub manifest conversion endpoint: {}", exc)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to contact GitHub to convert the manifest code.",
            ) from exc

    if response.status_code != status.HTTP_201_CREATED:
        logger.error(
            "GitHub manifest conversion failed (status={}, body={})",
            response.status_code,
            response.text,
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="GitHub rejected the manifest conversion request.",
        )

    app_config = response.json()

    # Persist credentials securely
    await store_credential(session, "github_app_private_key", app_config["pem"])
    await store_credential(
        session, "github_app_webhook_secret", app_config["webhook_secret"]
    )
    await store_credential(session, "github_app_client_id", app_config["client_id"])
    if app_config.get("client_secret"):
        await store_credential(
            session, "github_app_client_secret", app_config["client_secret"]
        )
    await store_credential(session, "github_app_id", str(app_config["id"]))
    await store_credential(session, "github_app_slug", app_config["slug"])

    await delete_manifest_record(session, record)

    slug = app_config["slug"]
    installation_url = f"https://github.com/apps/{slug}/installations/new"

    manage_url = app_config.get("html_url")

    instructions = [
        f"Install the app via {installation_url}.",
        "Store the generated private key PEM in a secure secret store (it has also been encrypted in the service database).",
        "Provide repository access by completing the installation flow for the desired organization or user account.",
    ]

    logger.success(
        "GitHub App manifest flow completed (slug={}, owner={}, owner_type={})",
        slug,
        record.owner_login,
        record.owner_type,
    )

    return ManifestConversionResponse(
        app_slug=slug,
        app_id=app_config["id"],
        client_id=app_config["client_id"],
        html_url=manage_url,
        installation_url=AnyHttpUrl(installation_url),
        instructions=instructions,
    )


@router.post(
    "/webhook",
    status_code=status.HTTP_202_ACCEPTED,
)
async def github_webhook(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> Response:
    """Handle webhook deliveries from GitHub for the self-hosted app."""
    payload_bytes = await request.body()
    signature_header = request.headers.get("x-hub-signature-256")
    event = request.headers.get("x-github-event")

    if not signature_header:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing X-Hub-Signature-256 header.",
        )

    secret = await fetch_credential(session, "github_app_webhook_secret")
    if not secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GitHub App webhook secret is not configured.",
        )

    computed_signature = (
        "sha256="
        + hmac.new(secret.encode("utf-8"), payload_bytes, hashlib.sha256).hexdigest()
    )

    if not hmac.compare_digest(signature_header, computed_signature):
        logger.warning("GitHub webhook signature mismatch for event {}", event)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook signature.",
        )

    if event != "pull_request":
        logger.info("Ignoring unsupported GitHub webhook event: {}", event)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    try:
        payload = json.loads(payload_bytes.decode("utf-8"))
    except json.JSONDecodeError:
        logger.warning("Received malformed JSON payload for GitHub webhook.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload.",
        )

    action = payload.get("action")
    pull_request = payload.get("pull_request", {})
    repo = payload.get("repository", {})

    logger.info(
        "Received pull_request webhook (action={}, repo={}, number={})",
        action,
        repo.get("full_name"),
        pull_request.get("number"),
    )

    # Placeholder: downstream processing (queue workflows, Temporal triggers, etc.)
    # For now we simply acknowledge the event.
    return Response(status_code=status.HTTP_202_ACCEPTED)
