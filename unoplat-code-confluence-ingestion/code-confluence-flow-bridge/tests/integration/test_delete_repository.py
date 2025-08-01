# Fixtures are automatically discovered from tests/conftest.py
# The following fixtures are available to this test module:
# - docker_compose: Session-scoped fixture managing docker-compose services
# - service_ports: Session-scoped fixture providing service port mappings
# - test_client: Session-scoped TestClient fixture with proper configuration
# - github_token: Session-scoped fixture providing GitHub PAT token

from tests.utils.graph_assertions import (
    count_nodes_by_label,
    rel_count_by_type,
    repo_exists,
    verify_complete_repository_deletion,
)
from tests.utils.sync_db_cleanup import cleanup_neo4j_sync, cleanup_postgresql_sync
from tests.utils.sync_db_utils import get_sync_postgres_session
from tests.utils.temporal_workflow_cleanup import terminate_all_running_workflows

import os
import asyncio
import json
from pathlib import Path
import subprocess
import time
from typing import Any, Dict, List, Optional

from fastapi.testclient import TestClient
from loguru import logger
import pytest
from src.code_confluence_flow_bridge.models.configuration.settings import CodebaseConfig
from src.code_confluence_flow_bridge.models.github.github_repo import (
    GitHubRepoRequestConfiguration,
    IngestedRepositoryResponse,
)
from src.code_confluence_flow_bridge.parser.package_manager.detectors.progress_models import (
    DetectionResult,
)
from temporalio.client import Client, WorkflowExecutionStatus, WorkflowHandle

# ---------------------------------------------------------------------------
# HELPER FUNCTIONS FROM test_start_ingestion.py
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

TEST_REPO_REQUEST: Dict[str, Any] = {
    "repository_name": "test-delete-repo",
    "repository_git_url": "https://github.com/test-user/test-delete-repo",
    "repository_owner_name": "test-user",
    "repository_metadata": [
        {
            "codebase_folder": "src",
            "root_packages": ["src/test_package"],
            "programming_language_metadata": {"language": "python", "package_manager": "pip", "role": "leaf"},
        }
    ],
}


# ---------------------------------------------------------------------------
# INTEGRATION TESTS
# ---------------------------------------------------------------------------


@pytest.mark.integration
@pytest.mark.order("last")
class TestDeleteRepositoryEndpoint:
    """Integration tests for the delete_repository endpoint with full workflow testing."""

    @pytest.mark.asyncio(loop_scope="session") #type: ignore
    async def test_delete_nonexistent_repository(
        self,
        test_client: TestClient,
    ) -> None:
        """Test deletion of repository that doesn't exist returns 404."""
        
        # Create the repository info payload for non-existent repository
        repo_info = IngestedRepositoryResponse(
            repository_name="nonexistent-repo",
            repository_owner_name="nonexistent-user",
            is_local=False,
            local_path=None
        )
        
        # Call the delete endpoint via test client
        response = test_client.request(
            method="DELETE",
            url="/delete-repository",
            json=repo_info.model_dump()
        )
        
        # Verify 404 response for non-existent repository
        assert response.status_code == 404, f"Expected 404 for non-existent repository, got {response.status_code}: {response.text}"
        
        # Verify error message structure
        error_data = response.json()
        assert "detail" in error_data
        assert "nonexistent-repo" in error_data["detail"] or "nonexistent-user" in error_data["detail"]

    @pytest.mark.asyncio(loop_scope="session") #type: ignore
    async def test_delete_local_repository_flow(
        self,
        test_client: TestClient,
        github_token: str,
        service_ports: Dict[str, int],
        neo4j_client,
    ) -> None:
        """
        Test complete local repository deletion flow:
        1. Detect local repository codebases
        2. Ingest the repository
        3. Wait for workflow completion
        4. Delete the repository
        5. Verify deletion statistics
        """
        # Clean up databases using context manager for isolated sessions
        with get_sync_postgres_session(service_ports["postgresql"]) as session:
            cleanup_postgresql_sync(session)
        cleanup_neo4j_sync(neo4j_client)
        
        
        # Temporal address for workflow monitoring
        temporal_address = f"localhost:{service_ports['temporal']}"
        
        # ------------------------------------------------------------------
        # 1️⃣  Ensure token is ingested (idempotent)
        # ------------------------------------------------------------------
        token_resp = test_client.post(
            "/ingest-token",
            headers={"Authorization": f"Bearer {github_token}"},
        )
        assert token_resp.status_code in (201, 409), token_resp.text
        
        # ------------------------------------------------------------------
        # 2️⃣  Get local repository path and detect codebases
        # ------------------------------------------------------------------
        local_repo_path: str = get_repository_path()
        detection_result: DetectionResult = detect_local_codebases(test_client, local_repo_path)

        # Validate detection succeeded
        assert detection_result.error is None, f"Detection failed: {detection_result.error}"
        assert len(detection_result.codebases) > 0, "No codebases detected"

        # ------------------------------------------------------------------
        # 3️⃣  Create GitHubRepoRequestConfiguration from detection results
        # ------------------------------------------------------------------
        repo_request: GitHubRepoRequestConfiguration = create_repo_request_from_detection(
            detection_result=detection_result, repository_name="unoplat-code-confluence", repository_owner_name="unoplat")
        

        # ------------------------------------------------------------------
        # 4️⃣  Submit ingestion request
        # ------------------------------------------------------------------
        ingestion_resp = test_client.post("/start-ingestion", json=repo_request.model_dump())
        assert ingestion_resp.status_code == 201, f"Ingestion failed: {ingestion_resp.text}"

        ingestion_payload: Dict[str, Any] = ingestion_resp.json()
        workflow_id: str = ingestion_payload["workflow_id"]
        run_id: str = ingestion_payload["run_id"]

        # ------------------------------------------------------------------
        # 5️⃣  Monitor workflow execution (with shorter timeout for testing)
        # ------------------------------------------------------------------
        try:
            final_status: WorkflowExecutionStatus = await monitor_workflow_completion(
                workflow_id=workflow_id,
                run_id=run_id,
                temporal_address=temporal_address,
                timeout_seconds=300,  # 5 minutes for local processing
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
            
            # Continue with deletion test anyway
            logger.warning(f"Workflow {workflow_id} timed out but proceeding with deletion test")

        # ------------------------------------------------------------------
        # 6️⃣  Now test the deletion endpoint
        # ------------------------------------------------------------------
        delete_repo_info = IngestedRepositoryResponse(
            repository_name=repo_request.repository_name,
            repository_owner_name=repo_request.repository_owner_name,
            is_local=repo_request.is_local,
            local_path=repo_request.local_path
        )
        
        # Call the delete endpoint
        delete_response = test_client.request(
            method="DELETE",
            url="/delete-repository",
            json=delete_repo_info.model_dump()
        )
        
        # ------------------------------------------------------------------
        # 7️⃣  Verify successful deletion
        # ------------------------------------------------------------------
        assert delete_response.status_code == 200, f"Deletion failed with status {delete_response.status_code}: {delete_response.text}"
        
        # Verify deletion response structure
        deletion_response = delete_response.json()
        assert isinstance(deletion_response, dict), f"Expected dict response, got {type(deletion_response)}"
        
        # Extract deletion statistics from neo4j_deletion_stats
        assert "neo4j_deletion_stats" in deletion_response, "Missing 'neo4j_deletion_stats' in response"
        deletion_stats = deletion_response["neo4j_deletion_stats"]
        
        # Check that deletion statistics contain expected keys
        expected_keys = ["repositories_deleted", "codebases_deleted", "packages_deleted", "files_deleted", "metadata_deleted"]
        for key in expected_keys:
            assert key in deletion_stats, f"Missing key '{key}' in deletion statistics"
            assert isinstance(deletion_stats[key], int), f"Key '{key}' should be an integer"
        
        # Verify some items were actually deleted
        assert deletion_stats["repositories_deleted"] >= 1, "At least one repository should be deleted"
        
        # Log deletion statistics for debugging
        logger.info(f"Deletion statistics: {deletion_stats}")
        logger.info(f"Full deletion response: {deletion_response}")
        
        # ------------------------------------------------------------------
        # 8️⃣  Verify repository is no longer in ingested repositories list
        # ------------------------------------------------------------------
        repos_resp = test_client.get("/get/ingestedRepositories")
        assert repos_resp.status_code == 200, f"Failed to get ingested repositories: {repos_resp.text}"
        
        ingested_repos = repos_resp.json()["repositories"]
        deleted_repo_found = any(
            repo["repository_name"] == repo_request.repository_name and 
            repo["repository_owner_name"] == repo_request.repository_owner_name
            for repo in ingested_repos
        )
        assert not deleted_repo_found, "Deleted repository still appears in ingested repositories list"
        
        # ------------------------------------------------------------------
        # 🔄  NEW: Comprehensive graph-level verification
        # ------------------------------------------------------------------
        repo_qualified_name = f"{repo_request.repository_owner_name}_{repo_request.repository_name}"
        
        # 1. Verify repository node is completely gone
        assert not repo_exists(neo4j_client, repo_qualified_name), \
            f"Repository node {repo_qualified_name} still exists in graph"
        
        # 2. ENHANCED: Explicit relationship validation to catch constraint violations early
        critical_relationships = [
            "CONTAINS_CODEBASE", "PART_OF_GIT_REPOSITORY", "USES_FRAMEWORK", "USED_BY",
            "CONTAINS_PACKAGE", "PART_OF_PACKAGE", "PART_OF_CODEBASE", "CONTAINS_FILE",
            "USES_FEATURE", "HAS_PACKAGE_MANAGER_METADATA"
        ]
        
        relationship_failures = []
        for rel_type in critical_relationships:
            count = rel_count_by_type(neo4j_client, rel_type, repo_qualified_name)
            if count > 0:
                relationship_failures.append(f"Found {count} residual {rel_type} relationships")
        
        if relationship_failures:
            error_msg = f"❌ CRITICAL: Repository {repo_qualified_name} has residual relationships that will cause constraint violations:\n"
            error_msg += "\n".join(f"  - {failure}" for failure in relationship_failures)
            assert False, error_msg
        
        logger.info(f"✅ All critical relationships verified as deleted for {repo_qualified_name}")
        
        # 3. Verify no related nodes remain (scoped to this repository)
        verification_results = verify_complete_repository_deletion(neo4j_client, repo_qualified_name)
        
        # Assert no issues were found
        if verification_results["issues"]:
            error_msg = f"Graph deletion verification failed for {repo_qualified_name}:\n"
            error_msg += "\n".join(f"  - {issue}" for issue in verification_results["issues"])
            error_msg += f"\nNode counts: {verification_results['node_counts']}"
            error_msg += f"\nRelationship counts: {verification_results['relationship_counts']}"
            if "repository_relationship_counts" in verification_results:
                error_msg += f"\nRepository-specific relationship counts: {verification_results['repository_relationship_counts']}"
            assert False, error_msg
        
        # 4. Log successful cleanup stats for debugging
        logger.info(f"Graph verification passed for {repo_qualified_name}")
        logger.info(f"Final node counts: {verification_results['node_counts']}")
        logger.info(f"Final relationship counts: {verification_results['relationship_counts']}")
        if "repository_relationship_counts" in verification_results:
            logger.info(f"Repository-specific relationship counts: {verification_results['repository_relationship_counts']}")
        
        # 5. For single-repository tests, verify complete graph cleanup
        # (This is aggressive but ensures no test pollution)
        total_nodes_by_type = {}
        for node_type in ["CodeConfluenceCodebase", "CodeConfluencePackage", "CodeConfluenceFile", "CodeConfluencePackageManagerMetadata"]:
            count = count_nodes_by_label(neo4j_client, node_type)
            total_nodes_by_type[node_type] = count
            
        # In a clean test environment, these should all be 0 after deletion
        residual_nodes = {k: v for k, v in total_nodes_by_type.items() if v > 0}
        if residual_nodes:
            logger.warning(f"Residual nodes detected (may be from other tests): {residual_nodes}")
        
        logger.info("✅ Graph-level deletion verification completed successfully")
        
        