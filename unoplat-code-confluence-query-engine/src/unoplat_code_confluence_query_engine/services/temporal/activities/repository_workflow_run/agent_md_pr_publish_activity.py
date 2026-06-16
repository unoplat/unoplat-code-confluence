"""Temporal activity for publishing the AGENTS.md PR after generation."""

from __future__ import annotations

from loguru import logger
from temporalio import activity
from temporalio.exceptions import ApplicationError
from unoplat_code_confluence_commons.pr_metadata_model import PrMetadata

from unoplat_code_confluence_query_engine.services.github.agent_md_pr_service import (
    AgentMdPrAuthError,
    AgentMdPrConfigurationError,
    AgentMdPrError,
    AgentMdPrNotFoundError,
    publish_agent_md_pr,
)
from unoplat_code_confluence_query_engine.services.temporal.workflow_envelopes import (
    AgentMdPrPublishEnvelope,
)


class AgentMdPrPublishActivity:
    """Activity that publishes the AGENTS.md PR via the shared service (in-process)."""

    @activity.defn(name="publish-agent-md-pr")
    async def publish_pr(self, envelope: AgentMdPrPublishEnvelope) -> PrMetadata:
        """Publish the AGENTS.md PR for a repository workflow run.

        The target snapshot is keyed by the scheduling workflow's run ID,
        taken from the activity context rather than the envelope.

        Idempotent: the service's one-shot guard on ``pr_metadata`` and the
        publisher's open-PR early-exit make Temporal retries safe.

        Raises:
            ApplicationError: non_retryable for missing repo/snapshot, missing or
                invalid PAT, and GitHub auth errors (retrying cannot heal these);
                retryable for transient GitHub/internal failures.
        """
        repository_workflow_run_id = activity.info().workflow_run_id
        if repository_workflow_run_id is None:
            raise ApplicationError(
                "publish-agent-md-pr requires a scheduling workflow; no workflow "
                "run ID is present in the activity context",
                type="AgentMdPrMissingRunContextError",
                non_retryable=True,
            )
        try:
            persisted, already_existed = await publish_agent_md_pr(
                owner_name=envelope.owner_name,
                repo_name=envelope.repo_name,
                repository_workflow_run_id=repository_workflow_run_id,
            )
        except (
            AgentMdPrNotFoundError,
            AgentMdPrConfigurationError,
            AgentMdPrAuthError,
        ) as permanent_error:
            raise ApplicationError(
                str(permanent_error),
                type=type(permanent_error).__name__,
                non_retryable=True,
            ) from permanent_error
        except AgentMdPrError as transient_error:
            raise ApplicationError(
                str(transient_error),
                type=type(transient_error).__name__,
                non_retryable=False,
            ) from transient_error

        logger.info(
            "[agent_md_pr_publish] PR publish for {}/{} run_id={}: status={}, "
            "pr_url={}, already_existed={}",
            envelope.owner_name,
            envelope.repo_name,
            repository_workflow_run_id,
            persisted.status,
            persisted.pr_url,
            already_existed,
        )
        return persisted
