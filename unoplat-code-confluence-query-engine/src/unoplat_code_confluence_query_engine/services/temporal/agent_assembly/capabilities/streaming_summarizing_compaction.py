"""Streaming-compatible conversation summarization capability."""

from __future__ import annotations

from collections.abc import AsyncIterable
from dataclasses import dataclass, field, fields, replace
from typing import TypeVar, override

from pydantic_ai import Agent, AgentStreamEvent, RunContext
from pydantic_ai.agent import EventStreamHandler
from pydantic_ai.messages import ModelMessage
from pydantic_ai.usage import UsageLimits
from pydantic_ai_harness.compaction import SummarizingCompaction
from pydantic_ai_harness.compaction._summarizing_compaction import _format_messages

AgentDepsT = TypeVar("AgentDepsT")

_SUMMARY_INSTRUCTIONS = (
    "You are a context summarization assistant. Extract the most important "
    "information from conversations."
)
_UPSTREAM_SUPPORTS_EVENT_STREAM_HANDLER = any(
    dataclass_field.name == "event_stream_handler"
    for dataclass_field in fields(SummarizingCompaction)
)


async def drain_summary_events(
    _ctx: RunContext[object],
    events: AsyncIterable[AgentStreamEvent],
) -> None:
    """Consume nested summary events without forwarding their token deltas."""
    async for _ in events:
        pass


def reserved_usage_limits(limits: UsageLimits | None) -> UsageLimits | None:
    """Reserve the pending parent request before a nested model call made from a hook.

    The hook may run after the parent request's limit check. Reducing a finite
    request limit prevents the nested call from spending the request that was
    already approved for the parent.
    """
    if limits is None or limits.request_limit is None:
        return limits
    return replace(limits, request_limit=max(0, limits.request_limit - 1))


@dataclass
class StreamingSummarizingCompaction(SummarizingCompaction[AgentDepsT]):
    """Backport streaming summary requests from pydantic-ai-harness PR #620.

    Once upstream exposes ``event_stream_handler``, this subclass delegates to
    its implementation. Older versions use the local fallback while retaining
    the parent capability's compaction behavior.
    """

    event_stream_handler: EventStreamHandler[object] | None = field(
        default=None,
        kw_only=True,
    )
    """Handler for the nested summary run; any handler selects streaming."""

    @override
    async def _summarize(
        self,
        messages: list[ModelMessage],
        ctx: RunContext[AgentDepsT],
        *,
        previous_summary: str | None = None,
    ) -> str:
        """Generate a summary through the upstream or compatibility path."""
        if _UPSTREAM_SUPPORTS_EVENT_STREAM_HANDLER:
            return await super()._summarize(
                messages,
                ctx,
                previous_summary=previous_summary,
            )

        formatted = _format_messages(messages)
        prompt = self.summary_prompt.format(messages=formatted)
        if previous_summary is not None:
            prompt = (
                f"{prompt}\n\n<previous_summary>\n"
                f"{previous_summary}\n</previous_summary>"
            )

        model = self.model if self.model is not None else ctx.model
        agent: Agent[None, str] = Agent(
            model,
            instructions=_SUMMARY_INSTRUCTIONS,
        )
        result = await agent.run(
            prompt,
            usage=ctx.usage,
            usage_limits=reserved_usage_limits(ctx.usage_limits),
            event_stream_handler=self.event_stream_handler,
        )
        return result.output.strip()
