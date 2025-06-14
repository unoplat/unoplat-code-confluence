import asyncio
import pytest
import time
from typing import Dict, Any

from fastapi.testclient import TestClient

# Re-use the docker-compose stack, service ports and auth helpers that are already
# available in the SSE test module. This avoids duplicating heavy-weight fixtures
# and keeps startup / teardown logic in one place.
# Import the full fixture chain so that pytest can discover all dependencies
from tests.parser.package_manager.detectors.test_detect_codebases_sse import (  # noqa: WPS433
    docker_compose,  # noqa: F401 – re-exported for fixture discovery
    service_ports,  # noqa: F401 – re-exported for fixture discovery
    test_client,  # pylint: disable=redefined-outer-name
    github_token,  # pylint: disable=redefined-outer-name
)


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
            "programming_language_metadata": {
                "language": "python",
                "package_manager": "uv",
                "role": "leaf"
            }
        }
    ]
}


# ---------------------------------------------------------------------------
# INTEGRATION TESTS
# ---------------------------------------------------------------------------

@pytest.mark.integration  # type: ignore[var-annotated]
class TestStartIngestionEndpoint:
    """Integration tests for the POST /start-ingestion endpoint."""

    @pytest.mark.asyncio  # type: ignore[var-annotated]
    async def test_start_ingestion_flow(
        self,
        test_client: TestClient,
        github_token: str,
    ) -> None:
        """Full happy-path flow: ingest token -> start ingestion -> verify response."""

        # ------------------------------------------------------------------
        # 1️⃣  make sure the PAT is stored (idempotent)
        # ------------------------------------------------------------------
        token_resp = test_client.post(
            "/ingest-token",
            headers={"Authorization": f"Bearer {github_token}"},
        )
        assert token_resp.status_code in (201, 409), token_resp.text
        
        # Wait for token ingestion to complete and services to stabilize
        await asyncio.sleep(30)
        
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