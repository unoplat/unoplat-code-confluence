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
    GitHubRepoRequestConfiguration,
    IngestedRepositoryResponse,
)
from temporalio.client import Client, WorkflowExecutionStatus, WorkflowHandle

from tests.utils.graph_assertions import (
    assert_deletion_stats_accuracy,
    assert_repository_completely_deleted,
    capture_repository_state_snapshot,
    count_nodes_by_label,
)
from tests.utils.sync_db_cleanup import cleanup_neo4j_sync, cleanup_postgresql_sync
from tests.utils.sync_db_utils import get_sync_postgres_session

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
            repository_owner_name="nonexistent-user"
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
    async def test_delete_remote_repository_flow(
        self,
        test_client: TestClient,
        github_token: str,
        service_ports: Dict[str, int],
        neo4j_client,
    ) -> None:
        """
        Test complete remote repository deletion flow:
        1. Ingest the repository (explicit metadata)
        2. Wait for workflow completion
        3. Delete the repository
        4. Verify deletion statistics

        This test validates the deletion workflow for remotely ingested repositories.
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
        # 2️⃣  Create ingestion request for remote repository with auto-detection
        # ------------------------------------------------------------------
        # Create request WITHOUT repository_metadata to trigger auto-detection
        repo_request = GitHubRepoRequestConfiguration(
            repository_name="unoplat-code-confluence",
            repository_git_url="https://github.com/unoplat/unoplat-code-confluence",
            repository_owner_name="unoplat",
            repository_metadata=None  # Triggers auto-detection
        )

        # ------------------------------------------------------------------
        # 3️⃣  Submit ingestion request (auto-detection happens internally)
        # ------------------------------------------------------------------
        ingestion_resp = test_client.post("/start-ingestion", json=repo_request.model_dump())
        assert ingestion_resp.status_code == 201, f"Ingestion failed: {ingestion_resp.text}"

        ingestion_payload: Dict[str, Any] = ingestion_resp.json()
        workflow_id: str = ingestion_payload["workflow_id"]
        run_id: str = ingestion_payload["run_id"]

        # ------------------------------------------------------------------
        # 4️⃣  Monitor workflow execution (with shorter timeout for testing)
        # ------------------------------------------------------------------
        try:
            final_status: WorkflowExecutionStatus = await monitor_workflow_completion(
                workflow_id=workflow_id,
                run_id=run_id,
                temporal_address=temporal_address,
                timeout_seconds=300,  # 5 minutes for remote repository processing
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
        # 5️⃣  ENHANCED: Capture pre-deletion state snapshot
        # ------------------------------------------------------------------
        repo_qualified_name = f"{repo_request.repository_owner_name}_{repo_request.repository_name}"
        
        # Capture comprehensive state before deletion to validate API statistics
        pre_deletion_snapshot = capture_repository_state_snapshot(neo4j_client, repo_qualified_name)
        
        # Log pre-deletion state for debugging
        logger.info(f"Pre-deletion state for {repo_qualified_name}:")
        logger.info(f"  Node counts: {pre_deletion_snapshot['node_counts']}")
        
        # Sanity check: Ensure we have content to delete
        files_count = pre_deletion_snapshot["node_counts"].get("CodeConfluenceFile", 0)
        assert files_count > 0, f"Sanity check failed: No files found after ingestion for {repo_qualified_name}"

        # ------------------------------------------------------------------
        # 6️⃣  Now test the deletion endpoint
        # ------------------------------------------------------------------
        delete_repo_info = IngestedRepositoryResponse(
            repository_name=repo_request.repository_name,
            repository_owner_name=repo_request.repository_owner_name
        )
        
        # Call the delete endpoint
        delete_response = test_client.request(
            method="DELETE",
            url="/delete-repository",
            json=delete_repo_info.model_dump()
        )

        # ------------------------------------------------------------------
        # 7️⃣  Verify successful deletion response
        # ------------------------------------------------------------------
        assert delete_response.status_code == 200, f"Deletion failed with status {delete_response.status_code}: {delete_response.text}"
        
        # Verify deletion response structure
        deletion_response = delete_response.json()
        assert isinstance(deletion_response, dict), f"Expected dict response, got {type(deletion_response)}"
        
        # Extract deletion statistics from neo4j_deletion_stats
        assert "neo4j_deletion_stats" in deletion_response, "Missing 'neo4j_deletion_stats' in response"
        deletion_stats = deletion_response["neo4j_deletion_stats"]
        
        # Check that deletion statistics contain expected keys
        expected_keys = [
            "repositories_deleted",
            "codebases_deleted",
            "files_deleted",
            "metadata_deleted",
        ]
        for key in expected_keys:
            assert key in deletion_stats, f"Missing key '{key}' in deletion statistics"
            assert isinstance(deletion_stats[key], int), f"Key '{key}' should be an integer"
        
        # Log deletion statistics for debugging
        logger.info(f"API deletion statistics: {deletion_stats}")
        logger.info(f"Full deletion response: {deletion_response}")

        # ------------------------------------------------------------------
        # 8️⃣  ENHANCED: Validate deletion stats against pre-snapshot
        # ------------------------------------------------------------------
        assert_deletion_stats_accuracy(deletion_stats, pre_deletion_snapshot)

        # ------------------------------------------------------------------
        # 9️⃣  Verify repository is no longer in ingested repositories list
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
        # 1️⃣0️⃣  ENHANCED: Comprehensive post-deletion verification
        # ------------------------------------------------------------------
        # Use the new comprehensive helper that replaces all the manual verification above
        assert_repository_completely_deleted(neo4j_client, repo_qualified_name)
        
        logger.info(f"✅ Enhanced deletion verification completed successfully for {repo_qualified_name}")
        
        # Optional: Log residual node counts for test pollution detection
        total_nodes_by_type = {}
        for node_type in [
            "CodeConfluenceCodebase",
            "CodeConfluenceFile",
            "CodeConfluencePackageManagerMetadata",
        ]:
            count = count_nodes_by_label(neo4j_client, node_type)
            total_nodes_by_type[node_type] = count
            
        residual_nodes = {k: v for k, v in total_nodes_by_type.items() if v > 0}
        if residual_nodes:
            logger.warning(f"Residual nodes detected (may be from other tests): {residual_nodes}")
        else:
            logger.info("✅ Complete graph cleanup verified - no residual nodes detected")
        
        
