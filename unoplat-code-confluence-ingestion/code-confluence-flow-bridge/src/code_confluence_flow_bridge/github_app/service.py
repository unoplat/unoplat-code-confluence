"""Supporting utilities for GitHub App manifest onboarding."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone

# Standard Library
import json
from pathlib import Path
import secrets
from typing import Any, Dict, Optional

# Third Party
from loguru import logger
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from unoplat_code_confluence_commons.credentials import Credentials
from unoplat_code_confluence_commons.security import decrypt_token, encrypt_token

# Local
from src.code_confluence_flow_bridge.models.configuration.settings import (
    EnvironmentSettings,
)

from .models import (
    GithubAppManifestRecord,
    ManifestGenerationRequest,
)

FALLBACK_MANIFEST: Dict[str, Any] = {
    "name": "Unoplat Code Confluence",
    "url": "https://example.com",
    "public": False,
    "description": "Self-hosted GitHub App for Unoplat Code Confluence ingestion.",
    "hook_attributes": {
        "url": "https://example.com/github/webhook",
        "active": True,
    },
    "redirect_url": "https://example.com/github/callback",
    "default_permissions": {
        "contents": "write",
        "pull_requests": "write",
        "metadata": "read",
    },
    "default_events": ["pull_request"],
    "callback_urls": [],
    "request_oauth_on_install": False,
    "setup_on_update": False,
}


def _ensure_leading_slash(path: str) -> str:
    """Ensure configuration paths start with a forward slash."""
    if not path:
        return "/"
    return path if path.startswith("/") else f"/{path}"


def build_absolute_url(base_url: str, path: str) -> str:
    """Combine the supplied base URL and path without duplicating slashes."""
    normalized_path = _ensure_leading_slash(path)
    return f"{base_url.rstrip('/')}{normalized_path}"


def load_manifest_template(env: EnvironmentSettings) -> Dict[str, Any]:
    """Load the manifest template from disk or fall back to the embedded template."""
    template_path = Path(env.github_app_manifest_template_path).expanduser()
    if not template_path.exists():
        logger.warning(
            "GitHub App manifest template not found at {}. Using fallback template.",
            template_path,
        )
        return deepcopy(FALLBACK_MANIFEST)

    try:
        content = template_path.read_text(encoding="utf-8")
        manifest = json.loads(content)
        logger.debug(
            "Loaded GitHub App manifest template from {}",
            template_path,
        )
        return manifest
    except json.JSONDecodeError as exc:
        logger.error(
            "Manifest template at {} is not valid JSON: {}. Falling back to default template.",
            template_path,
            exc,
        )
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.error(
            "Failed to read manifest template at {}: {}. Falling back to default template.",
            template_path,
            exc,
        )
    return deepcopy(FALLBACK_MANIFEST)


def prepare_manifest(
    base_manifest: Dict[str, Any],
    env: EnvironmentSettings,
    request_payload: ManifestGenerationRequest,
    redirect_url: str,
    webhook_delivery_url: str,
    post_install_redirect_url: Optional[str],
) -> Dict[str, Any]:
    """Apply service-level defaults to the manifest template."""
    manifest = deepcopy(base_manifest)

    # Ensure GitHub App visibility and core metadata
    manifest["public"] = False
    manifest["name"] = (
        request_payload.app_name or manifest.get("name") or env.github_app_name
    )
    manifest["description"] = (
        request_payload.description
        or manifest.get("description")
        or env.github_app_description
        or "Self-hosted GitHub App for Unoplat Code Confluence ingestion."
    )
    manifest["url"] = (
        str(request_payload.homepage_url)
        if request_payload.homepage_url
        else manifest.get("url")
        or env.github_app_homepage_url
        or request_payload.service_base_url
    )

    # Required permissions & events
    default_permissions = manifest.setdefault("default_permissions", {})
    default_permissions.update(
        {
            "contents": "write",
            "pull_requests": "write",
            "metadata": "read",
        }
    )
    manifest["default_events"] = ["pull_request"]

    # Webhook configuration
    hook_attributes = manifest.setdefault("hook_attributes", {})
    hook_attributes["url"] = webhook_delivery_url
    hook_attributes["active"] = hook_attributes.get("active", True)

    # Redirect and callback URLs
    manifest["redirect_url"] = redirect_url
    if post_install_redirect_url:
        callback_urls = manifest.setdefault("callback_urls", [])
        if post_install_redirect_url not in callback_urls:
            callback_urls.append(post_install_redirect_url)

    return manifest


def generate_state_token() -> str:
    """Generate a cryptographically secure state token."""
    return secrets.token_urlsafe(32)


def compute_expiry(env: EnvironmentSettings) -> datetime:
    """Calculate the expiration timestamp for manifest states."""
    return datetime.now(timezone.utc) + timedelta(
        minutes=env.github_app_manifest_state_ttl_minutes
    )


async def persist_manifest_record(
    session: AsyncSession,
    state: str,
    manifest: Dict[str, Any],
    owner: Optional[str],
    owner_type: str,
    registration_url: str,
    env: EnvironmentSettings,
    requested_by: Optional[str],
) -> GithubAppManifestRecord:
    """Persist or replace the manifest request for a given state."""
    expires_at = compute_expiry(env)
    manifest_json = json.dumps(manifest, separators=(",", ":"), sort_keys=True)

    record = GithubAppManifestRecord(
        state=state,
        manifest_json=manifest_json,
        owner_login=owner,
        owner_type=owner_type,
        registration_url=registration_url,
        requested_by=requested_by,
        expires_at=expires_at,
    )

    # Upsert by deleting any existing state first (defensive, should be unique)
    await session.execute(
        delete(GithubAppManifestRecord).where(GithubAppManifestRecord.state == state)
    )
    session.add(record)

    return record


async def get_manifest_record(
    session: AsyncSession, state: str
) -> Optional[GithubAppManifestRecord]:
    """Fetch the manifest record for the provided state token."""
    result = await session.execute(
        select(GithubAppManifestRecord).where(GithubAppManifestRecord.state == state)
    )
    return result.scalar_one_or_none()


async def delete_manifest_record(
    session: AsyncSession, record: GithubAppManifestRecord
) -> None:
    """Remove the manifest record after a successful conversion or explicit cleanup."""
    await session.delete(record)


async def cleanup_expired_manifest_requests(session: AsyncSession) -> int:
    """Delete stale manifest requests and return the count removed."""
    now = datetime.now(timezone.utc)
    stmt = (
        delete(GithubAppManifestRecord)
        .where(GithubAppManifestRecord.expires_at.is_not(None))
        .where(GithubAppManifestRecord.expires_at < now)
    )
    result = await session.execute(stmt)
    deleted = result.rowcount or 0
    if deleted:
        logger.info("Removed {} expired GitHub App manifest state(s)", deleted)
    return deleted


def build_registration_url(owner_type: str, owner: Optional[str], state: str) -> str:
    """Construct the GitHub URL used to register a manifest."""
    if owner_type == "organization":
        if not owner:
            raise ValueError(
                "Owner must be provided when owner_type is 'organization'."
            )
        return (
            f"https://github.com/organizations/{owner}/settings/apps/new?state={state}"
        )
    return f"https://github.com/settings/apps/new?state={state}"


async def store_credential(session: AsyncSession, key: str, value: str) -> None:
    """Encrypt and persist a credential using the shared credentials table."""
    encrypted_value = encrypt_token(value)
    result = await session.execute(
        select(Credentials).where(Credentials.credential_key == key)
    )
    credential = result.scalar_one_or_none()

    current_time = datetime.now(timezone.utc)

    if credential:
        credential.token_hash = encrypted_value
        credential.updated_at = current_time
        session.add(credential)
    else:
        session.add(
            Credentials(
                credential_key=key,
                token_hash=encrypted_value,
                created_at=current_time,
                updated_at=current_time,
            )
        )


async def fetch_credential(session: AsyncSession, key: str) -> Optional[str]:
    """Retrieve and decrypt a credential by key."""
    result = await session.execute(
        select(Credentials).where(Credentials.credential_key == key)
    )
    credential = result.scalar_one_or_none()
    if not credential:
        return None
    try:
        return decrypt_token(credential.token_hash)
    except Exception as exc:
        logger.error("Failed to decrypt credential {}: {}", key, exc)
        return None
