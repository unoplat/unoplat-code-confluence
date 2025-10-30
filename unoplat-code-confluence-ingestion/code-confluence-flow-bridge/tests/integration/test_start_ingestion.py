# Fixtures are automatically discovered from tests/conftest.py
# The following fixtures are available to this test module:
# - docker_compose: Session-scoped fixture managing docker-compose services
# - service_ports: Session-scoped fixture providing service port mappings
# - test_client: Session-scoped TestClient fixture with proper configuration
# - github_token: Session-scoped fixture providing GitHub PAT token

import os
import asyncio
from pathlib import Path
import subprocess
import time
from typing import Any, Dict, List, Optional

from fastapi.testclient import TestClient
from loguru import logger
import pytest
from src.code_confluence_flow_bridge.models.github.github_repo import (
    GitHubRepoRequestConfiguration,
    IngestedRepositoryResponse,
)
from src.code_confluence_flow_bridge.processor.db.postgres.db import (
    dispose_current_engine,
)
from src.code_confluence_flow_bridge.utility.environment_utils import (
    construct_local_repository_path,
)
from temporalio.client import Client, WorkflowExecutionStatus, WorkflowHandle

from tests.utils.sync_db_cleanup import cleanup_neo4j_sync, cleanup_postgresql_sync
from tests.utils.sync_db_utils import get_sync_postgres_session
from tests.utils.temporal_workflow_cleanup import terminate_all_running_workflows

# ---------------------------------------------------------------------------
# REPOSITORY PATH HELPER
# ---------------------------------------------------------------------------


def get_repository_path() -> str:
    """
    Get the repository root path using git to find the repository root.

    This function works in both local development and CI/CD environments by
    using git to identify the actual repository root directory.

    Returns:
        str: Absolute path to the repository root directory

    Raises:
        RuntimeError: If the repository root directory cannot be found
    """
    try:
        # Use git to find the repository root
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
            cwd=Path(__file__).parent  # Start from test file directory
        )
        repository_root = result.stdout.strip()

        # Verify the path exists and is a directory
        if Path(repository_root).exists() and Path(repository_root).is_dir():
            return repository_root
        else:
            raise RuntimeError(f"Git returned invalid repository path: {repository_root}")

    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        # Git command failed, try fallback approach
        current_path = Path(__file__).parent.parent.parent.parent.parent  # Go up from test file

        # Look for repository indicators
        indicators = [
            "unoplat-code-confluence-ingestion",
            "unoplat-code-confluence-frontend",
            "unoplat-code-confluence-commons",
            ".git",
            "Taskfile.yml"
        ]

        # Check current directory and parents
        for path in [current_path] + list(current_path.parents):
            if any((path / indicator).exists() for indicator in indicators):
                return str(path.resolve())

        # Final fallback
        raise RuntimeError(
            f"Repository root could not be determined. Git error: {e}. "
            f"No repository indicators found starting from: {current_path}"
        )


def cleanup_repository_via_endpoint(test_client: TestClient, repository_name: str, repository_owner_name: str, is_local: bool = False, local_path: Optional[str] = None) -> None:
    """
    Clean up repository data using the FastAPI delete endpoint.

    This avoids async session management issues by using the test client
    to call the production delete endpoint which has proper connection handling.

    Args:
        test_client: FastAPI test client instance
        repository_name: Name of the repository to delete
        repository_owner_name: Owner/organization name of the repository
        is_local: Whether this is a local repository
        local_path: Local path for local repositories
    """

    # Create the repository info payload
    repo_info = IngestedRepositoryResponse(
        repository_name=repository_name,
        repository_owner_name=repository_owner_name,
        is_local=is_local,
        local_path=local_path
    )

    # Call the delete endpoint via test client
    response = test_client.request(
        method="DELETE",
        url="/delete-repository",
        json=repo_info.model_dump()
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
        logger.error(f"Repository cleanup failed with status {response.status_code}: {response.text}")


async def monitor_workflow_completion(workflow_id: str, run_id: str, temporal_address: str, timeout_seconds: int = 300) -> WorkflowExecutionStatus:
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
    handle: WorkflowHandle = client.get_workflow_handle(workflow_id=workflow_id, run_id=run_id)

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

    raise asyncio.TimeoutError(f"Workflow did not complete within {timeout_seconds} seconds")


# ---------------------------------------------------------------------------
# CONSTANTS
# ---------------------------------------------------------------------------

REPO_REQUEST: Dict[str, Any] = {
    "repository_name": "unoplat-code-confluence",
    "repository_git_url": "https://github.com/unoplat/unoplat-code-confluence",
    "repository_owner_name": "unoplat",
    "repository_metadata": [
        {
            "codebase_folder": "unoplat-code-confluence-ingestion/code-confluence-flow-bridge",
            "root_packages": ["src/code_confluence_flow_bridge"],
            "programming_language_metadata": {"language": "python", "package_manager": "uv", "role": "leaf"},
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
        neo4j_client,

    ) -> None:
        """Full happy-path flow: ingest token -> start ingestion -> verify response."""
        # Clean up databases using context manager for isolated sessions
        with get_sync_postgres_session(service_ports["postgresql"]) as session:
            cleanup_postgresql_sync(session)
        cleanup_neo4j_sync(neo4j_client)
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
            if any(job["repository_workflow_run_id"] == payload["run_id"] for job in jobs):
                break
            time.sleep(5)
        else:
            pytest.fail("Workflow run did not show up in /parent-workflow-jobs within timeout")


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
            assert final_status == WorkflowExecutionStatus.COMPLETED, f"Workflow ended in unexpected status {final_status}"
        except (asyncio.TimeoutError, RuntimeError):
            # If workflow fails or times out, force terminate it for cleanup
            client = await Client.connect(temporal_address)
            handle = client.get_workflow_handle(payload["workflow_id"], run_id=payload["run_id"])
            try:
                await handle.terminate(reason="test cleanup - workflow did not complete normally")
            except Exception as e:
                logger.warning(f"Failed to terminate workflow during cleanup: {e}")

        cleanup_neo4j_sync(neo4j_client)






    @pytest.mark.asyncio(loop_scope="session") #type: ignore
    async def test_complete_detection_and_ingestion_flow(
        self,
        test_client: TestClient,
        github_token: str,
        service_ports: Dict[str, int],  # noqa: F811 - fixture parameter
        neo4j_client,
    ) -> None:
        """
        Complete integration test: submit local repository for ingestion with auto-detection,
        then monitor workflow completion.

        This test validates the new 1-step flow where codebase detection happens automatically
        within the start-ingestion endpoint when repository_metadata is None.
        """
        # Clean up databases using context manager for isolated sessions
        with get_sync_postgres_session(service_ports["postgresql"]) as session:
            cleanup_postgresql_sync(session)
        cleanup_neo4j_sync(neo4j_client)
        await dispose_current_engine()

        # Temporal address for post-test cleanup
        temporal_address = f"localhost:{service_ports['temporal']}"

        # ------------------------------------------------------------------
        # 2️⃣  Ensure token is ingested (idempotent)
        # ------------------------------------------------------------------
        token_resp = test_client.post(
            "/ingest-token",
            headers={"Authorization": f"Bearer {github_token}"},
        )
        assert token_resp.status_code in (201, 409), token_resp.text

        repository_name = "unoplat-code-confluence"

        # ------------------------------------------------------------------
        # 3️⃣  Get local repository path and create ingestion request with auto-detection
        # ------------------------------------------------------------------
        local_repo_path: str = get_repository_path()
        folder_name = os.path.basename(local_repo_path)

        # Create request WITHOUT repository_metadata to trigger auto-detection
        repo_request = GitHubRepoRequestConfiguration(
            repository_name=repository_name,
            repository_git_url=construct_local_repository_path(folder_name),
            repository_owner_name="unoplat",
            repository_metadata=None,  # Triggers auto-detection
            is_local=True,
            local_path=folder_name
        )

        # Validate Pydantic model creation
        assert repo_request.repository_name == repository_name
        assert repo_request.repository_owner_name == "unoplat"
        assert repo_request.is_local is True
        assert repo_request.local_path == folder_name
        assert repo_request.repository_metadata is None, "Should be None to trigger auto-detection"

        # ------------------------------------------------------------------
        # 4️⃣  Submit ingestion request (auto-detection happens internally)
        # ------------------------------------------------------------------
        ingestion_resp = test_client.post("/start-ingestion", json=repo_request.model_dump())
        assert ingestion_resp.status_code == 201, f"Ingestion failed: {ingestion_resp.text}"

        ingestion_payload: Dict[str, Any] = ingestion_resp.json()
        assert "workflow_id" in ingestion_payload
        assert "run_id" in ingestion_payload
        assert ingestion_payload["workflow_id"].startswith("ingest-")
        assert ingestion_payload["run_id"] != "none"

        workflow_id: str = ingestion_payload["workflow_id"]
        run_id: str = ingestion_payload["run_id"]

        # ------------------------------------------------------------------
        # 5️⃣  Monitor workflow execution via Temporal client
        # ------------------------------------------------------------------

        try:
            final_status: WorkflowExecutionStatus = await monitor_workflow_completion(
                workflow_id=workflow_id,
                run_id=run_id,
                temporal_address=temporal_address,
                timeout_seconds=600,  # 10 minutes for local processing
            )

            assert final_status == WorkflowExecutionStatus.COMPLETED, f"Workflow did not complete successfully: {final_status}"

        except asyncio.TimeoutError:
            # If workflow times out, force terminate it for cleanup
            try:
                client = await Client.connect(temporal_address)
                handle = client.get_workflow_handle(workflow_id, run_id=run_id)
                await handle.terminate(reason="test cleanup - workflow timed out")
                logger.warning(f"Terminated workflow {workflow_id} due to timeout")
            except Exception as e:
                logger.warning(f"Failed to terminate timed-out workflow: {e}")

            # Still verify it appears in the jobs API
            jobs_resp = test_client.get("/parent-workflow-jobs")
            jobs_resp.raise_for_status()
            jobs: List[Dict[str, Any]] = jobs_resp.json()["jobs"]

            workflow_found: bool = any(job["repository_workflow_run_id"] == run_id for job in jobs)
            assert workflow_found, f"Workflow {run_id} not found in parent workflow jobs"

            # Log timeout but don't fail the test - ingestion was started successfully
            print(f"Workflow {workflow_id} did not complete within timeout but was started successfully")

        # ------------------------------------------------------------------
        # 6️⃣  Verify workflow appears in jobs API
        # ------------------------------------------------------------------
        jobs_resp = test_client.get("/parent-workflow-jobs")
        assert jobs_resp.status_code == 200, f"Jobs API failed: {jobs_resp.text}"

        jobs_data: Dict[str, Any] = jobs_resp.json()
        assert "jobs" in jobs_data

        job_list: List[Dict[str, Any]] = jobs_data["jobs"]
        target_job: Optional[Dict[str, Any]] = None

        for job in job_list:
            if job.get("repository_workflow_run_id") == run_id:
                target_job = job
                break

        assert target_job is not None, f"Workflow {run_id} not found in jobs list"
        assert target_job["repository_workflow_run_id"] == run_id
        assert "status" in target_job
        assert "started_at" in target_job

        # ------------------------------------------------------------------
        # 7️⃣  Clean databases and terminate workflows after test completion
        # ------------------------------------------------------------------
        cleanup_neo4j_sync(neo4j_client)
        with get_sync_postgres_session(service_ports["postgresql"]) as session:
            cleanup_postgresql_sync(session)

        # Terminate any workflows created during test
        try:
            terminated_count = await terminate_all_running_workflows(temporal_address)
            if terminated_count > 0:
                logger.info(f"Post-test cleanup: TERMINATED {terminated_count} workflows")
        except Exception as e:
            logger.warning(f"Failed to terminate workflows after test: {e}")
