"""
Centralized pytest fixtures for the code confluence flow bridge tests.

This conftest.py file provides shared fixtures that are automatically
discovered by pytest and made available to all test files.
"""

# Standard Library
import os
from pathlib import Path
import socket
import subprocess
import time
from typing import Dict, Iterator
from uuid import uuid4

# from tests.utils.db_cleanup import cleanup_postgresql_data
# Local
from code_confluence_flow_bridge.main import app

# Third Party
import docker
from docker.errors import APIError
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from loguru import logger
import pytest
import requests
from testcontainers.compose import DockerCompose
from unoplat_code_confluence_commons.schema_readiness import RELEASE_SCHEMA_REVISION

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
COMPOSE_FILE = PROJECT_ROOT / "docker-compose-dependencies-test.yml"
QUERY_ENGINE_ROOT = PROJECT_ROOT.parents[1] / "unoplat-code-confluence-query-engine"
# Every Docker resource belongs to this run, so cleanup cannot reach a dev stack.
COMPOSE_PROJECT = f"unoplat-flow-bridge-test-{uuid4().hex[:12]}"


# ──────────────────────────────────────────────────────────────────────────────
# CUSTOM DOCKER COMPOSE WITH CLEANUP
# ──────────────────────────────────────────────────────────────────────────────


class DockerComposeWithCleanup(DockerCompose):
    """Custom DockerCompose that ensures proper cleanup of volumes and directories."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._compose_context = kwargs.get("context")
        if self._compose_context is None and args:
            self._compose_context = args[0]
        self._docker_client = docker.from_env()

    def stop(self, down: bool = True):
        """Stop compose with optional volume deletion control."""
        if down:
            super().stop()
        else:
            down_cmd = self.docker_compose_command() + ["down"]
            context_dir = self._compose_context
            subprocess.call(down_cmd, cwd=context_dir)

    def cleanup_volumes(self):
        """Remove only volumes labelled for this run's compose project."""
        volumes = self._docker_client.volumes.list(
            filters={"label": f"com.docker.compose.project={COMPOSE_PROJECT}"}
        )

        cleaned_count = 0
        for volume in volumes:
            try:
                volume.remove(force=True)
                logger.info("Removed volume: {}", volume.name)
                cleaned_count += 1
            except APIError as e:
                logger.warning("Could not remove volume {}: {}", volume.name, e)

        logger.info("Cleaned up {} volumes", cleaned_count)


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
    raise TimeoutError(
        f"Port {port} on {host} did not become available within {timeout} seconds"
    )


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
    raise TimeoutError(
        f"HTTP endpoint {url} did not become available within {timeout} seconds"
    )


def _get_service_port(compose: DockerCompose, service: str, port: int) -> int:
    service_port = compose.get_service_port(service, port)
    if service_port is None:
        raise RuntimeError(f"Service {service} port {port} not available")
    return int(service_port)


# ──────────────────────────────────────────────────────────────────────────────
# FIXTURES
# ──────────────────────────────────────────────────────────────────────────────


@pytest.fixture(scope="session")
def docker_compose():
    """Start docker-compose services with proper cleanup including volumes."""
    # Set Docker client timeouts to prevent hanging
    os.environ["DOCKER_CLIENT_TIMEOUT"] = "180"
    os.environ["COMPOSE_HTTP_TIMEOUT"] = "180"
    os.environ["COMPOSE_PROJECT_NAME"] = COMPOSE_PROJECT

    # Verify compose file exists
    if not COMPOSE_FILE.exists():
        raise FileNotFoundError(f"Docker compose file not found: {COMPOSE_FILE}")

    logger.info("Starting docker-compose from {}", COMPOSE_FILE)

    # Use our custom DockerCompose class
    compose = DockerComposeWithCleanup(
        context=str(COMPOSE_FILE.parent),
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
                pg_port = _get_service_port(compose, "postgresql", 5432)
                _wait_for_port("localhost", pg_port, timeout=60)
                logger.info("PostgreSQL is ready")

                # Temporal - wait for port
                logger.info("Waiting for Temporal...")
                temporal_port = _get_service_port(compose, "temporal", 7233)
                _wait_for_port("localhost", temporal_port, timeout=120)
                logger.info("Temporal is ready")

                # Elasticsearch - wait for HTTP interface
                logger.info("Waiting for Elasticsearch...")
                es_port = _get_service_port(compose, "elasticsearch", 9200)
                _wait_for_http(f"http://localhost:{es_port}", timeout=120)
                logger.info("Elasticsearch is ready")

            except Exception as e:
                logger.error("Service health check failed: {}", e)
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

        logger.info("Docker compose stopped and all resources cleaned up")


# ──────────────────────────────────────────────────────────────────────────────
# TEST DATABASE HELPER FUNCTIONS
# ──────────────────────────────────────────────────────────────────────────────


@pytest.fixture(scope="session")
def service_ports(docker_compose: DockerCompose) -> Dict[str, int]:
    """Get the exposed ports and migrate this run's disposable database.

    The explicit drain attestation is true only because the fixture owns this new,
    empty database. It must never become a default for shared databases.
    """
    ports = {
        "postgresql": _get_service_port(docker_compose, "postgresql", 5432),
        "temporal": _get_service_port(docker_compose, "temporal", 7233),
        "elasticsearch": _get_service_port(docker_compose, "elasticsearch", 9200),
    }
    subprocess.run(
        [
            "uv",
            "run",
            "--locked",
            "--group",
            "migrations",
            "alembic",
            "-x",
            "drained=true",
            "-x",
            "discard_legacy_artifacts=true",
            "upgrade",
            RELEASE_SCHEMA_REVISION,
        ],
        cwd=QUERY_ENGINE_ROOT,
        env={
            **os.environ,
            "ALEMBIC_DATABASE_URL": (
                f"postgresql://postgres:postgres@localhost:{ports['postgresql']}"
                "/code_confluence"
            ),
            "ALEMBIC_SCHEMA": "public",
        },
        check=True,
    )
    return ports


@pytest.fixture(scope="session")
def test_client(service_ports: Dict[str, int]) -> Iterator[TestClient]:
    """Create test client with proper configuration using FastAPI's TestClient."""
    # Set environment variables for the app
    project_root = Path(__file__).parent.parent
    framework_definitions_path = project_root / "framework-definitions"
    os.environ.update(
        {
            "DB_HOST": "localhost",
            "DB_PORT": str(service_ports["postgresql"]),
            "DB_USER": "postgres",
            "DB_PASSWORD": "postgres",
            "DB_NAME": "code_confluence",
            "TEMPORAL_SERVER_ADDRESS": f"localhost:{service_ports['temporal']}",
            "FRAMEWORK_DEFINITIONS_PATH": str(framework_definitions_path),
        }
    )

    # Wait briefly for app and Temporal worker initialization
    with TestClient(app) as client:
        yield client
        # Allow time for async cleanup of streaming responses
        time.sleep(0.5)


@pytest.fixture(scope="session")
def github_token() -> str:
    """
    Fixture that provides GitHub PAT token.
    First tries to read from environment variable, then falls back to .env.testing file
    """
    # Try getting from environment first
    token = os.getenv("GITHUB_PAT_TOKEN")

    if not token:
        # If not in env, try loading from .env.testing
        env_file = Path(__file__).parent / ".env.testing"
        if env_file.exists():
            load_dotenv(env_file)
            token = os.getenv("GITHUB_PAT_TOKEN")

    if not token:
        pytest.fail("GITHUB_PAT_TOKEN not found in environment or .env.testing file")

    return token
