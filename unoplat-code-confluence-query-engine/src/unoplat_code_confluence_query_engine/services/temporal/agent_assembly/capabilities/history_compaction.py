"""Temporal-safe message history compaction helpers for PydanticAI agents."""

from __future__ import annotations

from dataclasses import replace

from pydantic_ai.messages import (
    ModelMessage,
    ModelRequest,
    ModelResponse,
    ThinkingPart,
)


def compact_temporal_agent_history(messages: list[ModelMessage]) -> list[ModelMessage]:
    """Remove redundant historical bloat before durable model requests.

    PydanticAI's Temporal durable execution schedules each model request as an
    activity whose input contains the current message history. Large static
    instructions and old reasoning traces otherwise get re-sent in every later
    activity input, creating O(n²) Temporal history growth.

    This processor is intentionally pure and deterministic because it runs in
    Temporal workflow context via PydanticAI's HistoryProcessor capability.
    """
    latest_request_index = _latest_message_index(messages, ModelRequest)
    latest_response_index = _latest_message_index(messages, ModelResponse)

    compacted: list[ModelMessage] = []
    for index, message in enumerate(messages):
        if isinstance(message, ModelRequest) and index != latest_request_index:
            compacted.append(replace(message, instructions=None))
            continue

        if isinstance(message, ModelResponse) and index != latest_response_index:
            parts = tuple(
                part for part in message.parts if not isinstance(part, ThinkingPart)
            )
            if parts:
                compacted.append(replace(message, parts=parts))
            continue

        compacted.append(message)

    return compacted


def _latest_message_index(
    messages: list[ModelMessage],
    message_type: type[ModelRequest] | type[ModelResponse],
) -> int | None:
    return next(
        (
            index
            for index in range(len(messages) - 1, -1, -1)
            if isinstance(messages[index], message_type)
        ),
        None,
    )
