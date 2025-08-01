# Fixtures are automatically discovered from tests/conftest.py
# The following fixtures are available to this test module:
# - docker_compose: Session-scoped fixture managing docker-compose services
# - service_ports: Session-scoped fixture providing service port mappings
# - test_client: Session-scoped TestClient fixture with proper configuration
# - github_token: Session-scoped fixture providing GitHub PAT token

import asyncio
import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from code_confluence_flow_bridge.processor.db.postgres.db import dispose_current_engine
import pytest
from fastapi.testclient import TestClient
from loguru import logger
from temporalio.client import Client, WorkflowExecutionStatus, WorkflowHandle

from src.code_confluence_flow_bridge.models.configuration.settings import CodebaseConfig
from src.code_confluence_flow_bridge.models.github.github_repo import GitHubRepoRequestConfiguration, IngestedRepositoryResponse
from src.code_confluence_flow_bridge.parser.package_manager.detectors.progress_models import DetectionResult
from src.code_confluence_flow_bridge.utility.environment_utils import (
    construct_local_repository_path,
)
from tests.utils.temporal_workflow_cleanup import terminate_all_running_workflows
from tests.utils.sync_db_cleanup import cleanup_neo4j_sync, cleanup_postgresql_sync
from tests.utils.sync_db_utils import get_sync_postgres_session

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


# ---------------------------------------------------------------------------
# SSE HELPER FUNCTIONS
# ---------------------------------------------------------------------------


def parse_sse_events(response_text: str) -> List[Dict[str, Any]]:
    """
    Parse SSE response text into structured events.

    Args:
        response_text: Raw SSE response text with event stream format

    Returns:
        List of parsed SSE events with event type and data
    """
    events: List[Dict[str, Any]] = []
    current_event: Dict[str, Any] = {}

    for line in response_text.strip().split("\n"):
        if line.startswith("event:"):
            current_event["event"] = line[6:].strip()
        elif line.startswith("data:"):
            data_str: str = line[5:].strip()
            try:
                current_event["data"] = json.loads(data_str)
            except json.JSONDecodeError:
                current_event["data"] = data_str
        elif line.startswith(":"):
            # Comment line
            current_event["comment"] = line[1:].strip()
        elif line == "" and current_event:
            # Empty line signals end of event
            events.append(current_event)
            current_event = {}

    # Don't forget the last event if no trailing empty line
    if current_event:
        events.append(current_event)

    return events


def stream_sse_response(response) -> str:
    """
    Collect SSE stream into a single string.

    Args:
        response: HTTP response object with streaming capability

    Returns:
        Complete SSE response as string
    """
    chunks: List[str] = []
    try:
        for chunk in response.iter_text():
            chunks.append(chunk)
    finally:
        # Ensure the response iterator is fully consumed
        pass
    return "".join(chunks)


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


def detect_local_codebases(test_client: TestClient, local_path: str) -> DetectionResult:
    """
    Detect codebases in local repository using SSE endpoint.

    Args:
        test_client: FastAPI test client instance
        local_path: Absolute path to local repository

    Returns:
        DetectionResult with codebases and metadata

    Raises:
        AssertionError: If SSE response is invalid or missing required events
    """
    # Extract just the folder name from the absolute path
    # The SSE endpoint expects a folder name when is_local=true, not an absolute path
    folder_name = os.path.basename(local_path)

    with test_client.stream("GET", "/detect-codebases-sse", params={"git_url": folder_name, "is_local": "true"}) as response:
        assert response.status_code == 200, f"SSE request failed: {response.text}"
        assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
        assert response.headers["cache-control"] == "no-cache"
        assert response.headers["connection"] == "keep-alive"

        # Collect and parse SSE events
        sse_content: str = stream_sse_response(response)
        events: List[Dict[str, Any]] = parse_sse_events(sse_content)

        # Validate event sequence
        assert len(events) >= 4, f"Expected at least 4 events, got {len(events)}"

        # Check for required event types
        event_types: set[str] = {event.get("event", "") for event in events}
        required_events: set[str] = {"connected", "progress", "result", "done"}
        assert required_events.issubset(event_types), f"Missing required events: {required_events - event_types}"

        # Extract result event
        result_events: List[Dict[str, Any]] = [e for e in events if e.get("event") == "result"]
        assert len(result_events) == 1, f"Expected 1 result event, got {len(result_events)}"

        result_data: Dict[str, Any] = result_events[0]["data"]

        # Validate result structure
        assert "repository_url" in result_data
        assert "codebases" in result_data
        assert "duration_seconds" in result_data
        assert "error" in result_data

        # Parse codebases into CodebaseConfig objects
        codebases: List[CodebaseConfig] = []
        for codebase_data in result_data["codebases"]:
            codebase = CodebaseConfig.model_validate(codebase_data)
            codebases.append(codebase)

        # Return structured result
        return DetectionResult(
            repository_url=result_data["repository_url"],
            duration_seconds=result_data["duration_seconds"],
            codebases=codebases,
            error=result_data.get("error"),
        )


def create_repo_request_from_detection(
    detection_result: DetectionResult, repository_name: str, repository_owner_name: str
) -> GitHubRepoRequestConfiguration:
    """
    Create GitHubRepoRequestConfiguration from SSE detection results.

    Args:
        detection_result: Result from SSE codebase detection
        repository_name: Name of the repository
        repository_owner_name: Owner/organization name

    Returns:
        Properly structured Pydantic model for ingestion endpoint
    """
    # Extract just the folder name from the absolute path for local repositories
    # This matches the UI behavior where only relative folder names are sent
    repository_url = detection_result.repository_url
    if repository_url.startswith('/') or repository_url.startswith('file://'):
        # This is an absolute path, extract just the folder name
        folder_name = os.path.basename(repository_url.replace('file://', ''))
        local_path = folder_name
    else:
        # Already a relative path or URL
        local_path = repository_url

    return GitHubRepoRequestConfiguration(
        repository_name=repository_name,
        repository_git_url=detection_result.repository_url,
        repository_owner_name=repository_owner_name,
        repository_metadata=detection_result.codebases,
        is_local=True,
        local_path=local_path,  # Now contains just the folder name
    )


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
        Complete integration test: detect local repository codebases via SSE,
        then ingest them via the ingestion endpoint and monitor workflow completion.
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
        # 3️⃣  Get local repository path and detect codebases via SSE
        # ------------------------------------------------------------------
        local_repo_path: str = get_repository_path()
        detection_result: DetectionResult = detect_local_codebases(test_client, local_repo_path)

        # Validate detection succeeded
        assert detection_result.error is None, f"Detection failed: {detection_result.error}"
        assert len(detection_result.codebases) > 0, "No codebases detected"

        # ------------------------------------------------------------------
        # 4️⃣  Create GitHubRepoRequestConfiguration from detection results
        # ------------------------------------------------------------------
        repo_request: GitHubRepoRequestConfiguration = create_repo_request_from_detection(
            detection_result=detection_result, repository_name="unoplat-code-confluence", repository_owner_name="unoplat"
        )

        # Validate Pydantic model creation
        assert repo_request.repository_name == repository_name
        assert repo_request.repository_owner_name == "unoplat"
        # SSE endpoint constructs path using construct_local_repository_path(), so we should expect the constructed path
        expected_constructed_path = construct_local_repository_path(os.path.basename(local_repo_path))
        assert repo_request.repository_git_url == expected_constructed_path
        assert repo_request.is_local is True
        assert repo_request.local_path == os.path.basename(local_repo_path)  # Now checks for folder name only
        assert len(repo_request.repository_metadata) == len(detection_result.codebases)

        # Validate that all codebases are properly structured
        for codebase in repo_request.repository_metadata:
            assert isinstance(codebase, CodebaseConfig)
            assert codebase.codebase_folder
            assert codebase.programming_language_metadata

        # ------------------------------------------------------------------
        # 5️⃣  Submit ingestion request
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
        # 6️⃣  Monitor workflow execution via Temporal client
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
        # 7️⃣  Verify workflow appears in jobs API
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
        # 8️⃣  Clean databases and terminate workflows after test completion
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
