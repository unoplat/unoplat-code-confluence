from __future__ import annotations

import traceback

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from loguru import logger

    from unoplat_code_confluence_query_engine.models.repository.framework_feature_validation_models import (
        FrameworkFeatureValidationCandidate,
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
    from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.agents.user_prompts.build_user_prompt_call_expression_validator import (
        build_call_expression_validator_prompt,
    )
    from unoplat_code_confluence_query_engine.services.temporal.statistics_helpers import (
        create_zero_usage_statistics,
        extract_usage_statistics,
    )
    from unoplat_code_confluence_query_engine.services.temporal.temporal_agents import (
        TemporalAgentRegistry,
        get_cached_usage_limits,
    )
    from unoplat_code_confluence_query_engine.services.temporal.utils import (
        enrich_agent_error_with_model_details,
        raise_if_temporal_cancellation,
    )


async def run_call_expression_validation(
    temporal_agents: TemporalAgentRegistry,
    codebase_metadata: CodebaseMetadata,
    repository_qualified_name: str,
    repository_workflow_run_id: str,
    candidate_payloads: list[dict[str, object]],
    agent_stats: list[UsageStatistics],
    agent_errors: list[dict[str, object]],
) -> None:
    """Execute call_expression_validator for low-confidence candidates."""
    if not candidate_payloads:
        logger.info(
            "[workflow] No low-confidence CallExpression candidates found for {}",
            codebase_metadata.codebase_name,
        )
        return

    validator_agent = temporal_agents.call_expression_validator
    if validator_agent is None:
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
        validator_prompt = build_call_expression_validator_prompt(candidate)

        try:
            validator_result = await validator_agent.run(
                validator_prompt,
                deps=validator_deps,
                usage_limits=get_cached_usage_limits(),
            )
            agent_stats.append(extract_usage_statistics(validator_result.usage()))
        except Exception as validator_error:
            raise_if_temporal_cancellation(validator_error)
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
            validator_error_entry = enrich_agent_error_with_model_details(
                validator_error_entry,
                validator_error,
                "call_expression_validator",
                codebase_metadata.codebase_name,
            )
            agent_errors.append(validator_error_entry)
            agent_stats.append(create_zero_usage_statistics())
