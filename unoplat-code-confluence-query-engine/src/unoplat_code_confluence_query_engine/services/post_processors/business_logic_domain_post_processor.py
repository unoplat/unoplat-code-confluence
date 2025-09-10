"""Business Logic Domain post-processor implementation."""

from __future__ import annotations

from typing import List, Union

from loguru import logger

from unoplat_code_confluence_query_engine.db.neo4j.business_logic_repository import (
    db_get_data_model_files,
)
from unoplat_code_confluence_query_engine.models.agent_md_output import (
    BusinessLogicDomain,
    CoreFile,
)
from unoplat_code_confluence_query_engine.services.post_processors.post_processor_base import (
    PostProcessorProtocol,
    ProcessorDependencies,
)


class BusinessLogicDomainPostProcessor(PostProcessorProtocol[Union[str, BusinessLogicDomain], BusinessLogicDomain]):
    """Post-processor for business logic domain agent output."""
    
    async def process(
        self,
        *,
        agent_output: Union[str, BusinessLogicDomain],
        deps: ProcessorDependencies,
    ) -> BusinessLogicDomain:
        """Process business logic domain agent output by adding/enriching data models.

        Accepts either:
        - str: description only; builds BusinessLogicDomain with data_models from Neo4j
        - BusinessLogicDomain: returns the model, enriching data_models from Neo4j if empty
        """
        try:
            # If already a model, possibly enrich it and return
            if isinstance(agent_output, BusinessLogicDomain):
                existing = agent_output
                try:
                    file_paths: List[str] = await db_get_data_model_files(
                        deps.neo4j_conn_manager, deps.codebase_path
                    )
                except Exception as e:
                    logger.warning("Could not fetch data model files from Neo4j: {}", e)
                    file_paths = []

                if not existing.data_models:
                    existing.data_models = [
                        CoreFile(path=fp, responsibility=None) for fp in file_paths
                    ]
                return existing

            # Otherwise treat output as description string
            description = str(agent_output).strip().strip('"')
            
            # Get data model files from database
            try:
                file_paths: List[str] = await db_get_data_model_files(
                    deps.neo4j_conn_manager, deps.codebase_path
                )
            except Exception as e:
                logger.warning("Could not fetch data model files from Neo4j: {}", e)
                file_paths = []
            
            # Create CoreFile objects without static responsibility
            data_models = [
                CoreFile(path=file_path, responsibility=None) for file_path in file_paths
            ]
            
            # Create the final BusinessLogicDomain model
            business_logic_domain = BusinessLogicDomain(
                description=description,
                data_models=data_models,
            )
            
            # Return BaseModel directly instead of JSON string
            return business_logic_domain
            
        except Exception as e:
            logger.error("Error in BusinessLogicDomainPostProcessor: {}", e)
            # Return minimal valid structure if processing fails
            description = (
                str(agent_output).strip().strip('"')
                if agent_output else "Business logic domain"
            )
            return BusinessLogicDomain(description=description, data_models=[])
