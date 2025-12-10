"""Temporal workflow definitions for durable agent execution.

This module defines the RepositoryAgentWorkflow that orchestrates
sequential execution of all agents per codebase.
"""

from datetime import timedelta
from typing import Any

from temporalio import common, workflow

# Import non-deterministic/logging/DB-dependent modules outside the sandbox
# so the workflow sandbox does not attempt to proxy them.
with workflow.unsafe.imports_passed_through():
    from loguru import logger

    from unoplat_code_confluence_query_engine.models.output.agent_md_output import (
        DevelopmentWorkflow,
        ProjectConfiguration,
    )
    from unoplat_code_confluence_query_engine.models.repository.repository_ruleset_metadata import (
        CodebaseMetadata,
    )
    from unoplat_code_confluence_query_engine.models.runtime.agent_dependencies import (
        AgentDependencies,
    )
    from unoplat_code_confluence_query_engine.services.temporal.activities.repository_agent_snapshot_activity import (
        RepositoryAgentSnapshotActivity,
    )
    from unoplat_code_confluence_query_engine.services.temporal.interceptors.agent_workflow_interceptor import (
        DB_ACTIVITY_RETRY_POLICY,
    )
    from unoplat_code_confluence_query_engine.services.temporal.temporal_agents import (
        get_temporal_agents,
    )
    from unoplat_code_confluence_query_engine.services.temporal.workflow_envelopes import (
        AgentSnapshotCompleteEnvelope,
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
    ) -> dict[str, Any]:
        """Execute all agents sequentially for a single codebase.

        Args:
            repository_qualified_name: Repository identifier (e.g., "owner/repo")
            codebase_metadata_dict: Serialized CodebaseMetadata
            repository_workflow_run_id: Unique workflow run ID for event tracking
            trace_id: Trace ID for distributed tracing (from API level)

        Returns:
            Dictionary containing results from all agents
        """
        logger.debug("[workflow] CodebaseAgentWorkflow.run START")
        # Reconstruct CodebaseMetadata from dict
        logger.debug("[workflow] Validating codebase_metadata_dict...")
        codebase_metadata = CodebaseMetadata.model_validate(codebase_metadata_dict)
        logger.debug(
            f"[workflow] CodebaseMetadata validated: {codebase_metadata.codebase_name}"
        )

        logger.info(
            "[workflow] Starting CodebaseAgentWorkflow for {}/{}",
            repository_qualified_name,
            codebase_metadata.codebase_name,
        )

        # Get temporal agents
        logger.debug("[workflow] Getting temporal agents...")
        temporal_agents = get_temporal_agents()
        logger.debug("[workflow] Got temporal agents: {}", list(temporal_agents.keys()))

        results: dict[str, Any] = {
            "codebase_name": codebase_metadata.codebase_name,
            "project_configuration": None,
            "development_workflow": None,
            "business_logic_domain": None,
        }

        # Step 1: Project Configuration Agent
        if "project_configuration_agent" in temporal_agents:
            try:
                logger.info(
                    f"[workflow] Running project_configuration_agent for {codebase_metadata.codebase_name}"
                )
                project_config_deps = AgentDependencies(
                    repository_qualified_name=repository_qualified_name,
                    codebase_metadata=codebase_metadata,
                    repository_workflow_run_id=repository_workflow_run_id,
                    agent_name="project_configuration_agent",
                )
                logger.debug(
                    "[workflow] Calling temporal_agents['project_configuration_agent'].run()..."
                )
                config_result = await temporal_agents[
                    "project_configuration_agent"
                ].run(
                    f"Analyze the codebase at {codebase_metadata.codebase_path} "
                    f"for programming language {codebase_metadata.codebase_programming_language}",
                    deps=project_config_deps,
                )
                logger.debug("[workflow] project_configuration_agent.run() returned")
                results["project_configuration"] = (
                    config_result.output.model_dump()
                    if isinstance(config_result.output, ProjectConfiguration)
                    else config_result.output
                )
                logger.info(
                    "[workflow] project_configuration_agent completed for {}",
                    codebase_metadata.codebase_name,
                )
            except Exception as e:
                logger.error(
                    "[workflow] project_configuration_agent failed for {}: {}",
                    codebase_metadata.codebase_name,
                    e,
                )
                logger.exception("[workflow] Full traceback:")
                results["project_configuration_error"] = str(e)
        else:
            logger.info(
                "[workflow] project_configuration_agent is disabled, skipping for {}",
                codebase_metadata.codebase_name,
            )

        # Step 2: Development Workflow Agent (depends on Step 1)
        if "development_workflow_agent" in temporal_agents:
            try:
                logger.info(
                    "[workflow] Running development_workflow_agent for {}",
                    codebase_metadata.codebase_name,
                )
                config_context = (
                    f"Project configuration: {results['project_configuration']}"
                    if results["project_configuration"]
                    else ""
                )
                dev_workflow_deps = AgentDependencies(
                    repository_qualified_name=repository_qualified_name,
                    codebase_metadata=codebase_metadata,
                    repository_workflow_run_id=repository_workflow_run_id,
                    agent_name="development_workflow_agent",
                )
                logger.debug(
                    "[workflow] Calling temporal_agents['development_workflow_agent'].run()..."
                )
                workflow_result = await temporal_agents[
                    "development_workflow_agent"
                ].run(
                    f"Analyze development workflow for {codebase_metadata.codebase_path}. {config_context}",
                    deps=dev_workflow_deps,
                )
                logger.debug("[workflow] development_workflow_agent.run() returned")
                results["development_workflow"] = (
                    workflow_result.output.model_dump()
                    if isinstance(workflow_result.output, DevelopmentWorkflow)
                    else workflow_result.output
                )
                logger.info(
                    "[workflow] development_workflow_agent completed for {}",
                    codebase_metadata.codebase_name,
                )
            except Exception as e:
                logger.error(
                    "[workflow] development_workflow_agent failed for {}: {}",
                    codebase_metadata.codebase_name,
                    e,
                )
                logger.exception("[workflow] Full traceback:")
                results["development_workflow_error"] = str(e)
        else:
            logger.info(
                "[workflow] development_workflow_agent is disabled, skipping for {}",
                codebase_metadata.codebase_name,
            )

        # Step 3: Business Logic Domain Agent
        if "business_logic_domain_agent" in temporal_agents:
            try:
                logger.info(
                    "[workflow] Running business_logic_domain_agent for {}",
                    codebase_metadata.codebase_name,
                )
                business_logic_deps = AgentDependencies(
                    repository_qualified_name=repository_qualified_name,
                    codebase_metadata=codebase_metadata,
                    repository_workflow_run_id=repository_workflow_run_id,
                    agent_name="business_logic_domain_agent",
                )
                logger.debug(
                    "[workflow] Calling temporal_agents['business_logic_domain_agent'].run()..."
                )
                domain_result = await temporal_agents[
                    "business_logic_domain_agent"
                ].run(
                    f"Analyze business logic domain for {codebase_metadata.codebase_path}",
                    deps=business_logic_deps,
                )
                logger.debug("[workflow] business_logic_domain_agent.run() returned")
                results["business_logic_domain"] = domain_result.output
                logger.info(
                    "[workflow] business_logic_domain_agent completed for {}",
                    codebase_metadata.codebase_name,
                )
            except Exception as e:
                logger.error(
                    "[workflow] business_logic_domain_agent failed for {}: {}",
                    codebase_metadata.codebase_name,
                    e,
                )
                logger.exception("[workflow] Full traceback:")
                results["business_logic_domain_error"] = str(e)
        else:
            logger.info(
                "[workflow] business_logic_domain_agent is disabled, skipping for {}",
                codebase_metadata.codebase_name,
            )

        logger.info(
            "[workflow] CodebaseAgentWorkflow completed for {}/{}",
            repository_qualified_name,
            codebase_metadata.codebase_name,
        )
        logger.debug("[workflow] CodebaseAgentWorkflow.run END")

        return results


@workflow.defn(versioning_behavior=common.VersioningBehavior.AUTO_UPGRADE)
class RepositoryAgentWorkflow:
    """Main workflow to orchestrate agent execution across all codebases."""

    @workflow.run
    async def run(
        self,
        repository_qualified_name: str,
        codebase_metadata_list: list[dict[str, Any]],
        repository_workflow_run_id: str,
        trace_id: str = "",
    ) -> dict[str, Any]:
        """Execute agents for all codebases in a repository.

        Args:
            repository_qualified_name: Repository identifier (e.g., "owner/repo")
            codebase_metadata_list: List of serialized CodebaseMetadata dicts
            repository_workflow_run_id: Unique workflow run ID for event tracking
            trace_id: Trace ID for distributed tracing (from API level)

        Returns:
            Aggregated results from all codebases
        """
        logger.debug("[workflow] RepositoryAgentWorkflow.run START")
        logger.info(
            "[workflow] Starting RepositoryAgentWorkflow for {} with {} codebases",
            repository_qualified_name,
            len(codebase_metadata_list),
        )

        results: dict[str, Any] = {
            "repository": repository_qualified_name,
            "codebases": {},
        }

        # Execute CodebaseAgentWorkflow for each codebase
        # Note: In production, this could use child workflows for better isolation
        for idx, codebase_dict in enumerate(codebase_metadata_list):
            codebase_name = codebase_dict.get("codebase_name", "unknown")
            logger.debug(
                "[workflow] Processing codebase {}/{}: {}",
                idx + 1,
                len(codebase_metadata_list),
                codebase_name,
            )

            try:
                # Execute as child workflow for durability
                logger.debug(
                    "[workflow] Executing child workflow for {}", codebase_name
                )
                codebase_result = await workflow.execute_child_workflow(  # type: ignore[reportUnknownMemberType]
                    CodebaseAgentWorkflow.run,
                    args=[
                        repository_qualified_name,
                        codebase_dict,
                        repository_workflow_run_id,
                        trace_id,
                    ],
                    id=f"{repository_qualified_name.replace('/', '-')}-{codebase_name}",
                )
                logger.debug(
                    "[workflow] Child workflow completed for {}", codebase_name
                )
                results["codebases"][codebase_name] = codebase_result
            except Exception as e:
                logger.error(
                    "[workflow] CodebaseAgentWorkflow failed for {}/{}: {}",
                    repository_qualified_name,
                    codebase_name,
                    e,
                )
                logger.exception("[workflow] Full traceback:")
                results["codebases"][codebase_name] = {"error": str(e)}

        logger.info(
            f"[workflow] RepositoryAgentWorkflow completed for {repository_qualified_name}"
        )

        # Persist final agent output to database via activity
        owner_name, repo_name = repository_qualified_name.split("/", maxsplit=1)
        complete_envelope = AgentSnapshotCompleteEnvelope(
            owner_name=owner_name,
            repo_name=repo_name,
            final_payload=results,
            statistics_payload=None,  # task-013 will add statistics collection
        )
        await workflow.execute_activity(
            RepositoryAgentSnapshotActivity.persist_agent_snapshot_complete,
            args=[complete_envelope],
            start_to_close_timeout=timedelta(minutes=2),
            retry_policy=DB_ACTIVITY_RETRY_POLICY,
        )
        logger.info(
            "[workflow] Agent snapshot output persisted for {}",
            repository_qualified_name,
        )

        logger.debug("[workflow] RepositoryAgentWorkflow.run END")

        return results
