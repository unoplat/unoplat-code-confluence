"""Registry for post-processors."""

from __future__ import annotations

from typing import Dict, Optional

from unoplat_code_confluence_query_engine.services.post_processors.post_processor_base import (
    PostProcessorProtocol,
)


class PostProcessingRegistry:
    """Registry for managing post-processors by agent name."""

    def __init__(self) -> None:
        self._processors: Dict[str, PostProcessorProtocol] = {}

    def register(self, agent_name: str, processor: PostProcessorProtocol) -> None:
        """Register a post-processor for a specific agent."""
        self._processors[agent_name] = processor

    def get(self, agent_name: str) -> Optional[PostProcessorProtocol]:
        """Get a post-processor for a specific agent."""
        return self._processors.get(agent_name)