"""Engineering workflow file inspection activity for Temporal workflows."""

from __future__ import annotations

import asyncio

from loguru import logger
from temporalio import activity

from unoplat_code_confluence_query_engine.models.output.engineering_workflow_output import (
    EngineeringWorkflow,
    EngineeringWorkflowSectionInspection,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.agents.validators.development_workflow_validator import (
    INSPECT_ENGINEERING_WORKFLOW_SECTION_ACTIVITY,
    inspect_engineering_workflow_section,
)


class EngineeringWorkflowFetchActivity:
    """Activity for inspecting the Engineering Workflow section of AGENTS.md."""

    @activity.defn(name=INSPECT_ENGINEERING_WORKFLOW_SECTION_ACTIVITY)
    async def inspect_engineering_workflow_section(
        self,
        codebase_path: str,
        engineering_workflow: EngineeringWorkflow | None,
    ) -> EngineeringWorkflowSectionInspection:
        """Validate the section in the codebase AGENTS.md and digest its exact bytes.

        Args:
            codebase_path: Absolute path to the codebase root directory.
            engineering_workflow: Commands that must appear in the section, when known.

        Returns:
            The section digest, or retry guidance when it cannot be accepted.
        """
        inspection = await asyncio.to_thread(
            inspect_engineering_workflow_section, codebase_path, engineering_workflow
        )
        logger.info(
            "[engineering_workflow_fetch] Section valid={} for codebase: {}",
            inspection.section_sha256 is not None,
            codebase_path,
        )
        return inspection
