"""Business Logic Domain post-processor implementation."""

from __future__ import annotations

from typing import List

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


class BusinessLogicDomainPostProcessor(PostProcessorProtocol[str, BusinessLogicDomain]):
    """Post-processor for business logic domain agent output."""
    
    async def process(
        self,
        *,
        agent_output: str,
        deps: ProcessorDependencies,
    ) -> BusinessLogicDomain:
        """Process business logic domain agent output by adding core files list."""
        try:
            # Raw output should just be the description string
            description = agent_output.strip().strip('"')
            
            # Get data model files from database
            try:
                file_paths: List[str] = await db_get_data_model_files(
                    deps.neo4j_conn_manager, deps.codebase_path
                )
            except Exception as e:
                logger.warning("Could not fetch data model files from Neo4j: {}", e)
                file_paths = []
            
            # Create CoreFile objects without static responsibility
            core_files = []
            for file_path in file_paths:
                core_file = CoreFile(
                    path=file_path,
                    responsibility=None
                )
                core_files.append(core_file)
            
            # Create the final BusinessLogicDomain model
            business_logic_domain = BusinessLogicDomain(
                description=description,
                core_files=core_files
            )
            
            # Return BaseModel directly instead of JSON string
            return business_logic_domain
            
        except Exception as e:
            logger.error("Error in BusinessLogicDomainPostProcessor: {}", e)
            # Return minimal valid structure if processing fails
            fallback_domain = BusinessLogicDomain(
                description=agent_output.strip().strip('"') if agent_output else "Business logic domain",
                core_files=[]
            )
            return fallback_domain