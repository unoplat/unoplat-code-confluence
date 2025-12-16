"""Temporal activity retry policy configuration for TemporalAgent activities.

This module provides configurable retry policies for model, toolset, and tool activities
executed by TemporalAgent, ensuring all activities have bounded retries.

Why bounded retries matter:
- Temporal's default activity retry policy allows unlimited attempts (maximum_attempts=0)
- PydanticAI TemporalAgent wraps agent operations in Temporal activities
- Without explicit bounds, failed activities retry forever, consuming resources

Two-layer retry model:
1. Temporal activity retries (this module) - handles infrastructure failures
2. PydanticAI retries (Agent.retries, Tool.max_retries) - handles agent logic errors

By setting PydanticAI retries to 0 and using bounded Temporal retries, we avoid
multiplicative retry behavior (Temporal attempts × PydanticAI retries).

Activity types:
- Model activities: LLM provider requests (higher tolerance for rate limits)
- Toolset activities: get-tools/list-tools operations (moderate tolerance)
- Tool activities: individual tool call execution (conservative)
"""

from datetime import timedelta

from temporalio.common import RetryPolicy

from unoplat_code_confluence_query_engine.config.settings import EnvironmentSettings


class TemporalAgentRetryConfig:
    """Collection of Temporal retry policies for TemporalAgent activities.

    Provides factory methods to create RetryPolicy objects from environment settings,
    ensuring all policies have finite maximum_attempts.

    Usage:
        settings = EnvironmentSettings()
        retry_config = TemporalAgentRetryConfig(settings)

        # Use in TemporalAgent construction
        TemporalAgent(
            agent,
            activity_config=ActivityConfig(retry_policy=retry_config.base_retry_policy),
            model_activity_config=ActivityConfig(retry_policy=retry_config.model_retry_policy),
            toolset_activity_config={"<agent>": ActivityConfig(retry_policy=retry_config.toolset_retry_policy)},
        )
    """

    def __init__(self, settings: EnvironmentSettings) -> None:
        """Initialize retry config from environment settings.

        Args:
            settings: Environment settings with retry configuration
        """
        self._settings = settings

        # Pre-build policies for reuse (immutable once created)
        self._model_retry_policy = self._build_model_retry_policy()
        self._toolset_retry_policy = self._build_toolset_retry_policy()
        self._tool_retry_policy = self._build_tool_retry_policy()

    def _build_model_retry_policy(self) -> RetryPolicy:
        """Build retry policy for model request activities.

        Model activities (LLM calls) are more tolerant of transient failures:
        - Rate limiting (429 errors)
        - Provider outages
        - Network timeouts

        Returns:
            RetryPolicy with bounded maximum_attempts for model activities
        """
        return RetryPolicy(
            maximum_attempts=self._settings.temporal_model_activity_max_attempts,
            initial_interval=timedelta(
                seconds=self._settings.temporal_model_activity_initial_interval_s
            ),
            backoff_coefficient=self._settings.temporal_model_activity_backoff_coefficient,
            maximum_interval=timedelta(
                seconds=self._settings.temporal_model_activity_max_interval_s
            ),
        )

    def _build_toolset_retry_policy(self) -> RetryPolicy:
        """Build retry policy for toolset activities.

        Toolset activities (get-tools, list-tools) are moderately tolerant:
        - MCP server connectivity issues
        - Tool discovery failures

        Returns:
            RetryPolicy with bounded maximum_attempts for toolset activities
        """
        return RetryPolicy(
            maximum_attempts=self._settings.temporal_toolset_activity_max_attempts,
            initial_interval=timedelta(
                seconds=self._settings.temporal_toolset_activity_initial_interval_s
            ),
            backoff_coefficient=self._settings.temporal_toolset_activity_backoff_coefficient,
            maximum_interval=timedelta(
                seconds=self._settings.temporal_toolset_activity_max_interval_s
            ),
        )

    def _build_tool_retry_policy(self) -> RetryPolicy:
        """Build retry policy for individual tool call activities.

        Tool activities are more conservative:
        - May interact with local state/DB
        - Fewer retries to prevent amplification of side effects

        Returns:
            RetryPolicy with bounded maximum_attempts for tool activities
        """
        return RetryPolicy(
            maximum_attempts=self._settings.temporal_tool_activity_max_attempts,
            initial_interval=timedelta(
                seconds=self._settings.temporal_tool_activity_initial_interval_s
            ),
            backoff_coefficient=self._settings.temporal_tool_activity_backoff_coefficient,
            maximum_interval=timedelta(
                seconds=self._settings.temporal_tool_activity_max_interval_s
            ),
        )

    @property
    def model_retry_policy(self) -> RetryPolicy:
        """Get retry policy for model request activities.

        Returns:
            RetryPolicy configured for LLM provider requests
        """
        return self._model_retry_policy

    @property
    def toolset_retry_policy(self) -> RetryPolicy:
        """Get retry policy for toolset activities (get-tools/list-tools).

        Returns:
            RetryPolicy configured for toolset operations
        """
        return self._toolset_retry_policy

    @property
    def tool_retry_policy(self) -> RetryPolicy:
        """Get retry policy for individual tool call activities.

        Returns:
            RetryPolicy configured for tool execution
        """
        return self._tool_retry_policy

    @property
    def base_retry_policy(self) -> RetryPolicy:
        """Get base/fallback retry policy for uncategorized activities.

        Uses the toolset policy as the base fallback (moderate tolerance).

        Returns:
            RetryPolicy for base ActivityConfig
        """
        return self._toolset_retry_policy
