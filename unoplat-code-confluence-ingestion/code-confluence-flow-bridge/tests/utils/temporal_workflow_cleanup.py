"""
Temporal workflow cleanup utilities for test isolation.

These utilities provide forceful termination of running workflows to ensure
clean test environments without interference from previous workflow executions.
"""

from typing import List, Tuple

from loguru import logger
from temporalio.client import Client


async def terminate_all_running_workflows(
    temporal_address: str, namespace: str = "default"
) -> int:
    """
    Terminate (forcefully stop) all running workflows in Temporal server.

    This function uses TERMINATE (not CANCEL) to ensure immediate workflow stopping
    without waiting for graceful cleanup. This is appropriate for test isolation.

    Args:
        temporal_address: Temporal server address (e.g., "localhost:7233")
        namespace: Temporal namespace (default: "default")

    Returns:
        Number of workflows terminated

    Raises:
        ConnectionError: If unable to connect to Temporal server
        RuntimeError: If termination operations fail critically
    """
    try:
        client = await Client.connect(temporal_address, namespace=namespace)
        logger.debug(f"Connected to Temporal server at {temporal_address}")
    except Exception as e:
        logger.error(f"Failed to connect to Temporal server at {temporal_address}: {e}")
        raise ConnectionError(f"Cannot connect to Temporal: {e}")

    terminated_count = 0
    failed_terminations: List[Tuple[str, str, str]] = []  # (workflow_id, run_id, error)

    try:
        # List all running workflows using execution status filter
        # This includes RUNNING and CONTINUED_AS_NEW statuses
        query = "ExecutionStatus IN ('Running', 'ContinuedAsNew')"
        logger.debug(f"Querying workflows with: {query}")

        async for workflow in client.list_workflows(query):
            try:
                # Get workflow handle for termination
                handle = client.get_workflow_handle(
                    workflow_id=workflow.id, run_id=workflow.run_id
                )

                # TERMINATE (not cancel) - forceful immediate stop
                await handle.terminate(
                    reason="Test cleanup - forceful termination of running workflows"
                )
                terminated_count += 1
                logger.debug(
                    f"TERMINATED workflow: {workflow.id} (run: {workflow.run_id})"
                )

            except Exception as e:
                error_msg = f"Failed to terminate workflow {workflow.id}: {e}"
                logger.warning(error_msg)
                failed_terminations.append((workflow.id, workflow.run_id, str(e)))
                continue

    except Exception as e:
        logger.error(f"Failed to list workflows: {e}")
        raise RuntimeError(f"Workflow listing failed: {e}")

    # Log summary
    if terminated_count > 0:
        logger.info(f"Successfully TERMINATED {terminated_count} running workflows")
    if failed_terminations:
        logger.warning(
            f"Failed to terminate {len(failed_terminations)} workflows: {failed_terminations}"
        )

    return terminated_count


async def terminate_workflows_by_type(
    temporal_address: str, workflow_type: str, namespace: str = "default"
) -> int:
    """
    Terminate all running workflows of a specific type.

    Args:
        temporal_address: Temporal server address
        workflow_type: Specific workflow type to target (e.g., 'IngestionWorkflow')
        namespace: Temporal namespace

    Returns:
        Number of workflows terminated
    """
    try:
        client = await Client.connect(temporal_address, namespace=namespace)
    except Exception as e:
        logger.error(f"Failed to connect to Temporal server: {e}")
        raise ConnectionError(f"Cannot connect to Temporal: {e}")

    terminated_count = 0
    query = f"WorkflowType = '{workflow_type}' AND ExecutionStatus IN ('Running', 'ContinuedAsNew')"

    async for workflow in client.list_workflows(query):
        try:
            handle = client.get_workflow_handle(
                workflow_id=workflow.id, run_id=workflow.run_id
            )

            await handle.terminate(
                reason=f"Test cleanup - terminating {workflow_type} workflows"
            )
            terminated_count += 1
            logger.debug(f"TERMINATED {workflow_type} workflow: {workflow.id}")

        except Exception as e:
            logger.warning(
                f"Failed to terminate {workflow_type} workflow {workflow.id}: {e}"
            )
            continue

    return terminated_count
