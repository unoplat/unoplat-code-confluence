"""
Centralized pytest fixtures for the code confluence query engine tests.

This conftest.py file provides shared fixtures that are automatically
discovered by pytest and made available to all test files.
"""

import os
from pathlib import Path
import shutil
import socket
import subprocess
import time
from typing import Dict, Iterator

import docker
from fastapi.testclient import TestClient
from loguru import logger
import pytest
import pytest_asyncio
import requests
from testcontainers.compose import DockerCompose

from tests.utils.sync_db_utils import create_test_tables
from unoplat_code_confluence_query_engine.config.settings import EnvironmentSettings
from unoplat_code_confluence_query_engine.db.postgres.db import (
    dispose_db_connections,
    init_db_connections,
)
from unoplat_code_confluence_query_engine.main import app

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
COMPOSE_FILE = PROJECT_ROOT / "local-dependencies-docker-compose.yml"


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
        # Volume names as they appear in Docker for the query-engine compose
        volume_names = [
            "postgresql_data",
            "elasticsearch_data"
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
                logger.info(f"Removed empty neo4j base directory: {neo4j_base}")
            except Exception as e:
                logger.warning(f"Could not remove neo4j base directory: {e}")


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


# ──────────────────────────────────────────────────────────────────────────────
# FIXTURES
# ──────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def docker_compose():
    """Start docker-compose services with proper cleanup including volumes."""
    # Set Docker client timeouts to prevent hanging
    os.environ["DOCKER_CLIENT_TIMEOUT"] = "180"
    os.environ["COMPOSE_HTTP_TIMEOUT"] = "180"

    # Verify compose file exists
    if not COMPOSE_FILE.exists():
        raise FileNotFoundError(f"Docker compose file not found: {COMPOSE_FILE}")

    logger.info(f"Starting docker-compose from {COMPOSE_FILE}")

    # Use our custom DockerCompose class
    # Enable pulling in CI environments (GitHub Actions, etc.) where images aren't cached
    is_ci = os.getenv("CI", "false").lower() == "true"
    compose = DockerComposeWithCleanup(
        filepath=str(COMPOSE_FILE.parent),
        compose_file_name=COMPOSE_FILE.name,
        pull=is_ci,  # Pull images in CI, use local ones in development
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

                # Temporal UI - wait for HTTP interface
                logger.info("Waiting for Temporal UI...")
                temporal_ui_port = compose.get_service_port("temporal-ui", 8080)
                _wait_for_http(f"http://localhost:{temporal_ui_port}", timeout=120)
                logger.info("Temporal UI is ready")

                # Code Confluence Flow Bridge - wait for port and add delay for startup
                logger.info("Waiting for Code Confluence Flow Bridge...")
                flow_bridge_port = compose.get_service_port("code-confluence-flow-bridge", 8000)
                _wait_for_port("localhost", flow_bridge_port, timeout=120)
                logger.info("Code Confluence Flow Bridge port is available, waiting 15s for startup...")
                time.sleep(15)
                logger.info("Code Confluence Flow Bridge is ready")

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
        "temporal_ui": docker_compose.get_service_port("temporal-ui", 8080),
        "code_confluence_flow_bridge": docker_compose.get_service_port("code-confluence-flow-bridge", 8000),
    }


@pytest.fixture(scope="session")
def test_database_tables(service_ports: Dict[str, int]):
    """Create database tables for testing."""
    # Create tables once per test session
    create_test_tables(service_ports["postgresql"])
    yield
    # Tables will be cleaned up when docker-compose volumes are removed

@pytest_asyncio.fixture(scope="session")
async def app_settings(service_ports):
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

    return EnvironmentSettings()

@pytest_asyncio.fixture(scope="session")
async def db_connections(app_settings):
    await init_db_connections(app_settings)   # runs on pytest’s session loop
    yield
    await dispose_db_connections()
    
    
@pytest.fixture(scope="session")
def test_client(service_ports: Dict[str, int], test_database_tables, db_connections) -> Iterator[TestClient]:
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

    # Wait briefly for app initialization
    with TestClient(app) as client:
        yield client
        # Allow time for async cleanup
        time.sleep(0.5)