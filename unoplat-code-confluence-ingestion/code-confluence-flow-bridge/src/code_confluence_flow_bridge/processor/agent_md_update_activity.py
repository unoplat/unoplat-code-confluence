"""Temporal activities for post-refresh AGENTS.md update orchestration."""

from __future__ import annotations

from typing import Any, cast

import httpx2
from temporalio import activity
from temporalio.exceptions import ApplicationError

from code_confluence_flow_bridge.logging.trace_utils import (
    seed_and_bind_logger_from_trace_id,
)
from code_confluence_flow_bridge.models.configuration.settings import (
    EnvironmentSettings,
)
from code_confluence_flow_bridge.models.workflow.repo_workflow_base import (
    AgentMdUpdateActivityEnvelope,
)


class AgentMdUpdateActivity:
    """Activities that trigger query-engine AGENTS.md generation after refresh."""

    @activity.defn(name="trigger-agent-md-update")
    def trigger_agent_md_update(
        self, envelope: AgentMdUpdateActivityEnvelope
    ) -> dict[str, Any]:
        """Call query-engine to start/idempotently return an AGENTS.md workflow run."""
        owner_name = envelope.owner_name
        repo_name = envelope.repo_name

        info = activity.info()
        log = seed_and_bind_logger_from_trace_id(
            trace_id=envelope.trace_id,
            workflow_id=info.workflow_id,
            workflow_run_id=info.workflow_run_id,
            activity_id=info.activity_id,
            activity_name=info.activity_type,
        )

        settings = EnvironmentSettings()
        base_url = settings.query_engine_base_url.rstrip("/")
        url = f"{base_url}/v1/codebase-agent-rules"
        params = {"owner_name": owner_name, "repo_name": repo_name}

        log.info(
            "Triggering AGENTS.md update for {}/{} via {}",
            owner_name,
            repo_name,
            url,
        )
        try:
            response = httpx2.get(
                url,
                params=params,
                headers={"Accept": "application/json"},
                timeout=settings.query_engine_request_timeout_seconds,
            )
            response.raise_for_status()
            data: Any = response.json() if response.content else {}
            log.info(
                "AGENTS.md update trigger accepted for {}/{}: {}",
                owner_name,
                repo_name,
                data,
            )
            return cast(dict[str, Any], data) if isinstance(data, dict) else {"response": data}
        except httpx2.HTTPStatusError as exc:
            log.warning(
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
            log.warning(
                "Unable to reach query engine while triggering AGENTS.md update for {}/{}: {}",
                owner_name,
                repo_name,
                exc,
            )
            raise ApplicationError(
                f"Unable to reach query engine for AGENTS.md trigger: {exc}",
                type="AGENT_MD_TRIGGER_NETWORK_ERROR",
            ) from exc
