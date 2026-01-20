"""Business logic post-processing activity for Temporal workflows."""

from __future__ import annotations

from typing import Any

from loguru import logger
from temporalio import activity

from unoplat_code_confluence_query_engine.services.post_processors.business_logic_domain_post_processor import (
    BusinessLogicDomainPostProcessor,
)
from unoplat_code_confluence_query_engine.services.post_processors.post_processor_base import (
    ProcessorDependencies,
)


class BusinessLogicPostProcessActivity:
    """Activity for post-processing business logic agent output."""

    @activity.defn
    async def post_process_business_logic(
        self,
        agent_output: str,
        codebase_path: str,
        programming_language: str,
    ) -> dict[str, Any]:
        """Enrich business logic description with data model files from PostgreSQL.

        Args:
            agent_output: Plain text description from business_logic_domain_agent
            codebase_path: Path to the codebase for Postgres lookup
            programming_language: Programming language of the codebase

        Returns:
            BusinessLogicDomain as dict with description and data_models
        """
        logger.info(
            "[business_logic_post_process] Starting post-processing for codebase: {}",
            codebase_path,
        )

        processor = BusinessLogicDomainPostProcessor()
        deps = ProcessorDependencies(
            codebase_path=codebase_path,
            programming_language=programming_language,
        )

        result = await processor.process(agent_output=agent_output, deps=deps)

        logger.info(
            "[business_logic_post_process] Post-processing complete: {} data models found",
            len(result.data_models),
        )

        return result.model_dump()
