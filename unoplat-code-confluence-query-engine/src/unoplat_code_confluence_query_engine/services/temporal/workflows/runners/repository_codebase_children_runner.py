from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any

from temporalio import workflow
from temporalio.workflow import ChildWorkflowHandle, ParentClosePolicy

if TYPE_CHECKING:
    from unoplat_code_confluence_query_engine.services.temporal.workflows.codebase_agent_workflow import (
        CodebaseAgentWorkflow,
    )

with workflow.unsafe.imports_passed_through():
    import asyncio

    from loguru import logger

    from unoplat_code_confluence_query_engine.models.output.git_ref_info import (
        GitRefInfo,
    )
    from unoplat_code_confluence_query_engine.models.statistics.agent_usage_statistics import (
        UsageStatistics,
    )
    from unoplat_code_confluence_query_engine.services.temporal.statistics_helpers import (
        create_zero_usage_statistics,
    )
    from unoplat_code_confluence_query_engine.services.temporal.utils import (
        raise_if_temporal_cancellation,
    )
    from unoplat_code_confluence_query_engine.services.temporal.workflow_envelopes import (
        ArchitectureEvidenceSummary,
        CodebaseAgentWorkflowResult,
    )


async def start_codebase_child_workflows(
    codebase_workflow_run: Callable[..., Awaitable[CodebaseAgentWorkflowResult]],
    repository_qualified_name: str,
    codebase_metadata_list: list[dict[str, Any]],
    repository_workflow_run_id: str,
    trace_id: str,
    git_ref_info: GitRefInfo | None,
) -> list[
    tuple[
        str,
        ChildWorkflowHandle["CodebaseAgentWorkflow", CodebaseAgentWorkflowResult],
    ]
]:
    """Start all codebase child workflows and return their typed handles."""
    child_handles: list[
        tuple[
            str,
            ChildWorkflowHandle[
                "CodebaseAgentWorkflow", CodebaseAgentWorkflowResult
            ],
        ]
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
            codebase_workflow_run,
            args=[
                repository_qualified_name,
                codebase_dict,
                repository_workflow_run_id,
                trace_id,
                git_ref_info,
            ],
            id=f"{repository_qualified_name.replace('/', '-')}-{codebase_name}",
            parent_close_policy=ParentClosePolicy.TERMINATE,
        )
        child_handles.append((codebase_name, child_handle))

    logger.info(
        "[workflow] Started {} child workflows, waiting for parallel completion",
        len(child_handles),
    )
    return child_handles


async def collect_codebase_child_results(
    repository_qualified_name: str,
    child_handles: list[
        tuple[
            str,
            ChildWorkflowHandle[
                "CodebaseAgentWorkflow", CodebaseAgentWorkflowResult
            ],
        ]
    ],
    codebase_statistics_map: dict[str, UsageStatistics],
) -> tuple[list[dict[str, str]], list[ArchitectureEvidenceSummary]]:
    """Collect child results, including only successful current Architecture evidence."""
    results_list: list[CodebaseAgentWorkflowResult | BaseException] = (
        await asyncio.gather(
            *[handle for _, handle in child_handles],
            return_exceptions=True,
        )
    )

    child_errors: list[dict[str, str]] = []
    successful_evidence: list[ArchitectureEvidenceSummary] = []

    for (codebase_name, _), result in zip(child_handles, results_list):
        if isinstance(result, BaseException):
            raise_if_temporal_cancellation(result)
            logger.error(
                "[workflow] CodebaseAgentWorkflow failed for {}/{}: {}",
                repository_qualified_name,
                codebase_name,
                result,
            )
            child_errors.append(
                {
                    "codebase": codebase_name,
                    "error": str(result),
                }
            )
            codebase_statistics_map[codebase_name] = create_zero_usage_statistics()
        else:
            logger.debug("[workflow] Child workflow completed for {}", codebase_name)
            codebase_statistics_map[codebase_name] = result.statistics
            successful_evidence.append(result.architecture_evidence)

    logger.info(
        "[workflow] RepositoryAgentWorkflow processed {} codebases for {}",
        len(child_handles),
        repository_qualified_name,
    )
    return child_errors, successful_evidence
