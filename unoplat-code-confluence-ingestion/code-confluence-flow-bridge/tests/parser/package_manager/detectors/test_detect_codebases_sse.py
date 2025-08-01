"""
Integration test for /detect-codebases-sse endpoint using testcontainers.

This test module uses testcontainers-python DockerCompose to manage
the full docker-compose environment and test the SSE endpoint with real services.

Fixtures are auto-discovered from tests/conftest.py which provides:
- docker_compose: Session-scoped fixture that manages docker-compose services
- service_ports: Session-scoped fixture providing service port mappings
- test_client: Session-scoped TestClient fixture with proper configuration
- github_token: Session-scoped fixture providing GitHub PAT token

INTEGRATION TEST FLOW:

1. DOCKER SERVICES STARTUP
   - PostgreSQL on random port (health check via port connection)
   - Neo4j on random port (health check via HTTP)
   - Temporal on random port (health check via port connection) 
   - Elasticsearch on random port (health check via HTTP)
   - Custom DockerComposeWithCleanup ensures complete cleanup

2. SERVICE VALIDATION
   - Each service has specific health checks with timeouts
   - Additional 15-second stabilization period after all services ready
   - Environment variables automatically configured for test client

3. GITHUB TOKEN MANAGEMENT
   - POST /ingest-token with Bearer token (accepts 201/409 responses)
   - Verifies token storage and encryption
   - Sets isTokenSubmitted flag to true

4. FLAG VALIDATION
   - GET /flags/isTokenSubmitted endpoint
   - Check isTokenSubmitted flag is set to true

5. SSE ENDPOINT TESTING
   - GET /detect-codebases-sse with sample repository URL
   - Stream and validate SSE events:
     * Connection event
     * Progress events (INITIALIZING, CLONING, ANALYZING, COMPLETE)
     * Result event with codebase data
     * Done event
   - Verify correct SSE headers and format

6. CLEANUP
   - DockerCompose automatically handles container cleanup with enhanced volume removal
   - Named volumes are explicitly cleaned up: postgresql_data, elasticsearch_data, signoz-*
   - Neo4j host-mounted directories are removed: ~/neo4j/{data,logs,import,plugins}
   - Additional dangling volume pruning for complete cleanup
   - Networks are cleaned up
"""

# Standard Library
import functools
import json
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List
from pathlib import Path

# Third Party
import docker
import pytest
from fastapi.testclient import TestClient
from loguru import logger

# Note: Fixtures are now auto-discovered from tests/conftest.py


# ──────────────────────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ──────────────────────────────────────────────────────────────────────────────

def verify_cleanup():
    """Verify that all expected volumes and directories were cleaned up."""
    client = docker.from_env()
    
    # Check named volumes
    expected_gone_volumes = [
        "postgresql_data",
        "elasticsearch_data", 
        "signoz-clickhouse",
        "signoz-sqlite",
        "signoz-zookeeper-1"
    ]
    
    existing_volumes = []
    for volume_name in expected_gone_volumes:
        try:
            client.volumes.get(volume_name)
            existing_volumes.append(volume_name)
        except docker.errors.NotFound:
            pass  # Good, volume was cleaned up
    
    # Check Neo4j directories
    neo4j_base = Path.home() / "neo4j"
    existing_dirs = []
    for subdir in ["data", "logs", "import", "plugins"]:
        dir_path = neo4j_base / subdir
        if dir_path.exists():
            existing_dirs.append(str(dir_path))
    
    return existing_volumes, existing_dirs


def parse_sse_events(response_text: str) -> List[Dict]:
    """Parse SSE response into structured events."""
    events = []
    current_event = {}
    
    for line in response_text.strip().split('\n'):
        if line.startswith('event:'):
            current_event['event'] = line[6:].strip()
        elif line.startswith('data:'):
            data_str = line[5:].strip()
            try:
                current_event['data'] = json.loads(data_str)
            except json.JSONDecodeError:
                current_event['data'] = data_str
        elif line.startswith(':'):
            # Comment line
            current_event['comment'] = line[1:].strip()
        elif line == '' and current_event:
            # Empty line signals end of event
            events.append(current_event)
            current_event = {}
    
    # Don't forget the last event if no trailing empty line
    if current_event:
        events.append(current_event)
    
    return events


def stream_sse_response(response) -> str:
    """Collect SSE stream into string."""
    chunks = []
    try:
        for chunk in response.iter_text():
            chunks.append(chunk)
    finally:
        # Ensure the response iterator is fully consumed
        # This helps with cleanup of the underlying stream
        pass
    return ''.join(chunks)


def make_sse_request(test_client: TestClient, url: str) -> Dict:
    """Make an SSE request and return summary."""
    with test_client.stream(
        "GET",
        "/detect-codebases-sse",
        params={"git_url": url}
    ) as response:
        assert response.status_code == 200
        
        sse_content = stream_sse_response(response)
        events = parse_sse_events(sse_content)
        
        # Verify each request gets proper events
        assert any(e.get('event') == 'connected' for e in events)
        assert any(e.get('event') == 'progress' for e in events)
        assert any(e.get('event') == 'done' for e in events)
        
        # Get result
        result_events = [e for e in events if e.get('event') == 'result']
        if result_events:
            result_data = result_events[0]['data']
            assert result_data['repository_url'] == url
            return {
                "url": url,
                "codebases_count": len(result_data.get('codebases', [])),
                "duration": result_data.get('duration_seconds', 0)
            }
        
        return {"url": url, "codebases_count": 0, "duration": 0}


# ──────────────────────────────────────────────────────────────────────────────
# INTEGRATION TESTS
# ──────────────────────────────────────────────────────────────────────────────

@pytest.mark.integration
class TestDetectCodebasesSSEIntegration:
    """Integration tests for SSE endpoint with real services via DockerCompose."""
    
    def test_full_sse_flow_with_token_ingestion(
        self,
        test_client: TestClient,
        github_token: str
    ):
        """Test complete SSE flow including token ingestion with real services."""
        # Step 1: Ingest token
        logger.info("Step 1: Ingesting GitHub token")
        response = test_client.post(
            "/ingest-token",
            headers={"Authorization": f"Bearer {github_token}"}
        )
        # Accept both 201 (new token) and 409 (token already exists)
        assert response.status_code in [201, 409]
        if response.status_code == 201:
            assert response.json()["message"] == "Token ingested successfully."
        else:  # 409
            assert response.json()["detail"] == "Token already ingested. Use update-token to update it."
        
        # Step 2: Verify token flag
        logger.info("Step 2: Verifying token flag")
        response = test_client.get("/flags/isTokenSubmitted")
        assert response.status_code == 200
        assert response.json()["status"] is True
        
        # Step 3: Test SSE endpoint
        logger.info("Step 3: Testing SSE endpoint with real detection")
        test_repo_url = "https://github.com/unoplat/unoplat-code-confluence"
        
        with test_client.stream(
            "GET",
            "/detect-codebases-sse",
            params={"git_url": test_repo_url}
        ) as response:
            assert response.status_code == 200
            assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
            assert response.headers["cache-control"] == "no-cache"
            assert response.headers["connection"] == "keep-alive"
            assert response.headers.get("x-accel-buffering") == "no"
            
            # Collect SSE events
            sse_content = stream_sse_response(response)
            events = parse_sse_events(sse_content)
            
            logger.info("Received {} SSE events", len(events))
            
            # Validate event sequence
            assert len(events) >= 4, f"Expected at least 4 events, got {len(events)}"
            
            # Check connected event
            connected_events = [e for e in events if e.get('event') == 'connected']
            assert len(connected_events) == 1
            assert connected_events[0]['data'] == {'status': 'connected'}
            logger.info("✓ Connected event received")
            
            # Check progress events
            progress_events = [e for e in events if e.get('event') == 'progress']
            assert len(progress_events) > 0, "No progress events received"
            
            # Verify we see expected states
            states_seen = {e['data']['state'] for e in progress_events}
            logger.info("Progress states seen: {}", states_seen)
            
            # Should see at least some of these states
            expected_states = {'initializing', 'cloning', 'analyzing', 'complete'}
            assert len(states_seen.intersection(expected_states)) > 0
            
            # All progress events should have required fields
            for event in progress_events:
                assert 'state' in event['data']
                assert 'message' in event['data']
                assert 'repository_url' in event['data']
                assert event['data']['repository_url'] == test_repo_url
            
            logger.info("✓ Progress events validated")
            
            # Check result event
            result_events = [e for e in events if e.get('event') == 'result']
            assert len(result_events) == 1, f"Expected 1 result event, got {len(result_events)}"
            
            result_data = result_events[0]['data']
            assert 'repository_url' in result_data
            assert result_data['repository_url'] == test_repo_url
            assert 'codebases' in result_data
            assert isinstance(result_data['codebases'], list)
            assert 'duration_seconds' in result_data
            assert result_data['error'] is None
            
            logger.info("✓ Result event received with {} codebases", len(result_data['codebases']))
            
            # Check done event
            done_events = [e for e in events if e.get('event') == 'done']
            assert len(done_events) == 1
            assert done_events[0]['data'] == {'status': 'complete'}
            logger.info("✓ Done event received")
    
    def test_sse_with_invalid_git_url(
        self,
        test_client: TestClient,
        github_token: str
    ):
        """Test SSE endpoint with invalid repository URL."""
        # First ingest token (accept both new token and existing token)
        response = test_client.post(
            "/ingest-token",
            headers={"Authorization": f"Bearer {github_token}"}
        )
        assert response.status_code in [201, 409]
        
        logger.info("Testing SSE endpoint with invalid repository URL")
        
        with test_client.stream(
            "GET",
            "/detect-codebases-sse",
            params={"git_url": "https://github.com/invalid-user-12345/invalid-repo-67890"}
        ) as response:
            assert response.status_code == 200  # SSE still returns 200
            
            sse_content = stream_sse_response(response)
            events = parse_sse_events(sse_content)
            
            # Should receive error in SSE stream
            error_events = [e for e in events if e.get('event') == 'error']
            assert len(error_events) > 0 or any(
                'error' in e.get('data', {}) 
                for e in events if e.get('event') == 'result'
            )
            logger.info("✓ Error properly handled for invalid repository")
    
    def test_concurrent_sse_requests(
        self,
        test_client: TestClient,
        github_token: str
    ):
        """Test multiple concurrent SSE requests."""
        # Ingest token first (accept both new token and existing token)
        response = test_client.post(
            "/ingest-token",
            headers={"Authorization": f"Bearer {github_token}"}
        )
        assert response.status_code in [201, 409]
        
        logger.info("Testing concurrent SSE requests")
        
        # Different repository URLs for concurrent requests
        urls = [
            "https://github.com/psf/requests",
            "https://github.com/encode/httpx",
            "https://github.com/pallets/flask"
        ]
        
        # Create partial function with test_client bound
        make_request_func = functools.partial(make_sse_request, test_client)
        
        # Run requests concurrently using ThreadPoolExecutor since TestClient is sync
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(make_request_func, url) for url in urls]
            results = [f.result() for f in futures]
        
        logger.info("Concurrent request results:")
        for result in results:
            logger.info("  - {}: {} codebases in {:.2f}s", result['url'], result['codebases_count'], result['duration'])
        
        # Verify all requests completed
        assert len(results) == len(urls)
        logger.info("✓ All concurrent requests completed successfully")
    
    def test_sse_missing_git_url_parameter(self, test_client: TestClient):
        """Test SSE endpoint with missing git_url parameter."""
        logger.info("Testing SSE endpoint with missing git_url parameter")
        
        response = test_client.get("/detect-codebases-sse")
        assert response.status_code == 422  # Validation error
        assert "git_url" in response.text
        logger.info("✓ Correctly rejected request without git_url parameter")