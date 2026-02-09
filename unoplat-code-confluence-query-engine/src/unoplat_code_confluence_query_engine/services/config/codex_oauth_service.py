"""Codex OAuth flow + token lifecycle service for model provider auth."""

from __future__ import annotations

import asyncio
import base64
from dataclasses import dataclass
from datetime import datetime
import hashlib
import json
import secrets
import time
from typing import Any, Literal, Optional
from urllib.parse import urlencode
import uuid

import httpx
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from unoplat_code_confluence_commons.credential_enums import SecretKind

from unoplat_code_confluence_query_engine.config.settings import EnvironmentSettings
from unoplat_code_confluence_query_engine.services.config.credentials_service import (
    CredentialsService,
)

FlowState = Literal["pending", "success", "failed", "expired"]


@dataclass
class TokenResponse:
    """OAuth token response payload."""

    access_token: str
    refresh_token: Optional[str]
    id_token: Optional[str]
    expires_in: int


@dataclass
class CodexAuthContext:
    """Resolved auth context used for request auth headers."""

    access_token: str
    account_id: Optional[str]
    expires_at: int


@dataclass
class CodexOAuthStatus:
    """Current persisted Codex OAuth connection status."""

    connected: bool
    account_id: Optional[str]
    expires_at: Optional[int]
    configured_at: Optional[datetime]


@dataclass
class CodexOAuthFlow:
    """In-memory PKCE flow state."""

    flow_id: str
    state: str
    verifier: str
    redirect_uri: str
    frontend_origin: Optional[str]
    expires_at: int
    status: FlowState
    error: Optional[str] = None


class CodexOAuthService:
    """Handles Codex OAuth authorize/callback/token-refresh lifecycle."""

    def __init__(self, settings: EnvironmentSettings) -> None:
        self._settings = settings
        self._flows: dict[str, CodexOAuthFlow] = {}
        self._flow_id_by_state: dict[str, str] = {}
        self._flow_lock = asyncio.Lock()

    @property
    def codex_api_endpoint(self) -> str:
        """Full Codex backend endpoint used by request rewriting."""
        return self._settings.codex_openai_api_endpoint

    def build_redirect_uri(self) -> str:
        """Return fixed callback redirect URI for Codex OAuth."""
        return self._settings.codex_openai_redirect_uri

    @staticmethod
    def _now_ms() -> int:
        return int(time.time() * 1000)

    @staticmethod
    def _code_verifier() -> str:
        # RFC 7636 verifier allowed charset, 43-128 chars
        return secrets.token_urlsafe(48)

    @staticmethod
    def _code_challenge(verifier: str) -> str:
        digest = hashlib.sha256(verifier.encode("utf-8")).digest()
        return base64.urlsafe_b64encode(digest).decode("utf-8").rstrip("=")

    async def _mark_expired_flows_locked(self) -> None:
        now = self._now_ms()
        for flow in self._flows.values():
            if flow.status == "pending" and now >= flow.expires_at:
                flow.status = "expired"
                flow.error = "OAuth flow expired"

    def _build_authorize_url(
        self,
        *,
        redirect_uri: str,
        challenge: str,
        state: str,
    ) -> str:
        params = {
            "response_type": "code",
            "client_id": self._settings.codex_openai_client_id,
            "redirect_uri": redirect_uri,
            "scope": "openid profile email offline_access",
            "code_challenge": challenge,
            "code_challenge_method": "S256",
            "id_token_add_organizations": "true",
            "codex_cli_simplified_flow": "true",
            "originator": self._settings.codex_openai_originator,
            "state": state,
        }
        return f"{self._settings.codex_openai_issuer}/oauth/authorize?{urlencode(params)}"

    async def create_authorization_flow(
        self, frontend_origin: Optional[str] = None
    ) -> dict[str, Any]:
        """Create a new PKCE flow and return authorize URL payload."""
        flow_id = str(uuid.uuid4())
        verifier = self._code_verifier()
        state = secrets.token_urlsafe(32)
        expires_at = self._now_ms() + self._settings.codex_openai_flow_ttl_seconds * 1000
        redirect_uri = self.build_redirect_uri()
        authorize_url = self._build_authorize_url(
            redirect_uri=redirect_uri,
            challenge=self._code_challenge(verifier),
            state=state,
        )

        async with self._flow_lock:
            await self._mark_expired_flows_locked()
            flow = CodexOAuthFlow(
                flow_id=flow_id,
                state=state,
                verifier=verifier,
                redirect_uri=redirect_uri,
                frontend_origin=frontend_origin,
                expires_at=expires_at,
                status="pending",
                error=None,
            )
            self._flows[flow_id] = flow
            self._flow_id_by_state[state] = flow_id

        return {
            "flow_id": flow_id,
            "authorization_url": authorize_url,
            "expires_at": expires_at,
            "poll_interval_ms": self._settings.codex_openai_poll_interval_ms,
        }

    async def get_flow_status(self, flow_id: str) -> dict[str, Optional[str]]:
        """Get current flow status for polling."""
        async with self._flow_lock:
            await self._mark_expired_flows_locked()
            flow = self._flows.get(flow_id)
            if not flow:
                return {"status": "failed", "error": "Flow not found"}
            return {"status": flow.status, "error": flow.error}

    async def get_flow_frontend_origin(self, state: Optional[str]) -> Optional[str]:
        """Resolve stored frontend origin by flow state."""
        if not state:
            return None
        async with self._flow_lock:
            flow_id = self._flow_id_by_state.get(state)
            flow = self._flows.get(flow_id) if flow_id else None
            if not flow:
                return None
            return flow.frontend_origin

    async def complete_authorization_callback(
        self,
        session: AsyncSession,
        *,
        state: Optional[str],
        code: Optional[str],
        error: Optional[str],
        error_description: Optional[str],
    ) -> tuple[bool, str]:
        """Process OAuth callback, persist credentials, and update flow state."""
        if not state:
            return False, "Missing state parameter"

        async with self._flow_lock:
            await self._mark_expired_flows_locked()
            flow_id = self._flow_id_by_state.get(state)
            flow = self._flows.get(flow_id) if flow_id else None
            if not flow:
                return False, "Unknown or expired OAuth flow state"
            if flow.status != "pending":
                return flow.status == "success", flow.error or "OAuth flow not pending"

        if error:
            message = error_description or error
            await self._set_flow_failure(state=state, message=message)
            return False, message

        if not code:
            message = "Missing authorization code"
            await self._set_flow_failure(state=state, message=message)
            return False, message

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                token_payload = await self._exchange_code_for_tokens(
                    client=client,
                    code=code,
                    redirect_uri=flow.redirect_uri,
                    verifier=flow.verifier,
                )

            account_id = self.extract_account_id(token_payload)
            expires_at = self._now_ms() + token_payload.expires_in * 1000
            if not token_payload.refresh_token:
                raise ValueError("OAuth token exchange did not return refresh_token")

            await CredentialsService.upsert_model_oauth_credentials(
                session,
                access_token=token_payload.access_token,
                refresh_token=token_payload.refresh_token,
                id_token=token_payload.id_token,
                expires_at=expires_at,
                account_id=account_id,
            )

            await self._set_flow_success(state=state)
            logger.info("Codex OAuth callback completed successfully")
            return True, "Authorization successful"
        except Exception as exc:
            message = f"OAuth callback failed: {exc}"
            logger.error(message)
            await self._set_flow_failure(state=state, message=message)
            return False, message

    async def _set_flow_success(self, *, state: str) -> None:
        async with self._flow_lock:
            flow_id = self._flow_id_by_state.get(state)
            if not flow_id:
                return
            flow = self._flows.get(flow_id)
            if not flow:
                return
            flow.status = "success"
            flow.error = None

    async def _set_flow_failure(self, *, state: str, message: str) -> None:
        async with self._flow_lock:
            flow_id = self._flow_id_by_state.get(state)
            if not flow_id:
                return
            flow = self._flows.get(flow_id)
            if not flow:
                return
            flow.status = "failed"
            flow.error = message

    async def _exchange_code_for_tokens(
        self,
        *,
        client: httpx.AsyncClient,
        code: str,
        redirect_uri: str,
        verifier: str,
    ) -> TokenResponse:
        response = await client.post(
            f"{self._settings.codex_openai_issuer}/oauth/token",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
                "client_id": self._settings.codex_openai_client_id,
                "code_verifier": verifier,
            },
        )
        response.raise_for_status()
        payload = response.json()
        return self._parse_token_response(payload)

    async def _refresh_access_token(
        self, *, client: httpx.AsyncClient, refresh_token: str
    ) -> TokenResponse:
        response = await client.post(
            f"{self._settings.codex_openai_issuer}/oauth/token",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": self._settings.codex_openai_client_id,
            },
        )
        response.raise_for_status()
        payload = response.json()
        return self._parse_token_response(payload)

    @staticmethod
    def _parse_token_response(payload: dict[str, Any]) -> TokenResponse:
        access_token = payload.get("access_token")
        if not isinstance(access_token, str) or not access_token:
            raise ValueError("OAuth token response missing access_token")

        refresh_token_raw = payload.get("refresh_token")
        refresh_token = (
            refresh_token_raw if isinstance(refresh_token_raw, str) else None
        )
        id_token_raw = payload.get("id_token")
        id_token = id_token_raw if isinstance(id_token_raw, str) else None

        expires_in_raw = payload.get("expires_in")
        expires_in = int(expires_in_raw) if isinstance(expires_in_raw, int | float) else 3600

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            id_token=id_token,
            expires_in=max(expires_in, 60),
        )

    async def ensure_valid_access_token(
        self, session: AsyncSession
    ) -> CodexAuthContext:
        """Get a valid access token; refresh if missing/expired."""
        refresh_token = await CredentialsService.get_model_oauth_refresh_token(session)
        if not refresh_token:
            raise ValueError("Codex OAuth not connected: refresh token missing")

        access_token = await CredentialsService.get_model_oauth_access_token(session)
        metadata = await CredentialsService.get_model_oauth_access_metadata(session) or {}

        expires_at_raw = metadata.get("expires_at")
        expires_at = int(expires_at_raw) if isinstance(expires_at_raw, int | float) else 0
        account_id_raw = metadata.get("account_id")
        account_id = account_id_raw if isinstance(account_id_raw, str) else None

        now = self._now_ms()
        refresh_margin_ms = (
            self._settings.codex_openai_token_refresh_safety_margin_seconds * 1000
        )

        if not access_token or expires_at <= now + refresh_margin_ms:
            logger.info("Refreshing Codex OAuth access token")
            async with httpx.AsyncClient(timeout=30.0) as client:
                refreshed = await self._refresh_access_token(
                    client=client,
                    refresh_token=refresh_token,
                )

            resolved_refresh = refreshed.refresh_token or refresh_token
            resolved_account_id = self.extract_account_id(refreshed) or account_id
            resolved_expires_at = now + refreshed.expires_in * 1000

            await CredentialsService.upsert_model_oauth_credentials(
                session,
                access_token=refreshed.access_token,
                refresh_token=resolved_refresh,
                id_token=refreshed.id_token,
                expires_at=resolved_expires_at,
                account_id=resolved_account_id,
            )
            access_token = refreshed.access_token
            account_id = resolved_account_id
            expires_at = resolved_expires_at

        return CodexAuthContext(
            access_token=access_token,
            account_id=account_id,
            expires_at=expires_at,
        )

    async def get_oauth_status(self, session: AsyncSession) -> CodexOAuthStatus:
        """Read persisted Codex OAuth connection status."""
        refresh_exists = await CredentialsService.model_oauth_connected(session)
        if not refresh_exists:
            return CodexOAuthStatus(
                connected=False,
                account_id=None,
                expires_at=None,
                configured_at=None,
            )

        access_row = await CredentialsService.execute_get_model_secret_query(
            session, SecretKind.OAUTH_ACCESS_TOKEN
        )
        metadata = access_row.metadata_json if access_row and access_row.metadata_json else {}
        expires_at_raw = metadata.get("expires_at") if isinstance(metadata, dict) else None
        expires_at = int(expires_at_raw) if isinstance(expires_at_raw, int | float) else None
        account_id_raw = metadata.get("account_id") if isinstance(metadata, dict) else None
        account_id = account_id_raw if isinstance(account_id_raw, str) else None

        return CodexOAuthStatus(
            connected=True,
            account_id=account_id,
            expires_at=expires_at,
            configured_at=access_row.updated_at if access_row else None,
        )

    async def disconnect(self, session: AsyncSession) -> bool:
        """Delete persisted model OAuth credentials."""
        return await CredentialsService.delete_model_oauth_credentials(session)

    @staticmethod
    def _parse_jwt_claims(token: str) -> Optional[dict[str, Any]]:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        payload = parts[1]
        payload += "=" * (-len(payload) % 4)
        try:
            decoded = base64.urlsafe_b64decode(payload.encode("utf-8")).decode("utf-8")
            parsed = json.loads(decoded)
            return parsed if isinstance(parsed, dict) else None
        except Exception:
            return None

    @staticmethod
    def _extract_account_id_from_claims(claims: dict[str, Any]) -> Optional[str]:
        direct = claims.get("chatgpt_account_id")
        if isinstance(direct, str) and direct:
            return direct

        api_auth = claims.get("https://api.openai.com/auth")
        if isinstance(api_auth, dict):
            nested = api_auth.get("chatgpt_account_id")
            if isinstance(nested, str) and nested:
                return nested

        organizations = claims.get("organizations")
        if isinstance(organizations, list) and organizations:
            first = organizations[0]
            if isinstance(first, dict):
                org_id = first.get("id")
                if isinstance(org_id, str) and org_id:
                    return org_id

        return None

    def extract_account_id(self, tokens: TokenResponse) -> Optional[str]:
        """Extract ChatGPT account ID from id/access JWT claims."""
        if tokens.id_token:
            claims = self._parse_jwt_claims(tokens.id_token)
            if claims:
                account_id = self._extract_account_id_from_claims(claims)
                if account_id:
                    return account_id

        claims = self._parse_jwt_claims(tokens.access_token)
        if claims:
            return self._extract_account_id_from_claims(claims)
        return None
