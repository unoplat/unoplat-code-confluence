# Standard Library
import os
from pathlib import Path
from typing import AsyncGenerator

# Third Party
import pytest
from loguru import logger
from testcontainers.neo4j import Neo4jContainer
from unoplat_code_confluence_commons.graph_models.code_confluence_codebase import CodeConfluenceCodebase
from unoplat_code_confluence_commons.graph_models.code_confluence_git_repository import CodeConfluenceGitRepository
from pydantic import SecretStr

# First Party
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_codebase import UnoplatCodebase
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_git_repository import UnoplatGitRepository
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_package_manager_metadata import UnoplatPackageManagerMetadata
from src.code_confluence_flow_bridge.models.configuration.settings import EnvironmentSettings
from src.code_confluence_flow_bridge.models.workflow.parent_child_clone_metadata import ParentChildCloneMetadata
from src.code_confluence_flow_bridge.processor.db.graph_db.code_confluence_graph_ingestion import CodeConfluenceGraphIngestion

# Constants for Neo4j container
NEO4J_VERSION = "5.26.0-community"  # Latest stable version
NEO4J_PASSWORD = "password"
NEO4J_PORT = 7687

@pytest.fixture(scope="session")
def neo4j_container():
    """Create and start Neo4j test container"""
    container = Neo4jContainer(
        image=f"neo4j:{NEO4J_VERSION}"
    )
    
    # Configure Neo4j auth and other settings
    container.with_env("NEO4J_AUTH", f"neo4j/{NEO4J_PASSWORD}")
    
    # Expose the bolt port
    container.with_exposed_ports(NEO4J_PORT)
    
    # Start container
    container.start()
    
    yield container

@pytest.fixture
def env_settings(neo4j_container: Neo4jContainer) -> EnvironmentSettings:
    """Create test environment settings from container"""
    # Get the mapped port for bolt
    neo4j_port = neo4j_container.get_exposed_port(NEO4J_PORT)
    
    return EnvironmentSettings(
        NEO4J_HOST=neo4j_container.get_container_host_ip(),
        NEO4J_PORT=neo4j_port,  # Use the mapped port instead of default
        NEO4J_USERNAME="neo4j",
        NEO4J_PASSWORD=SecretStr(NEO4J_PASSWORD),
        NEO4J_MAX_CONNECTION_LIFETIME=3600,
        NEO4J_MAX_CONNECTION_POOL_SIZE=50,
        NEO4J_CONNECTION_ACQUISITION_TIMEOUT=60
    )

@pytest.fixture
async def graph_ingestion(env_settings: EnvironmentSettings) -> AsyncGenerator[CodeConfluenceGraphIngestion, None]:
    """Create and initialize graph ingestion instance"""
    ingestion = CodeConfluenceGraphIngestion(code_confluence_env=env_settings)
    await ingestion.initialize()
    yield ingestion
    await ingestion.close()
        
        

@pytest.fixture
def sample_git_repo() -> UnoplatGitRepository:
    """Create sample git repository data"""
    return UnoplatGitRepository(
        repository_url="https://github.com/unoplat/unoplat-code-confluence",
        repository_name="unoplat-code-confluence",
        github_organization="unoplat",
        repository_metadata={
            "stars": 10,
            "forks": 5,
            "language": "Python"
        },
        readme="# Sample README",
        codebases=[
            UnoplatCodebase(
                name="unoplat_code_confluence",
                readme="# Sample Codebase README",
                local_path="/tmp/unoplat-code-confluence",
                package_manager_metadata=UnoplatPackageManagerMetadata(
                    programming_language="python",
                    package_manager="poetry"
                )
            )
        ]
    )

class TestCodeConfluenceGraphIngestion:
    """Test cases for CodeConfluenceGraphIngestion"""

    @pytest.mark.asyncio
    async def test_initialize_and_close(self, env_settings: EnvironmentSettings):
        """Test initialization and closing of graph connection"""
        ingestion = CodeConfluenceGraphIngestion(code_confluence_env=env_settings)
        
        # Test initialization
        await ingestion.initialize()
        assert ingestion.code_confluence_graph is not None
        
        # Test closing
        await ingestion.close()

    @pytest.mark.asyncio
    async def test_insert_git_repo(self, graph_ingestion: CodeConfluenceGraphIngestion, sample_git_repo: UnoplatGitRepository):
        """Test inserting git repository data"""
        # Get the actual instance from the generator
        async for ingestion in graph_ingestion:
            # Insert repository
            metadata = await ingestion.insert_code_confluence_git_repo(sample_git_repo)
            
            # Verify metadata
            assert isinstance(metadata, ParentChildCloneMetadata)
            assert metadata.repository_qualified_name == "unoplat_unoplat-code-confluence"
            assert len(metadata.codebase_qualified_name) == 1
            assert metadata.codebase_qualified_name[0] == "unoplat_unoplat-code-confluence_unoplat_code_confluence"

            # Verify repository node
            repo_nodes = await CodeConfluenceGitRepository.nodes.filter(
                qualified_name=metadata.repository_qualified_name
            ).all()
            assert len(repo_nodes) == 1
            repo_node: CodeConfluenceGitRepository = repo_nodes[0]
            assert repo_node.repository_url == sample_git_repo.repository_url
            assert repo_node.repository_name == sample_git_repo.repository_name
            

            # Verify codebase node
            codebase_nodes = await CodeConfluenceCodebase.nodes.filter(
                qualified_name=metadata.codebase_qualified_name[0]
            ).all()
            assert len(codebase_nodes) == 1
            codebase_node = codebase_nodes[0]
            assert codebase_node.name == sample_git_repo.codebases[0].name

            # Verify relationships
            repo_codebases = await repo_node.codebases.all()
            assert len(repo_codebases) == 1
            assert repo_codebases[0].qualified_name == metadata.codebase_qualified_name[0]

    @pytest.mark.asyncio
    async def test_error_handling(self, graph_ingestion: CodeConfluenceGraphIngestion):
        """Test error handling for invalid data"""
        invalid_repo = UnoplatGitRepository(
            repository_url="invalid-url",
            repository_name="",  # Invalid empty name
            github_organization="",  # Invalid empty org
            repository_metadata={},
            readme="",
            codebases=[]
        )

        with pytest.raises(Exception):
            await graph_ingestion.insert_code_confluence_git_repo(invalid_repo) 