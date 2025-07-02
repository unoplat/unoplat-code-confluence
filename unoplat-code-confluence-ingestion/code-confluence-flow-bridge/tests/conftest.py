"""
Centralized pytest fixtures for the code confluence flow bridge tests.

This conftest.py file provides shared fixtures that are automatically
discovered by pytest and made available to all test files.
"""

# Standard Library
import os
import shutil
import socket
import subprocess
import time
from pathlib import Path
from typing import Dict, Iterator

# Third Party
import docker
from pydantic import SecretStr
import pytest
import pytest_asyncio
import requests
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from loguru import logger
from testcontainers.compose import DockerCompose
from neomodel import adb
# Local
from src.code_confluence_flow_bridge.main import app
from src.code_confluence_flow_bridge.models.configuration.settings import EnvironmentSettings
from src.code_confluence_flow_bridge.processor.db.graph_db.code_confluence_graph import CodeConfluenceGraph
from src.code_confluence_flow_bridge.processor.db.postgres.db import AsyncSessionLocal
from tests.utils.db_cleanup import quick_cleanup

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
COMPOSE_FILE = PROJECT_ROOT / "docker-compose-dependencies-test.yml"


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
        # Actual volume names as they appear in Docker for test compose
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
        # Allow time for async cleanup of streaming responses
        time.sleep(0.5)


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
        env_file = Path(__file__).parent / '.env.testing'
        if env_file.exists():
            load_dotenv(env_file)
            token = os.getenv('GITHUB_PAT_TOKEN')
    
    if not token:
        pytest.fail("GITHUB_PAT_TOKEN not found in environment or .env.testing file")
        
    return token


# ──────────────────────────────────────────────────────────────────────────────
# DATABASE CLIENT FIXTURES FOR CLEANUP
# ──────────────────────────────────────────────────────────────────────────────

@pytest_asyncio.fixture(scope="session")
async def neo4j_client(service_ports: Dict[str, int]):
    """Session-scoped Neo4j client for database operations."""
    
    
    # Create environment settings from service ports
    env_settings = EnvironmentSettings(
        NEO4J_HOST="localhost",
        NEO4J_PORT=service_ports["neo4j"],
        NEO4J_USERNAME="neo4j",
        NEO4J_PASSWORD=SecretStr("password")
    )
    
    # Initialize and connect to Neo4j
    graph = CodeConfluenceGraph(env_settings)
    await graph.connect()
    
    # Yield the adb client for use in tests and cleanup
    yield adb
    
    # Session cleanup handled by docker_compose fixture


@pytest_asyncio.fixture(scope="session")
async def postgres_session(service_ports: Dict[str, int]):
    """Session-scoped PostgreSQL session for database operations."""
    # Environment variables are already set by test_client fixture
    # Just create a session from the existing AsyncSessionLocal
    async with AsyncSessionLocal() as session:
        yield session
        # Session will be closed automatically


