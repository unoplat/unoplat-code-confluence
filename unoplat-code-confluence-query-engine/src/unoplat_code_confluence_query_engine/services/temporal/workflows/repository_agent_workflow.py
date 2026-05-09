from __future__ import annotations

from typing import Any

from temporalio import common, workflow
from temporalio.exceptions import ApplicationError

with workflow.unsafe.imports_passed_through():
    from loguru import logger

    from unoplat_code_confluence_query_engine.models.statistics.agent_usage_statistics import (
        UsageStatistics,
    )
    from unoplat_code_confluence_query_engine.services.temporal.statistics_helpers import (
        build_workflow_statistics,
    )
    from unoplat_code_confluence_query_engine.services.temporal.workflows.codebase_agent_workflow import (
        CodebaseAgentWorkflow,
    )
    from unoplat_code_confluence_query_engine.services.temporal.workflows.runners.repository_codebase_children_runner import (
        collect_codebase_child_results,
        start_codebase_child_workflows,
    )
    from unoplat_code_confluence_query_engine.services.temporal.workflows.runners.repository_git_ref_runner import (
        resolve_repository_git_ref,
    )
    from unoplat_code_confluence_query_engine.services.temporal.workflows.runners.repository_snapshot_completion_runner import (
        persist_repository_snapshot_completion,
    )


@workflow.defn(versioning_behavior=common.VersioningBehavior.AUTO_UPGRADE)
class RepositoryAgentWorkflow:
    """Main workflow to orchestrate agent execution across all codebases."""

    @workflow.run
    async def run(
        self,
        repository_qualified_name: str,
        codebase_metadata_list: list[dict[str, Any]],
        trace_id: str = "",
    ) -> dict[str, Any]:
        """Execute agents for all codebases in a repository."""
        repository_workflow_run_id = workflow.info().run_id
        logger.debug("[workflow] RepositoryAgentWorkflow.run START")
        logger.info(
            "[workflow] Starting RepositoryAgentWorkflow for {} with {} codebases",
            repository_qualified_name,
            len(codebase_metadata_list),
        )

        codebase_statistics_map: dict[str, UsageStatistics] = {}

        git_ref_info = await resolve_repository_git_ref(repository_qualified_name)
        child_handles = await start_codebase_child_workflows(
            codebase_workflow_run=CodebaseAgentWorkflow.run,
            repository_qualified_name=repository_qualified_name,
            codebase_metadata_list=codebase_metadata_list,
            repository_workflow_run_id=repository_workflow_run_id,
            trace_id=trace_id,
            git_ref_info=git_ref_info,
        )
        child_errors = await collect_codebase_child_results(
            repository_qualified_name=repository_qualified_name,
            child_handles=child_handles,
            codebase_statistics_map=codebase_statistics_map,
        )

        workflow_statistics = build_workflow_statistics(codebase_statistics_map)
        workflow_statistics_payload = workflow_statistics.model_dump()
        await persist_repository_snapshot_completion(
            repository_qualified_name=repository_qualified_name,
            repository_workflow_run_id=repository_workflow_run_id,
            statistics_payload=workflow_statistics_payload,
        )

        if child_errors:
            error_summary = (
                f"{len(child_errors)} codebase(s) failed during agent execution"
            )
            logger.warning(
                "[workflow] {} - raising ApplicationError to propagate to interceptor",
                error_summary,
            )
            raise ApplicationError(
                error_summary,
                child_errors,
                type="CodebaseWorkflowError",
                non_retryable=True,
            )

        logger.debug("[workflow] RepositoryAgentWorkflow.run END")
        return workflow_statistics_payload
