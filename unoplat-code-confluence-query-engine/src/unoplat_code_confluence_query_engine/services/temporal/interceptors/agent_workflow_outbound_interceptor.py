"""Outbound interceptor for header propagation in workflows.

This module provides the outbound interceptor that forwards workflow headers
to activities and child workflows, enabling distributed tracing and context
propagation throughout the workflow execution tree.
"""

from __future__ import annotations

import contextvars
from typing import TYPE_CHECKING

from temporalio import workflow
from temporalio.worker._interceptor import (
    StartActivityInput,
    StartChildWorkflowInput,
    WorkflowOutboundInterceptor,
)

with workflow.unsafe.imports_passed_through():
    from loguru import logger

if TYPE_CHECKING:
    from temporalio.api.common.v1 import Payload

# Context variable to store workflow headers for propagation
# Set by the inbound interceptor, read by this outbound interceptor
workflow_headers_var: contextvars.ContextVar[dict[str, Payload]] = (
    contextvars.ContextVar("workflow_headers", default={})
)


class AgentWorkflowOutboundInterceptor(WorkflowOutboundInterceptor):
    """Outbound interceptor to forward workflow headers to activities and child workflows.

    This interceptor ensures that headers set in the workflow inbound interceptor
    are properly forwarded to all activity calls and child workflows, enabling:
    - trace_id propagation for distributed tracing
    - repository/codebase context propagation
    - workflow run ID correlation
    """

    def start_activity(  # pyright: ignore[reportUnknownParameterType]
        self, input: StartActivityInput
    ) -> workflow.ActivityHandle[object]:
        """Forward headers to activity calls.

        Args:
            input: Activity start input containing activity configuration

        Returns:
            Activity handle for the started activity
        """
        headers = workflow_headers_var.get()

        if headers:
            # Merge existing headers with workflow headers
            input.headers = {
                **input.headers,
                **headers,
            }
            logger.debug(
                "[agent_workflow_outbound] Forwarding headers to activity: {}",
                list(headers.keys()),
            )

        return super().start_activity(input)

    async def start_child_workflow(  # pyright: ignore[reportUnknownParameterType]
        self, input: StartChildWorkflowInput
    ) -> workflow.ChildWorkflowHandle[object, object]:
        """Forward headers to child workflow calls.

        Args:
            input: Child workflow start input containing workflow configuration

        Returns:
            Child workflow handle for the started workflow
        """
        try:
            headers = workflow_headers_var.get()

            if headers:
                # Merge existing headers with workflow headers
                input.headers = {
                    **(input.headers or {}),
                    **headers,
                }
                logger.debug(
                    "[agent_workflow_outbound] Forwarding headers to child workflow: {}",
                    list(headers.keys()),
                )
        except Exception as e:
            logger.error(
                "[agent_workflow_outbound] Error forwarding headers to child workflow: {}",
                str(e),
            )
            # Continue execution even if header forwarding fails

        return await self.next.start_child_workflow(input)
