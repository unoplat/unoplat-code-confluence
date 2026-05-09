"""Temporal activity for persisting agent MD snapshot output to PostgreSQL."""

from loguru import logger
from temporalio import activity

from unoplat_code_confluence_query_engine.services.temporal.service_registry import (
    get_snapshot_writer,
)
from unoplat_code_confluence_query_engine.services.temporal.workflow_envelopes import (
    AgentSnapshotBeginRunEnvelope,
    AgentSnapshotCodebasePatchEnvelope,
    AgentSnapshotCompleteEnvelope,
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
            repository_qualified_name=envelope.repository_qualified_name,
            repository_workflow_run_id=envelope.repository_workflow_run_id,
            codebase_names=envelope.codebase_names,
        )

        logger.info(
            "[agent_snapshot_activity] Successfully began run for {}/{} run_id={}",
            envelope.owner_name,
            envelope.repo_name,
            envelope.repository_workflow_run_id,
        )

    @activity.defn(name="persist-agent-snapshot-codebase-patch")
    async def persist_agent_snapshot_codebase_patch(
        self, envelope: AgentSnapshotCodebasePatchEnvelope
    ) -> None:
        """Persist a partial codebase patch into the agent snapshot."""
        logger.info(
            "[agent_snapshot_activity] Patching output for {}/{} run_id={} codebase={}",
            envelope.owner_name,
            envelope.repo_name,
            envelope.repository_workflow_run_id,
            envelope.codebase_name,
        )

        writer = get_snapshot_writer()
        await writer.patch_codebase_output(
            owner_name=envelope.owner_name,
            repo_name=envelope.repo_name,
            repository_workflow_run_id=envelope.repository_workflow_run_id,
            codebase_name=envelope.codebase_name,
            codebase_patch=envelope.codebase_patch,
        )

        logger.info(
            "[agent_snapshot_activity] Successfully patched output for {}/{} run_id={} codebase={}",
            envelope.owner_name,
            envelope.repo_name,
            envelope.repository_workflow_run_id,
            envelope.codebase_name,
        )

    @activity.defn(name="persist-agent-snapshot-complete")
    async def persist_agent_snapshot_complete(
        self, envelope: AgentSnapshotCompleteEnvelope
    ) -> None:
        """Persist final agent output and statistics to snapshot.

        Called by RepositoryAgentWorkflow after successful completion
        to persist agent_md_output and statistics to the database.

        Args:
            envelope: Contains owner_name, repo_name, repository_workflow_run_id,
                     final_payload, and optional statistics_payload
        """
        logger.info(
            "[agent_snapshot_activity] Persisting output for {}/{} run_id={}",
            envelope.owner_name,
            envelope.repo_name,
            envelope.repository_workflow_run_id,
        )

        writer = get_snapshot_writer()
        await writer.complete_run(
            owner_name=envelope.owner_name,
            repo_name=envelope.repo_name,
            repository_workflow_run_id=envelope.repository_workflow_run_id,
            final_payload=envelope.final_payload,
            statistics_payload=envelope.statistics_payload,
        )

        logger.info(
            "[agent_snapshot_activity] Successfully persisted output for {}/{} run_id={}",
            envelope.owner_name,
            envelope.repo_name,
            envelope.repository_workflow_run_id,
        )
