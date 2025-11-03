"""Statistics models for tracking agent execution usage and costs."""

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class UsageStatistics(BaseModel):
    """Statistics for tracking LLM usage and costs.

    Used for per-codebase aggregation.
    """

    requests: int = Field(
        default=0,
        description="Number of requests made to the LLM API",
    )
    tool_calls: int = Field(
        default=0,
        description="Number of successful tool calls executed",
    )
    input_tokens: int = Field(
        default=0,
        description="Total number of input/prompt tokens",
    )
    output_tokens: int = Field(
        default=0,
        description="Total number of output/completion tokens",
    )
    cache_write_tokens: int = Field(
        default=0,
        description="Total number of tokens written to cache",
    )
    cache_read_tokens: int = Field(
        default=0,
        description="Total number of tokens read from cache",
    )
    total_tokens: int = Field(
        default=0,
        description="Total tokens (input + output)",
    )
    estimated_cost_usd: Optional[float] = Field(
        default=None,
        description="Estimated cost in USD (requires gen-ai-prices integration)",
    )


class UsageSummary(BaseModel):
    """Temporary aggregation helper for combining usage and cost.

    Used during agent execution to track both usage metrics and cost
    before final aggregation into WorkflowStatistics.
    """

    usage: Dict[str, Any] = Field(
        default_factory=dict,
        description="RunUsage fields as dict (requests, tool_calls, tokens, etc., including nested 'details')",
    )
    cost_usd: Optional[float] = Field(
        default=None,
        description="Estimated cost in USD for this execution",
    )


class WorkflowStatistics(BaseModel):
    """Complete workflow statistics aggregated across all codebases."""

    total_requests: int = Field(
        default=0,
        description="Total number of requests across all codebases",
    )
    total_tool_calls: int = Field(
        default=0,
        description="Total number of tool calls across all codebases",
    )
    total_input_tokens: int = Field(
        default=0,
        description="Total input tokens across all codebases",
    )
    total_output_tokens: int = Field(
        default=0,
        description="Total output tokens across all codebases",
    )
    total_cache_write_tokens: int = Field(
        default=0,
        description="Total cache write tokens",
    )
    total_cache_read_tokens: int = Field(
        default=0,
        description="Total cache read tokens",
    )
    total_tokens: int = Field(
        default=0,
        description="Total tokens (input + output) across all processing",
    )
    total_estimated_cost_usd: Optional[float] = Field(
        default=None,
        description="Total estimated cost in USD for the entire workflow",
    )
    by_codebase: Dict[str, UsageStatistics] = Field(
        default_factory=dict,
        description="Statistics broken down by codebase name",
    )
