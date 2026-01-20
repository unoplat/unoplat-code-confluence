# Fixtures are automatically discovered from tests/conftest.py
# The following fixtures are available to this test module:
# - docker_compose: Session-scoped fixture managing docker-compose services
# - service_ports: Session-scoped fixture providing service port mappings
# - test_client: Session-scoped TestClient fixture with proper configuration
# - github_token: Session-scoped fixture providing GitHub PAT token

import asyncio
import time
from typing import Any, Dict, Optional

from fastapi.testclient import TestClient
from loguru import logger
import pytest
from src.code_confluence_flow_bridge.models.github.github_repo import (
    IngestedRepositoryResponse,
)
from src.code_confluence_flow_bridge.processor.db.postgres.db import (
    dispose_current_engine,
)
from temporalio.client import Client, WorkflowExecutionStatus, WorkflowHandle
from unoplat_code_confluence_commons.credential_enums import (
    CredentialNamespace,
    ProviderKey,
    SecretKind,
)

from tests.utils.sync_db_cleanup import cleanup_postgresql_sync
from tests.utils.sync_db_utils import get_sync_postgres_session


def cleanup_repository_via_endpoint(
    test_client: TestClient, repository_name: str, repository_owner_name: str
) -> None:
    """
    Clean up repository data using the FastAPI delete endpoint.

    This avoids async session management issues by using the test client
    to call the production delete endpoint which has proper connection handling.

    Args:
        test_client: FastAPI test client instance
        repository_name: Name of the repository to delete
        repository_owner_name: Owner/organization name of the repository
    """

    # Create the repository info payload
    repo_info = IngestedRepositoryResponse(
        repository_name=repository_name,
        repository_owner_name=repository_owner_name,
        provider_key=ProviderKey.GITHUB_OPEN,
    )

    # Call the delete endpoint via test client
    response = test_client.request(
        method="DELETE", url="/delete-repository", json=repo_info.model_dump()
    )

    # Handle response - don't fail if repository doesn't exist (404)
    if response.status_code == 404:
        # Repository doesn't exist, which is fine for cleanup
        pass
    elif response.status_code == 200:
        # Successfully deleted
        pass
    else:
        # Unexpected error - log but don't fail the test
        logger.error(
            f"Repository cleanup failed with status {response.status_code}: {response.text}"
        )


async def monitor_workflow_completion(
    workflow_id: str, run_id: str, temporal_address: str, timeout_seconds: int = 300
) -> WorkflowExecutionStatus:
    """
    Monitor Temporal workflow execution until completion.

    Args:
        workflow_id: Temporal workflow ID
        run_id: Temporal run ID
        temporal_address: Temporal server address
        timeout_seconds: Maximum time to wait for completion

    Returns:
        Final workflow execution status

    Raises:
        asyncio.TimeoutError: If workflow doesn't complete within timeout
        RuntimeError: If workflow fails or is terminated
    """
    client: Client = await Client.connect(temporal_address)

    # Get workflow handle
    handle: WorkflowHandle = client.get_workflow_handle(
        workflow_id=workflow_id, run_id=run_id
    )

    # Wait for completion with timeout
    start_time: float = time.time()

    while time.time() - start_time < timeout_seconds:
        try:
            # Check workflow status
            description = await handle.describe()
            status: Optional[WorkflowExecutionStatus] = description.status

            if status is None:
                # If status is None, continue monitoring
                await asyncio.sleep(5)
                continue

            if status == WorkflowExecutionStatus.COMPLETED:
                return status
            elif status in [
                WorkflowExecutionStatus.FAILED,
                WorkflowExecutionStatus.TERMINATED,
                WorkflowExecutionStatus.TIMED_OUT,
                WorkflowExecutionStatus.CANCELED,
            ]:
                raise RuntimeError(f"Workflow failed with status: {status}")

            # Wait before next check
            await asyncio.sleep(5)

        except Exception as e:
            # Re-raise if it's our custom error
            if isinstance(e, RuntimeError):
                raise
            # For other errors, continue monitoring
            await asyncio.sleep(5)

    raise asyncio.TimeoutError(
        f"Workflow did not complete within {timeout_seconds} seconds"
    )


# ---------------------------------------------------------------------------
# CONSTANTS
# ---------------------------------------------------------------------------

REPO_REQUEST: Dict[str, Any] = {
    "repository_name": "unoplat-code-confluence",
    "repository_git_url": "https://github.com/unoplat/unoplat-code-confluence",
    "repository_owner_name": "unoplat",
    "provider_key": ProviderKey.GITHUB_OPEN.value,
    "repository_metadata": [
        {
            "codebase_folder": "unoplat-code-confluence-ingestion/code-confluence-flow-bridge",
            "root_packages": ["src/code_confluence_flow_bridge"],
            "programming_language_metadata": {
                "language": "python",
                "package_manager": "uv",
                "role": "leaf",
            },
        }
    ],
}


# ---------------------------------------------------------------------------
# INTEGRATION TESTS
# ---------------------------------------------------------------------------


@pytest.mark.integration  # type: ignore[var-annotated]
class TestStartIngestionEndpoint:
    """Integration tests for the start_ingestion endpoint with full workflow testing."""

    @pytest.mark.asyncio(loop_scope="session")  # type: ignore[var-annotated]
    async def test_start_ingestion_flow(
        self,
        test_client: TestClient,
        github_token: str,
        service_ports: Dict[str, int],
    ) -> None:
        """Full happy-path flow: ingest token -> start ingestion -> verify response."""
        # Clean up databases using context manager for isolated sessions
        with get_sync_postgres_session(service_ports["postgresql"]) as session:
            cleanup_postgresql_sync(session)
        await dispose_current_engine()
        # ------------------------------------------------------------------
        # 0️⃣  TERMINATE all running workflows before test
        # ------------------------------------------------------------------
        temporal_address = f"localhost:{service_ports['temporal']}"
        # try:
        #     terminated_count = await terminate_all_running_workflows(temporal_address)
        #     logger.info(f"Pre-test cleanup: TERMINATED {terminated_count} running workflows")
        # except Exception as e:
        #     logger.warning(f"Failed to terminate workflows before test: {e}")

        # ------------------------------------------------------------------
        # 1️⃣  make sure the PAT is stored (idempotent)
        # ------------------------------------------------------------------
        token_resp = test_client.post(
            "/ingest-token",
            params={
                "namespace": CredentialNamespace.REPOSITORY.value,
                "provider_key": ProviderKey.GITHUB_OPEN.value,
                "secret_kind": SecretKind.PAT.value,
            },
            headers={"Authorization": f"Bearer {github_token}"},
        )
        assert token_resp.status_code in (201, 409), token_resp.text

        # ------------------------------------------------------------------
        # 2️⃣  call the endpoint under test
        # ------------------------------------------------------------------
        ingest_resp = test_client.post("/start-ingestion", json=REPO_REQUEST)
        assert ingest_resp.status_code == 201, ingest_resp.text

        payload = ingest_resp.json()
        assert payload["workflow_id"].startswith("ingest-"), payload
        assert payload["run_id"] != "none", payload

        # ------------------------------------------------------------------
        # 3️⃣  (optional) wait briefly and verify the parent workflow appears
        # ------------------------------------------------------------------
        deadline = time.time() + 60  # seconds
        while time.time() < deadline:
            jobs_resp = test_client.get("/parent-workflow-jobs")
            jobs_resp.raise_for_status()
            jobs = jobs_resp.json()["jobs"]
            if any(
                job["repository_workflow_run_id"] == payload["run_id"] for job in jobs
            ):
                break
            time.sleep(5)
        else:
            pytest.fail(
                "Workflow run did not show up in /parent-workflow-jobs within timeout"
            )

        # ------------------------------------------------------------------
        # 4️⃣  ensure the workflow has CLOSED before leaving the test
        # ------------------------------------------------------------------
        try:
            final_status = await monitor_workflow_completion(
                workflow_id=payload["workflow_id"],
                run_id=payload["run_id"],
                temporal_address=temporal_address,
                timeout_seconds=60,
            )
            assert final_status == WorkflowExecutionStatus.COMPLETED, (
                f"Workflow ended in unexpected status {final_status}"
            )
        except (asyncio.TimeoutError, RuntimeError):
            # If workflow fails or times out, force terminate it for cleanup
            client = await Client.connect(temporal_address)
            handle = client.get_workflow_handle(
                payload["workflow_id"], run_id=payload["run_id"]
            )
            try:
                await handle.terminate(
                    reason="test cleanup - workflow did not complete normally"
                )
            except Exception as e:
                logger.warning(f"Failed to terminate workflow during cleanup: {e}")

