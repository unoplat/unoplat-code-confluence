"""Temporal activity for persisting agent run metadata to PostgreSQL."""

from loguru import logger
from temporalio import activity

from unoplat_code_confluence_query_engine.services.temporal.service_registry import (
    get_snapshot_writer,
)
from unoplat_code_confluence_query_engine.services.temporal.workflow_envelopes import (
    AgentSnapshotBeginRunEnvelope,
    AgentSnapshotCompleteEnvelope,
    RepositoryActivityCompletionEnvelope,
)


class RepositoryAgentSnapshotActivity:
    """Activity class for agent snapshot database operations.

    This activity wraps database calls that cannot run directly in
    Temporal workflows due to the deterministic sandbox constraint.
    """

    @activity.defn(name="persist-agent-snapshot-begin-run")
    async def persist_agent_snapshot_begin_run(
        self, envelope: AgentSnapshotBeginRunEnvelope
    ) -> None:
        """Initialize snapshot and per-codebase progress rows for a repository run."""
        logger.info(
            "[agent_snapshot_activity] Beginning run for {}/{} run_id={} codebases={}",
            envelope.owner_name,
            envelope.repo_name,
            envelope.repository_workflow_run_id,
            len(envelope.codebase_names),
        )

        writer = get_snapshot_writer()
        await writer.begin_run(
            owner_name=envelope.owner_name,
            repo_name=envelope.repo_name,
            repository_workflow_run_id=envelope.repository_workflow_run_id,
            codebase_names=envelope.codebase_names,
            repository_activity_names=envelope.repository_activity_names,
        )

        logger.info(
            "[agent_snapshot_activity] Successfully began run for {}/{} run_id={}",
            envelope.owner_name,
            envelope.repo_name,
            envelope.repository_workflow_run_id,
        )

    @activity.defn(name="complete-repository-activity")
    async def complete_repository_activity(
        self, envelope: RepositoryActivityCompletionEnvelope
    ) -> None:
        """Mark a repository-level activity complete and refresh overall progress."""
        await get_snapshot_writer().complete_repository_activity(
            owner_name=envelope.owner_name,
            repo_name=envelope.repo_name,
            repository_workflow_run_id=envelope.repository_workflow_run_id,
            activity_name=envelope.activity_name,
        )

    @activity.defn(name="persist-agent-snapshot-complete")
    async def persist_agent_snapshot_complete(
        self, envelope: AgentSnapshotCompleteEnvelope
    ) -> None:
        """Persist final statistics to the snapshot row.

        Called by RepositoryAgentWorkflow after successful completion.

        Args:
            envelope: Contains owner_name, repo_name, repository_workflow_run_id,
                     and optional statistics_payload
        """
        logger.info(
            "[agent_snapshot_activity] Persisting statistics for {}/{} run_id={}",
            envelope.owner_name,
            envelope.repo_name,
            envelope.repository_workflow_run_id,
        )

        writer = get_snapshot_writer()
        await writer.complete_run(
            owner_name=envelope.owner_name,
            repo_name=envelope.repo_name,
            repository_workflow_run_id=envelope.repository_workflow_run_id,
            statistics_payload=envelope.statistics_payload,
        )

        logger.info(
            "[agent_snapshot_activity] Successfully persisted statistics for {}/{} run_id={}",
            envelope.owner_name,
            envelope.repo_name,
            envelope.repository_workflow_run_id,
        )
