"""Temporal workflow definitions for durable agent execution.

This module defines the RepositoryAgentWorkflow that orchestrates
parallel execution of CodebaseAgentWorkflows for each codebase in a repository.
"""

from datetime import timedelta
import traceback
from typing import Any

from temporalio import common, workflow
from temporalio.exceptions import ApplicationError
from temporalio.workflow import ChildWorkflowHandle, ParentClosePolicy

# Import non-deterministic/logging/DB-dependent modules outside the sandbox
# so the workflow sandbox does not attempt to proxy them.
with workflow.unsafe.imports_passed_through():
    import asyncio

    from loguru import logger

    from unoplat_code_confluence_query_engine.models.output.agent_md_output import (
        DependencyGuideEntry,
        DevelopmentWorkflow,
        ProjectConfiguration,
    )
    from unoplat_code_confluence_query_engine.models.repository.repository_ruleset_metadata import (
        CodebaseMetadata,
    )
    from unoplat_code_confluence_query_engine.models.runtime.agent_dependencies import (
        AgentDependencies,
    )
    from unoplat_code_confluence_query_engine.models.statistics.agent_usage_statistics import (
        UsageStatistics,
    )
    from unoplat_code_confluence_query_engine.services.temporal.activities.business_logic_post_process_activity import (
        BusinessLogicPostProcessActivity,
    )
    from unoplat_code_confluence_query_engine.services.temporal.activities.dependency_guide_completion_activity import (
        DependencyGuideCompletionActivity,
    )
    from unoplat_code_confluence_query_engine.services.temporal.activities.dependency_guide_fetch_activity import (
        DependencyGuideFetchActivity,
    )
    from unoplat_code_confluence_query_engine.services.temporal.activities.repository_agent_snapshot_activity import (
        RepositoryAgentSnapshotActivity,
    )
    from unoplat_code_confluence_query_engine.services.temporal.interceptors.agent_workflow_interceptor import (
        DB_ACTIVITY_RETRY_POLICY,
    )
    from unoplat_code_confluence_query_engine.services.temporal.statistics_helpers import (
        aggregate_usage_statistics,
        build_workflow_statistics,
        create_zero_usage_statistics,
        extract_usage_statistics,
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
            "programming_language_metadata": {
                "primary_language": codebase_metadata.codebase_programming_language,
                "package_manager": codebase_metadata.codebase_package_manager,
            },
            "project_configuration": None,
            "development_workflow": None,
            "dependency_guide": None,
            "business_logic_domain": None,
        }

        # Track usage statistics from each agent for aggregation
        agent_stats: list[UsageStatistics] = []

        # Track errors from agent execution (continue & collect all strategy)
        agent_errors: list[dict[str, Any]] = []

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
                # Extract usage statistics from successful agent run
                agent_stats.append(extract_usage_statistics(config_result.usage()))
            except Exception as e:
                logger.error(
                    "[workflow] project_configuration_agent failed for {}: {}",
                    codebase_metadata.codebase_name,
                    e,
                )
                logger.exception("[workflow] Full traceback:")
                # Collect error for aggregation - do NOT store in results
                agent_errors.append({
                    "agent": "project_configuration_agent",
                    "codebase": codebase_metadata.codebase_name,
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                })
                # Failed agents contribute zero to statistics
                agent_stats.append(create_zero_usage_statistics())
        else:
            logger.info(
                "[workflow] project_configuration_agent is disabled, skipping for {}",
                codebase_metadata.codebase_name,
            )
            # Disabled agents contribute zero to statistics
            agent_stats.append(create_zero_usage_statistics())

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
                # Extract usage statistics from successful agent run
                agent_stats.append(extract_usage_statistics(workflow_result.usage()))
            except Exception as e:
                logger.error(
                    "[workflow] development_workflow_agent failed for {}: {}",
                    codebase_metadata.codebase_name,
                    e,
                )
                logger.exception("[workflow] Full traceback:")
                # Collect error for aggregation - do NOT store in results
                agent_errors.append({
                    "agent": "development_workflow_agent",
                    "codebase": codebase_metadata.codebase_name,
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                })
                # Failed agents contribute zero to statistics
                agent_stats.append(create_zero_usage_statistics())
        else:
            logger.info(
                "[workflow] development_workflow_agent is disabled, skipping for {}",
                codebase_metadata.codebase_name,
            )
            # Disabled agents contribute zero to statistics
            agent_stats.append(create_zero_usage_statistics())

        # Step 3: Dependency Guide Agent
        if "dependency_guide_agent" in temporal_agents:
            try:
                # Fetch dependency names from PostgreSQL via activity (deterministic)
                dependency_names: list[str] = await workflow.execute_activity(
                    DependencyGuideFetchActivity.fetch_codebase_dependencies,
                    args=[codebase_metadata.codebase_path],
                    start_to_close_timeout=timedelta(seconds=30),
                    retry_policy=DB_ACTIVITY_RETRY_POLICY,
                )

                logger.info(
                    "[workflow] Found {} dependencies for {}",
                    len(dependency_names),
                    codebase_metadata.codebase_name,
                )

                # Process each dependency sequentially
                dependency_entries: list[dict[str, Any]] = []
                dependency_agent_stats: list[UsageStatistics] = []

                for dep_name in dependency_names:
                    try:
                        deps = AgentDependencies(
                            repository_qualified_name=repository_qualified_name,
                            codebase_metadata=codebase_metadata,
                            repository_workflow_run_id=repository_workflow_run_id,
                            agent_name="dependency_guide_agent_item",
                        )
                        result = await temporal_agents["dependency_guide_agent"].run(
                            f"Document the library '{dep_name}' for programming language {codebase_metadata.codebase_programming_language}",
                            deps=deps,
                        )

                        entry_dict = (
                            result.output.model_dump()
                            if isinstance(result.output, DependencyGuideEntry)
                            else result.output
                        )
                        dependency_entries.append(entry_dict)
                        dependency_agent_stats.append(
                            extract_usage_statistics(result.usage())
                        )
                    except Exception as dep_error:
                        logger.warning(
                            "[workflow] Failed to document dependency '{}': {}",
                            dep_name,
                            dep_error,
                        )
                        # Continue with other dependencies - don't fail entire agent
                        dependency_agent_stats.append(create_zero_usage_statistics())

                # Aggregate into DependencyGuide
                results["dependency_guide"] = {"dependencies": dependency_entries}

                # Emit a single completion event for the dependency guide agent
                await workflow.execute_activity(
                    DependencyGuideCompletionActivity.emit_dependency_guide_completion,
                    args=[
                        repository_qualified_name,
                        repository_workflow_run_id,
                        codebase_metadata.codebase_name,
                    ],
                    start_to_close_timeout=timedelta(seconds=30),
                    retry_policy=DB_ACTIVITY_RETRY_POLICY,
                )

                # Aggregate stats from all dependency runs
                if dependency_agent_stats:
                    agent_stats.append(aggregate_usage_statistics(dependency_agent_stats))
                else:
                    agent_stats.append(create_zero_usage_statistics())

                logger.info(
                    "[workflow] dependency_guide_agent completed for {}: {} entries",
                    codebase_metadata.codebase_name,
                    len(dependency_entries),
                )
            except Exception as e:
                logger.error(
                    "[workflow] dependency_guide_agent failed for {}: {}",
                    codebase_metadata.codebase_name,
                    e,
                )
                logger.exception("[workflow] Full traceback:")
                agent_errors.append({
                    "agent": "dependency_guide_agent",
                    "codebase": codebase_metadata.codebase_name,
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                })
                agent_stats.append(create_zero_usage_statistics())
        else:
            logger.info(
                "[workflow] dependency_guide_agent is disabled, skipping for {}",
                codebase_metadata.codebase_name,
            )
            agent_stats.append(create_zero_usage_statistics())

        # Step 4: Business Logic Domain Agent
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
                # Post-process to enrich with data model files from PostgreSQL
                business_logic_result = await workflow.execute_activity(
                    BusinessLogicPostProcessActivity.post_process_business_logic,
                    args=[
                        domain_result.output,  # str description from agent
                        codebase_metadata.codebase_path,
                        codebase_metadata.codebase_programming_language,
                    ],
                    start_to_close_timeout=timedelta(minutes=1),
                    retry_policy=DB_ACTIVITY_RETRY_POLICY,
                )
                results["business_logic_domain"] = business_logic_result
                logger.info(
                    "[workflow] business_logic_domain_agent completed for {}",
                    codebase_metadata.codebase_name,
                )
                # Extract usage statistics from successful agent run
                agent_stats.append(extract_usage_statistics(domain_result.usage()))
            except Exception as e:
                logger.error(
                    "[workflow] business_logic_domain_agent failed for {}: {}",
                    codebase_metadata.codebase_name,
                    e,
                )
                logger.exception("[workflow] Full traceback:")
                # Collect error for aggregation - do NOT store in results
                agent_errors.append({
                    "agent": "business_logic_domain_agent",
                    "codebase": codebase_metadata.codebase_name,
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                })
                # Failed agents contribute zero to statistics
                agent_stats.append(create_zero_usage_statistics())
        else:
            logger.info(
                "[workflow] business_logic_domain_agent is disabled, skipping for {}",
                codebase_metadata.codebase_name,
            )
            # Disabled agents contribute zero to statistics
            agent_stats.append(create_zero_usage_statistics())

        # Aggregate statistics from all agents and add to results
        codebase_statistics = aggregate_usage_statistics(agent_stats)
        results["statistics"] = codebase_statistics.model_dump()

        # If any agents failed, raise ApplicationError to propagate to interceptor
        # This triggers ERROR status in DB and populates error_report
        if agent_errors:
            error_summary = f"Agent execution failed for {len(agent_errors)} agent(s) in codebase '{codebase_metadata.codebase_name}'"
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

        # Track per-codebase statistics for workflow-level aggregation
        codebase_statistics_map: dict[str, UsageStatistics] = {}

        # Phase 1: Start all child workflows (non-blocking)
        # Each start_child_workflow returns immediately with a handle
        child_handles: list[tuple[str, ChildWorkflowHandle[CodebaseAgentWorkflow, dict[str, Any]]]] = []

        for idx, codebase_dict in enumerate(codebase_metadata_list):
            codebase_name = codebase_dict.get("codebase_name", "unknown")
            logger.debug(
                "[workflow] Starting child workflow {}/{}: {}",
                idx + 1,
                len(codebase_metadata_list),
                codebase_name,
            )

            child_handle = await workflow.start_child_workflow(  # type: ignore[reportUnknownMemberType]
                CodebaseAgentWorkflow.run,
                args=[
                    repository_qualified_name,
                    codebase_dict,
                    repository_workflow_run_id,
                    trace_id,
                ],
                id=f"{repository_qualified_name.replace('/', '-')}-{codebase_name}",
                parent_close_policy=ParentClosePolicy.TERMINATE,
            )
            child_handles.append((codebase_name, child_handle))

        logger.info(
            "[workflow] Started {} child workflows, waiting for parallel completion",
            len(child_handles),
        )

        # Phase 2: Wait for all children in parallel using asyncio.gather
        # return_exceptions=True ensures partial failures don't stop other children
        results_list: list[dict[str, Any] | BaseException] = await asyncio.gather(
            *[handle for _, handle in child_handles],
            return_exceptions=True,
        )

        # Phase 3: Process results, build statistics map, and track child errors
        # Track child workflow errors for aggregation - do NOT store in results
        child_errors: list[dict[str, str]] = []

        for (codebase_name, _), result in zip(child_handles, results_list):
            if isinstance(result, BaseException):
                logger.error(
                    "[workflow] CodebaseAgentWorkflow failed for {}/{}: {}",
                    repository_qualified_name,
                    codebase_name,
                    result,
                )
                # Collect error for aggregation - do NOT store in results
                child_errors.append({
                    "codebase": codebase_name,
                    "error": str(result),
                })
                codebase_statistics_map[codebase_name] = create_zero_usage_statistics()
            else:
                logger.debug(
                    "[workflow] Child workflow completed for {}", codebase_name
                )
                results["codebases"][codebase_name] = result

                # Extract per-codebase statistics from child workflow result
                if "statistics" in result and result["statistics"]:
                    codebase_stats = UsageStatistics.model_validate(result["statistics"])
                    codebase_statistics_map[codebase_name] = codebase_stats
                else:
                    codebase_statistics_map[codebase_name] = create_zero_usage_statistics()

        logger.info(
            f"[workflow] RepositoryAgentWorkflow processed {len(codebase_metadata_list)} codebases for {repository_qualified_name}"
        )

        # Build workflow-level statistics from all codebases
        workflow_statistics = build_workflow_statistics(codebase_statistics_map)

        # Persist final agent output to database via activity
        owner_name, repo_name = repository_qualified_name.split("/", maxsplit=1)
        complete_envelope = AgentSnapshotCompleteEnvelope(
            owner_name=owner_name,
            repo_name=repo_name,
            repository_workflow_run_id=repository_workflow_run_id,
            final_payload=results,
            statistics_payload=workflow_statistics.model_dump(),
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

        # If any child workflows failed, raise ApplicationError to propagate to interceptor
        # This triggers ERROR status in DB and populates error_report
        # Raise AFTER persisting snapshot so we don't lose partial results
        if child_errors:
            error_summary = f"{len(child_errors)} codebase(s) failed during agent execution"
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

        return results
