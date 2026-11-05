from __future__ import annotations

from datetime import timedelta
from typing import TypeVar

from temporalio import workflow
from temporalio.common import RetryPolicy
from temporalio.exceptions import ActivityError
from temporalio.workflow import ActivityCancellationType, ActivityHandle

with workflow.unsafe.imports_passed_through():
    import asyncio

    from loguru import logger
    from unoplat_code_confluence_commons.pr_metadata_model import PrMetadata

    from unoplat_code_confluence_query_engine.models.output.repository_artifacts import (
        ArtifactIdentityResult,
    )
    from unoplat_code_confluence_query_engine.services.temporal.activities.repository_workflow_run.agent_md_pr_publish_activity import (
        AgentMdPrPublishActivity,
    )
    from unoplat_code_confluence_query_engine.services.temporal.utils import (
        raise_if_temporal_cancellation,
    )
    from unoplat_code_confluence_query_engine.services.temporal.workflow_envelopes import (
        AgentMdPrPublishEnvelope,
        ArtifactIdentitySaveEnvelope,
    )

_T = TypeVar("_T")

PR_PUBLISH_RETRY_POLICY = RetryPolicy(
    initial_interval=timedelta(seconds=2),
    backoff_coefficient=2.0,
    maximum_attempts=3,
    maximum_interval=timedelta(seconds=30),
)

# Complete inventories and exact-byte recovery may require many Git Data reads.
PR_PUBLISH_TIMEOUT = timedelta(minutes=10)
# Cancellation reaches these activities only through heartbeats. This also detects
# a lost worker well before the start-to-close timeout.
PR_PUBLISH_HEARTBEAT_TIMEOUT = timedelta(seconds=30)


async def _await_activity_propagating_cancel(handle: ActivityHandle[_T]) -> _T:
    """Await an activity so that a workflow cancel request is never consumed.

    Without the shield, an activity that finishes successfully before it learns of
    the request returns its result, the request is spent, and the workflow goes on
    to schedule later work. Here the activity still gets to finish and release its
    locks, because of WAIT_CANCELLATION_COMPLETED, and the cancellation is re-raised
    whatever its outcome.
    """
    try:
        return await asyncio.shield(handle)
    except asyncio.CancelledError:
        handle.cancel()
        await asyncio.gather(handle, return_exceptions=True)
        raise


async def save_repository_artifact_identity(
    repository_qualified_name: str,
    required_artifact_paths: list[str],
) -> ArtifactIdentityResult:
    """Require a saved Git identity before generation can succeed.

    The activity derives the exact owning run ID from its context. Failures retry
    under the policy and then propagate to fail the run, as does cancellation.
    """
    owner_name, repo_name = repository_qualified_name.split("/", maxsplit=1)
    envelope = ArtifactIdentitySaveEnvelope(
        owner_name=owner_name,
        repo_name=repo_name,
        required_artifact_paths=required_artifact_paths,
    )
    return await _await_activity_propagating_cancel(
        workflow.start_activity(
            AgentMdPrPublishActivity.save_identity,
            args=[envelope],
            start_to_close_timeout=PR_PUBLISH_TIMEOUT,
            heartbeat_timeout=PR_PUBLISH_HEARTBEAT_TIMEOUT,
            retry_policy=PR_PUBLISH_RETRY_POLICY,
            cancellation_type=ActivityCancellationType.WAIT_CANCELLATION_COMPLETED,
        )
    )


async def reconcile_repository_agent_md_pr(
    repository_qualified_name: str,
) -> PrMetadata | None:
    """Attempt PR reconciliation from the saved identity without failing generation.

    The activity records a static safe error when it can. The saved SHA and manifest
    survive, and manual retry reuses them. Only ActivityError is optional, so
    cancellation and defects in this workflow code still propagate.
    """
    owner_name, repo_name = repository_qualified_name.split("/", maxsplit=1)
    envelope = AgentMdPrPublishEnvelope(owner_name=owner_name, repo_name=repo_name)
    try:
        return await _await_activity_propagating_cancel(
            workflow.start_activity(
                AgentMdPrPublishActivity.publish_pr,
                args=[envelope],
                start_to_close_timeout=PR_PUBLISH_TIMEOUT,
                heartbeat_timeout=PR_PUBLISH_HEARTBEAT_TIMEOUT,
                retry_policy=PR_PUBLISH_RETRY_POLICY,
                cancellation_type=ActivityCancellationType.WAIT_CANCELLATION_COMPLETED,
            )
        )
    except ActivityError as error:
        raise_if_temporal_cancellation(error)
        logger.warning(
            "[workflow] Pull request reconciliation failed for {}; the saved artifact "
            "identity is retained",
            repository_qualified_name,
        )
        return None
