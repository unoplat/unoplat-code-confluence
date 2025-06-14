"""
Integration test for /detect-codebases-sse endpoint using testcontainers.

This test module uses testcontainers-python DockerCompose to manage
the full docker-compose environment and test the SSE endpoint with real services.
"""

# Standard Library
import asyncio
import functools
import json
import os
import shutil
import socket
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Dict, List, Iterator

# Third Party
import docker
import pytest
import requests
from dotenv import load_dotenv
from loguru import logger
from testcontainers.compose import DockerCompose
from src.code_confluence_flow_bridge.main import app
from fastapi.testclient import TestClient
# Note: create_db_and_tables is called during app startup

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
COMPOSE_FILE = PROJECT_ROOT / "local-dependencies-only-docker-compose.yml"


# ──────────────────────────────────────────────────────────────────────────────
# CUSTOM DOCKER COMPOSE WITH CLEANUP
# ──────────────────────────────────────────────────────────────────────────────

class DockerComposeWithCleanup(DockerCompose):
    """Custom DockerCompose that ensures proper cleanup of volumes and directories."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._docker_client = docker.from_env()
    
    def stop(self, delete_volumes=True):
        """Stop compose with optional volume deletion control."""
        if delete_volumes:
            # Default behavior - volumes will be deleted by docker-compose down -v
            super().stop()
        else:
            # Custom stop without -v flag
            down_cmd = self.docker_compose_command() + ['down']
            subprocess.call(down_cmd, cwd=self.filepath)
    
    def cleanup_volumes(self):
        """Explicitly clean up named volumes from compose file."""
        # Actual volume names as they appear in Docker
        volume_names = [
            "postgresql_data",
            "elasticsearch_data", 
            "signoz-clickhouse",     # Note: actual name, not compose key
            "signoz-sqlite",         # Note: actual name, not compose key
            "signoz-zookeeper-1"     # Note: actual name, not compose key
        ]
        
        cleaned_count = 0
        for volume_name in volume_names:
            try:
                volume = self._docker_client.volumes.get(volume_name)
                volume.remove(force=True)
                logger.info(f"Removed volume: {volume_name}")
                cleaned_count += 1
            except docker.errors.NotFound:
                logger.debug(f"Volume {volume_name} not found (may already be removed)")
            except docker.errors.APIError as e:
                logger.warning(f"Could not remove volume {volume_name}: {e}")
        
        logger.info(f"Cleaned up {cleaned_count} volumes")
    
    def cleanup_neo4j_directories(self):
        """Clean up Neo4j host-mounted directories."""
        neo4j_base = Path.home() / "neo4j"
        neo4j_subdirs = ["data", "logs", "import", "plugins"]
        
        cleaned_count = 0
        for subdir in neo4j_subdirs:
            dir_path = neo4j_base / subdir
            if dir_path.exists():
                try:
                    shutil.rmtree(dir_path)
                    logger.info(f"Removed directory: {dir_path}")
                    cleaned_count += 1
                except Exception as e:
                    logger.warning(f"Could not remove directory {dir_path}: {e}")
        
        # Remove the base neo4j directory if empty
        if neo4j_base.exists() and not any(neo4j_base.iterdir()):
            try:
                neo4j_base.rmdir()
                logger.info(f"Removed empty directory: {neo4j_base}")
            except Exception as e:
                logger.debug(f"Could not remove {neo4j_base}: {e}")
        
        logger.info(f"Cleaned up {cleaned_count} Neo4j directories")


# ──────────────────────────────────────────────────────────────────────────────
# INTEGRATION TEST PLAN
# ──────────────────────────────────────────────────────────────────────────────

"""
TESTCONTAINERS INTEGRATION TEST PLAN FOR /detect-codebases-sse
===============================================================

1. INFRASTRUCTURE SETUP
   - Use DockerCompose from testcontainers to manage services
   - Start services from local-dependencies-only-docker-compose.yml
   - Services: PostgreSQL, Neo4j, Temporal, Elasticsearch, SignOz stack
   - Wait for all services to be healthy before tests

2. SERVICE HEALTH CHECKS
   - PostgreSQL: Check port 5432 is accessible
   - Neo4j: Check port 7687 is accessible
   - Temporal: Check port 7233 is accessible
   - Elasticsearch: Check port 9200 is accessible
   - Use wait_for_logs or port checks to ensure readiness

3. FASTAPI APPLICATION SETUP
   - Set environment variables to point to container services
   - Import and start FastAPI app after services are ready
   - Wait for Temporal worker to initialize
   - Ensure all activities are registered

4. TOKEN INGESTION FLOW
   - POST /ingest-token with test GitHub token
   - Verify token is stored in PostgreSQL
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


# ──────────────────────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ──────────────────────────────────────────────────────────────────────────────

def _wait_for_port(host: str, port: int, timeout: int = 60) -> None:
    """Wait for a port to become available."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.create_connection((host, port), timeout=1):
                return
        except (socket.error, OSError):
            time.sleep(1)
    raise TimeoutError(f"Port {port} on {host} did not become available within {timeout} seconds")


def _wait_for_http(url: str, timeout: int = 60) -> None:
    """Wait for an HTTP endpoint to respond."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code < 500:  # Accept any non-server-error response
                return
        except requests.exceptions.RequestException:
            time.sleep(2)
    raise TimeoutError(f"HTTP endpoint {url} did not become available within {timeout} seconds")


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


# ──────────────────────────────────────────────────────────────────────────────
# FIXTURES
# ──────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def docker_compose():
    """Start docker-compose services with proper cleanup including volumes."""
    # Verify compose file exists
    if not COMPOSE_FILE.exists():
        raise FileNotFoundError(f"Docker compose file not found: {COMPOSE_FILE}")
    
    logger.info(f"Starting docker-compose from {COMPOSE_FILE}")
    
    # Use our custom DockerCompose class
    compose = DockerComposeWithCleanup(
        filepath=str(COMPOSE_FILE.parent),
        compose_file_name=COMPOSE_FILE.name,
        pull=False,  # Don't pull images, use local ones
    )
    
    try:
        # Start the services
        with compose:
            logger.info("Docker compose started, waiting for services to be ready...")
            
            # Wait for services using port and HTTP health checks
            try:
                # PostgreSQL - wait for port to be available
                logger.info("Waiting for PostgreSQL...")
                pg_port = compose.get_service_port("postgresql", 5432)
                _wait_for_port("localhost", pg_port, timeout=60)
                logger.info("PostgreSQL is ready")
                
                # Neo4j - wait for HTTP interface
                logger.info("Waiting for Neo4j...")
                neo4j_http_port = compose.get_service_port("neo4j", 7474)
                _wait_for_http(f"http://localhost:{neo4j_http_port}", timeout=120)
                logger.info("Neo4j is ready")
                
                # Temporal - wait for port
                logger.info("Waiting for Temporal...")
                temporal_port = compose.get_service_port("temporal", 7233)
                _wait_for_port("localhost", temporal_port, timeout=120)
                logger.info("Temporal is ready")
                
                # Elasticsearch - wait for HTTP interface
                logger.info("Waiting for Elasticsearch...")
                es_port = compose.get_service_port("elasticsearch", 9200)
                _wait_for_http(f"http://localhost:{es_port}", timeout=120)
                logger.info("Elasticsearch is ready")
                
            except Exception as e:
                logger.error(f"Service health check failed: {e}")
                raise
            
            # Additional wait for services to stabilize
            logger.info("Services started, waiting for stabilization...")
            time.sleep(15)
            
            yield compose
    finally:
        # The 'with' context has already called stop() which removes volumes due to -v flag
        # But we'll ensure complete cleanup
        logger.info("Ensuring complete post-test cleanup...")
        
        # Double-check volume cleanup (in case some were missed)
        compose.cleanup_volumes()
        
        # Clean up Neo4j host directories
        compose.cleanup_neo4j_directories()
        
        # Additional cleanup using docker client for any dangling resources
        client = docker.from_env()
        
        # Prune any remaining dangling volumes
        try:
            pruned = client.volumes.prune()
            if pruned['VolumesDeleted']:
                logger.info(f"Pruned {len(pruned['VolumesDeleted'])} additional dangling volumes")
        except Exception as e:
            logger.warning(f"Error pruning volumes: {e}")
        
        logger.info("Docker compose stopped and all resources cleaned up")


@pytest.fixture(scope="session")
def service_ports(docker_compose: DockerCompose) -> Dict[str, int]:
    """Get the exposed ports for each service."""
    return {
        "postgresql": docker_compose.get_service_port("postgresql", 5432),
        "neo4j": docker_compose.get_service_port("neo4j", 7687),
        "temporal": docker_compose.get_service_port("temporal", 7233),
        "elasticsearch": docker_compose.get_service_port("elasticsearch", 9200),
    }


@pytest.fixture(scope="session")
def test_client(service_ports: Dict[str, int]) -> Iterator[TestClient]:
    """Create test client with proper configuration using FastAPI's TestClient."""
    # Set environment variables for the app
    os.environ.update({
        "DB_HOST": "localhost",
        "DB_PORT": str(service_ports["postgresql"]),
        "DB_USER": "postgres",
        "DB_PASSWORD": "postgres",
        "DB_NAME": "code_confluence",
        "NEO4J_HOST": "localhost",
        "NEO4J_PORT": str(service_ports["neo4j"]),
        "NEO4J_USERNAME": "neo4j",
        "NEO4J_PASSWORD": "password",
        "TEMPORAL_SERVER_ADDRESS": f"localhost:{service_ports['temporal']}",
    })

    # Wait briefly for app and Temporal worker initialization
    time.sleep(15)
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="session")
def github_token() -> str:
    """
    Fixture that provides GitHub PAT token.
    First tries to read from environment variable, then falls back to .env.testing file
    """
    # Try getting from environment first
    token = os.getenv('GITHUB_PAT_TOKEN')
    
    if not token:
        # If not in env, try loading from .env.testing
        env_file = Path(__file__).parent.parent.parent.parent / '.env.testing'
        if env_file.exists():
            load_dotenv(env_file)
            token = os.getenv('GITHUB_PAT_TOKEN')
    
    if not token:
        pytest.fail("GITHUB_PAT_TOKEN not found in environment or .env.testing file")
        
    return token


# ──────────────────────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ──────────────────────────────────────────────────────────────────────────────

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
    for chunk in response.iter_text():
        chunks.append(chunk)
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
            
            logger.info(f"Received {len(events)} SSE events")
            
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
            logger.info(f"Progress states seen: {states_seen}")
            
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
            
            logger.info(f"✓ Result event received with {len(result_data['codebases'])} codebases")
            
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
            logger.info(f"  - {result['url']}: {result['codebases_count']} codebases in {result['duration']:.2f}s")
        
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



