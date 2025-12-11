"""Pure helper functions for statistics extraction and aggregation.

This module contains stateless, side-effect-free functions that are safe
to import in Temporal workflows via workflow.unsafe.imports_passed_through().

These functions were extracted from the old AgentExecutionService
(removed in PR #1044) which had _build_workflow_statistics() inline.
"""

from pydantic_ai.usage import RunUsage

from unoplat_code_confluence_query_engine.models.statistics.agent_usage_statistics import (
    UsageStatistics,
    WorkflowStatistics,
)


def extract_usage_statistics(run_usage: RunUsage) -> UsageStatistics:
    """Extract UsageStatistics from pydantic-ai RunUsage object.

    Args:
        run_usage: The RunUsage object from AgentRunResult.usage()

    Returns:
        UsageStatistics with all token counts and metrics extracted
    """
    return UsageStatistics(
        requests=run_usage.requests,
        tool_calls=run_usage.tool_calls,
        input_tokens=run_usage.input_tokens,
        output_tokens=run_usage.output_tokens,
        cache_write_tokens=run_usage.cache_write_tokens,
        cache_read_tokens=run_usage.cache_read_tokens,
        total_tokens=run_usage.total_tokens,
        estimated_cost_usd=None,  # Future: integrate with genai-prices
    )


def create_zero_usage_statistics() -> UsageStatistics:
    """Create UsageStatistics with all zeros.

    Used for failed or disabled agents to maintain consistent
    statistics structure without affecting aggregated totals.

    Returns:
        UsageStatistics with all fields set to zero/None
    """
    return UsageStatistics()


def aggregate_usage_statistics(stats_list: list[UsageStatistics]) -> UsageStatistics:
    """Sum all numeric fields across a list of UsageStatistics.

    Args:
        stats_list: List of UsageStatistics to aggregate

    Returns:
        Single UsageStatistics with summed values
    """
    if not stats_list:
        return create_zero_usage_statistics()

    # Collect non-None cost values for aggregation
    cost_values = [s.estimated_cost_usd for s in stats_list if s.estimated_cost_usd is not None]
    aggregated_cost = sum(cost_values) if cost_values else None

    return UsageStatistics(
        requests=sum(s.requests for s in stats_list),
        tool_calls=sum(s.tool_calls for s in stats_list),
        input_tokens=sum(s.input_tokens for s in stats_list),
        output_tokens=sum(s.output_tokens for s in stats_list),
        cache_write_tokens=sum(s.cache_write_tokens for s in stats_list),
        cache_read_tokens=sum(s.cache_read_tokens for s in stats_list),
        total_tokens=sum(s.total_tokens for s in stats_list),
        estimated_cost_usd=aggregated_cost,
    )


def build_workflow_statistics(
    by_codebase: dict[str, UsageStatistics],
) -> WorkflowStatistics:
    """Build WorkflowStatistics from per-codebase statistics.

    Args:
        by_codebase: Dictionary mapping codebase names to their UsageStatistics

    Returns:
        WorkflowStatistics with totals across all codebases and per-codebase breakdown
    """
    aggregated = aggregate_usage_statistics(list(by_codebase.values()))

    return WorkflowStatistics(
        total_requests=aggregated.requests,
        total_tool_calls=aggregated.tool_calls,
        total_input_tokens=aggregated.input_tokens,
        total_output_tokens=aggregated.output_tokens,
        total_cache_write_tokens=aggregated.cache_write_tokens,
        total_cache_read_tokens=aggregated.cache_read_tokens,
        total_tokens=aggregated.total_tokens,
        total_estimated_cost_usd=aggregated.estimated_cost_usd,
        by_codebase=by_codebase,
    )
