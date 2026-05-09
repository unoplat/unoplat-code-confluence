from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta
from typing import Literal

from temporalio.workflow import ActivityConfig

from unoplat_code_confluence_query_engine.services.temporal.activity_retry_config import (
    TemporalAgentRetryConfig,
)


@dataclass(frozen=True, slots=True)
class TemporalActivityDefaults:
    """Default Temporal activity policies applied during assembly."""

    base: ActivityConfig
    model: ActivityConfig
    toolset: ActivityConfig
    tool: ActivityConfig


@dataclass(frozen=True, slots=True)
class ResolvedTemporalActivityConfig:
    """Resolved TemporalAgent configuration keyed by toolset ID and tool name.

    Per the official PydanticAI `TemporalAgent.__init__` API, the relevant
    parameters are:
    - `toolset_activity_config: dict[str, ActivityConfig] | None`
    - `tool_activity_config: dict[str, dict[str, ActivityConfig | Literal[False]]] | None`

    Reference:
    https://ai.pydantic.dev/api/durable_exec/#pydantic_ai.durable_exec.temporal.TemporalAgent.__init__
    """

    activity_config: ActivityConfig
    model_activity_config: ActivityConfig
    toolset_activity_config: dict[str, ActivityConfig] = field(default_factory=dict)
    tool_activity_config: dict[
        str,
        dict[str, ActivityConfig | Literal[False]],
    ] = field(default_factory=dict)


def create_temporal_activity_defaults(
    retry_config: TemporalAgentRetryConfig,
) -> TemporalActivityDefaults:
    """Create the package-default Temporal activity configuration bundle."""

    return TemporalActivityDefaults(
        base=ActivityConfig(
            start_to_close_timeout=timedelta(seconds=300),
            retry_policy=retry_config.base_retry_policy,
        ),
        model=ActivityConfig(
            start_to_close_timeout=timedelta(seconds=300),
            retry_policy=retry_config.model_retry_policy,
        ),
        toolset=ActivityConfig(
            start_to_close_timeout=timedelta(seconds=120),
            retry_policy=retry_config.toolset_retry_policy,
        ),
        tool=ActivityConfig(
            start_to_close_timeout=timedelta(seconds=120),
            retry_policy=retry_config.tool_retry_policy,
        ),
    )


def resolve_toolset_activity_config(
    *,
    toolset_ids: tuple[str, ...],
    defaults: TemporalActivityDefaults,
    toolset_overrides: dict[str, ActivityConfig],
) -> dict[str, ActivityConfig]:
    """Resolve per-toolset activity config keyed by Temporal toolset ID.

    Per the official `TemporalAgent.__init__` API:
    - `toolset_activity_config` is `dict[str, ActivityConfig] | None`
    - entries are keyed by toolset ID
    - those values are used for get-tools and call-tool activity handling for
      the matching toolset

    Reference:
    https://ai.pydantic.dev/api/durable_exec/#pydantic_ai.durable_exec.temporal.TemporalAgent.__init__
    """

    resolved_overrides: dict[str, ActivityConfig] = {}
    for toolset_id in toolset_ids:
        resolved_overrides[toolset_id] = toolset_overrides.get(
            toolset_id,
            defaults.toolset,
        )
    return resolved_overrides


def resolve_tool_activity_config(
    *,
    function_tool_names: tuple[str, ...],
    toolset_ids: tuple[str, ...],
    default_function_toolset_id: str,
    defaults: TemporalActivityDefaults,
    tool_overrides: dict[str, dict[str, ActivityConfig | Literal[False]]],
) -> dict[str, dict[str, ActivityConfig | Literal[False]]]:
    """Resolve per-tool activity config keyed by toolset ID and tool name.

    Per the official `TemporalAgent.__init__` API:
    - `tool_activity_config` is
      `dict[str, dict[str, ActivityConfig | Literal[False]]] | None`
    - the first key is the toolset ID and the nested key is the tool name
    - a nested value may be `False` to disable activity offloading for async
      non-IO tools

    Reference:
    https://ai.pydantic.dev/api/durable_exec/#pydantic_ai.durable_exec.temporal.TemporalAgent.__init__
    """

    resolved_overrides: dict[str, dict[str, ActivityConfig | Literal[False]]] = {
        toolset_id: dict(tool_overrides.get(toolset_id, {}))
        for toolset_id in toolset_ids
    }
    default_tool_overrides = resolved_overrides.setdefault(
        default_function_toolset_id, {}
    )
    for tool_name in function_tool_names:
        default_tool_overrides.setdefault(tool_name, defaults.tool)
    return resolved_overrides


def resolve_temporal_activity_config(
    *,
    function_tool_names: tuple[str, ...],
    toolset_ids: tuple[str, ...],
    default_function_toolset_id: str,
    defaults: TemporalActivityDefaults,
    toolset_overrides: dict[str, ActivityConfig],
    tool_overrides: dict[str, dict[str, ActivityConfig | Literal[False]]],
) -> ResolvedTemporalActivityConfig:
    """Resolve the TemporalAgent activity config bundle for one assembled agent.

    This function prepares values for the official `TemporalAgent.__init__`
    parameters `activity_config`, `model_activity_config`,
    `toolset_activity_config`, and `tool_activity_config`.

    Reference:
    https://ai.pydantic.dev/api/durable_exec/#pydantic_ai.durable_exec.temporal.TemporalAgent.__init__
    """

    return ResolvedTemporalActivityConfig(
        activity_config=defaults.base,
        model_activity_config=defaults.model,
        toolset_activity_config=resolve_toolset_activity_config(
            toolset_ids=toolset_ids,
            defaults=defaults,
            toolset_overrides=toolset_overrides,
        ),
        tool_activity_config=resolve_tool_activity_config(
            function_tool_names=function_tool_names,
            toolset_ids=toolset_ids,
            default_function_toolset_id=default_function_toolset_id,
            defaults=defaults,
            tool_overrides=tool_overrides,
        ),
    )
