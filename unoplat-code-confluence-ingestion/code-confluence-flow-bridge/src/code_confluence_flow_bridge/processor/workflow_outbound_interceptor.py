import contextvars
from typing import Any

from temporalio import workflow
from temporalio.worker._interceptor import (
    StartActivityInput,
    StartChildWorkflowInput,
    WorkflowOutboundInterceptor,
)

# Context variables to store workflow headers
workflow_headers_var: contextvars.ContextVar[dict] = contextvars.ContextVar(
    "workflow_headers", default={}
)


class ParentWorkflowOutboundInterceptor(WorkflowOutboundInterceptor):
    """Outbound interceptor to forward workflow headers to activities.

    This interceptor ensures that headers set in workflow inbound interceptors
    are properly forwarded to all activity calls.
    """

    def start_activity(
        self, input: StartActivityInput
    ) -> workflow.ActivityHandle[Any]:
        # Get headers from context
        headers = workflow_headers_var.get()

        if headers:
            # Forward headers from workflow to activity
            input.headers = {
                **input.headers,  # Keep any existing headers
                **headers,  # Add headers from workflow
            }

            # Log the forwarding for debugging
            workflow.logger.debug(
                "Forwarding headers from workflow to activity: %s", list(headers.keys())
            )

        return super().start_activity(input)

    async def start_child_workflow(
        self, input: StartChildWorkflowInput
    ) -> workflow.ChildWorkflowHandle[Any, Any]:
        try:
            # Get headers from context
            headers = workflow_headers_var.get()

            if headers:
                # Forward headers from workflow to child workflow
                input.headers = {
                    **(
                        input.headers or {}
                    ),  # Keep any existing headers, default to empty dict if None
                    **headers,  # Add headers from workflow
                }

                workflow.logger.debug(
                    "Forwarding headers from workflow to child workflow: %s",
                    list(headers.keys()),
                )
        except Exception as e:
            workflow.logger.error("Error forwarding headers to child workflow: %s", str(e))
            # Continue execution even if header forwarding fails

        return await self.next.start_child_workflow(input)
