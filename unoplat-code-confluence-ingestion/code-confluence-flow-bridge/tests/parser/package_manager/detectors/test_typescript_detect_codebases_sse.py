"""
Integration test for TypeScript codebase detection via /detect-codebases-sse endpoint.

This test module validates TypeScript-specific codebase detection using the SSE endpoint.
It uses the same test infrastructure as the Python SSE tests (testcontainers-python DockerCompose).

Fixtures are auto-discovered from tests/conftest.py which provides:
- docker_compose: Session-scoped fixture that manages docker-compose services
- service_ports: Session-scoped fixture providing service port mappings
- test_client: Session-scoped TestClient fixture with proper configuration
- github_token: Session-scoped fixture providing GitHub PAT token

INTEGRATION TEST FLOW:

1. DOCKER SERVICES STARTUP (shared with Python tests)
   - PostgreSQL, Neo4j, Temporal, Elasticsearch
   - Health checks and stabilization period

2. GITHUB TOKEN MANAGEMENT
   - POST /ingest-token with Bearer token
   - Verify token storage

3. TYPESCRIPT SSE ENDPOINT TESTING
   - GET /detect-codebases-sse (multi-language detection)
   - Stream and validate SSE events
   - Verify TypeScript-specific detection results

TEST REPOSITORY:
   - Uses unoplat/unoplat-code-confluence (contains both Python and TypeScript)
   - Expected to detect: unoplat-code-confluence-frontend/ with yarn package manager
"""

# Standard Library
import json
from typing import Dict, List

# Third Party
import pytest
from fastapi.testclient import TestClient
from loguru import logger


# ──────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ──────────────────────────────────────────────────────────────────────────────

# Repository containing both Python and TypeScript codebases
TEST_REPO_URL = "https://github.com/unoplat/unoplat-code-confluence"

# Expected TypeScript package managers from rules.yaml
TYPESCRIPT_PACKAGE_MANAGERS = {"npm", "yarn", "pnpm", "bun"}


# ──────────────────────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ──────────────────────────────────────────────────────────────────────────────

def parse_sse_events(response_text: str) -> List[Dict]:
    """Parse SSE response into structured events."""
    events = []
    current_event = {}

    for line in response_text.strip().split('\n'):
        line = line.rstrip('\r')  # Handle CRLF line endings
        if line.startswith('id:'):
            current_event['id'] = line[3:].strip()
        elif line.startswith('event:'):
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
        pass
    return ''.join(chunks)


# ──────────────────────────────────────────────────────────────────────────────
# INTEGRATION TESTS
# ──────────────────────────────────────────────────────────────────────────────

@pytest.mark.integration
class TestTypescriptDetectCodebasesSSEIntegration:
    """Integration tests for TypeScript SSE endpoint with real services via DockerCompose."""

    def test_typescript_sse_detection(
        self,
        test_client: TestClient,
        github_token: str
    ):
        """Test TypeScript codebase detection via SSE endpoint for unoplat-code-confluence."""
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

        # Step 3: Test TypeScript SSE endpoint
        logger.info("Step 3: Testing TypeScript SSE endpoint with real detection")

        with test_client.stream(
            "GET",
            "/detect-codebases-sse",
            params={"git_url": TEST_REPO_URL}
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

            for event in progress_events:
                assert 'state' in event['data']
                assert 'message' in event['data']
                assert 'repository_url' in event['data']
                assert 'language' in event['data']
                assert event['data']['repository_url'] == TEST_REPO_URL

            languages_seen = {event['data']['language'] for event in progress_events}
            logger.info("Progress languages seen: {}", languages_seen)
            assert 'typescript' in languages_seen

            logger.info("✓ Progress events validated")

            # Check result event
            result_events = [e for e in events if e.get('event') == 'result']
            assert len(result_events) == 1, f"Expected 1 result event, got {len(result_events)}"

            result_data = result_events[0]['data']
            assert 'repository_url' in result_data
            assert result_data['repository_url'] == TEST_REPO_URL
            assert 'codebases' in result_data
            assert isinstance(result_data['codebases'], list)
            assert result_data['error'] is None

            codebases = result_data['codebases']
            ts_codebases = [
                cb for cb in codebases
                if cb.get('programming_language_metadata', {}).get('language') == 'typescript'
            ]
            assert ts_codebases, "No TypeScript codebases detected"

            logger.info(
                "✓ Result event received with {} TypeScript codebases",
                len(ts_codebases)
            )

            for codebase in ts_codebases:
                metadata = codebase['programming_language_metadata']
                package_manager = metadata.get('package_manager')
                assert package_manager in TYPESCRIPT_PACKAGE_MANAGERS, (
                    f"Expected TypeScript package manager, got {package_manager}"
                )
                logger.info(
                    "  - Codebase: {} | Package Manager: {}",
                    codebase.get('codebase_folder', 'unknown'),
                    package_manager,
                )

            frontend_codebases = [
                cb for cb in ts_codebases
                if 'frontend' in cb.get('codebase_folder', '').lower()
            ]
            assert frontend_codebases, "Expected to detect unoplat-code-confluence-frontend"

            frontend_pm = frontend_codebases[0]['programming_language_metadata'].get('package_manager')
            assert frontend_pm == 'yarn', (
                f"Expected frontend to use yarn, got {frontend_pm}"
            )

            logger.info("✓ TypeScript codebase validation complete")

            # Check done event
            done_events = [e for e in events if e.get('event') == 'done']
            assert len(done_events) == 1
            assert done_events[0]['data'] == {'status': 'complete'}
            logger.info("✓ Done event received")
