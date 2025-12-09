"""Business Logic Domain post-processor implementation."""

from __future__ import annotations

from loguru import logger

from unoplat_code_confluence_query_engine.db.neo4j.business_logic_repository import (
    db_get_data_model_files,
)
from unoplat_code_confluence_query_engine.models.output.agent_md_output import (
    BusinessLogicDomain,
    CoreFile,
)
from unoplat_code_confluence_query_engine.services.post_processors.post_processor_base import (
    PostProcessorProtocol,
    ProcessorDependencies,
)


class BusinessLogicDomainPostProcessor(PostProcessorProtocol[str, BusinessLogicDomain]):
    """Post-processor for business logic domain agent output.

    The agent returns only a description string. This processor:
    1. Fetches all data model files from Neo4j
    2. Creates CoreFile entries for each file path
    3. Returns complete BusinessLogicDomain with description + data_models
    """

    async def process(
        self,
        *,
        agent_output: str,
        deps: ProcessorDependencies,
    ) -> BusinessLogicDomain:
        """Process business logic domain agent output by enriching with data model files.

        Args:
            agent_output: Plain text description of the business domain (2-4 sentences)
            deps: Processor dependencies including Neo4j connection manager

        Returns:
            Complete BusinessLogicDomain with description and data_models list
        """
        try:
            description = str(agent_output).strip().strip('"')

            try:
                span_map = await db_get_data_model_files(
                    deps.neo4j_conn_manager, deps.codebase_path
                )
            except Exception as e:
                logger.warning("Could not fetch data model files from Neo4j: {}", e)
                span_map = {}

            file_paths = sorted(span_map.keys())
            data_models = [
                CoreFile(path=file_path, responsibility=None)
                for file_path in file_paths
            ]

            return BusinessLogicDomain(
                description=description,
                data_models=data_models,
            )

        except Exception as e:
            logger.error(f"Error in BusinessLogicDomainPostProcessor: {e}")
            description = (
                str(agent_output).strip().strip('"')
                if agent_output
                else "Business logic domain"
            )
            return BusinessLogicDomain(description=description, data_models=[])
