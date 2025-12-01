"""Post-processing orchestrator service."""

from __future__ import annotations

from typing import Any, Dict, Optional, Union

from pydantic import BaseModel

from unoplat_code_confluence_query_engine.models.repository.repository_ruleset_metadata import (
    CodebaseMetadata,
)
from unoplat_code_confluence_query_engine.models.runtime.agent_dependencies import (
    AgentDependencies,
)
from unoplat_code_confluence_query_engine.services.post_processors.business_logic_domain_post_processor import (
    BusinessLogicDomainPostProcessor,
)
from unoplat_code_confluence_query_engine.services.post_processors.post_processor_base import (
    ProcessorDependencies,
)
from unoplat_code_confluence_query_engine.services.post_processors.registry import (
    PostProcessingRegistry,
)


class PostProcessingService:
    def __init__(self, registry: Optional[PostProcessingRegistry] = None) -> None:
        self.registry = registry or PostProcessingRegistry()
        # Register built-in processors
        # self.registry.register("framework_explorer", FrameworkExplorerPostProcessor())
        self.registry.register(
            "business_logic_domain", BusinessLogicDomainPostProcessor()
        )

    async def run(
        self,
        *,
        agent_name: str,
        agent_output: Union[BaseModel, list[BaseModel], str],
        repository: str,
        codebase: CodebaseMetadata,
        deps: AgentDependencies,
        options: Optional[Dict[str, Any]] = None,
    ) -> Union[BaseModel, list[BaseModel], str]:
        processor = self.registry.get(agent_name)
        if not processor:
            return agent_output

        # Adapt old interface to new simplified processor interface
        processor_deps = ProcessorDependencies(
            codebase_path=codebase.codebase_path,
            neo4j_conn_manager=deps.neo4j_conn_manager,
            programming_language=codebase.codebase_programming_language,
        )
        return await processor.process(
            agent_output=agent_output,
            deps=processor_deps,
        )
