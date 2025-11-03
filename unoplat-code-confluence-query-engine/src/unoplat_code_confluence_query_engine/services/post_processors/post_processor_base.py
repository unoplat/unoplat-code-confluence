"""Base protocol and dependencies for post-processors."""

from __future__ import annotations

from typing import Any, Protocol, TypeVar


class ProcessorDependencies:
    """Simplified dependencies for post-processors."""

    def __init__(
        self,
        *,
        codebase_path: str,
        neo4j_conn_manager: Any,
        programming_language: str,
    ) -> None:
        self.codebase_path = codebase_path
        self.neo4j_conn_manager = neo4j_conn_manager
        self.programming_language = programming_language


T_in = TypeVar("T_in", contravariant=True)
T_out = TypeVar("T_out", covariant=True)


class PostProcessorProtocol(Protocol[T_in, T_out]):
    """Protocol for agent output post-processors."""

    async def process(
        self,
        *,
        agent_output: T_in,
        deps: ProcessorDependencies,
    ) -> T_out:
        """Transform agent's raw output into final result."""
