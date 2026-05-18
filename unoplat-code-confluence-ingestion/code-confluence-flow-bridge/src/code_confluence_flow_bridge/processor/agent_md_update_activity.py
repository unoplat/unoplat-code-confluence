"""Temporal activities for post-refresh AGENTS.md update orchestration."""

from __future__ import annotations

from typing import Any, cast

import httpx2
from loguru import logger
from temporalio import activity
from temporalio.exceptions import ApplicationError

from src.code_confluence_flow_bridge.models.configuration.settings import (
    EnvironmentSettings,
)


class AgentMdUpdateActivity:
    """Activities that trigger query-engine AGENTS.md generation after refresh."""

    @activity.defn(name="trigger-agent-md-update")
    def trigger_agent_md_update(self, owner_name: str, repo_name: str) -> dict[str, Any]:
        """Call query-engine to start/idempotently return an AGENTS.md workflow run."""
        settings = EnvironmentSettings()
        base_url = settings.query_engine_base_url.rstrip("/")
        url = f"{base_url}/v1/codebase-agent-rules"
        params = {"owner_name": owner_name, "repo_name": repo_name}

        logger.info("Triggering AGENTS.md update for {}/{} via {}", owner_name, repo_name, url)
        try:
            response = httpx2.get(
                url,
                params=params,
                headers={"Accept": "application/json"},
                timeout=settings.query_engine_request_timeout_seconds,
            )
            response.raise_for_status()
            data = response.json() if response.content else {}
            logger.info(
                "AGENTS.md update trigger accepted for {}/{}: {}",
                owner_name,
                repo_name,
                data,
            )
            return cast(dict[str, Any], data) if isinstance(data, dict) else {"response": data}
        except httpx2.HTTPStatusError as exc:
            logger.warning(
                "Query engine returned HTTP {} while triggering AGENTS.md update for {}/{}: {}",
                exc.response.status_code,
                owner_name,
                repo_name,
                exc.response.text,
            )
            raise ApplicationError(
                (
                    "Query engine AGENTS.md trigger failed with HTTP "
                    f"{exc.response.status_code}: {exc.response.text}"
                ),
                type="AGENT_MD_TRIGGER_HTTP_ERROR",
            ) from exc
        except httpx2.RequestError as exc:
            logger.warning(
                "Unable to reach query engine while triggering AGENTS.md update for {}/{}: {}",
                owner_name,
                repo_name,
                exc,
            )
            raise ApplicationError(
                f"Unable to reach query engine for AGENTS.md trigger: {exc}",
                type="AGENT_MD_TRIGGER_NETWORK_ERROR",
            ) from exc
