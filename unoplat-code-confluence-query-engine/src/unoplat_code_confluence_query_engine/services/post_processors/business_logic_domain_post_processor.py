"""Business Logic Domain post-processor implementation."""

from __future__ import annotations

from loguru import logger

from unoplat_code_confluence_query_engine.db.postgres.code_confluence_business_logic_repository import (
    db_get_data_model_files,
)
from unoplat_code_confluence_query_engine.models.output.agent_md_output import (
    BusinessLogicDomain,
    CoreFile,
    CoreFileReference,
)
from unoplat_code_confluence_query_engine.services.agents_md.rendering.business_references.renderer import (
    write_business_domain_references_if_changed,
)
from unoplat_code_confluence_query_engine.services.post_processors.post_processor_base import (
    PostProcessorProtocol,
    ProcessorDependencies,
)


class BusinessLogicDomainPostProcessor(PostProcessorProtocol[str, BusinessLogicDomain]):
    """Post-processor for business logic domain agent output.

    The agent returns only a description string. This processor:
    1. Fetches all data model files from PostgreSQL
    2. Creates CoreFile entries for each file path
    3. Builds a complete BusinessLogicDomain with description + data_models
    4. Deterministically renders business_domain_references.md when content differs
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
            deps: Processor dependencies

        Returns:
            Complete BusinessLogicDomain with description and data_models list
        """
        try:
            description = str(agent_output).strip().strip('"')

            try:
                span_map = await db_get_data_model_files(deps.codebase_path)
            except Exception as e:
                logger.warning(
                    "Could not fetch data model files from PostgreSQL: {}", e
                )
                span_map = {}

            data_models: list[CoreFile] = []
            for file_path, model_spans in sorted(span_map.items()):
                references = [
                    CoreFileReference(
                        identifier=identifier,
                        start_line=start_line,
                        end_line=end_line,
                    )
                    for identifier, (start_line, end_line) in sorted(
                        model_spans.items(),
                        key=lambda item: (item[1][0], item[1][1], item[0]),
                    )
                ]
                data_models.append(
                    CoreFile(
                        path=file_path,
                        responsibility=None,
                        references=references,
                    )
                )

            domain = BusinessLogicDomain(
                description=description,
                data_models=data_models,
            )
            references_changed = write_business_domain_references_if_changed(
                deps.codebase_path,
                domain,
            )
            logger.info(
                "business_domain_references.md canonical render changed={}",
                references_changed,
            )
            return domain

        except Exception as e:
            logger.error("Error in BusinessLogicDomainPostProcessor: {}", e)
            description = (
                str(agent_output).strip().strip('"')
                if agent_output
                else "Business logic domain"
            )
            domain = BusinessLogicDomain(description=description, data_models=[])
            try:
                write_business_domain_references_if_changed(deps.codebase_path, domain)
            except Exception as render_error:
                logger.warning(
                    "Could not render business_domain_references.md after post-processing failure: {}",
                    render_error,
                )
            return domain
