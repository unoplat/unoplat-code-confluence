"""Framework Explorer post-processor implementation."""

from __future__ import annotations

from typing import List

from loguru import logger

from unoplat_code_confluence_query_engine.models.agent_md_output import (
    FrameworkLibraryOutput,
)
from unoplat_code_confluence_query_engine.services.framework_baseline_service import (
    fetch_baseline_frameworks_as_outputs,
)
from unoplat_code_confluence_query_engine.services.post_processors.post_processor_base import (
    PostProcessorProtocol,
    ProcessorDependencies,
)


def has_locations(item: FrameworkLibraryOutput) -> bool:
    """Check if an item has any location data in its features."""
    return any(
        feature.locations for feature in item.features_used
    )


class FrameworkExplorerPostProcessor(PostProcessorProtocol[List[FrameworkLibraryOutput], List[FrameworkLibraryOutput]]):
    """Post-processor for framework explorer agent output."""
    
    async def process(
        self,
        *,
        agent_output: List[FrameworkLibraryOutput],
        deps: ProcessorDependencies,
    ) -> List[FrameworkLibraryOutput]:
        """Filter and process framework explorer output with database preference."""
        # Handle fallback for unexpected string input
        if isinstance(agent_output, str):
            logger.debug("FrameworkExplorerPostProcessor: received unexpected string input")
            return agent_output
            
        # agent_output is now List[FrameworkLibraryOutput]
        items = agent_output

        # Step 1: Fetch complete framework data from database
        try:
            db_frameworks = await fetch_baseline_frameworks_as_outputs(
                deps.neo4j_conn_manager, deps.codebase_path, deps.programming_language
            )
        except Exception as e:
            logger.warning("Could not fetch baseline frameworks from Neo4j: {}", e)
            db_frameworks = []

        # Step 2: Create index of database frameworks by normalized name
        db_frameworks_by_name = {fw.name.strip().lower(): fw for fw in db_frameworks}
        logger.debug(
            "FrameworkExplorerPostProcessor: found {} database frameworks for codebase {} => {}",
            len(db_frameworks),
            deps.codebase_path,
            sorted(db_frameworks_by_name.keys())
        )

        # Step 3: Process agent output to filter novel frameworks
        filtered_agent_items: List[FrameworkLibraryOutput] = []

        # Counters + reasons for visibility
        filtered_empty = 0
        filtered_covered = 0
        filtered_no_locations = 0

        for item in items:
            norm_name = item.name.strip().lower()
            features_count = len(item.features_used)
            total_locations = sum(len(f.locations) for f in item.features_used)

            logger.debug(
                "FrameworkExplorerPostProcessor: evaluating agent lib name='{}' features={} total_locations={}",
                item.name,
                features_count,
                total_locations,
            )

            if not norm_name:
                filtered_empty += 1
                logger.debug(
                    "FrameworkExplorerPostProcessor: filtered '{}' — reason=empty-name",
                    item.name,
                )
                continue

            if norm_name in db_frameworks_by_name:
                filtered_covered += 1
                logger.debug(
                    "FrameworkExplorerPostProcessor: filtered '{}' — reason=covered-in-database",
                    item.name,
                )
                continue

            if not has_locations(item):
                filtered_no_locations += 1
                logger.debug(
                    "FrameworkExplorerPostProcessor: filtered '{}' — reason=no-feature-locations",
                    item.name,
                )
                continue

            filtered_agent_items.append(item)
            logger.debug(
                "FrameworkExplorerPostProcessor: included novel agent lib '{}'",
                item.name,
            )

        # Step 4: Combine database frameworks (preferred) + novel agent frameworks
        final_frameworks = list(db_frameworks) + filtered_agent_items

        logger.debug(
            "FrameworkExplorerPostProcessor: merge summary for {} — db_frameworks={} novel_agent={} filtered_total={} (empty_name={}, covered_in_db={}, no_locations={})",
            deps.codebase_path,
            len(db_frameworks),
            len(filtered_agent_items),
            filtered_empty + filtered_covered + filtered_no_locations,
            filtered_empty,
            filtered_covered,
            filtered_no_locations,
        )
        logger.debug(
            "FrameworkExplorerPostProcessor: final merged libs => {}",
            [fw.name for fw in final_frameworks],
        )

        return final_frameworks
