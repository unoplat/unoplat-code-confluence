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

    from unoplat_code_confluence_query_engine.models.output.agents_md_updater_output import (
        SectionId,
    )
    from unoplat_code_confluence_query_engine.models.repository.framework_feature_validation_models import (
        FrameworkFeatureValidationCandidate,
    )
    from unoplat_code_confluence_query_engine.models.repository.repository_ruleset_metadata import (
        CodebaseMetadata,
    )
    from unoplat_code_confluence_query_engine.models.runtime.agent_dependencies import (
        AgentDependencies,
    )
    from unoplat_code_confluence_query_engine.models.runtime.dependency_guide_target import (
        DependencyGuideTarget,
    )
    from unoplat_code_confluence_query_engine.models.statistics.agent_usage_statistics import (
        UsageStatistics,
    )
    from unoplat_code_confluence_query_engine.services.repository.engineering_workflow_service import (
        normalize_engineering_workflow,
    )
    from unoplat_code_confluence_query_engine.services.temporal.activities.app_interfaces_activity import (
        AppInterfacesActivity,
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
    from unoplat_code_confluence_query_engine.services.temporal.activities.engineering_workflow_completion_activity import (
        EngineeringWorkflowCompletionActivity,
    )
    from unoplat_code_confluence_query_engine.services.temporal.activities.repository_agent_snapshot_activity import (
        RepositoryAgentSnapshotActivity,
    )
    from unoplat_code_confluence_query_engine.services.temporal.cancellation_helpers import (
        is_temporal_cancellation_exception,
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
        SECTION_UPDATER_AGENT_NAMES,
        TemporalAgentRegistry,
        build_section_updater_prompt,
        get_cached_usage_limits,
        get_temporal_agents,
    )
    from unoplat_code_confluence_query_engine.services.temporal.workflow_envelopes import (
        AgentSnapshotCompleteEnvelope,
    )
    from unoplat_code_confluence_query_engine.utils.agent_error_logger import (
        extract_model_error_from_exception,
    )
    from unoplat_code_confluence_query_engine.utils.framework_feature_language_support import (
        is_app_interfaces_supported,
    )


def _enrich_agent_error_with_model_details(
    error_dict: dict[str, object],
    exception: BaseException,
    agent_name: str,
    codebase_name: str,
) -> dict[str, object]:
    """Enrich an agent error dict with model error details if present.

    Args:
        error_dict: Existing error dictionary to enrich
        exception: The exception that was caught
        agent_name: Name of the agent that failed
        codebase_name: Name of the codebase being processed

    Returns:
        Enriched error dictionary with model_error_details if found
    """
    context: dict[str, object] = {
        "agent_name": agent_name,
        "codebase": codebase_name,
    }
    model_error_details = extract_model_error_from_exception(exception, context=context)
    if model_error_details:
        error_dict["model_error_details"] = model_error_details
    return error_dict


def _raise_if_temporal_cancellation(exception: BaseException) -> None:
    """Re-raise cancellation-shaped exceptions so workflow cancel is preserved."""
    if is_temporal_cancellation_exception(exception):
        logger.info("[workflow] Cancellation detected, re-raising")
        raise exception


def _build_dependency_guide_prompt(
    dependency_target: DependencyGuideTarget,
    programming_language: str,
) -> str:
    """Build the dependency-guide prompt for one normalized target."""
    prompt = (
        f"Document the library '{dependency_target.name}' for programming language "
        f"{programming_language}."
    )
    if dependency_target.search_query:
        prompt += (
            " When searching for official documentation, use this exact primary "
            f"query hint: '{dependency_target.search_query}'."
        )
    if len(dependency_target.source_packages) > 1:
        prompt += (
            " This configured UI component library family represents the following "
            f"packages: {', '.join(dependency_target.source_packages)}."
        )
    return prompt


async def _run_section_updater(
    temporal_agents: TemporalAgentRegistry,
    section_id: SectionId,
    codebase_metadata: CodebaseMetadata,
    repository_qualified_name: str,
    repository_workflow_run_id: str,
    programming_language_metadata: dict[str, object],
    section_data: object,
    agent_stats: list[UsageStatistics],
    agent_errors: list[dict[str, object]],
    updater_runs: list[dict[str, object]],
) -> None:
    """Run agents_md_updater for a specific section after its guide completes."""
    if "agents_md_updater" not in temporal_agents:
        agent_stats.append(create_zero_usage_statistics())
        return

    updater_agent_name = SECTION_UPDATER_AGENT_NAMES[section_id]
    try:
        logger.info(
            "[workflow] Running {} for {}",
            updater_agent_name,
            codebase_metadata.codebase_name,
        )
        updater_deps = AgentDependencies(
            repository_qualified_name=repository_qualified_name,
            codebase_metadata=codebase_metadata,
            repository_workflow_run_id=repository_workflow_run_id,
            agent_name=updater_agent_name,
        )
        updater_prompt = build_section_updater_prompt(
            section_id=section_id,
            codebase_path=codebase_metadata.codebase_path,
            programming_language_metadata=programming_language_metadata,
            section_data=section_data,
        )
        updater_result = await temporal_agents["agents_md_updater"].run(
            updater_prompt,
            deps=updater_deps,
            usage_limits=get_cached_usage_limits(),
        )
        output_dict = updater_result.output.model_dump(mode="json")
        updater_runs.append(
            {
                "section_id": section_id.value,
                "agent_name": updater_agent_name,
                "output": output_dict,
            }
        )
        agent_stats.append(extract_usage_statistics(updater_result.usage()))
        logger.info(
            "[workflow] {} completed for {}",
            updater_agent_name,
            codebase_metadata.codebase_name,
        )
    except Exception as e:
        _raise_if_temporal_cancellation(e)
        logger.error(
            "[workflow] {} failed for {}: {}",
            updater_agent_name,
            codebase_metadata.codebase_name,
            e,
        )
        logger.exception("[workflow] Full traceback:")
        error_entry: dict[str, object] = {
            "agent": updater_agent_name,
            "codebase": codebase_metadata.codebase_name,
            "error": str(e),
            "traceback": traceback.format_exc(),
        }
        error_entry = _enrich_agent_error_with_model_details(
            error_entry,
            e,
            updater_agent_name,
            codebase_metadata.codebase_name,
        )
        agent_errors.append(error_entry)
        agent_stats.append(create_zero_usage_statistics())


def _build_call_expression_validator_prompt(
    candidate: FrameworkFeatureValidationCandidate,
) -> str:
    """Build validator prompt for a single low-confidence CallExpression candidate.

    Args:
        candidate: Candidate payload selected from low-confidence CallExpression rows.

    Returns:
        Prompt text instructing a strict tool-execution sequence.
    """
    candidate_fields = (
        "identity, concept, match_confidence, validation_status, match_text, "
        "evidence_json, base_confidence, notes, construct_query, absolute_paths"
    )
    identity_fields = "file_path, feature_language, feature_library, feature_key, start_line, end_line"
    evidence_fields = (
        "concept, source, match_confidence, call_match_kind, matched_absolute_path, "
        "matched_alias, call_match_policy_version, callee, args_text, validator"
    )
    return (
        "Validate this low-confidence CallExpression candidate for app-interface mapping.\n"
        "You are given candidate metadata plus detector evidence to verify against official documentation and local code.\n"
        "You MUST persist writes using both validator write tools in order.\n\n"
        "Candidate payload guide:\n"
        f"- top-level fields: {candidate_fields}\n"
        f"- identity fields: {identity_fields}\n"
        "- evidence_json may be partial or absent; when present for CallExpression it commonly contains detector metadata and parsed call evidence.\n"
        f"- expected CallExpression evidence_json keys: {evidence_fields}\n\n"
        "Required review order:\n"
        "1) Review official framework documentation first and determine what the claimed API usage should look like.\n"
        "2) Compare docs expectations against candidate metadata/evidence_json and note present vs missing fields.\n"
        "3) Read local file context with read_file_content.\n"
        "4) Expand nearby symbol/object evidence with search_across_codebase.\n"
        "5) Record gaps/mismatches before deciding (for example: import-binding mismatch, alias/path mismatch, API-shape mismatch, insufficient provenance, unsupported args, or docs mismatch).\n"
        "6) Persist evidence/confidence, then persist status, then return output.\n\n"
        "Required write sequence:\n"
        "1) upsert_framework_feature_validation_evidence(request=...)\n"
        "2) set_framework_feature_validation_status(request=...)\n"
        "3) return output for the same identity\n\n"
        "When you upsert evidence_json, include documentation findings, metadata review, local code findings, gap analysis, and final rationale.\n\n"
        "Candidate payload JSON:\n"
        f"{candidate.model_dump_json(indent=2)}"
    )


async def _run_call_expression_validation(
    temporal_agents: TemporalAgentRegistry,
    codebase_metadata: CodebaseMetadata,
    repository_qualified_name: str,
    repository_workflow_run_id: str,
    candidate_payloads: list[dict[str, object]],
    agent_stats: list[UsageStatistics],
    agent_errors: list[dict[str, object]],
) -> None:
    """Execute call_expression_validator for low-confidence candidates.

    Args:
        temporal_agents: Initialized temporal agent registry.
        codebase_metadata: Current codebase metadata.
        repository_qualified_name: Repository qualified name.
        repository_workflow_run_id: Workflow run identifier.
        candidate_payloads: Serialized low-confidence candidate payloads.
        agent_stats: Mutable list for usage-stat aggregation.
        agent_errors: Mutable list for workflow error aggregation.
    """
    if not candidate_payloads:
        logger.info(
            "[workflow] No low-confidence CallExpression candidates found for {}",
            codebase_metadata.codebase_name,
        )
        return

    if "call_expression_validator" not in temporal_agents:
        logger.info(
            "[workflow] call_expression_validator is disabled; skipping {} candidates for {}",
            len(candidate_payloads),
            codebase_metadata.codebase_name,
        )
        agent_stats.append(create_zero_usage_statistics())
        return

    logger.info(
        "[workflow] Running call_expression_validator for {} candidates in {}",
        len(candidate_payloads),
        codebase_metadata.codebase_name,
    )

    for candidate_payload in candidate_payloads:
        candidate = FrameworkFeatureValidationCandidate.model_validate(
            candidate_payload
        )
        validator_deps = AgentDependencies(
            repository_qualified_name=repository_qualified_name,
            codebase_metadata=codebase_metadata,
            repository_workflow_run_id=repository_workflow_run_id,
            agent_name="call_expression_validator",
        )
        validator_prompt = _build_call_expression_validator_prompt(candidate)

        try:
            validator_result = await temporal_agents["call_expression_validator"].run(
                validator_prompt,
                deps=validator_deps,
                usage_limits=get_cached_usage_limits(),
            )
            agent_stats.append(extract_usage_statistics(validator_result.usage()))
        except Exception as validator_error:
            _raise_if_temporal_cancellation(validator_error)
            logger.error(
                "[workflow] call_expression_validator failed for {}:{}:{}:{}:{}-{}: {}",
                candidate.identity.feature_language,
                candidate.identity.feature_library,
                candidate.identity.feature_key,
                candidate.identity.file_path,
                candidate.identity.start_line,
                candidate.identity.end_line,
                validator_error,
            )
            logger.exception("[workflow] Full traceback:")
            validator_error_entry: dict[str, object] = {
                "agent": "call_expression_validator",
                "codebase": codebase_metadata.codebase_name,
                "error": str(validator_error),
                "traceback": traceback.format_exc(),
                "candidate_identity": candidate.identity.model_dump(mode="json"),
            }
            validator_error_entry = _enrich_agent_error_with_model_details(
                validator_error_entry,
                validator_error,
                "call_expression_validator",
                codebase_metadata.codebase_name,
            )
            agent_errors.append(validator_error_entry)
            agent_stats.append(create_zero_usage_statistics())


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
            "engineering_workflow": None,
            "dependency_guide": None,
            "business_logic_domain": None,
            "app_interfaces": None,
            "agents_md_updater_runs": [],
        }

        # Track usage statistics from each agent for aggregation
        agent_stats: list[UsageStatistics] = []

        # Track errors from agent execution (continue & collect all strategy)
        agent_errors: list[dict[str, Any]] = []

        # Step 1: Development Workflow Guide
        if "development_workflow_guide" in temporal_agents:
            try:
                logger.info(
                    "[workflow] Running development_workflow_guide for {}",
                    codebase_metadata.codebase_name,
                )
                engineering_workflow_deps = AgentDependencies(
                    repository_qualified_name=repository_qualified_name,
                    codebase_metadata=codebase_metadata,
                    repository_workflow_run_id=repository_workflow_run_id,
                    agent_name="development_workflow_guide",
                )
                logger.debug(
                    "[workflow] Calling temporal_agents['development_workflow_guide'].run()..."
                )
                workflow_result = await temporal_agents[
                    "development_workflow_guide"
                ].run(
                    (
                        f"Analyze engineering workflow for {codebase_metadata.codebase_path} "
                        f"using language {codebase_metadata.codebase_programming_language} "
                        f"and package manager {codebase_metadata.codebase_package_manager}"
                    ),
                    deps=engineering_workflow_deps,
                    usage_limits=get_cached_usage_limits(),
                )
                logger.debug("[workflow] development_workflow_guide.run() returned")

                raw_engineering_workflow = workflow_result.output.model_dump(
                    mode="json"
                )
                normalized_workflow = normalize_engineering_workflow(
                    raw_engineering_workflow
                )
                results["engineering_workflow"] = normalized_workflow.model_dump()

                # Emit completion event for deterministic progress tracking.
                await workflow.execute_activity(
                    EngineeringWorkflowCompletionActivity.emit_engineering_workflow_completion,
                    args=[
                        repository_qualified_name,
                        repository_workflow_run_id,
                        codebase_metadata.codebase_name,
                        codebase_metadata.codebase_programming_language,
                    ],
                    start_to_close_timeout=timedelta(seconds=30),
                    retry_policy=DB_ACTIVITY_RETRY_POLICY,
                )

                logger.info(
                    "[workflow] development_workflow_guide completed for {}",
                    codebase_metadata.codebase_name,
                )
                agent_stats.append(extract_usage_statistics(workflow_result.usage()))

                # Run section-scoped updater for engineering workflow
                await _run_section_updater(
                    temporal_agents=temporal_agents,
                    section_id=SectionId.ENGINEERING_WORKFLOW,
                    codebase_metadata=codebase_metadata,
                    repository_qualified_name=repository_qualified_name,
                    repository_workflow_run_id=repository_workflow_run_id,
                    programming_language_metadata=results[
                        "programming_language_metadata"
                    ],
                    section_data=results["engineering_workflow"],
                    agent_stats=agent_stats,
                    agent_errors=agent_errors,
                    updater_runs=results["agents_md_updater_runs"],
                )
            except Exception as e:
                _raise_if_temporal_cancellation(e)
                logger.error(
                    "[workflow] development_workflow_guide failed for {}: {}",
                    codebase_metadata.codebase_name,
                    e,
                )
                logger.exception("[workflow] Full traceback:")
                engineering_error: dict[str, object] = {
                    "agent": "development_workflow_guide",
                    "codebase": codebase_metadata.codebase_name,
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                }
                engineering_error = _enrich_agent_error_with_model_details(
                    engineering_error,
                    e,
                    "development_workflow_guide",
                    codebase_metadata.codebase_name,
                )
                agent_errors.append(engineering_error)
                agent_stats.append(create_zero_usage_statistics())
        else:
            logger.info(
                "[workflow] development_workflow_guide is disabled, skipping for {}",
                codebase_metadata.codebase_name,
            )
            agent_stats.append(create_zero_usage_statistics())

        # Step 2: Dependency Guide
        if "dependency_guide" in temporal_agents:
            try:
                # Fetch dependency names from PostgreSQL via activity (deterministic)
                dependency_targets: list[
                    DependencyGuideTarget
                ] = await workflow.execute_activity(
                    DependencyGuideFetchActivity.fetch_codebase_dependencies,
                    args=[
                        codebase_metadata.codebase_path,
                        codebase_metadata.codebase_programming_language,
                        codebase_metadata.codebase_package_manager,
                    ],
                    start_to_close_timeout=timedelta(seconds=30),
                    retry_policy=DB_ACTIVITY_RETRY_POLICY,
                )

                logger.info(
                    "[workflow] Found {} dependency-guide targets for {}",
                    len(dependency_targets),
                    codebase_metadata.codebase_name,
                )

                # Process each dependency sequentially
                dependency_entries: list[dict[str, Any]] = []
                dependency_agent_stats: list[UsageStatistics] = []

                for dependency_target in dependency_targets:
                    try:
                        deps = AgentDependencies(
                            repository_qualified_name=repository_qualified_name,
                            codebase_metadata=codebase_metadata,
                            repository_workflow_run_id=repository_workflow_run_id,
                            agent_name="dependency_guide_item",
                        )
                        result = await temporal_agents["dependency_guide"].run(
                            _build_dependency_guide_prompt(
                                dependency_target=dependency_target,
                                programming_language=codebase_metadata.codebase_programming_language,
                            ),
                            deps=deps,
                            usage_limits=get_cached_usage_limits(),
                        )

                        entry_dict = result.output.model_dump()
                        dependency_entries.append(entry_dict)
                        dependency_agent_stats.append(
                            extract_usage_statistics(result.usage())
                        )
                    except Exception as dep_error:
                        _raise_if_temporal_cancellation(dep_error)
                        logger.warning(
                            "[workflow] Failed to document dependency '{}': {}",
                            dependency_target.name,
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
                        codebase_metadata.codebase_programming_language,
                    ],
                    start_to_close_timeout=timedelta(seconds=30),
                    retry_policy=DB_ACTIVITY_RETRY_POLICY,
                )

                # Aggregate stats from all dependency runs
                if dependency_agent_stats:
                    agent_stats.append(
                        aggregate_usage_statistics(dependency_agent_stats)
                    )
                else:
                    agent_stats.append(create_zero_usage_statistics())

                logger.info(
                    "[workflow] dependency_guide completed for {}: {} entries",
                    codebase_metadata.codebase_name,
                    len(dependency_entries),
                )

                # Run section-scoped updater for dependency guide
                await _run_section_updater(
                    temporal_agents=temporal_agents,
                    section_id=SectionId.DEPENDENCY_GUIDE,
                    codebase_metadata=codebase_metadata,
                    repository_qualified_name=repository_qualified_name,
                    repository_workflow_run_id=repository_workflow_run_id,
                    programming_language_metadata=results[
                        "programming_language_metadata"
                    ],
                    section_data=results["dependency_guide"],
                    agent_stats=agent_stats,
                    agent_errors=agent_errors,
                    updater_runs=results["agents_md_updater_runs"],
                )
            except Exception as e:
                _raise_if_temporal_cancellation(e)
                logger.error(
                    "[workflow] dependency_guide failed for {}: {}",
                    codebase_metadata.codebase_name,
                    e,
                )
                logger.exception("[workflow] Full traceback:")
                dependency_error: dict[str, object] = {
                    "agent": "dependency_guide",
                    "codebase": codebase_metadata.codebase_name,
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                }
                dependency_error = _enrich_agent_error_with_model_details(
                    dependency_error,
                    e,
                    "dependency_guide",
                    codebase_metadata.codebase_name,
                )
                agent_errors.append(dependency_error)
                agent_stats.append(create_zero_usage_statistics())
        else:
            logger.info(
                "[workflow] dependency_guide is disabled, skipping for {}",
                codebase_metadata.codebase_name,
            )
            agent_stats.append(create_zero_usage_statistics())

        # Step 4: Business Domain Guide
        if "business_domain_guide" in temporal_agents:
            try:
                logger.info(
                    "[workflow] Running business_domain_guide for {}",
                    codebase_metadata.codebase_name,
                )
                business_logic_deps = AgentDependencies(
                    repository_qualified_name=repository_qualified_name,
                    codebase_metadata=codebase_metadata,
                    repository_workflow_run_id=repository_workflow_run_id,
                    agent_name="business_domain_guide",
                )
                logger.debug(
                    "[workflow] Calling temporal_agents['business_domain_guide'].run()..."
                )
                domain_result = await temporal_agents["business_domain_guide"].run(
                    f"Analyze business logic domain for {codebase_metadata.codebase_path}",
                    deps=business_logic_deps,
                    usage_limits=get_cached_usage_limits(),
                )
                logger.debug("[workflow] business_domain_guide.run() returned")
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
                    "[workflow] business_domain_guide completed for {}",
                    codebase_metadata.codebase_name,
                )
                # Extract usage statistics from successful agent run
                agent_stats.append(extract_usage_statistics(domain_result.usage()))

                # Run section-scoped updater for business domain
                await _run_section_updater(
                    temporal_agents=temporal_agents,
                    section_id=SectionId.BUSINESS_DOMAIN,
                    codebase_metadata=codebase_metadata,
                    repository_qualified_name=repository_qualified_name,
                    repository_workflow_run_id=repository_workflow_run_id,
                    programming_language_metadata=results[
                        "programming_language_metadata"
                    ],
                    section_data=results["business_logic_domain"],
                    agent_stats=agent_stats,
                    agent_errors=agent_errors,
                    updater_runs=results["agents_md_updater_runs"],
                )
            except Exception as e:
                _raise_if_temporal_cancellation(e)
                logger.error(
                    "[workflow] business_domain_guide failed for {}: {}",
                    codebase_metadata.codebase_name,
                    e,
                )
                logger.exception("[workflow] Full traceback:")
                # Collect error for aggregation - do NOT store in results
                business_logic_error: dict[str, object] = {
                    "agent": "business_domain_guide",
                    "codebase": codebase_metadata.codebase_name,
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                }
                business_logic_error = _enrich_agent_error_with_model_details(
                    business_logic_error,
                    e,
                    "business_domain_guide",
                    codebase_metadata.codebase_name,
                )
                agent_errors.append(business_logic_error)
                # Failed agents contribute zero to statistics
                agent_stats.append(create_zero_usage_statistics())
        else:
            logger.info(
                "[workflow] business_domain_guide is disabled, skipping for {}",
                codebase_metadata.codebase_name,
            )
            # Disabled agents contribute zero to statistics
            agent_stats.append(create_zero_usage_statistics())

        # Step 5: App Interfaces (Python + TypeScript - deterministic DB activity, not LLM agent)
        if is_app_interfaces_supported(codebase_metadata.codebase_programming_language):
            try:
                candidate_payloads = await workflow.execute_activity(
                    AppInterfacesActivity.fetch_low_confidence_call_expression_candidates,
                    args=[
                        codebase_metadata.codebase_path,
                        codebase_metadata.codebase_programming_language,
                    ],
                    start_to_close_timeout=timedelta(minutes=2),
                    retry_policy=DB_ACTIVITY_RETRY_POLICY,
                )

                await _run_call_expression_validation(
                    temporal_agents=temporal_agents,
                    codebase_metadata=codebase_metadata,
                    repository_qualified_name=repository_qualified_name,
                    repository_workflow_run_id=repository_workflow_run_id,
                    candidate_payloads=candidate_payloads,
                    agent_stats=agent_stats,
                    agent_errors=agent_errors,
                )

                logger.info(
                    "[workflow] Running app_interfaces_agent for {}",
                    codebase_metadata.codebase_name,
                )
                app_interfaces_result = await workflow.execute_activity(
                    AppInterfacesActivity.build_app_interfaces,
                    args=[
                        codebase_metadata.codebase_path,
                        codebase_metadata.codebase_programming_language,
                    ],
                    start_to_close_timeout=timedelta(minutes=2),
                    retry_policy=DB_ACTIVITY_RETRY_POLICY,
                )
                results["app_interfaces"] = app_interfaces_result.model_dump()

                # Emit completion event for progress tracking
                await workflow.execute_activity(
                    AppInterfacesActivity.emit_app_interfaces_completion,
                    args=[
                        repository_qualified_name,
                        repository_workflow_run_id,
                        codebase_metadata.codebase_name,
                        codebase_metadata.codebase_programming_language,
                    ],
                    start_to_close_timeout=timedelta(seconds=30),
                    retry_policy=DB_ACTIVITY_RETRY_POLICY,
                )

                logger.info(
                    "[workflow] app_interfaces_agent completed for {}",
                    codebase_metadata.codebase_name,
                )

                # Run section-scoped updater for app interfaces
                await _run_section_updater(
                    temporal_agents=temporal_agents,
                    section_id=SectionId.APP_INTERFACES,
                    codebase_metadata=codebase_metadata,
                    repository_qualified_name=repository_qualified_name,
                    repository_workflow_run_id=repository_workflow_run_id,
                    programming_language_metadata=results[
                        "programming_language_metadata"
                    ],
                    section_data=results["app_interfaces"],
                    agent_stats=agent_stats,
                    agent_errors=agent_errors,
                    updater_runs=results["agents_md_updater_runs"],
                )
            except Exception as e:
                _raise_if_temporal_cancellation(e)
                logger.error(
                    "[workflow] app_interfaces_agent failed for {}: {}",
                    codebase_metadata.codebase_name,
                    e,
                )
                logger.exception("[workflow] Full traceback:")
                # Collect error for aggregation - do NOT store in results
                app_interfaces_error: dict[str, object] = {
                    "agent": "app_interfaces_agent",
                    "codebase": codebase_metadata.codebase_name,
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                }
                app_interfaces_error = _enrich_agent_error_with_model_details(
                    app_interfaces_error,
                    e,
                    "app_interfaces_agent",
                    codebase_metadata.codebase_name,
                )
                agent_errors.append(app_interfaces_error)
        else:
            logger.info(
                "[workflow] app_interfaces_agent skipped (language: {})",
                codebase_metadata.codebase_programming_language,
            )

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
        child_handles: list[
            tuple[str, ChildWorkflowHandle[CodebaseAgentWorkflow, dict[str, Any]]]
        ] = []

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
                _raise_if_temporal_cancellation(result)
                logger.error(
                    "[workflow] CodebaseAgentWorkflow failed for {}/{}: {}",
                    repository_qualified_name,
                    codebase_name,
                    result,
                )
                # Collect error for aggregation - do NOT store in results
                child_errors.append(
                    {
                        "codebase": codebase_name,
                        "error": str(result),
                    }
                )
                codebase_statistics_map[codebase_name] = create_zero_usage_statistics()
            else:
                logger.debug(
                    "[workflow] Child workflow completed for {}", codebase_name
                )
                results["codebases"][codebase_name] = result

                # Extract per-codebase statistics from child workflow result
                if "statistics" in result and result["statistics"]:
                    codebase_stats = UsageStatistics.model_validate(
                        result["statistics"]
                    )
                    codebase_statistics_map[codebase_name] = codebase_stats
                else:
                    codebase_statistics_map[codebase_name] = (
                        create_zero_usage_statistics()
                    )

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

        return results
