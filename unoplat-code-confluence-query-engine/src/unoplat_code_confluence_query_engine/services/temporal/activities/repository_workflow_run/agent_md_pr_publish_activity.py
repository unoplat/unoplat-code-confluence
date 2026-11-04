"""Temporal activities for saving artifact identity and reconciling its PR."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable
from typing import TypeVar

from loguru import logger
from sqlalchemy.exc import SQLAlchemyError
from temporalio import activity
from temporalio.exceptions import ApplicationError
from unoplat_code_confluence_commons.pr_metadata_model import PrMetadata

from unoplat_code_confluence_query_engine.models.output.repository_artifacts import (
    ArtifactIdentityResult,
)
from unoplat_code_confluence_query_engine.services.github.agent_md_pr_service import (
    AgentMdPrError,
    reconcile_agent_md_pr_after_generation,
    save_artifact_identity_after_generation,
)
from unoplat_code_confluence_query_engine.services.temporal.workflow_envelopes import (
    AgentMdPrPublishEnvelope,
    ArtifactIdentitySaveEnvelope,
)

_T = TypeVar("_T")
_HEARTBEAT_INTERVAL_SECONDS = 5.0


def _owning_run_id() -> str:
    run_id = activity.info().workflow_run_id
    if run_id is None:
        raise ApplicationError(
            "Artifact publication requires a scheduling workflow; no workflow "
            "run ID is present in the activity context",
            type="AgentMdPrMissingRunContextError",
            non_retryable=True,
        )
    return run_id


async def _heartbeat_forever() -> None:
    while True:
        activity.heartbeat()
        await asyncio.sleep(_HEARTBEAT_INTERVAL_SECONDS)


async def _run_with_heartbeat(operation: Awaitable[_T]) -> _T:
    """Await the operation while heartbeating, which is how cancellation arrives.

    Temporal delivers an activity cancellation only through a heartbeat. Heartbeats
    continue while cancellation unwinds, because a blocking provider call and the
    locks it holds must finish first. The heartbeat task is reaped before returning,
    and its own failure is only logged: the operation's outcome is already durable,
    but a failed heartbeat means cancellation could not have been delivered.
    """
    heartbeat = asyncio.create_task(_heartbeat_forever())
    try:
        return await operation
    finally:
        heartbeat.cancel()
        outcome = (await asyncio.gather(heartbeat, return_exceptions=True))[0]
        if isinstance(outcome, Exception):
            logger.warning(
                "[agent_md_pr_publish] Heartbeat stopped early: {}",
                type(outcome).__name__,
            )


def _application_error(error: AgentMdPrError | SQLAlchemyError) -> ApplicationError:
    """Build a static failure. Callers raise it ``from None``.

    Temporal stores the ``__cause__`` chain in workflow history, and that chain can
    hold raw provider and database text.
    """
    if isinstance(error, AgentMdPrError):
        return ApplicationError(
            str(error),
            type=type(error).__name__,
            non_retryable=not error.retryable,
        )
    return ApplicationError(
        "Artifact publication metadata could not be persisted",
        type="AgentMdPrInternalError",
    )


class AgentMdPrPublishActivity:
    """Activities that publish artifacts through the shared service, in-process."""

    @activity.defn(name="save-artifact-identity")
    async def save_identity(
        self, envelope: ArtifactIdentitySaveEnvelope
    ) -> ArtifactIdentityResult:
        """Capture, commit and durably save the run's verified Git identity.

        The target snapshot is keyed by the scheduling workflow's run ID, taken
        from the activity context rather than the envelope. Retries reuse the
        frozen manifest or saved SHA under the shared per-run publisher lock.

        Args:
            envelope: Repository and the files its completed stages must have left.

        Returns:
            The saved identity, or an explicit no_artifacts outcome.

        Raises:
            ApplicationError: non_retryable for stale/conflicting artifacts,
                ineligible runs, credentials and permission errors; retryable for
                transient provider/infrastructure failures.
        """
        run_id = _owning_run_id()
        try:
            identity = await _run_with_heartbeat(
                save_artifact_identity_after_generation(
                    owner_name=envelope.owner_name,
                    repo_name=envelope.repo_name,
                    repository_workflow_run_id=run_id,
                    required_artifact_paths=envelope.required_artifact_paths,
                )
            )
        except (AgentMdPrError, SQLAlchemyError) as publication_error:
            raise _application_error(publication_error) from None
        logger.info(
            "[agent_md_pr_publish] Artifact identity for {}/{} run_id={}: status={}, "
            "commit_sha={}",
            envelope.owner_name,
            envelope.repo_name,
            run_id,
            identity.status,
            identity.commit_sha,
        )
        return identity

    @activity.defn(name="publish-agent-md-pr")
    async def publish_pr(self, envelope: AgentMdPrPublishEnvelope) -> PrMetadata:
        """Reconcile the PR for a run whose Git identity is already saved.

        Args:
            envelope: Repository whose scheduling workflow run owns the snapshot.

        Returns:
            The persisted PR metadata.

        Raises:
            ApplicationError: The PR was not reconciled. The service has recorded a
                static safe error and retained the saved identity.
        """
        run_id = _owning_run_id()
        try:
            persisted, already_existed = await _run_with_heartbeat(
                reconcile_agent_md_pr_after_generation(
                    owner_name=envelope.owner_name,
                    repo_name=envelope.repo_name,
                    repository_workflow_run_id=run_id,
                )
            )
        except (AgentMdPrError, SQLAlchemyError) as publication_error:
            raise _application_error(publication_error) from None
        logger.info(
            "[agent_md_pr_publish] PR publish for {}/{} run_id={}: status={}, "
            "pr_url={}, already_existed={}",
            envelope.owner_name,
            envelope.repo_name,
            run_id,
            persisted.status,
            persisted.pr_url,
            already_existed,
        )
        return persisted
