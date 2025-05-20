from typing import AsyncGenerator, Generator, List

import pytest
from neomodel import config, adb, install_all_labels
from testcontainers.neo4j import Neo4jContainer

from unoplat_code_confluence_commons.graph_models import (
    CodeConfluenceGitRepository,
    CodeConfluenceCodebase,
    CodeConfluencePackage,
    CodeConfluenceClass,
    CodeConfluenceInternalFunction,
    CodeConfluencePackageManagerMetadata,
    CodeConfluenceFile
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
        name="main-codebase",
        local_path="/test/repo/path"
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
    """Test creating a complete hierarchy from repo to function with the new package -> file -> node structure."""
    # Create repository
    repo: CodeConfluenceGitRepository = await CodeConfluenceGitRepository(
        qualified_name="github.com/org/repo2",
        repository_url="https://github.com/org/repo2",
        repository_name="test-repo-2"
    ).save()
    
    # Create codebase
    codebase: CodeConfluenceCodebase = await CodeConfluenceCodebase(
        qualified_name="org/repo/main",
        name="main-codebase",
        local_path="/test/repo/path"
    ).save()
    
    # Create package
    package: CodeConfluencePackage = await CodeConfluencePackage(
        qualified_name="org/repo/main/package",
        name="test_package"
    ).save()
    
    # Create file
    file: CodeConfluenceFile = await CodeConfluenceFile(
        qualified_name="org/repo/main/package/path.py",
        file_path="/test/path.py",
        content="# Test file content",
        checksum="abcdef123456"
    ).save()
    
    # Create class
    class_node: CodeConfluenceClass = await CodeConfluenceClass(
        qualified_name="org/repo/main/package/TestClass",
        name="TestClass",
        file_path="/test/path.py",
        line_number=1
    ).save()
    
    # Create function
    function: CodeConfluenceInternalFunction = await CodeConfluenceInternalFunction(
        qualified_name="org/repo/main/package/TestClass/test_function",
        name="test_function",
        file_path="/test/path.py",
        line_number=2,
        return_type="str",
        docstring="Test function"
    ).save()
    
    # Connect nodes according to new hierarchy: repo -> codebase -> package -> file -> class -> function
    await repo.codebases.connect(codebase)
    await codebase.packages.connect(package)
    await package.files.connect(file)  # Package contains file
    await file.nodes.connect(class_node)  # File contains class node
    await class_node.file.connect(file)  # Class belongs to file (bidirectional)
    await class_node.functions.connect(function)  # Class contains function
    
    # Verify repository and connections
    found_repo = await CodeConfluenceGitRepository.nodes.get_or_none(repository_name="test-repo-2")
    assert found_repo is not None
    
    # Verify codebase connections
    repo_codebases: List[CodeConfluenceCodebase] = await found_repo.codebases.all()
    assert len(repo_codebases) == 1
    found_codebase: CodeConfluenceCodebase = repo_codebases[0]
    assert found_codebase.name == "main-codebase"
    
    # Verify package connections
    codebase_packages: List[CodeConfluencePackage] = await found_codebase.packages.all()
    assert len(codebase_packages) == 1
    found_package: CodeConfluencePackage = codebase_packages[0]
    assert found_package.name == "test_package"
    
    # Verify file connections 
    package_files: List[CodeConfluenceFile] = await found_package.files.all()
    assert len(package_files) == 1
    found_file: CodeConfluenceFile = package_files[0]
    assert found_file.file_path == "/test/path.py"
    
    # Verify bidirectional relationship between file and class
    # 1. File -> Class
    file_classes = await found_file.nodes.all()
    assert len(file_classes) == 1
    found_class: CodeConfluenceClass = file_classes[0]
    assert found_class.name == "TestClass"
    
    # 2. Class -> File
    class_file = await found_class.file.all()
    assert len(class_file) == 1
    assert class_file[0].file_path == "/test/path.py"
    assert class_file[0].qualified_name == found_file.qualified_name
    
    # Verify function in class
    class_functions: List[CodeConfluenceInternalFunction] = await found_class.functions.all()
    assert len(class_functions) == 1
    found_function: CodeConfluenceInternalFunction = class_functions[0]
    assert found_function.name == "test_function"
    
    # Test traversal from repo all the way to function
    # repo -> codebase -> package -> file -> class -> function
    # Need to await each step in the chain
    codebases = await found_repo.codebases.all()
    codebase = codebases[0]
    packages = await codebase.packages.all()
    package = packages[0]
    files = await package.files.all()
    file = files[0]
    nodes = await file.nodes.all()
    node = nodes[0]
    functions = await node.functions.all()
    function = functions[0]
    assert function.name == "test_function" 