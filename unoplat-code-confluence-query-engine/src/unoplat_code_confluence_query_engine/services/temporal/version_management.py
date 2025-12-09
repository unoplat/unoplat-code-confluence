"""Version management for Temporal Worker Versioning.

This module provides utilities for managing worker deployment versions,
including setting the current version via gRPC API.
"""

from __future__ import annotations

from loguru import logger
from temporalio.api.workflowservice.v1 import SetWorkerDeploymentCurrentVersionRequest
from temporalio.client import Client

from unoplat_code_confluence_query_engine.services.temporal.build_id_generator import (
    DEPLOYMENT_NAME,
)


async def set_current_version(client: Client, build_id: str) -> None:
    """Set the current version for the worker deployment.

    This calls the Temporal gRPC API to mark the given build_id as the
    current version for the deployment, allowing new workflows to be
    dispatched to workers with this version.

    Args:
        client: Temporal client with gRPC connection
        build_id: The build ID to set as current version

    Raises:
        Exception: If the gRPC call fails
    """
    request = SetWorkerDeploymentCurrentVersionRequest(
        namespace=client.namespace,
        deployment_name=DEPLOYMENT_NAME,
        build_id=build_id,
    )

    try:
        await client.workflow_service.set_worker_deployment_current_version(request)
        logger.info(
            "Set current worker deployment version",
            deployment_name=DEPLOYMENT_NAME,
            build_id=build_id,
        )
    except Exception as e:
        logger.error(
            "Failed to set current worker deployment version",
            deployment_name=DEPLOYMENT_NAME,
            build_id=build_id,
            error=str(e),
        )
        raise
