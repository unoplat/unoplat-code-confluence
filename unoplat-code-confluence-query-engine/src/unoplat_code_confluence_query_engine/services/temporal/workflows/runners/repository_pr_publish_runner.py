from __future__ import annotations

from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from loguru import logger
    from unoplat_code_confluence_commons.pr_metadata_model import PrMetadata

    from unoplat_code_confluence_query_engine.services.temporal.activities.repository_workflow_run.agent_md_pr_publish_activity import (
        AgentMdPrPublishActivity,
    )
    from unoplat_code_confluence_query_engine.services.temporal.workflow_envelopes import (
        AgentMdPrPublishEnvelope,
    )

PR_PUBLISH_RETRY_POLICY = RetryPolicy(
    initial_interval=timedelta(seconds=2),
    backoff_coefficient=2.0,
    maximum_attempts=3,
    maximum_interval=timedelta(seconds=30),
)

PR_PUBLISH_TIMEOUT = timedelta(minutes=3)


async def publish_repository_agent_md_pr(
    repository_qualified_name: str,
) -> PrMetadata | None:
    """Publish the AGENTS.md PR for a completed run; never fails the generation run.

    The activity resolves the workflow run ID from its own activity context
    (``activity.info().workflow_run_id``), so only the repository identity is
    sent. Returns the persisted PR metadata, or None when publishing failed —
    in that case pr_metadata stays unset and the manual `agent-md pr` fallback
    remains available.
    """
    owner_name, repo_name = repository_qualified_name.split("/", maxsplit=1)
    envelope = AgentMdPrPublishEnvelope(
        owner_name=owner_name,
        repo_name=repo_name,
    )
    try:
        return await workflow.execute_activity(
            AgentMdPrPublishActivity.publish_pr,
            args=[envelope],
            start_to_close_timeout=PR_PUBLISH_TIMEOUT,
            retry_policy=PR_PUBLISH_RETRY_POLICY,
        )
    except Exception as e:
        logger.warning(
            "[workflow] AGENTS.md PR publish failed for {}; pr_metadata left unset, "
            "manual `agent-md pr` fallback remains available: {}",
            repository_qualified_name,
            e,
        )
        return None
