import asyncio
from typing import AsyncGenerator, Generator, List

import pytest
from neomodel import config, adb, install_all_labels
from testcontainers.neo4j import Neo4jContainer
from asyncio import get_event_loop_policy

from unoplat_code_confluence_commons.graph_models import (
    CodeConfluenceGitRepository,
    CodeConfluenceCodebase,
    CodeConfluencePackage,
    CodeConfluenceClass,
    CodeConfluenceInternalFunction,
    CodeConfluencePackageManagerMetadata
)



@pytest.fixture(scope="session")
def neo4j_container() -> Generator[Neo4jContainer, None, None]:
    """Start Neo4j container and configure connection."""
    with Neo4jContainer("neo4j:5.24") as container:
        config.DATABASE_URL = (
            f"bolt://neo4j:password@{container.get_container_host_ip()}"
            f":{container.get_exposed_port(7687)}"
        )
        yield container


@pytest.fixture(autouse=True)
async def setup_database(neo4j_container: Neo4jContainer) -> AsyncGenerator[None, None]:
    """Setup database before each test and cleanup after."""
    await adb.cypher_query("MATCH (n) DETACH DELETE n")
    install_all_labels()
    yield
    await adb.cypher_query("MATCH (n) DETACH DELETE n")


@pytest.mark.asyncio(scope="session")
async def test_create_git_repository() -> None:
    """Test creating a git repository node."""
    repo = await CodeConfluenceGitRepository(
        qualified_name="github.com/org/repo",
        repository_url="https://github.com/org/repo",
        repository_name="test-repo",
        repository_metadata={"stars": 100}
    ).save()
    
    assert repo.repository_name == "test-repo"
    assert repo.repository_metadata["stars"] == 100
    
    found_repo = await CodeConfluenceGitRepository.nodes.get_or_none(repository_name="test-repo")
    assert found_repo is not None
    assert found_repo.repository_name == "test-repo"

@pytest.mark.asyncio(scope="session")
async def test_git_repository_codebase_relationship() -> None:
    """Test creating a git repository with a codebase."""
    repo: CodeConfluenceGitRepository = await CodeConfluenceGitRepository(
        qualified_name="github.com/org/repo",
        repository_url="https://github.com/org/repo",
        repository_name="test-repo"
    ).save()
    
    codebase: CodeConfluenceCodebase = await CodeConfluenceCodebase(
        qualified_name="org/repo/main",
        name="main-codebase"
    ).save()
    
    metadata: CodeConfluencePackageManagerMetadata = await CodeConfluencePackageManagerMetadata(
        qualified_name="org/repo/main/metadata",
        package_manager="pip",
        programming_language="python",
        package_name="test-package"
    ).save()
    
    await repo.codebases.connect(codebase)
    await codebase.package_manager_metadata.connect(metadata)
    
    connected_codebases: List[CodeConfluenceCodebase] = await repo.codebases.all()
    assert len(connected_codebases) == 1
    assert connected_codebases[0].name == "main-codebase"
    
    codebase_metadata = await connected_codebases[0].package_manager_metadata.all()
    assert len(codebase_metadata) == 1
    assert codebase_metadata[0].package_manager == "pip"


@pytest.mark.asyncio(scope="session")
async def test_complete_hierarchy() -> None:
    """Test creating a complete hierarchy from repo to function."""
    repo: CodeConfluenceGitRepository = await CodeConfluenceGitRepository(
        qualified_name="github.com/org/repo2",
        repository_url="https://github.com/org/repo2",
        repository_name="test-repo-2"
    ).save()
    
    codebase: CodeConfluenceCodebase = await CodeConfluenceCodebase(
        qualified_name="org/repo/main",
        name="main-codebase"
    ).save()
    
    package: CodeConfluencePackage = await CodeConfluencePackage(
        qualified_name="org/repo/main/package",
        name="test_package"
    ).save()
    
    class_node: CodeConfluenceClass = await CodeConfluenceClass(
        qualified_name="org/repo/main/package/TestClass",
        name="TestClass",
        file_path="/test/path.py",
        line_number=1
    ).save()
    
    function: CodeConfluenceInternalFunction = await CodeConfluenceInternalFunction(
        qualified_name="org/repo/main/package/TestClass/test_function",
        name="test_function",
        file_path="/test/path.py",
        line_number=2,
        return_type="str",
        docstring="Test function"
    ).save()
    
    await repo.codebases.connect(codebase)
    await codebase.packages.connect(package)
    await package.classes.connect(class_node)
    await class_node.functions.connect(function)
    
    found_repo = await CodeConfluenceGitRepository.nodes.get_or_none(repository_name="test-repo-2")
    assert found_repo is not None
    
    repo_codebases: List[CodeConfluenceCodebase] = await found_repo.codebases.all()
    assert len(repo_codebases) == 1
    found_codebase: CodeConfluenceCodebase = repo_codebases[0]
    assert found_codebase.name == "main-codebase"
    
    codebase_packages: List[CodeConfluencePackage] = await found_codebase.packages.all()
    assert len(codebase_packages) == 1
    found_package: CodeConfluencePackage = codebase_packages[0]
    assert found_package.name == "test_package"
    
    package_classes: List[CodeConfluenceClass] = await found_package.classes.all()
    assert len(package_classes) == 1
    found_class: CodeConfluenceClass = package_classes[0]
    assert found_class.name == "TestClass"
    
    class_functions: List[CodeConfluenceInternalFunction] = await found_class.functions.all()
    assert len(class_functions) == 1
    found_function: CodeConfluenceInternalFunction = class_functions[0]
    assert found_function.name == "test_function" 