"""Streaming-compatible conversation summarization capability."""

from __future__ import annotations

from collections.abc import AsyncIterable
from dataclasses import dataclass, field, fields
from typing import TypeVar, override

from pydantic_ai import Agent, AgentStreamEvent, RunContext
from pydantic_ai.messages import ModelMessage
from pydantic_ai_harness.compaction import SummarizingCompaction
from pydantic_ai_harness.compaction._summarizing_compaction import _format_messages

AgentDepsT = TypeVar("AgentDepsT")

_SUMMARY_INSTRUCTIONS = (
    "You are a context summarization assistant. Extract the most important "
    "information from conversations."
)
_UPSTREAM_SUPPORTS_STREAM = any(
    dataclass_field.name == "stream"
    for dataclass_field in fields(SummarizingCompaction)
)


async def drain_summary_events(
    _ctx: RunContext[object],
    events: AsyncIterable[AgentStreamEvent],
) -> None:
    """Consume nested summary events without forwarding their token deltas."""
    async for _ in events:
        pass


@dataclass
class StreamingSummarizingCompaction(SummarizingCompaction[AgentDepsT]):
    """Use streaming requests for LLM-powered conversation summaries.

    This is a compatibility subclass for pydantic-ai-harness PR #620. With a
    harness version that already provides its ``stream`` field, the subclass
    delegates directly to the upstream implementation. Older versions use the
    local fallback below while retaining the parent capability's compaction
    behavior.
    """

    stream: bool = field(default=True, kw_only=True)
    """Whether to stream and internally drain the nested summary request."""

    @override
    async def _summarize(
        self,
        messages: list[ModelMessage],
        ctx: RunContext[AgentDepsT],
        *,
        previous_summary: str | None = None,
    ) -> str:
        """Generate a summary through the upstream or compatibility path."""
        if _UPSTREAM_SUPPORTS_STREAM:
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
            event_stream_handler=drain_summary_events if self.stream else None,
        )
        return result.output.strip()
