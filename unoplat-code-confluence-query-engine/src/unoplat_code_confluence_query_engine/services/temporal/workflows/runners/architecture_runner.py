from __future__ import annotations

from datetime import timedelta
import traceback

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from loguru import logger

    from unoplat_code_confluence_query_engine.models.runtime.architecture_agent_dependencies import (
        ArchitectureAgentDependencies,
        build_architecture_run_metadata,
    )
    from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.agents.user_prompts.build_user_prompt_architecture import (
        build_architecture_prompt,
    )
    from unoplat_code_confluence_query_engine.services.temporal.agent_backend_paths import (
        resolve_common_repository_root,
    )
    from unoplat_code_confluence_query_engine.services.temporal.interceptors.agent_workflow import (
        DB_ACTIVITY_RETRY_POLICY,
    )
    from unoplat_code_confluence_query_engine.services.temporal.interceptors.agent_workflow.activity.repository_agent_snapshot_activity import (
        RepositoryAgentSnapshotActivity,
    )
    from unoplat_code_confluence_query_engine.services.temporal.temporal_agents import (
        TemporalAgentRegistry,
        get_cached_usage_limits,
    )
    from unoplat_code_confluence_query_engine.services.temporal.utils import (
        enrich_agent_error_with_model_details,
        raise_if_temporal_cancellation,
    )
    from unoplat_code_confluence_query_engine.services.temporal.workflow_envelopes import (
        ARCHITECTURE_REPOSITORY_ACTIVITY,
        ArchitectureEvidenceSummary,
        RepositoryActivityCompletionEnvelope,
    )


async def run_architecture_agent(
    *,
    temporal_agents: TemporalAgentRegistry,
    repository_qualified_name: str,
    repository_workflow_run_id: str,
    successful_evidence: list[ArchitectureEvidenceSummary],
) -> dict[str, object] | None:
    """Run one repository Architecture agent from successful current evidence."""
    metadata = [entry.codebase_metadata for entry in successful_evidence]
    fresh_evidence = [
        entry for entry in successful_evidence if entry.app_interfaces_generated
    ]
    if not any(entry.has_external_boundary for entry in fresh_evidence):
        await _complete_architecture_activity(
            repository_qualified_name, repository_workflow_run_id
        )
        logger.info(
            "[workflow] Architecture skipped: no fresh external-boundary evidence"
        )
        return None

    architecture_agent = temporal_agents.architecture
    if architecture_agent is None:
        await _complete_architecture_activity(
            repository_qualified_name, repository_workflow_run_id
        )
        logger.info("[workflow] Architecture skipped: agent disabled")
        return None

    try:
        repository_root = resolve_common_repository_root(metadata)
    except Exception as error:
        return {
            "agent": ARCHITECTURE_REPOSITORY_ACTIVITY,
            "error": str(error),
            "traceback": traceback.format_exc(),
        }

    deps = ArchitectureAgentDependencies(
        repository_qualified_name=repository_qualified_name,
        repository_root=repository_root,
        repository_workflow_run_id=repository_workflow_run_id,
    )
    try:
        fresh_paths = [
            f"{entry.codebase_metadata.codebase_name}/app_interfaces.md"
            if entry.codebase_metadata.codebase_name not in {"", "."}
            else "app_interfaces.md"
            for entry in fresh_evidence
        ]
        await architecture_agent.run(
            build_architecture_prompt(
                repository_root,
                [item.codebase_name for item in metadata],
                fresh_paths,
            ),
            deps=deps,
            usage_limits=get_cached_usage_limits(),
            metadata=build_architecture_run_metadata(deps),
        )
        await _complete_architecture_activity(
            repository_qualified_name, repository_workflow_run_id
        )
        logger.info(
            "[workflow] Architecture completed for {}", repository_qualified_name
        )
        return None
    except Exception as error:
        raise_if_temporal_cancellation(error)
        details: dict[str, object] = {
            "agent": "architecture",
            "error": str(error),
            "traceback": traceback.format_exc(),
        }
        return enrich_agent_error_with_model_details(
            details, error, "architecture", repository_qualified_name
        )
    finally:
        deps.release_backend()


async def _complete_architecture_activity(
    repository_qualified_name: str, repository_workflow_run_id: str
) -> None:
    owner_name, repo_name = repository_qualified_name.split("/", 1)
    await workflow.execute_activity(
        RepositoryAgentSnapshotActivity.complete_repository_activity,
        args=[
            RepositoryActivityCompletionEnvelope(
                owner_name=owner_name,
                repo_name=repo_name,
                repository_workflow_run_id=repository_workflow_run_id,
                activity_name=ARCHITECTURE_REPOSITORY_ACTIVITY,
            )
        ],
        start_to_close_timeout=timedelta(seconds=30),
        retry_policy=DB_ACTIVITY_RETRY_POLICY,
    )
