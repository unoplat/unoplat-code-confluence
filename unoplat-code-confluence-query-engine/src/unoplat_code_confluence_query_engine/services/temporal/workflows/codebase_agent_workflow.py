from __future__ import annotations

from typing import Any

from temporalio import common, workflow
from temporalio.exceptions import ApplicationError

with workflow.unsafe.imports_passed_through():
    from loguru import logger

    from unoplat_code_confluence_query_engine.models.output.git_ref_info import (
        GitRefInfo,
    )
    from unoplat_code_confluence_query_engine.models.repository.repository_ruleset_metadata import (
        CodebaseMetadata,
    )
    from unoplat_code_confluence_query_engine.models.statistics.agent_usage_statistics import (
        UsageStatistics,
    )
    from unoplat_code_confluence_query_engine.services.temporal.statistics_helpers import (
        aggregate_usage_statistics,
    )
    from unoplat_code_confluence_query_engine.services.temporal.temporal_agents import (
        get_temporal_agents,
    )
    from unoplat_code_confluence_query_engine.services.temporal.workflows.runners.agent_snapshot_patch_runner import (
        persist_codebase_snapshot_patch,
    )
    from unoplat_code_confluence_query_engine.services.temporal.workflows.runners.app_interfaces_runner import (
        run_app_interfaces_agent,
    )
    from unoplat_code_confluence_query_engine.services.temporal.workflows.runners.business_domain_runner import (
        run_business_domain_agent,
    )
    from unoplat_code_confluence_query_engine.services.temporal.workflows.runners.dependency_guide_runner import (
        run_dependency_guide_agent,
    )
    from unoplat_code_confluence_query_engine.services.temporal.workflows.runners.development_workflow_runner import (
        run_development_workflow_agent,
    )
    from unoplat_code_confluence_query_engine.services.temporal.workflows.runners.managed_block_runner import (
        run_managed_block_bootstrap,
    )


@workflow.defn(versioning_behavior=common.VersioningBehavior.AUTO_UPGRADE)
class CodebaseAgentWorkflow:
    """Workflow to execute all agents for a single codebase."""

    @workflow.run
    async def run(
        self,
        repository_qualified_name: str,
        codebase_metadata_dict: dict[str, Any],
        repository_workflow_run_id: str,
        trace_id: str = "",
        git_ref_info: GitRefInfo | None = None,
    ) -> dict[str, Any]:
        """Execute all agents sequentially for a single codebase."""
        codebase_workflow_run_id = workflow.info().run_id
        logger.debug("[workflow] CodebaseAgentWorkflow.run START")
        logger.debug("[workflow] Validating codebase_metadata_dict...")
        codebase_metadata = CodebaseMetadata.model_validate(codebase_metadata_dict)
        logger.debug(
            "[workflow] CodebaseMetadata validated: {}",
            codebase_metadata.codebase_name,
        )

        logger.info(
            "[workflow] Starting CodebaseAgentWorkflow for {}/{}",
            repository_qualified_name,
            codebase_metadata.codebase_name,
        )

        _ = trace_id

        logger.debug("[workflow] Getting temporal agents...")
        temporal_agents = get_temporal_agents()
        logger.debug(
            "[workflow] Got temporal agents: {}",
            temporal_agents.enabled_agent_names(),
        )

        programming_language_metadata: dict[str, object] = {
            "primary_language": codebase_metadata.codebase_programming_language,
            "package_manager": codebase_metadata.codebase_package_manager,
        }

        agent_stats: list[UsageStatistics] = []
        agent_errors: list[dict[str, Any]] = []

        await persist_codebase_snapshot_patch(
            repository_qualified_name=repository_qualified_name,
            repository_workflow_run_id=repository_workflow_run_id,
            codebase_name=codebase_metadata.codebase_name,
            codebase_patch={
                "codebase_name": codebase_metadata.codebase_name,
                "programming_language_metadata": programming_language_metadata,
                "engineering_workflow": None,
                "dependency_guide": None,
                "business_logic": None,
                "app_interfaces": None,
            },
        )

        await run_managed_block_bootstrap(
            codebase_metadata=codebase_metadata,
            git_ref_info=git_ref_info,
        )
        await run_development_workflow_agent(
            temporal_agents=temporal_agents,
            repository_qualified_name=repository_qualified_name,
            codebase_metadata=codebase_metadata,
            repository_workflow_run_id=repository_workflow_run_id,
            codebase_workflow_run_id=codebase_workflow_run_id,
            programming_language_metadata=programming_language_metadata,
            agent_stats=agent_stats,
            agent_errors=agent_errors,
        )
        await run_dependency_guide_agent(
            temporal_agents=temporal_agents,
            repository_qualified_name=repository_qualified_name,
            codebase_metadata=codebase_metadata,
            repository_workflow_run_id=repository_workflow_run_id,
            codebase_workflow_run_id=codebase_workflow_run_id,
            programming_language_metadata=programming_language_metadata,
            agent_stats=agent_stats,
            agent_errors=agent_errors,
        )
        await run_business_domain_agent(
            temporal_agents=temporal_agents,
            repository_qualified_name=repository_qualified_name,
            codebase_metadata=codebase_metadata,
            repository_workflow_run_id=repository_workflow_run_id,
            codebase_workflow_run_id=codebase_workflow_run_id,
            programming_language_metadata=programming_language_metadata,
            agent_stats=agent_stats,
            agent_errors=agent_errors,
        )
        await run_app_interfaces_agent(
            temporal_agents=temporal_agents,
            repository_qualified_name=repository_qualified_name,
            codebase_metadata=codebase_metadata,
            repository_workflow_run_id=repository_workflow_run_id,
            codebase_workflow_run_id=codebase_workflow_run_id,
            programming_language_metadata=programming_language_metadata,
            agent_stats=agent_stats,
            agent_errors=agent_errors,
        )

        codebase_statistics = aggregate_usage_statistics(agent_stats)

        if agent_errors:
            error_summary = (
                f"Agent execution failed for {len(agent_errors)} agent(s) in codebase "
                f"'{codebase_metadata.codebase_name}'"
            )
            logger.warning(
                "[workflow] {} - raising ApplicationError to propagate to interceptor",
                error_summary,
            )
            raise ApplicationError(
                error_summary,
                agent_errors,
                type="AgentExecutionError",
                non_retryable=True,
            )

        logger.info(
            "[workflow] CodebaseAgentWorkflow completed for {}/{}",
            repository_qualified_name,
            codebase_metadata.codebase_name,
        )
        logger.debug("[workflow] CodebaseAgentWorkflow.run END")

        return codebase_statistics.model_dump()
